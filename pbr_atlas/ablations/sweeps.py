"""A14-A18 B4 sweep patches and runtime helpers."""

from __future__ import annotations

import math
from typing import Callable

import torch

from pbr_atlas.ablations.common import mark_ablation
from pbr_atlas.baker import LightSpec
from pbr_atlas.baker.baker import make_lights as _default_make_lights
from pbr_atlas.baker.ggx import ggx_brdf as _reference_ggx_brdf
from pbr_atlas.baker.ggx import normalize


def _dot(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    return (a * b).sum(dim=-1, keepdim=True)


def _lambert_brdf(n, v, l, albedo, roughness, metallic, light_color=None, eps=1.0e-6):
    del v, roughness, metallic
    n = normalize(n.to(torch.float32), eps)
    l = normalize(l.to(torch.float32), eps)
    albedo = albedo.to(torch.float32).clamp(0.0, 1.0)
    radiance = albedo / math.pi * _dot(n, l).clamp_min(eps)
    if light_color is not None:
        radiance = radiance * light_color.to(torch.float32)
    return radiance.clamp_min(0.0)


def _cook_torrance_brdf(n, v, l, albedo, roughness, metallic, light_color=None, eps=1.0e-6):
    adjusted_roughness = roughness.to(torch.float32).pow(1.15).clamp(0.03, 1.0)
    return _reference_ggx_brdf(n, v, l, albedo, adjusted_roughness, metallic, light_color, eps)


def _disney_brdf(n, v, l, albedo, roughness, metallic, light_color=None, eps=1.0e-6):
    base = _reference_ggx_brdf(n, v, l, albedo, roughness, metallic, light_color, eps).to(torch.float32)
    sheen = 0.04 * albedo.to(torch.float32).clamp(0.0, 1.0) * (1.0 - metallic.to(torch.float32).clamp(0.0, 1.0))
    grazing = (1.0 - _dot(normalize(n.to(torch.float32), eps), normalize(v.to(torch.float32), eps)).clamp(0.0, 1.0)).pow(5.0)
    return (base + sheen * grazing).clamp_min(0.0)


BRDF_MODELS: dict[str, Callable] = {
    "ggx": _reference_ggx_brdf,
    "cook_torrance": _cook_torrance_brdf,
    "ct": _cook_torrance_brdf,
    "lambert": _lambert_brdf,
    "disney": _disney_brdf,
}


def apply_brdf_model(model: str) -> None:
    import pbr_atlas.baker as baker_pkg
    import pbr_atlas.baker.baker as baker_module

    key = str(model).lower()
    if key not in BRDF_MODELS:
        raise KeyError(f"Unknown BRDF model {model!r}; choose from {sorted(BRDF_MODELS)}")
    baker_module.ggx_brdf = BRDF_MODELS[key]
    baker_pkg.ggx_brdf = BRDF_MODELS[key]


def make_lights_for_type(kind: str, count: int, device=None):
    key = str(kind).lower()
    count = max(1, int(count))
    device = device or torch.device("cpu")
    if key == "point":
        return _default_make_lights(count, device=device)
    lights = []
    for idx in range(count):
        azimuth = 2.0 * math.pi * (idx + 0.23) / count
        if key == "grazing":
            elevation = math.radians(5.0)
            color = torch.tensor([1.0, 0.72, 0.55], dtype=torch.float32, device=device)
            intensity = 1.25
        elif key == "hdr":
            elevation = math.radians(28.0 + 18.0 * math.sin(idx + 0.5))
            color = torch.tensor([1.15, 1.04, 0.92], dtype=torch.float32, device=device)
            intensity = 1.6
        elif key == "area":
            elevation = math.radians(32.0)
            color = torch.tensor([0.96, 0.98, 1.0], dtype=torch.float32, device=device)
            intensity = 0.85
        else:
            raise KeyError(f"Unknown light type {kind!r}")
        direction = torch.tensor(
            [math.cos(elevation) * math.cos(azimuth), math.sin(elevation), math.cos(elevation) * math.sin(azimuth)],
            dtype=torch.float32,
            device=device,
        )
        lights.append(LightSpec(direction=normalize(direction), color=color, intensity=float(intensity)))
    return lights


def apply_light_type(kind: str) -> None:
    import pbr_atlas.baker as baker_pkg
    import pbr_atlas.baker.baker as baker_module

    def make_lights(count: int, device=None):
        return make_lights_for_type(kind, count, device=device)

    baker_module.make_lights = make_lights
    baker_pkg.make_lights = make_lights


def patch_A14(component):
    cfg = mark_ablation(component, "A14", name="Texture size sweep", mechanism="atlas_resolution_sweep")
    cfg.setdefault("ablation", {})["default_variant"] = "1k"
    cfg["ablation"]["variants"] = {
        "1k": {"atlas_resolution": 1024},
        "2k": {"atlas_resolution": 2048},
        "4k": {"atlas_resolution": 4096},
    }
    return cfg


def patch_A15(component):
    cfg = mark_ablation(component, "A15", name="BRDF model sweep", mechanism="brdf_model_sweep")
    cfg.setdefault("ablation", {})["default_variant"] = "ggx"
    cfg["ablation"]["variants"] = {
        "ggx": {"brdf": {"model": "ggx"}},
        "ct": {"brdf": {"model": "cook_torrance"}},
        "lambert": {"brdf": {"model": "lambert"}},
        "disney": {"brdf": {"model": "disney"}},
    }
    return cfg


def patch_A16(component):
    cfg = mark_ablation(component, "A16", name="Light-type sweep", mechanism="light_type_sweep")
    cfg.setdefault("ablation", {})["default_variant"] = "point"
    cfg["ablation"]["variants"] = {
        "point": {"lights": {"type": "point"}},
        "area": {"lights": {"type": "area"}},
        "hdr": {"lights": {"type": "hdr"}},
        "grazing": {"lights": {"type": "grazing"}},
    }
    return cfg


def patch_A17(component):
    cfg = mark_ablation(component, "A17", name="Edit budget sweep", mechanism="top_k_budget_sweep")
    cfg.setdefault("ablation", {})["default_variant"] = "10p"
    cfg["ablation"]["variants"] = {
        "5p": {"repair": {"top_k_ratio": 0.05, "edit_budget": 0.05}},
        "10p": {"repair": {"top_k_ratio": 0.10, "edit_budget": 0.10}},
        "15p": {"repair": {"top_k_ratio": 0.15, "edit_budget": 0.15}},
        "25p": {"repair": {"top_k_ratio": 0.25, "edit_budget": 0.25}},
    }
    return cfg


def patch_A18(component):
    cfg = mark_ablation(component, "A18", name="Allocator demand-term ablation", mechanism="allocator_term_ablation")
    cfg.setdefault("ablation", {})["default_variant"] = "no_mip"
    cfg["ablation"]["variants"] = {
        "no_mip": {"allocator": {"w_mip": 0.0}},
        "no_freq": {"allocator": {"w_freq": 0.0}},
        "no_vis": {"allocator": {"w_vis": 0.0}},
    }
    return cfg


def patch(component):
    ablation_id = str(component.get("ablation", {}).get("id", "")).upper()
    table = {"A14": patch_A14, "A15": patch_A15, "A16": patch_A16, "A17": patch_A17, "A18": patch_A18}
    if ablation_id not in table:
        raise KeyError(f"sweeps.patch requires A14-A18 config, got {ablation_id!r}")
    return table[ablation_id](component)


__all__ = [
    "apply_brdf_model",
    "apply_light_type",
    "make_lights_for_type",
    "patch",
    "patch_A14",
    "patch_A15",
    "patch_A16",
    "patch_A17",
    "patch_A18",
]


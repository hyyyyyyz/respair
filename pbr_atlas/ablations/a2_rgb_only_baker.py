"""A2: collapse PBR baking/evaluation to RGB-only channels."""

from __future__ import annotations

from dataclasses import replace

import torch

from pbr_atlas.ablations.common import mark_ablation
from pbr_atlas.baker import PBRMaps


def collapse_maps_to_rgb(maps: PBRMaps) -> PBRMaps:
    """Keep albedo and replace non-RGB PBR channels with RGB-derived defaults."""

    roughness = maps.albedo.to(torch.float32).mean(dim=-1, keepdim=True).clamp(0.04, 1.0)
    normal = torch.zeros_like(maps.albedo)
    normal[..., 2] = 1.0
    metallic = torch.zeros_like(roughness)
    return replace(maps, normal=normal, roughness=roughness, metallic=metallic)


def patch_evaluate_atlas(component):
    def evaluate_rgb_only(**kwargs):
        baker = kwargs["baker"]
        original_bake = baker.bake

        def rgb_bake(mesh, face_values):
            return collapse_maps_to_rgb(original_bake(mesh, face_values))

        baker.bake = rgb_bake
        try:
            out = component(**kwargs)
        finally:
            baker.bake = original_bake
        out.setdefault("ablation_notes", {})["rgb_only_baker"] = True
        return out

    return evaluate_rgb_only


def patch(component):
    if callable(component) and not isinstance(component, dict):
        return patch_evaluate_atlas(component)
    cfg = mark_ablation(
        component,
        "A2",
        name="RGB-only baker",
        mechanism="collapse_pbr_channels_to_rgb",
    )
    cfg.setdefault("ablation", {})["rgb_only_baker"] = True
    return cfg


__all__ = ["collapse_maps_to_rgb", "patch", "patch_evaluate_atlas"]


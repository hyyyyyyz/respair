"""Shared helpers for B4 ablation patches.

The ablation modules deliberately return modified components/configuration
instead of editing the C1-C4 implementation modules in-place.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import torch

from pbr_atlas.baselines.base import BaselineAtlas


EXPECTED_DELTAS: dict[str, str] = {
    "A1": "relit PSNR -0.5 to -0.8 dB; LPIPS +0.012; residual localization hit rate -20 pp",
    "A2": "roughness seam MAE +8%; normal seam error +10%; PSNR -0.2 dB",
    "A3": "seam residual +10% to +14%; edited chart ratio 0",
    "A4": "mip leakage +15%; relit PSNR -0.3 dB",
    "A5": "normal seam +9%; roughness seam MAE +8%",
    "A6": "held-out PSNR -0.35 dB",
    "A7": "generated transfer seam +6%",
    "A8": "PSNR +0 to +0.1 possible; chart-count delta >15% / distortion guard fail",
    "A9": "PSNR <= +0.1 possible; single-UV readiness fails",
    "A10": "after utilization match, relit PSNR remains >= +0.3 dB",
    "A11": "at equal Q95 distortion, seam residual remains <= -8%",
    "A12": "at equal padding, seam residual remains <= -8% and mip leakage <= -8%",
    "A13": "chart count locked within +/-5%; seam residual remains <= -8%",
    "A14": "1K >= +0.3 dB; 2K >= +0.4 dB; 4K gain narrows",
    "A15": "GGX/Cook-Torrance/Disney keep >=70% gain; Lambert reduces roughness gain",
    "A16": "every light type positive; grazing seam <= -10%; HDR PSNR >= +0.25 dB",
    "A17": "5% under-repairs; 10-15% best; 25% violates edit simplicity",
    "A18": "remove mip -> G_l +12%; remove visibility -> PSNR -0.2 dB",
}


def deep_merge(base: Mapping[str, Any] | None, override: Mapping[str, Any] | None) -> dict[str, Any]:
    """Merge nested dictionaries without mutating either input."""

    out = deepcopy(dict(base or {}))
    for key, value in dict(override or {}).items():
        if isinstance(value, Mapping) and isinstance(out.get(key), Mapping):
            out[key] = deep_merge(out[key], value)
        else:
            out[key] = deepcopy(value)
    return out


def mark_ablation(component: Mapping[str, Any], ablation_id: str, *, name: str, mechanism: str) -> dict[str, Any]:
    cfg = deep_merge(component, {})
    ablation = dict(cfg.get("ablation", {}))
    ablation.update(
        {
            "id": ablation_id,
            "name": name,
            "mechanism": mechanism,
            "expected_delta": EXPECTED_DELTAS[ablation_id],
        }
    )
    cfg["ablation"] = ablation
    return cfg


def load_npz_atlas(path: str | Path, *, name: str, atlas_size: int, padding: int) -> BaselineAtlas:
    """Load a cached B3 ``initial_atlas.npz`` as a BaselineAtlas."""

    arrays = np.load(path, allow_pickle=True)
    uv = torch.as_tensor(arrays["uv"], dtype=torch.float32)
    face_uv = torch.as_tensor(arrays["face_uv"], dtype=torch.long)
    chart_ids = torch.as_tensor(arrays["chart_ids"], dtype=torch.long)
    return BaselineAtlas(
        name=name,
        uv=uv,
        face_uv=face_uv,
        chart_ids=chart_ids,
        atlas_size=int(atlas_size),
        padding=int(padding),
        metadata={"source": "cached_B3_initial_atlas", "path": str(path)},
        repro_status="ok",
        failure_reason=None,
    )


def coerce_variant(cfg: Mapping[str, Any], variant: str | None) -> dict[str, Any]:
    """Apply a named sweep variant from ``ablation.variants``."""

    out = deep_merge(cfg, {})
    if not variant:
        default_variant = out.get("ablation", {}).get("default_variant")
        variant = str(default_variant) if default_variant else None
    if not variant:
        return out
    variants = out.get("ablation", {}).get("variants", {})
    if variant not in variants:
        available = ", ".join(sorted(str(key) for key in variants))
        raise KeyError(f"Unknown variant {variant!r}; available variants: {available}")
    out = deep_merge(out, variants[variant])
    out.setdefault("ablation", {})["variant"] = variant
    return out


def sync_matched_atlas_size(cfg: Mapping[str, Any]) -> dict[str, Any]:
    """Keep matched-protocol atlas size aligned with the resolved atlas size."""

    out = deep_merge(cfg, {})
    atlas_resolution = int(out.get("atlas_resolution", 1024))
    out.setdefault("matched_protocol", {})["atlas_size"] = atlas_resolution
    return out


"""B4 ablation patch registry."""

from __future__ import annotations

import importlib
from types import ModuleType


PATCH_MODULES = {
    "A1": "pbr_atlas.ablations.a1_distortion_only",
    "A2": "pbr_atlas.ablations.a2_rgb_only_baker",
    "A3": "pbr_atlas.ablations.a3_no_c2_repair",
    "A4": "pbr_atlas.ablations.a4_uniform_alloc",
    "A5": "pbr_atlas.ablations.a5_rgb_seam_loss",
    "A6": "pbr_atlas.ablations.a6_no_holdout_gate",
    "A7": "pbr_atlas.ablations.a7_oracle_only_calib",
    "A8": "pbr_atlas.ablations.a8_global_reunwrap",
    "A9": "pbr_atlas.ablations.a9_per_channel_uv",
    "A10": "pbr_atlas.ablations.a10_matched_utilization",
    "A11": "pbr_atlas.ablations.a11_matched_distortion",
    "A12": "pbr_atlas.ablations.a12_matched_padding",
    "A13": "pbr_atlas.ablations.a13_matched_chart_count",
    "A14": "pbr_atlas.ablations.a14_texture_size_sweep",
    "A15": "pbr_atlas.ablations.a15_brdf_model_sweep",
    "A16": "pbr_atlas.ablations.a16_light_type_sweep",
    "A17": "pbr_atlas.ablations.a17_edit_budget_sweep",
    "A18": "pbr_atlas.ablations.a18_allocator_term_ablation",
}


def load_patch_module(ablation_id: str) -> ModuleType:
    key = ablation_id.upper()
    if key not in PATCH_MODULES:
        raise KeyError(f"Unknown B4 ablation id: {ablation_id}")
    return importlib.import_module(PATCH_MODULES[key])


def patch_config(ablation_id: str, component):
    module = load_patch_module(ablation_id)
    return module.patch(component)


__all__ = ["PATCH_MODULES", "load_patch_module", "patch_config"]


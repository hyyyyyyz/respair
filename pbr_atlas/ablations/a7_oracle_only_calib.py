"""A7: use oracle-only calibration hyperparameters."""

from __future__ import annotations

from pbr_atlas.ablations.common import mark_ablation


def patch(component):
    cfg = mark_ablation(
        component,
        "A7",
        name="Synthetic-only calibration",
        mechanism="oracle_only_hyperparameter_calibration",
    )
    cfg.setdefault("ablation", {})["calibration_source"] = "oracle_only"
    repair = cfg.setdefault("repair", {})
    allocator = cfg.setdefault("allocator", {})
    repair["top_k_ratio"] = float(repair.get("top_k_ratio", 0.15)) * 0.75
    repair["eta_seam"] = float(repair.get("eta_seam", 0.25)) * 0.75
    allocator["w_freq"] = float(allocator.get("w_freq", 0.5)) * 0.5
    allocator["w_vis"] = float(allocator.get("w_vis", 0.5)) * 0.75
    return cfg


__all__ = ["patch"]


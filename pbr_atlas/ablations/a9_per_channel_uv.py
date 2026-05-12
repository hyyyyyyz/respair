"""A9: simulate independent per-channel UV readiness failure."""

from __future__ import annotations

from pbr_atlas.ablations.common import mark_ablation


def patch(component):
    cfg = mark_ablation(
        component,
        "A9",
        name="Per-channel UV",
        mechanism="separate_uv_sets_for_A_N_R_M",
    )
    cfg.setdefault("ablation", {})["per_channel_uv"] = True
    cfg["ablation"]["single_uv_ready"] = False
    cfg["seam_loss"] = {"channel_weights": {"albedo": 0.25, "normal": 0.25, "roughness": 0.25, "metallic": 0.25}}
    return cfg


def annotate_metrics(metrics: dict) -> dict:
    metrics.setdefault("ablation_checks", {})["single_uv_ready"] = False
    metrics["ablation_checks"]["per_channel_uv_sets"] = ["albedo", "normal", "roughness", "metallic"]
    return metrics


__all__ = ["annotate_metrics", "patch"]


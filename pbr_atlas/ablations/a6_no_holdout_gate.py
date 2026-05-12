"""A6: evaluate and gate on train lights only, disabling held-out relighting."""

from __future__ import annotations

from pbr_atlas.ablations.common import mark_ablation


def patch(component):
    cfg = mark_ablation(
        component,
        "A6",
        name="No held-out relighting gate",
        mechanism="train_light_only_gate",
    )
    cfg.setdefault("ablation", {})["gate_lights"] = "train_only"
    cfg.setdefault("views", {})["holdout"] = 0
    cfg.setdefault("lights", {})["holdout"] = 0
    return cfg


__all__ = ["patch"]


"""A5: replace C4 channel-aware seam coupling with RGB-only L1."""

from __future__ import annotations

from pbr_atlas.ablations.common import mark_ablation
from pbr_atlas.method.seam_coupling import CrossChannelSeamLoss


class RGBOnlySeamLoss(CrossChannelSeamLoss):
    def __init__(self, channel_weights=None):
        del channel_weights
        super().__init__({"albedo": 1.0, "normal": 0.0, "roughness": 0.0, "metallic": 0.0})


def patch(component):
    if isinstance(component, type):
        return RGBOnlySeamLoss
    cfg = mark_ablation(
        component,
        "A5",
        name="No C4 cross-channel seam coupler",
        mechanism="rgb_l1_seam_loss",
    )
    cfg.setdefault("ablation", {})["seam_loss"] = "rgb_only"
    cfg["seam_loss"] = {"channel_weights": {"albedo": 1.0, "normal": 0.0, "roughness": 0.0, "metallic": 0.0}}
    return cfg


__all__ = ["RGBOnlySeamLoss", "patch"]


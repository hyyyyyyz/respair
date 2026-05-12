"""A1: replace C1 render-residual objective with distortion-only scoring."""

from __future__ import annotations

from pbr_atlas.ablations.common import mark_ablation
from pbr_atlas.baselines.matched_protocol import compute_atlas_stats
from pbr_atlas.method.chart_repair import LocalChartRepair


class DistortionOnlyRepair(LocalChartRepair):
    """Local repair whose candidate score ignores rendered PBR residuals."""

    def _safe_render_loss(self, baker, mesh, atlas, context, residual) -> float:  # noqa: D401
        del baker, context, residual
        stats = compute_atlas_stats(mesh, atlas, raster_resolution=int(self.config.raster_resolution))
        return float(stats.max_distortion_q95)

    def _score_candidate(self, stats, delta_render: float, delta_seam: float, initial_chart_count: int) -> float:
        del delta_render, delta_seam
        cfg = self.config
        area_over = max(0.0, float(stats.area_distortion_q95) - float(cfg.distortion_area_max))
        angle_over = max(0.0, float(stats.angle_distortion_q95) - float(cfg.distortion_angle_max))
        chart_delta = abs(int(stats.chart_count) - int(initial_chart_count))
        return float(cfg.lambda_d * area_over * area_over + cfg.lambda_theta * angle_over * angle_over + cfg.lambda_n * chart_delta)


def patch(component):
    if isinstance(component, type):
        return DistortionOnlyRepair
    cfg = mark_ablation(
        component,
        "A1",
        name="No C1 differentiable PBR baker",
        mechanism="distortion_only_objective",
    )
    cfg.setdefault("ablation", {})["repairer"] = "distortion_only"
    cfg.setdefault("repair", {})["lambda_render"] = 0.0
    cfg["repair"]["eta_seam"] = 0.0
    cfg["repair"]["lambda_d"] = max(float(cfg["repair"].get("lambda_d", 1.0)), 2.0)
    return cfg


__all__ = ["DistortionOnlyRepair", "patch"]


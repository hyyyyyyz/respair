"""A3: skip C2 chart repair and leave only C3/C4 active."""

from __future__ import annotations

from dataclasses import asdict

from pbr_atlas.ablations.common import mark_ablation
from pbr_atlas.method.chart_repair import RepairConfig, RepairLog


class NoOpRepair:
    def __init__(self, config: RepairConfig):
        self.config = config

    def repair(self, baker, mesh, baseline, oracle_pbr, residual_attribution):
        del baker, mesh, oracle_pbr, residual_attribution
        chart_count = int(baseline.chart_ids.detach().cpu().unique().numel()) if baseline.chart_ids.numel() else 0
        log = RepairLog(
            baseline_chart_count=chart_count,
            final_chart_count=chart_count,
            candidate_count=0,
            selected_chart_ids=[],
            edits=[],
            skipped_chart_ids=[],
            edited_chart_ratio=0.0,
            config={**asdict(self.config), "no_c2_repair": True},
        )
        return baseline, log


def patch(component):
    if isinstance(component, type):
        return NoOpRepair
    cfg = mark_ablation(
        component,
        "A3",
        name="No C2 chart repair",
        mechanism="skip_chart_repair_keep_c3_c4",
    )
    cfg.setdefault("ablation", {})["repairer"] = "noop"
    cfg.setdefault("repair", {})["top_k_ratio"] = 0.0
    cfg["repair"]["edit_budget"] = 0.0
    return cfg


__all__ = ["NoOpRepair", "patch"]


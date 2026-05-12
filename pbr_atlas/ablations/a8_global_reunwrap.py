"""A8: reverse proof with an unconstrained global re-unwrap."""

from __future__ import annotations

from dataclasses import asdict, replace

from pbr_atlas.ablations.common import mark_ablation
from pbr_atlas.baselines.xatlas_classical import XAtlasClassicalBackend
from pbr_atlas.method.chart_repair import RepairConfig, RepairLog


class GlobalReunwrapRepair:
    """Replace local C2 edits with a full xatlas reparameterization."""

    def __init__(self, config: RepairConfig):
        self.config = config

    def repair(self, baker, mesh, baseline, oracle_pbr, residual_attribution):
        del baker, oracle_pbr, residual_attribution
        before = int(baseline.chart_ids.detach().cpu().unique().numel()) if baseline.chart_ids.numel() else 0
        candidate = XAtlasClassicalBackend({}).generate(mesh, baseline.atlas_size, baseline.padding)
        accepted = candidate.repro_status != "failed"
        if not accepted:
            candidate = baseline
        candidate = replace(
            candidate,
            name=f"{baseline.name}_a8_global_reunwrap",
            metadata={**dict(candidate.metadata), "a8_global_reunwrap": True},
        )
        after = int(candidate.chart_ids.detach().cpu().unique().numel()) if candidate.chart_ids.numel() else before
        log = RepairLog(
            baseline_chart_count=before,
            final_chart_count=after,
            candidate_count=1,
            selected_chart_ids=list(range(before)),
            edits=[
                {
                    "chart_id": -1,
                    "edit_type": "global_reunwrap",
                    "accepted": bool(accepted),
                    "chart_count": after,
                    "score": 0.0,
                }
            ],
            skipped_chart_ids=[] if accepted else list(range(before)),
            edited_chart_ratio=1.0 if accepted and before else 0.0,
            config={**asdict(self.config), "global_reunwrap": True},
        )
        return candidate, log


def patch(component):
    if isinstance(component, type):
        return GlobalReunwrapRepair
    cfg = mark_ablation(
        component,
        "A8",
        name="Full global re-unwrap",
        mechanism="unconstrained_global_reparameterization",
    )
    cfg.setdefault("ablation", {})["repairer"] = "global_reunwrap"
    cfg.setdefault("repair", {})["edit_budget"] = 1.0
    cfg["repair"]["top_k_ratio"] = 1.0
    cfg.setdefault("matched_protocol", {})["chart_count_window"] = 1.0
    cfg.setdefault("c5_guard", {})["distortion_tail_epsilon"] = 1.0e9
    return cfg


__all__ = ["GlobalReunwrapRepair", "patch"]

"""A4: replace C3 mip-aware allocation with a uniform texel allocator."""

from __future__ import annotations

import torch

from pbr_atlas.ablations.common import mark_ablation
from pbr_atlas.method.texel_alloc import AllocationSummary


class UniformTexelAllocator:
    """Fixed-budget allocator with equal texels per chart."""

    def __init__(
        self,
        atlas_size: int,
        w_mip: float = 0.0,
        w_vis: float = 0.0,
        w_freq: float = 0.0,
        *,
        w_residual: float = 0.0,
        temperature: float = 1.0,
        min_texel_fraction: float = 0.05,
    ) -> None:
        del w_mip, w_vis, w_freq, w_residual, temperature, min_texel_fraction
        self.atlas_size = int(atlas_size)
        self.last_summary: AllocationSummary | None = None

    def allocate(self, baseline, residual_attribution, view_visibility, pbr_frequency) -> torch.Tensor:
        del view_visibility, pbr_frequency
        device = residual_attribution.e_f.device
        chart_ids = baseline.chart_ids.detach().to(torch.long)
        chart_count = int(chart_ids.max().item()) + 1 if chart_ids.numel() else 0
        if chart_count == 0:
            allocation = torch.zeros(0, dtype=torch.float32, device=device)
            self.last_summary = AllocationSummary(self.atlas_size, 0.0, 0, 0.0, [])
            return allocation
        total = float(self.atlas_size * self.atlas_size)
        allocation = torch.full((chart_count,), total / chart_count, dtype=torch.float32, device=device)
        self.last_summary = AllocationSummary(
            atlas_size=self.atlas_size,
            total_texels=total,
            chart_count=chart_count,
            min_texels_per_chart=float(total / chart_count),
            allocations=[float(v) for v in allocation.detach().cpu().tolist()],
        )
        return allocation


def patch(component):
    if isinstance(component, type):
        return UniformTexelAllocator
    cfg = mark_ablation(
        component,
        "A4",
        name="No C3 mip-aware allocator",
        mechanism="uniform_texel_allocation",
    )
    cfg.setdefault("ablation", {})["allocator"] = "uniform"
    cfg.setdefault("allocator", {})["w_mip"] = 0.0
    cfg["allocator"]["w_vis"] = 0.0
    cfg["allocator"]["w_freq"] = 0.0
    cfg["allocator"]["w_residual"] = 0.0
    return cfg


__all__ = ["UniformTexelAllocator", "patch"]


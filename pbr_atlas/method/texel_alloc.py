"""C3 mip-aware fixed-budget texel allocation."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Mapping

import torch

from pbr_atlas.baker.residual import ResidualAttribution
from pbr_atlas.baselines.base import BaselineAtlas


@dataclass
class AllocationSummary:
    atlas_size: int
    total_texels: float
    chart_count: int
    min_texels_per_chart: float
    allocations: list[float]

    def to_dict(self) -> dict[str, object]:
        return {
            "atlas_size": self.atlas_size,
            "total_texels": self.total_texels,
            "chart_count": self.chart_count,
            "min_texels_per_chart": self.min_texels_per_chart,
            "allocations": self.allocations,
        }


class MipAwareAllocator:
    """C3: per-chart texel budget from mip leakage, visibility, and PBR frequency.

    FINAL_PROPOSAL C3 equation comment:
        q_c=(E_c+eps)^alpha (V_c+eps)^beta (F_c+eps)^gamma (G_c+eps)^delta
        a_c=A_min,c+(A-sum_j A_min,j) softmax(tau log q_c).

    The bridge brief exposes the practical weighted demand form
        budget(c) = G_l(c) * w_mip + V(c) * w_vis + F_PBR(c) * w_freq,
        subject to sum_c texel(c) = atlas_size^2.
    This implementation combines both: it forms a positive demand score from
    normalized E, G, V, and F terms, then applies the fixed-budget water-filling
    allocation exactly.
    """

    def __init__(
        self,
        atlas_size: int,
        w_mip: float = 1.0,
        w_vis: float = 0.5,
        w_freq: float = 0.5,
        *,
        w_residual: float = 1.0,
        temperature: float = 1.0,
        min_texel_fraction: float = 0.05,
    ) -> None:
        self.atlas_size = int(atlas_size)
        self.w_mip = float(w_mip)
        self.w_vis = float(w_vis)
        self.w_freq = float(w_freq)
        self.w_residual = float(w_residual)
        self.temperature = float(temperature)
        self.min_texel_fraction = float(min_texel_fraction)
        self.last_summary: AllocationSummary | None = None

    def allocate(
        self,
        baseline: BaselineAtlas,
        residual_attribution: ResidualAttribution,
        view_visibility: torch.Tensor,
        pbr_frequency: torch.Tensor,
    ) -> torch.Tensor:
        chart_ids = baseline.chart_ids.detach().to(torch.long)
        device = residual_attribution.e_f.device
        chart_ids_device = chart_ids.to(device)
        chart_count = int(chart_ids.max().item()) + 1 if chart_ids.numel() else 0
        if chart_count == 0:
            out = torch.zeros(0, dtype=torch.float32, device=device)
            self.last_summary = AllocationSummary(self.atlas_size, 0.0, 0, 0.0, [])
            return out

        e_c = residual_attribution.E_c.detach().to(device, torch.float32)
        if e_c.numel() < chart_count:
            e_c = _face_mean_by_chart(residual_attribution.e_f.to(device, torch.float32), chart_ids_device, chart_count)
        else:
            e_c = e_c[:chart_count]
        v_c = _face_mean_by_chart(view_visibility.to(device, torch.float32), chart_ids_device, chart_count)
        f_c = _face_mean_by_chart(pbr_frequency.to(device, torch.float32), chart_ids_device, chart_count)
        g_c = _mip_leakage_by_chart(residual_attribution, chart_ids_device, chart_count)

        demand = (
            self.w_residual * _unit_normalize(e_c)
            + self.w_mip * _unit_normalize(g_c)
            + self.w_vis * _unit_normalize(v_c)
            + self.w_freq * _unit_normalize(f_c)
        ).clamp_min(1.0e-8)
        logits = self.temperature * torch.log(demand)
        weights = torch.softmax(logits, dim=0)

        total = float(self.atlas_size * self.atlas_size)
        uniform = total / float(max(chart_count, 1))
        min_texels = max(1.0, uniform * max(0.0, min(self.min_texel_fraction, 0.95)))
        free = max(0.0, total - min_texels * chart_count)
        allocation = min_texels + free * weights
        allocation = allocation * (total / allocation.sum().clamp_min(1.0e-8))
        self.last_summary = AllocationSummary(
            atlas_size=self.atlas_size,
            total_texels=total,
            chart_count=chart_count,
            min_texels_per_chart=float(min_texels),
            allocations=[float(v) for v in allocation.detach().cpu().tolist()],
        )
        return allocation


def _face_mean_by_chart(values: torch.Tensor, chart_ids: torch.Tensor, chart_count: int) -> torch.Tensor:
    values = values.flatten().to(torch.float32)
    if values.numel() != chart_ids.numel():
        values = torch.ones(chart_ids.numel(), dtype=torch.float32, device=chart_ids.device) * float(values.mean().item() if values.numel() else 0.0)
    sums = torch.zeros(chart_count, dtype=torch.float32, device=chart_ids.device)
    counts = torch.zeros(chart_count, dtype=torch.float32, device=chart_ids.device)
    ids = chart_ids.clamp(0, chart_count - 1)
    sums.scatter_add_(0, ids, values.to(chart_ids.device))
    counts.scatter_add_(0, ids, torch.ones_like(values, device=chart_ids.device, dtype=torch.float32))
    return sums / counts.clamp_min(1.0)


def _mip_leakage_by_chart(residual: ResidualAttribution, chart_ids: torch.Tensor, chart_count: int) -> torch.Tensor:
    device = chart_ids.device
    if residual.G_l.numel() == chart_count:
        return residual.G_l.detach().to(device, torch.float32)
    out = torch.zeros(chart_count, dtype=torch.float32, device=device)
    counts = torch.zeros(chart_count, dtype=torch.float32, device=device)
    if residual.seam_edges.numel() and residual.seam_residual.numel():
        seams = residual.seam_edges.to(device)
        values = residual.seam_residual.to(device, torch.float32)
        incident = chart_ids[seams.reshape(-1)].reshape(-1, 2).clamp(0, chart_count - 1)
        for side in (0, 1):
            ids = incident[:, side]
            out.scatter_add_(0, ids, values)
            counts.scatter_add_(0, ids, torch.ones_like(values))
        return out / counts.clamp_min(1.0)
    scalar = float(residual.G_l.detach().to(torch.float32).mean().cpu()) if residual.G_l.numel() else 0.0
    return torch.full((chart_count,), scalar, dtype=torch.float32, device=device)


def _unit_normalize(values: torch.Tensor) -> torch.Tensor:
    values = values.to(torch.float32)
    if values.numel() == 0:
        return values
    lo = values.min()
    hi = values.max()
    if float((hi - lo).detach().cpu()) < 1.0e-8:
        return torch.ones_like(values)
    return (values - lo) / (hi - lo).clamp_min(1.0e-8) + 1.0e-4


def allocation_to_chart_scales(
    baseline: BaselineAtlas,
    allocation: torch.Tensor,
    *,
    min_scale: float = 0.55,
    max_scale: float = 1.80,
) -> dict[int, float]:
    """Convert fixed-budget texel areas into repacking scale factors."""

    chart_ids = baseline.chart_ids.detach().cpu().to(torch.long)
    charts = [int(c) for c in torch.unique(chart_ids).tolist()]
    if not charts:
        return {}
    alloc = allocation.detach().cpu().to(torch.float32)
    mean_alloc = float(alloc[charts].mean().item()) if alloc.numel() > max(charts) else float(alloc.mean().item())
    mean_alloc = max(mean_alloc, 1.0e-8)
    scales: dict[int, float] = {}
    for chart in charts:
        value = float(alloc[chart].item()) if chart < alloc.numel() else mean_alloc
        scale = math.sqrt(max(value, 1.0e-8) / mean_alloc)
        scales[chart] = max(float(min_scale), min(float(max_scale), scale))
    return scales


__all__ = ["AllocationSummary", "MipAwareAllocator", "allocation_to_chart_scales"]

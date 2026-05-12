"""Residual attribution helpers for B1 metric reporting."""

from __future__ import annotations

import torch


def residual_localization_hit_rate(e_f: torch.Tensor, artifact_mask: torch.Tensor, top_fraction: float = 0.2) -> float:
    """Measure how much known artifact mass is covered by top residual faces.

    FINAL_PROPOSAL/B1 comment:
        B1 success asks whether residual top-20% faces cover visible seam/mip
        artifacts. This helper computes |TopK(e_f) intersect A| / |A| when an
        artifact face mask A is available. For pure oracle sanity without a
        manual mask, scripts use seam-adjacent faces as the deterministic proxy.
    """

    e_f = e_f.detach().to(torch.float32)
    artifact_mask = artifact_mask.to(e_f.device, torch.bool)
    if artifact_mask.sum() == 0 or e_f.numel() == 0:
        return 0.0
    k = max(1, int(round(float(e_f.numel()) * float(top_fraction))))
    top = torch.zeros_like(artifact_mask)
    top_idx = torch.topk(e_f, k=min(k, e_f.numel())).indices
    top[top_idx] = True
    return float((top & artifact_mask).sum().to(torch.float32).div(artifact_mask.sum()).detach().cpu())


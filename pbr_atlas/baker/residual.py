"""Residual attribution and mip leakage estimators for B1 C1 sanity."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import torch
import torch.nn.functional as nnF

from .baker import PBRMaps


@dataclass
class ResidualAttribution:
    pixel_l1: torch.Tensor
    e_f: torch.Tensor
    E_c: torch.Tensor
    seam_edges: torch.Tensor
    seam_residual: torch.Tensor
    G_l: torch.Tensor


def compute_pixel_l1(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    """Per-pixel L1 residual over RGB channels."""

    return (pred.to(torch.float32) - target.to(torch.float32)).abs().mean(dim=-1)


def per_face_residual(
    pixel_l1: torch.Tensor,
    face_ids: torch.Tensor,
    alpha: torch.Tensor,
    num_faces: int,
    eps: float = 1.0e-6,
) -> torch.Tensor:
    """Back-project rendered residual to mesh faces.

    FINAL_PROPOSAL C1 equation comment:
        e_f = sum_{v,l,x} alpha^{v,l}_{x,f} ||I_hat_{v,l}(x)-I*_{v,l}(x)||_1
              / (sum_{v,l,x} alpha^{v,l}_{x,f} + eps).
    B1 uses alpha=1 for the visible rasterized face id and 0 otherwise.
    """

    flat_ids = face_ids.reshape(-1)
    flat_residual = pixel_l1.reshape(-1)
    flat_alpha = alpha.reshape(-1).to(torch.float32)
    valid = (flat_ids >= 0) & (flat_ids < num_faces) & (flat_alpha > 0)
    sums = torch.zeros(num_faces, dtype=torch.float32, device=pixel_l1.device)
    weights = torch.zeros(num_faces, dtype=torch.float32, device=pixel_l1.device)
    if valid.any():
        ids = flat_ids[valid]
        sums.scatter_add_(0, ids, flat_residual[valid] * flat_alpha[valid])
        weights.scatter_add_(0, ids, flat_alpha[valid])
    return sums / weights.clamp_min(eps)


def per_chart_residual(e_f: torch.Tensor, chart_ids: torch.Tensor, eps: float = 1.0e-6) -> torch.Tensor:
    """Average face residual inside each UV chart.

    FINAL_PROPOSAL C1 equation comment:
        E_c = (1 / |F_c|) * sum_{f in F_c} e_f.
    """

    chart_ids = chart_ids.to(e_f.device, torch.long)
    chart_count = int(chart_ids.max().item()) + 1 if chart_ids.numel() else 0
    sums = torch.zeros(chart_count, dtype=torch.float32, device=e_f.device)
    counts = torch.zeros(chart_count, dtype=torch.float32, device=e_f.device)
    if chart_count:
        sums.scatter_add_(0, chart_ids, e_f)
        counts.scatter_add_(0, chart_ids, torch.ones_like(e_f))
    return sums / counts.clamp_min(eps)


def mesh_seam_edges(faces: torch.Tensor, chart_ids: torch.Tensor) -> torch.Tensor:
    """Return adjacent face pairs whose chart ids differ."""

    faces_cpu = faces.detach().cpu()
    charts_cpu = chart_ids.detach().cpu()
    edge_to_faces: Dict[Tuple[int, int], list[int]] = {}
    for face_idx, face in enumerate(faces_cpu.tolist()):
        for a, b in ((face[0], face[1]), (face[1], face[2]), (face[2], face[0])):
            key = (min(a, b), max(a, b))
            edge_to_faces.setdefault(key, []).append(face_idx)
    seam_pairs = []
    for adjacent in edge_to_faces.values():
        if len(adjacent) != 2:
            continue
        f0, f1 = adjacent
        if int(charts_cpu[f0]) != int(charts_cpu[f1]):
            seam_pairs.append((f0, f1))
    if not seam_pairs:
        return torch.empty(0, 2, dtype=torch.long, device=faces.device)
    return torch.tensor(seam_pairs, dtype=torch.long, device=faces.device)


def seam_residual_map(e_f: torch.Tensor, faces: torch.Tensor, chart_ids: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
    """Compute seam residual for chart-boundary face pairs.

    FINAL_PROPOSAL C1 residual comment:
        S_e measures residual concentrated on chart boundaries. B1 stores a
        per-seam value S_e(f_i,f_j)=0.5*(e_{f_i}+e_{f_j}) for visualization and
        storage-safe diagnostics.
    """

    seams = mesh_seam_edges(faces, chart_ids)
    if seams.numel() == 0:
        return seams, torch.empty(0, dtype=torch.float32, device=e_f.device)
    values = 0.5 * (e_f[seams[:, 0]] + e_f[seams[:, 1]])
    return seams, values


def _sample_map_at_uv(map_tensor: torch.Tensor, uv: torch.Tensor) -> torch.Tensor:
    tex = map_tensor.permute(2, 0, 1).unsqueeze(0)
    grid = uv.clamp(0.0, 1.0).view(1, -1, 1, 2) * 2.0 - 1.0
    sampled = nnF.grid_sample(tex, grid, mode="bilinear", padding_mode="border", align_corners=True)
    return sampled.squeeze(0).squeeze(-1).T


def estimate_mip_leakage(
    maps: PBRMaps,
    mesh,
    chart_ids: torch.Tensor,
    mip_levels: int = 4,
) -> torch.Tensor:
    """Estimate chart-boundary mip leakage.

    FINAL_PROPOSAL C3/C1 diagnostic equation comment:
        G_l = sum_l sum_{(t+,t-) in partial c}
              ||D_l(T)(t+) - D_l(T)(t-)||_1.
    B1 evaluates the same consistency over adjacent chart-boundary faces by
    sampling their UV centroids at mip level k and k+1.
    """

    seams = mesh_seam_edges(mesh.faces, chart_ids)
    if seams.numel() == 0:
        return torch.zeros(1, dtype=torch.float32, device=maps.albedo.device)
    uv_centers = mesh.uv[mesh.face_uv].mean(dim=1).to(maps.albedo.device)
    channels = torch.cat([maps.albedo, maps.roughness, maps.metallic], dim=-1).to(torch.float32)
    current = channels
    leakage = torch.zeros(1, dtype=torch.float32, device=maps.albedo.device)
    for _level in range(max(1, mip_levels)):
        plus = _sample_map_at_uv(current, uv_centers[seams[:, 0]])
        minus = _sample_map_at_uv(current, uv_centers[seams[:, 1]])
        leakage = leakage + (plus - minus).abs().mean()
        if min(current.shape[0], current.shape[1]) <= 4:
            break
        current = nnF.avg_pool2d(current.permute(2, 0, 1).unsqueeze(0), kernel_size=2, stride=2).squeeze(0).permute(1, 2, 0)
    return leakage


def compute_residual_attribution(
    pred: torch.Tensor,
    target: torch.Tensor,
    face_ids: torch.Tensor,
    alpha: torch.Tensor,
    mesh,
    maps: PBRMaps,
    chart_ids: torch.Tensor,
    mip_levels: int = 4,
) -> ResidualAttribution:
    """Compute all B1 residual observables: pixel L1, e_f, E_c, S_e, G_l."""

    pixel_l1 = compute_pixel_l1(pred, target)
    e_f = per_face_residual(pixel_l1, face_ids, alpha, int(mesh.faces.shape[0]))
    E_c = per_chart_residual(e_f, chart_ids)
    seam_edges, seam_values = seam_residual_map(e_f, mesh.faces, chart_ids)
    G_l = estimate_mip_leakage(maps, mesh, chart_ids, mip_levels=mip_levels)
    return ResidualAttribution(pixel_l1=pixel_l1, e_f=e_f, E_c=E_c, seam_edges=seam_edges, seam_residual=seam_values, G_l=G_l)


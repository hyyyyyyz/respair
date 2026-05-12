"""C4 cross-channel seam coupling losses and diagnostics."""

from __future__ import annotations

from typing import Mapping

import torch
import torch.nn.functional as nnF

from pbr_atlas.baker import PBRMaps
from pbr_atlas.baker.ggx import normalize
from pbr_atlas.baker.residual import mesh_seam_edges
from pbr_atlas.data.mesh_loader import MeshData


class CrossChannelSeamLoss:
    """C4: channel-aware seam consistency on one shared UV set.

    FINAL_PROPOSAL C4 equation comment:
        L_seam = sum_(p+,p- in E_seam) sum_k lambda_k
                 ||T_k(p+) - T_k(p-)||_1 / sigma_k
                 + lambda_n (1 - <N(p+), N(p-)>).

    Bridge-brief equation comment:
        L_seam_C4 = sum_{c in {A,N,R,M}} sum_{(t+,t-) in boundary c}
                   w_c * ||T_c(t+) - T_c(t-)||_1.

    The implementation samples the two adjacent face UV centroids for every
    chart-boundary face pair and applies the requested L1 channel weights while
    preserving U_A = U_N = U_R = U_M.
    """

    def __init__(self, channel_weights: Mapping[str, float]):
        self.channel_weights = {
            "albedo": float(channel_weights.get("albedo", 0.5)),
            "normal": float(channel_weights.get("normal", 1.0)),
            "roughness": float(channel_weights.get("roughness", 1.0)),
            "metallic": float(channel_weights.get("metallic", 1.0)),
        }

    def __call__(self, maps: PBRMaps, mesh: MeshData, chart_ids: torch.Tensor) -> torch.Tensor:
        seams = mesh_seam_edges(mesh.faces, chart_ids.to(mesh.faces.device))
        if seams.numel() == 0:
            return torch.zeros((), dtype=torch.float32, device=maps.albedo.device)
        uv_centers = mesh.uv[mesh.face_uv].mean(dim=1).to(maps.albedo.device)
        plus_uv = uv_centers[seams[:, 0]]
        minus_uv = uv_centers[seams[:, 1]]
        loss = torch.zeros((), dtype=torch.float32, device=maps.albedo.device)
        for name, tensor in _map_channels(maps).items():
            weight = self.channel_weights.get(name, 0.0)
            if weight == 0.0:
                continue
            plus = _sample_nhwc(tensor, plus_uv)
            minus = _sample_nhwc(tensor, minus_uv)
            loss = loss + float(weight) * (plus.to(torch.float32) - minus.to(torch.float32)).abs().mean()
        return loss


def channel_seam_metrics(maps: PBRMaps, mesh: MeshData, chart_ids: torch.Tensor) -> dict[str, float]:
    """Report per-channel seam discontinuities for C4 tables."""

    seams = mesh_seam_edges(mesh.faces, chart_ids.to(mesh.faces.device))
    if seams.numel() == 0:
        return {
            "albedo_seam_mae": 0.0,
            "normal_seam_l1": 0.0,
            "normal_seam_angular_error_deg": 0.0,
            "roughness_seam_mae": 0.0,
            "metallic_seam_mae": 0.0,
        }
    uv_centers = mesh.uv[mesh.face_uv].mean(dim=1).to(maps.albedo.device)
    plus_uv = uv_centers[seams[:, 0]]
    minus_uv = uv_centers[seams[:, 1]]
    albedo_plus, albedo_minus = _sample_nhwc(maps.albedo, plus_uv), _sample_nhwc(maps.albedo, minus_uv)
    normal_plus, normal_minus = normalize(_sample_nhwc(maps.normal, plus_uv)), normalize(_sample_nhwc(maps.normal, minus_uv))
    rough_plus, rough_minus = _sample_nhwc(maps.roughness, plus_uv), _sample_nhwc(maps.roughness, minus_uv)
    metal_plus, metal_minus = _sample_nhwc(maps.metallic, plus_uv), _sample_nhwc(maps.metallic, minus_uv)
    cos = (normal_plus * normal_minus).sum(dim=-1).clamp(-1.0, 1.0)
    return {
        "albedo_seam_mae": float((albedo_plus - albedo_minus).abs().mean().detach().cpu()),
        "normal_seam_l1": float((normal_plus - normal_minus).abs().mean().detach().cpu()),
        "normal_seam_angular_error_deg": float(torch.rad2deg(torch.acos(cos)).mean().detach().cpu()),
        "roughness_seam_mae": float((rough_plus - rough_minus).abs().mean().detach().cpu()),
        "metallic_seam_mae": float((metal_plus - metal_minus).abs().mean().detach().cpu()),
    }


def _map_channels(maps: PBRMaps) -> dict[str, torch.Tensor]:
    return {
        "albedo": maps.albedo,
        "normal": maps.normal,
        "roughness": maps.roughness,
        "metallic": maps.metallic,
    }


def _sample_nhwc(map_tensor: torch.Tensor, uv: torch.Tensor) -> torch.Tensor:
    tex = map_tensor.permute(2, 0, 1).unsqueeze(0)
    grid = uv.clamp(0.0, 1.0).view(1, -1, 1, 2) * 2.0 - 1.0
    sampled = nnF.grid_sample(tex, grid, mode="bilinear", padding_mode="border", align_corners=True)
    return sampled.squeeze(0).squeeze(-1).T


__all__ = ["CrossChannelSeamLoss", "channel_seam_metrics"]

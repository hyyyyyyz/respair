"""Helper signals for B3 C2-C4 integration."""

from __future__ import annotations

from typing import Sequence

import torch
import torch.nn.functional as nnF

from pbr_atlas.baker import PBRMaps, ViewSpec
from pbr_atlas.baker.ggx import normalize
from pbr_atlas.data.mesh_loader import MeshData


def estimate_face_visibility(mesh: MeshData, views: Sequence[ViewSpec] | None = None) -> torch.Tensor:
    """Estimate V(f) for C3 from held-out/train view directions."""

    normals = mesh.normals_per_face.to(torch.float32)
    centers = mesh.vertices[mesh.faces].mean(dim=1).to(torch.float32)
    if views:
        scores = []
        for view in views:
            eye = view.eye.to(centers.device, torch.float32).view(1, 3)
            view_dir = normalize(eye - centers)
            scores.append((normals * view_dir).sum(dim=1).clamp_min(0.0))
        return torch.stack(scores, dim=0).mean(dim=0)
    dirs = torch.tensor(
        [
            [1.0, 0.0, 0.0],
            [-1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, -1.0, 0.0],
            [0.0, 0.0, 1.0],
            [0.0, 0.0, -1.0],
        ],
        dtype=torch.float32,
        device=normals.device,
    )
    return (normals @ dirs.T).clamp_min(0.0).amax(dim=1)


def estimate_face_pbr_frequency(mesh: MeshData, maps: PBRMaps) -> torch.Tensor:
    """Estimate F_PBR(f) from per-channel atlas Laplacian magnitude."""

    channels = torch.cat(
        [
            maps.albedo.to(torch.float32),
            maps.normal.to(torch.float32),
            maps.roughness.to(torch.float32),
            maps.metallic.to(torch.float32),
        ],
        dim=-1,
    )
    x = channels.permute(2, 0, 1).unsqueeze(0)
    kernel = torch.tensor(
        [[0.0, 1.0, 0.0], [1.0, -4.0, 1.0], [0.0, 1.0, 0.0]],
        dtype=torch.float32,
        device=x.device,
    ).view(1, 1, 3, 3)
    weight = kernel.repeat(x.shape[1], 1, 1, 1)
    lap = nnF.conv2d(x, weight, padding=1, groups=x.shape[1]).abs().mean(dim=1, keepdim=True)
    uv_centers = mesh.uv[mesh.face_uv].mean(dim=1).to(lap.device)
    grid = uv_centers.clamp(0.0, 1.0).view(1, -1, 1, 2) * 2.0 - 1.0
    sampled = nnF.grid_sample(lap, grid, mode="bilinear", padding_mode="border", align_corners=True)
    return sampled.squeeze(0).squeeze(0).squeeze(-1).to(torch.float32)


__all__ = ["estimate_face_pbr_frequency", "estimate_face_visibility"]

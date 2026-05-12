"""Residual atlas visualization for B1 storage-safe outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import numpy as np
import torch

from .io import save_png


def residual_to_rgb(values: torch.Tensor) -> torch.Tensor:
    values = values.to(torch.float32)
    if values.numel() == 0:
        return torch.empty(0, 3, dtype=torch.float32, device=values.device)
    norm = values / values.quantile(0.98).clamp_min(1.0e-6)
    norm = norm.clamp(0.0, 1.0)
    # Blue -> yellow -> red heat ramp, readable in papers and PNG previews.
    r = torch.clamp(2.0 * norm, 0.0, 1.0)
    g = torch.clamp(2.0 - 2.0 * (norm - 0.5).abs(), 0.0, 1.0)
    b = torch.clamp(1.0 - 2.0 * norm, 0.0, 1.0)
    return torch.stack([r, g, b], dim=-1)


def save_residual_atlas_png(
    path: str | Path,
    mesh,
    e_f: torch.Tensor,
    resolution: int,
) -> Path:
    """Rasterize per-face residuals into a UV atlas PNG.

    FINAL_PROPOSAL C1 visualization comment:
        The image is a storage-safe rendering of e_f over U, i.e. residual
        atlas(t)=sum_f w_{t,f} e_f / (sum_f w_{t,f}+eps), matching the same
        coverage weights used by the C1 bake equation.
    """

    image = residual_atlas_image(mesh, e_f, resolution)
    return save_png(path, image.detach().cpu().numpy())


def save_residual_chain_png(
    path: str | Path,
    residual_items: Sequence[tuple[object, torch.Tensor]],
    resolution: int,
) -> Path:
    """Save a left-to-right chain of residual atlases for B3 figures."""

    images = [residual_atlas_image(mesh, e_f, resolution) for mesh, e_f in residual_items]
    if not images:
        images = [torch.zeros(resolution, resolution, 3, dtype=torch.float32)]
    chain = torch.cat([img.detach().cpu() for img in images], dim=1)
    return save_png(path, chain.numpy())


def residual_atlas_image(mesh, e_f: torch.Tensor, resolution: int) -> torch.Tensor:
    device = e_f.device
    colors = residual_to_rgb(e_f)
    image = torch.zeros(resolution, resolution, 3, dtype=torch.float32, device=device)
    uv_pixels = mesh.uv[mesh.face_uv].to(device, torch.float32) * float(resolution - 1)
    for face_idx in range(mesh.faces.shape[0]):
        tri = uv_pixels[face_idx]
        min_xy = torch.floor(tri.min(dim=0).values).clamp(0, resolution - 1).to(torch.long)
        max_xy = torch.ceil(tri.max(dim=0).values).clamp(0, resolution - 1).to(torch.long)
        ys = torch.arange(min_xy[1], max_xy[1] + 1, device=device)
        xs = torch.arange(min_xy[0], max_xy[0] + 1, device=device)
        if ys.numel() == 0 or xs.numel() == 0:
            continue
        grid_y, grid_x = torch.meshgrid(ys, xs, indexing="ij")
        p = torch.stack([grid_x.to(torch.float32), grid_y.to(torch.float32)], dim=-1)
        bary = _barycentric_2d(p, tri)
        inside = (bary >= -1.0e-5).all(dim=-1)
        if inside.any():
            ys_in = grid_y[inside]
            xs_in = grid_x[inside]
            color = colors[face_idx].view(1, 3).expand(ys_in.shape[0], 3)
            image[ys_in, xs_in] = color
    return image


def _barycentric_2d(points: torch.Tensor, tri: torch.Tensor) -> torch.Tensor:
    a, b, c = tri[0], tri[1], tri[2]
    v0 = b - a
    v1 = c - a
    v2 = points - a
    denom = v0[0] * v1[1] - v1[0] * v0[1]
    if torch.abs(denom) < 1.0e-12:
        return torch.full(points.shape[:-1] + (3,), -1.0, dtype=points.dtype, device=points.device)
    inv = 1.0 / denom
    v = (v2[..., 0] * v1[1] - v1[0] * v2[..., 1]) * inv
    w = (v0[0] * v2[..., 1] - v2[..., 0] * v0[1]) * inv
    u = 1.0 - v - w
    return torch.stack([u, v, w], dim=-1)

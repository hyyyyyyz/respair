"""C5 deterministic synthetic oracle PBR maps."""

from __future__ import annotations

import hashlib
import math
from typing import Optional

import torch

from pbr_atlas.baker import PBRMaps
from pbr_atlas.baker.ggx import normalize
from pbr_atlas.data.mesh_loader import MeshData


def generate_synthetic_oracle_pbr(
    mesh: MeshData,
    seed: int,
    pattern: str = "voronoi_albedo+smooth_normal+region_roughness",
    *,
    resolution: int = 1024,
    num_voronoi_seeds: int = 16,
    device: Optional[torch.device] = None,
) -> PBRMaps:
    """Generate deterministic per-mesh PBR ground truth for B3/C5.

    FINAL_PROPOSAL C5 oracle-control comment:
        Synthetic oracle PBR fixes T*_k for a mesh/seed pair so residual,
        repair, and matched-control comparisons cannot be explained by an
        upstream material predictor. For the same mesh and seed, this function
        returns bit-stable A/N/R/M_t maps.
    """

    device = device or mesh.vertices.device
    resolution = int(resolution)
    gen = torch.Generator(device="cpu")
    gen.manual_seed(_mesh_aware_seed(mesh, seed))

    coords = torch.linspace(0.0, 1.0, resolution, dtype=torch.float32)
    v, u = torch.meshgrid(coords, coords, indexing="ij")
    uv = torch.stack([u, v], dim=-1)
    flat_uv = uv.reshape(-1, 2)

    region_count = max(1, int(num_voronoi_seeds))
    centers = torch.rand(region_count, 2, generator=gen)
    palette = torch.rand(region_count, 3, generator=gen) * 0.68 + 0.20
    rough_table = torch.rand(region_count, 1, generator=gen) * 0.58 + 0.18
    metal_table = (torch.rand(region_count, 1, generator=gen) > 0.86).to(torch.float32) * 0.55
    labels = torch.cdist(flat_uv, centers).argmin(dim=1).reshape(resolution, resolution)

    albedo = torch.full((resolution, resolution, 3), 0.55, dtype=torch.float32)
    normal = torch.zeros((resolution, resolution, 3), dtype=torch.float32)
    normal[..., 2] = 1.0
    roughness = torch.full((resolution, resolution, 1), 0.42, dtype=torch.float32)
    metallic = torch.zeros((resolution, resolution, 1), dtype=torch.float32)

    if "voronoi_albedo" in pattern:
        stripes = 0.07 * torch.sin(2.0 * math.pi * (7.0 * u + 3.0 * v))[..., None]
        fine = 0.03 * torch.cos(2.0 * math.pi * (19.0 * u - 11.0 * v))[..., None]
        albedo = (palette[labels] + stripes + fine).clamp(0.0, 1.0)

    if "smooth_normal" in pattern:
        height = 0.035 * torch.sin(2.0 * math.pi * (11.0 * u + 5.0 * v))
        height = height + 0.025 * torch.cos(2.0 * math.pi * (4.0 * u - 13.0 * v))
        height = height + 0.015 * torch.sin(2.0 * math.pi * (centers[:, 0].mean() * 9.0 + u * 2.0 + v * 3.0))
        dh_dv, dh_du = torch.gradient(height, spacing=(coords, coords))
        normal = normalize(torch.stack([-dh_du, -dh_dv, torch.ones_like(height)], dim=-1))

    if "region_roughness" in pattern:
        roughness = (rough_table[labels] + 0.045 * torch.sin(2.0 * math.pi * 17.0 * u)[..., None]).clamp(0.04, 1.0)
        metallic = metal_table[labels].clamp(0.0, 1.0)

    return PBRMaps(
        albedo=albedo.to(device),
        normal=normal.to(device),
        roughness=roughness.to(device),
        metallic=metallic.to(device),
    )


def _mesh_aware_seed(mesh: MeshData, seed: int) -> int:
    vertices = mesh.vertices.detach().to(torch.float32).cpu()
    faces = mesh.faces.detach().to(torch.long).cpu()
    payload = torch.cat(
        [
            vertices.flatten()[:: max(1, vertices.numel() // 256)].round(decimals=5).to(torch.float32).view(-1),
            faces.flatten()[:: max(1, faces.numel() // 256)].to(torch.float32).view(-1),
            torch.tensor([vertices.shape[0], faces.shape[0]], dtype=torch.float32),
        ]
    )
    digest = hashlib.sha256(payload.numpy().tobytes()).digest()
    mixed = int.from_bytes(digest[:8], byteorder="little", signed=False)
    return (int(seed) + mixed) % (2**31 - 1)


__all__ = ["generate_synthetic_oracle_pbr"]

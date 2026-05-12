"""B2 matched-protocol statistics and constraint enforcement."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Mapping, Optional

import torch

from pbr_atlas.baker.residual import mesh_seam_edges
from pbr_atlas.data.mesh_loader import MeshData

from .base import BaselineAtlas


@dataclass
class MatchedProtocolConfig:
    atlas_size: int = 1024
    padding: int = 8
    chart_count_window: float = 0.1
    utilization_min: float = 0.5
    distortion_tol: float = 2.0
    raster_resolution: int = 256

    @classmethod
    def from_mapping(cls, payload: Optional[Mapping[str, Any]]) -> "MatchedProtocolConfig":
        data = dict(payload or {})
        return cls(
            atlas_size=int(data.get("atlas_size", 1024)),
            padding=int(data.get("padding", 8)),
            chart_count_window=float(data.get("chart_count_window", 0.1)),
            utilization_min=float(data.get("utilization_min", data.get("texture_utilization_min", 0.5))),
            distortion_tol=float(data.get("distortion_tol", 2.0)),
            raster_resolution=int(data.get("raster_resolution", 256)),
        )


@dataclass
class AtlasStats:
    chart_count: int
    texture_utilization: float
    seam_length: float
    area_distortion_q50: float
    area_distortion_q95: float
    angle_distortion_q50: float
    angle_distortion_q95: float
    max_distortion_q95: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MatchedProtocolReport:
    matched_constraint_violated: bool
    violations: List[str]
    stats: AtlasStats
    reference_stats: AtlasStats
    chart_count_bounds: tuple[int, int]
    max_distortion_q95_limit: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "matched_constraint_violated": self.matched_constraint_violated,
            "violations": list(self.violations),
            "stats": self.stats.to_dict(),
            "reference_stats": self.reference_stats.to_dict(),
            "chart_count_bounds": list(self.chart_count_bounds),
            "max_distortion_q95_limit": self.max_distortion_q95_limit,
        }


def _triangle_area_2d(tri: torch.Tensor) -> torch.Tensor:
    return 0.5 * torch.abs(
        (tri[:, 1, 0] - tri[:, 0, 0]) * (tri[:, 2, 1] - tri[:, 0, 1])
        - (tri[:, 1, 1] - tri[:, 0, 1]) * (tri[:, 2, 0] - tri[:, 0, 0])
    )


def _triangle_area_3d(tri: torch.Tensor) -> torch.Tensor:
    return 0.5 * torch.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0], dim=1).norm(dim=1)


def _triangle_angles(tri: torch.Tensor) -> torch.Tensor:
    a = tri[:, 1] - tri[:, 0]
    b = tri[:, 2] - tri[:, 1]
    c = tri[:, 0] - tri[:, 2]
    la = a.norm(dim=1).clamp_min(1.0e-8)
    lb = b.norm(dim=1).clamp_min(1.0e-8)
    lc = c.norm(dim=1).clamp_min(1.0e-8)
    ang0 = torch.rad2deg(torch.acos(((-c) * a).sum(dim=1).div(lc * la).clamp(-1.0, 1.0)))
    ang1 = torch.rad2deg(torch.acos(((-a) * b).sum(dim=1).div(la * lb).clamp(-1.0, 1.0)))
    ang2 = 180.0 - ang0 - ang1
    return torch.stack([ang0, ang1, ang2], dim=1)


def _uv_occupancy(uv: torch.Tensor, face_uv: torch.Tensor, resolution: int) -> float:
    uv = uv.detach().to(torch.float32).cpu()
    face_uv = face_uv.detach().to(torch.long).cpu()
    if uv.numel() == 0 or face_uv.numel() == 0:
        return 0.0
    image = torch.zeros(resolution, resolution, dtype=torch.bool)
    uv_pixels = uv[face_uv] * float(max(resolution - 1, 1))
    for tri in uv_pixels:
        min_xy = torch.floor(tri.min(dim=0).values).clamp(0, resolution - 1).to(torch.long)
        max_xy = torch.ceil(tri.max(dim=0).values).clamp(0, resolution - 1).to(torch.long)
        ys = torch.arange(min_xy[1], max_xy[1] + 1)
        xs = torch.arange(min_xy[0], max_xy[0] + 1)
        if ys.numel() == 0 or xs.numel() == 0:
            continue
        grid_y, grid_x = torch.meshgrid(ys, xs, indexing="ij")
        points = torch.stack([grid_x.to(torch.float32), grid_y.to(torch.float32)], dim=-1)
        bary = _barycentric(points, tri)
        inside = (bary >= -1.0e-5).all(dim=-1)
        if inside.any():
            image[grid_y[inside], grid_x[inside]] = True
    return float(image.to(torch.float32).mean().item())


def _barycentric(points: torch.Tensor, tri: torch.Tensor) -> torch.Tensor:
    a, b, c = tri[0], tri[1], tri[2]
    v0 = b - a
    v1 = c - a
    v2 = points - a
    denom = v0[0] * v1[1] - v1[0] * v0[1]
    if torch.abs(denom) < 1.0e-12:
        return torch.full(points.shape[:-1] + (3,), -1.0, dtype=points.dtype)
    inv = 1.0 / denom
    v = (v2[..., 0] * v1[1] - v1[0] * v2[..., 1]) * inv
    w = (v0[0] * v2[..., 1] - v2[..., 0] * v0[1]) * inv
    u = 1.0 - v - w
    return torch.stack([u, v, w], dim=-1)


def compute_atlas_stats(mesh: MeshData, atlas: BaselineAtlas, *, raster_resolution: int = 256) -> AtlasStats:
    vertices = mesh.vertices.detach().to(torch.float32).cpu()
    faces = mesh.faces.detach().to(torch.long).cpu()
    uv = atlas.uv.detach().to(torch.float32).cpu()
    face_uv = atlas.face_uv.detach().to(torch.long).cpu()
    chart_ids = atlas.chart_ids.detach().to(torch.long).cpu()

    tri_3d = vertices[faces]
    tri_uv = uv[face_uv]
    area_3d = _triangle_area_3d(tri_3d).clamp_min(1.0e-8)
    area_uv = _triangle_area_2d(tri_uv).clamp_min(1.0e-8)
    uv_scale = area_3d.sum() / area_uv.sum().clamp_min(1.0e-8)
    area_ratio = (area_uv * uv_scale / area_3d).clamp_min(1.0e-8)
    area_distortion = torch.abs(torch.log(area_ratio))

    ang_3d = _triangle_angles(tri_3d)
    ang_uv = _triangle_angles(tri_uv)
    angle_distortion = torch.abs(ang_3d - ang_uv).mean(dim=1)

    seam_pairs = mesh_seam_edges(faces, chart_ids)
    seam_length = 0.0
    if seam_pairs.numel():
        for face_i, face_j in seam_pairs.tolist():
            shared = set(faces[face_i].tolist()).intersection(faces[face_j].tolist())
            if len(shared) == 2:
                a, b = sorted(shared)
                seam_length += float((vertices[a] - vertices[b]).norm().item())

    utilization = _uv_occupancy(uv, face_uv, max(int(raster_resolution), 64))
    chart_count = int(torch.unique(chart_ids).numel()) if chart_ids.numel() else 0
    area_q50 = float(torch.quantile(area_distortion, 0.50).item()) if area_distortion.numel() else 0.0
    area_q95 = float(torch.quantile(area_distortion, 0.95).item()) if area_distortion.numel() else 0.0
    angle_q50 = float(torch.quantile(angle_distortion, 0.50).item()) if angle_distortion.numel() else 0.0
    angle_q95 = float(torch.quantile(angle_distortion, 0.95).item()) if angle_distortion.numel() else 0.0
    return AtlasStats(
        chart_count=chart_count,
        texture_utilization=utilization,
        seam_length=seam_length,
        area_distortion_q50=area_q50,
        area_distortion_q95=area_q95,
        angle_distortion_q50=angle_q50,
        angle_distortion_q95=angle_q95,
        max_distortion_q95=max(area_q95, angle_q95),
    )


def enforce(
    mesh: MeshData,
    atlas: BaselineAtlas,
    reference_atlas: BaselineAtlas,
    config: MatchedProtocolConfig,
) -> MatchedProtocolReport:
    stats = compute_atlas_stats(mesh, atlas, raster_resolution=config.raster_resolution)
    reference_stats = compute_atlas_stats(mesh, reference_atlas, raster_resolution=config.raster_resolution)
    lower = max(1, int(reference_stats.chart_count * (1.0 - config.chart_count_window)))
    upper = max(lower, int(reference_stats.chart_count * (1.0 + config.chart_count_window) + 0.999))
    distortion_limit = float(reference_stats.max_distortion_q95 + 2.0 * config.distortion_tol)
    violations: List[str] = []
    if int(atlas.atlas_size) != int(config.atlas_size):
        violations.append(f"atlas_size={atlas.atlas_size} != {config.atlas_size}")
    if int(atlas.padding) != int(config.padding):
        violations.append(f"padding={atlas.padding} != {config.padding}")
    if stats.chart_count < lower or stats.chart_count > upper:
        violations.append(f"chart_count={stats.chart_count} outside [{lower}, {upper}]")
    if stats.texture_utilization < config.utilization_min:
        violations.append(f"texture_utilization={stats.texture_utilization:.4f} < {config.utilization_min:.4f}")
    if stats.max_distortion_q95 > distortion_limit:
        violations.append(f"max_distortion_q95={stats.max_distortion_q95:.4f} > {distortion_limit:.4f}")
    return MatchedProtocolReport(
        matched_constraint_violated=bool(violations),
        violations=violations,
        stats=stats,
        reference_stats=reference_stats,
        chart_count_bounds=(lower, upper),
        max_distortion_q95_limit=distortion_limit,
    )

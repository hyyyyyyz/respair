"""Shared B2 baseline interfaces and UV helper utilities."""

from __future__ import annotations

import math
import os
import shutil
import subprocess
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Dict, Iterable, Literal, Mapping, Optional, Protocol, Sequence

import torch

from pbr_atlas.data.mesh_loader import MeshData


@dataclass
class BaselineAtlas:
    name: str
    uv: torch.Tensor
    face_uv: torch.Tensor
    chart_ids: torch.Tensor
    atlas_size: int
    padding: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    repro_status: Literal["ok", "partial", "failed"] = "ok"
    failure_reason: Optional[str] = None

    def to(self, device: torch.device) -> "BaselineAtlas":
        return replace(
            self,
            uv=self.uv.to(device),
            face_uv=self.face_uv.to(device),
            chart_ids=self.chart_ids.to(device),
        )


class BaselineBackend(Protocol):
    name: str

    def generate(self, mesh: MeshData, atlas_size: int, padding: int, **kw: Any) -> BaselineAtlas: ...

    def is_available(self) -> bool: ...


@dataclass
class ChartPatch:
    chart_id: int
    face_indices: torch.Tensor
    local_faces: torch.Tensor
    local_uv: torch.Tensor
    metadata: Dict[str, Any] = field(default_factory=dict)


class BackendBase:
    """Small utility base class for B2 backends."""

    name = "backend"
    paper_id: Optional[str] = None

    def __init__(self, config: Optional[Mapping[str, Any]] = None) -> None:
        self.config = dict(config or {})

    def is_available(self) -> bool:
        return True

    def _metadata(self, **extra: Any) -> Dict[str, Any]:
        metadata = dict(self.config.get("metadata", {}))
        metadata.setdefault("paper_id", self.paper_id)
        metadata.update(extra)
        return metadata

    def _success(
        self,
        *,
        uv: torch.Tensor,
        face_uv: torch.Tensor,
        chart_ids: torch.Tensor,
        atlas_size: int,
        padding: int,
        repro_status: Literal["ok", "partial", "failed"] = "ok",
        failure_reason: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> BaselineAtlas:
        return BaselineAtlas(
            name=self.name,
            uv=canonicalize_uv(uv),
            face_uv=face_uv.to(torch.long),
            chart_ids=chart_ids.to(torch.long),
            atlas_size=int(atlas_size),
            padding=int(padding),
            metadata=dict(metadata or {}),
            repro_status=repro_status,
            failure_reason=failure_reason,
        )

    def _failed(
        self,
        mesh: MeshData,
        *,
        atlas_size: int,
        padding: int,
        reason: str,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> BaselineAtlas:
        return BaselineAtlas(
            name=self.name,
            uv=mesh.uv.detach().cpu(),
            face_uv=mesh.face_uv.detach().cpu(),
            chart_ids=mesh.chart_ids.detach().cpu(),
            atlas_size=int(atlas_size),
            padding=int(padding),
            metadata=dict(metadata or {}),
            repro_status="failed",
            failure_reason=reason,
        )

    def _repo_root(self, override: Optional[str] = None) -> Optional[Path]:
        path = override or self.config.get("repo_root")
        if not path:
            return None
        root = Path(path).expanduser()
        return root if root.exists() else None

    def _command_available(self, command: str) -> bool:
        return shutil.which(command) is not None

    def _load_external_npz(self, path: str | Path, atlas_size: int, padding: int, *, metadata: Optional[Mapping[str, Any]] = None) -> BaselineAtlas:
        payload = torch.load(str(path), map_location="cpu") if str(path).endswith(".pt") else None
        if payload is None:
            import numpy as np

            arrays = np.load(path, allow_pickle=True)
            payload = {key: arrays[key] for key in arrays.files}
        uv = torch.as_tensor(payload["uv"], dtype=torch.float32)
        face_uv = torch.as_tensor(payload["face_uv"], dtype=torch.long)
        chart_ids = torch.as_tensor(payload.get("chart_ids", infer_chart_ids(face_uv)), dtype=torch.long)
        status = str(payload.get("repro_status", "ok"))
        reason = payload.get("failure_reason")
        if not isinstance(reason, str):
            reason = None
        return self._success(
            uv=uv,
            face_uv=face_uv,
            chart_ids=chart_ids,
            atlas_size=atlas_size,
            padding=padding,
            repro_status="partial" if status == "partial" else "ok",
            failure_reason=reason,
            metadata={**self._metadata(external_artifact=str(path)), **dict(metadata or {})},
        )

    def _run_command(self, command: str, *, cwd: Optional[Path] = None, env: Optional[Mapping[str, str]] = None) -> subprocess.CompletedProcess[str]:
        merged_env = os.environ.copy()
        if env:
            merged_env.update({key: str(value) for key, value in env.items()})
        return subprocess.run(
            command,
            shell=True,
            cwd=str(cwd) if cwd else None,
            env=merged_env,
            check=False,
            capture_output=True,
            text=True,
        )


def clone_mesh_with_atlas(mesh: MeshData, atlas: BaselineAtlas, device: Optional[torch.device] = None) -> MeshData:
    target_device = device or mesh.vertices.device
    return replace(
        mesh,
        uv=atlas.uv.to(target_device, torch.float32),
        face_uv=atlas.face_uv.to(target_device, torch.long),
        chart_ids=atlas.chart_ids.to(target_device, torch.long),
    )


def canonicalize_uv(uv: torch.Tensor) -> torch.Tensor:
    uv = uv.detach().to(torch.float32).cpu()
    if uv.numel() == 0:
        return uv
    min_xy = uv.min(dim=0).values
    max_xy = uv.max(dim=0).values
    span = (max_xy - min_xy).clamp_min(1.0e-6)
    uv = (uv - min_xy) / span.max()
    return uv.clamp(0.0, 1.0)


def infer_chart_ids(face_uv: torch.Tensor) -> torch.Tensor:
    face_uv = face_uv.detach().cpu().to(torch.long)
    face_count = int(face_uv.shape[0])
    parent = list(range(face_count))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    edge_to_face: Dict[tuple[int, int], int] = {}
    for face_idx, fuv in enumerate(face_uv.tolist()):
        for a, b in ((fuv[0], fuv[1]), (fuv[1], fuv[2]), (fuv[2], fuv[0])):
            key = (min(a, b), max(a, b))
            if key in edge_to_face:
                union(face_idx, edge_to_face[key])
            else:
                edge_to_face[key] = face_idx
    roots = torch.tensor([find(idx) for idx in range(face_count)], dtype=torch.long)
    _, chart_ids = torch.unique(roots, sorted=True, return_inverse=True)
    return chart_ids


def dominant_axis_face_groups(mesh: MeshData) -> torch.Tensor:
    normals = mesh.normals_per_face.detach().to(torch.float32).cpu()
    axis = normals.abs().argmax(dim=1)
    sign = (normals.gather(1, axis[:, None]).squeeze(1) < 0).to(torch.long)
    return axis * 2 + sign


def pca_grid_face_groups(mesh: MeshData) -> torch.Tensor:
    centroids = mesh.vertices[mesh.faces].mean(dim=1).detach().to(torch.float32).cpu()
    centered = centroids - centroids.mean(dim=0, keepdim=True)
    if centered.shape[0] < 2:
        return torch.zeros(centroids.shape[0], dtype=torch.long)
    _, _, vh = torch.linalg.svd(centered, full_matrices=False)
    projected = centered @ vh[:2].T
    quadrant_x = (projected[:, 0] >= projected[:, 0].median()).to(torch.long)
    quadrant_y = (projected[:, 1] >= projected[:, 1].median()).to(torch.long)
    return quadrant_x * 2 + quadrant_y


def visibility_face_groups(mesh: MeshData) -> torch.Tensor:
    normals = mesh.normals_per_face.detach().to(torch.float32).cpu()
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
    )
    scores = normals @ dirs.T
    return scores.argmax(dim=1).to(torch.long)


def face_surface_areas(mesh: MeshData) -> torch.Tensor:
    tri = mesh.vertices[mesh.faces].detach().to(torch.float32).cpu()
    cross = torch.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0], dim=1)
    return 0.5 * cross.norm(dim=1)


def chart_surface_areas(mesh: MeshData, chart_ids: torch.Tensor) -> Dict[int, float]:
    areas = face_surface_areas(mesh)
    chart_ids = chart_ids.detach().cpu().to(torch.long)
    out: Dict[int, float] = {}
    for chart in torch.unique(chart_ids).tolist():
        mask = chart_ids == int(chart)
        out[int(chart)] = float(areas[mask].sum())
    return out


def chart_visibility_scores(mesh: MeshData, chart_ids: torch.Tensor) -> Dict[int, float]:
    normals = mesh.normals_per_face.detach().to(torch.float32).cpu()
    dirs = torch.tensor(
        [
            [0.0, 0.0, 1.0],
            [0.0, 0.0, -1.0],
            [0.0, 1.0, 0.0],
            [0.0, -1.0, 0.0],
            [1.0, 0.0, 0.0],
            [-1.0, 0.0, 0.0],
        ],
        dtype=torch.float32,
    )
    visibility = (normals @ dirs.T).clamp_min(0.0).amax(dim=1)
    chart_ids = chart_ids.detach().cpu().to(torch.long)
    out: Dict[int, float] = {}
    for chart in torch.unique(chart_ids).tolist():
        mask = chart_ids == int(chart)
        out[int(chart)] = float(visibility[mask].mean()) if mask.any() else 0.0
    return out


def extract_chart_patches(uv: torch.Tensor, face_uv: torch.Tensor, chart_ids: torch.Tensor) -> list[ChartPatch]:
    uv = uv.detach().to(torch.float32).cpu()
    face_uv = face_uv.detach().to(torch.long).cpu()
    chart_ids = chart_ids.detach().to(torch.long).cpu()
    patches: list[ChartPatch] = []
    for chart in torch.unique(chart_ids).tolist():
        mask = chart_ids == int(chart)
        face_indices = torch.nonzero(mask, as_tuple=False).flatten()
        chart_face_uv = face_uv[mask]
        uv_ids = torch.unique(chart_face_uv)
        remap = {int(old): new for new, old in enumerate(uv_ids.tolist())}
        local_faces = torch.tensor([[remap[int(idx)] for idx in face.tolist()] for face in chart_face_uv], dtype=torch.long)
        local_uv = uv[uv_ids]
        patches.append(
            ChartPatch(
                chart_id=int(chart),
                face_indices=face_indices,
                local_faces=local_faces,
                local_uv=local_uv,
            )
        )
    return patches


def project_chart_patches(mesh: MeshData, chart_ids: torch.Tensor, projection: str) -> list[ChartPatch]:
    chart_ids = chart_ids.detach().to(torch.long).cpu()
    faces = mesh.faces.detach().to(torch.long).cpu()
    vertices = mesh.vertices.detach().to(torch.float32).cpu()
    normals = mesh.normals_per_face.detach().to(torch.float32).cpu()
    patches: list[ChartPatch] = []
    for chart in torch.unique(chart_ids).tolist():
        mask = chart_ids == int(chart)
        face_indices = torch.nonzero(mask, as_tuple=False).flatten()
        chart_faces = faces[mask]
        vertex_ids = torch.unique(chart_faces)
        remap = {int(old): new for new, old in enumerate(vertex_ids.tolist())}
        local_faces = torch.tensor([[remap[int(idx)] for idx in face.tolist()] for face in chart_faces], dtype=torch.long)
        local_vertices = vertices[vertex_ids]
        local_uv = project_vertices(local_vertices, projection=projection, dominant_label=int(chart), chart_normals=normals[mask])
        patches.append(
            ChartPatch(
                chart_id=int(chart),
                face_indices=face_indices,
                local_faces=local_faces,
                local_uv=local_uv,
            )
        )
    return patches


def project_vertices(
    vertices: torch.Tensor,
    *,
    projection: str,
    dominant_label: Optional[int] = None,
    chart_normals: Optional[torch.Tensor] = None,
) -> torch.Tensor:
    vertices = vertices.to(torch.float32)
    if projection == "cylindrical":
        theta = torch.atan2(vertices[:, 2], vertices[:, 0])
        u = (theta + math.pi) / (2.0 * math.pi)
        y = vertices[:, 1]
        v = (y - y.min()) / max(float(y.max() - y.min()), 1.0e-6)
        return torch.stack([u, v], dim=1)
    if projection == "spherical":
        radius = vertices.norm(dim=1).clamp_min(1.0e-6)
        theta = torch.atan2(vertices[:, 2], vertices[:, 0])
        phi = torch.acos((vertices[:, 1] / radius).clamp(-1.0, 1.0))
        return torch.stack([(theta + math.pi) / (2.0 * math.pi), phi / math.pi], dim=1)
    if projection == "axis_planar":
        axis = int(dominant_label or 0) // 2
        if axis == 0:
            uv = vertices[:, [2, 1]]
        elif axis == 1:
            uv = vertices[:, [0, 2]]
        else:
            uv = vertices[:, [0, 1]]
        return uv
    if projection == "normal_planar" and chart_normals is not None and chart_normals.numel():
        normal = chart_normals.mean(dim=0)
        normal = normal / normal.norm().clamp_min(1.0e-6)
        up = torch.tensor([0.0, 1.0, 0.0], dtype=torch.float32)
        if torch.abs(torch.dot(up, normal)) > 0.95:
            up = torch.tensor([1.0, 0.0, 0.0], dtype=torch.float32)
        tangent = torch.cross(up, normal, dim=0)
        tangent = tangent / tangent.norm().clamp_min(1.0e-6)
        bitangent = torch.cross(normal, tangent, dim=0)
        return torch.stack([vertices @ tangent, vertices @ bitangent], dim=1)
    centered = vertices - vertices.mean(dim=0, keepdim=True)
    if centered.shape[0] < 2:
        return centered[:, :2]
    _, _, vh = torch.linalg.svd(centered, full_matrices=False)
    basis = vh[:2]
    return centered @ basis.T


def pack_chart_patches(
    patches: Sequence[ChartPatch],
    *,
    atlas_size: int,
    padding: int,
    chart_scales: Optional[Mapping[int, float]] = None,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    if not patches:
        return (
            torch.zeros(0, 2, dtype=torch.float32),
            torch.zeros(0, 3, dtype=torch.long),
            torch.zeros(0, dtype=torch.long),
        )

    gap = float(padding) / float(max(int(atlas_size), 1))
    chart_scales = dict(chart_scales or {})
    normalized_patches = []
    total_area = 0.0
    max_width = 0.0
    for patch in patches:
        coords = patch.local_uv.to(torch.float32)
        min_xy = coords.min(dim=0).values
        max_xy = coords.max(dim=0).values
        span = max_xy - min_xy
        max_extent = float(span.max().item()) if span.numel() else 1.0
        if max_extent < 1.0e-6:
            max_extent = 1.0
        unit = (coords - min_xy) / max_extent
        width = float((span[0] / max_extent).item()) if span.numel() else 1.0
        height = float((span[1] / max_extent).item()) if span.numel() else 1.0
        width = max(width, 1.0e-3)
        height = max(height, 1.0e-3)
        scale = max(float(chart_scales.get(patch.chart_id, 1.0)), 1.0e-3)
        total_area += width * height * scale * scale
        max_width = max(max_width, width * scale)
        normalized_patches.append((patch, unit, width, height, scale))

    if total_area <= 1.0e-8:
        total_area = 1.0
    target_fill = 0.78
    scale = min(math.sqrt(target_fill / total_area), (1.0 - 2.0 * gap) / max(max_width, 1.0e-3))
    scale = max(scale, 1.0e-3)

    def layout(current_scale: float) -> tuple[list[tuple[ChartPatch, torch.Tensor, float, float, float, float]], float]:
        ordered = sorted(normalized_patches, key=lambda item: item[3] * item[4], reverse=True)
        cursor_x = gap
        cursor_y = gap
        row_height = 0.0
        placements = []
        limit = 1.0 - gap
        for patch, unit, width, height, weight in ordered:
            w = width * weight * current_scale
            h = height * weight * current_scale
            if cursor_x + w > limit and cursor_x > gap:
                cursor_x = gap
                cursor_y += row_height + gap
                row_height = 0.0
            placements.append((patch, unit, cursor_x, cursor_y, w, h))
            cursor_x += w + gap
            row_height = max(row_height, h)
        total_height = cursor_y + row_height + gap
        return placements, total_height

    placements, total_height = layout(scale)
    if total_height > 1.0 - gap:
        fit = max((1.0 - 2.0 * gap) / max(total_height, 1.0e-3), 1.0e-3)
        placements, total_height = layout(scale * fit)

    uv_chunks: list[torch.Tensor] = []
    face_count = sum(int(patch.local_faces.shape[0]) for patch in patches)
    face_uv_out = torch.zeros(face_count, 3, dtype=torch.long)
    chart_ids_out = torch.zeros(face_count, dtype=torch.long)
    uv_offset = 0
    for patch, unit, origin_x, origin_y, width, height in placements:
        transformed = unit.clone()
        transformed[:, 0] = origin_x + transformed[:, 0] * width
        transformed[:, 1] = origin_y + transformed[:, 1] * height
        transformed = transformed.clamp(0.0, 1.0)
        uv_chunks.append(transformed)
        face_uv_out[patch.face_indices] = patch.local_faces + uv_offset
        chart_ids_out[patch.face_indices] = patch.chart_id
        uv_offset += transformed.shape[0]
    return torch.cat(uv_chunks, dim=0), face_uv_out, chart_ids_out


def repack_existing_charts(
    uv: torch.Tensor,
    face_uv: torch.Tensor,
    chart_ids: torch.Tensor,
    *,
    atlas_size: int,
    padding: int,
    chart_scales: Optional[Mapping[int, float]] = None,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    patches = extract_chart_patches(uv, face_uv, chart_ids)
    return pack_chart_patches(patches, atlas_size=atlas_size, padding=padding, chart_scales=chart_scales)


def load_external_or_none(path: Optional[str | Path]) -> Optional[Path]:
    if not path:
        return None
    candidate = Path(path).expanduser()
    return candidate if candidate.exists() else None


def first_existing(paths: Iterable[str | Path]) -> Optional[Path]:
    for path in paths:
        candidate = Path(path).expanduser()
        if candidate.exists():
            return candidate
    return None

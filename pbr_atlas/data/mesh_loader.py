"""Mesh loader with UV extraction/generation for B1 C1 baker."""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Optional

import numpy as np
import torch


@dataclass
class MeshData:
    vertices: torch.Tensor
    faces: torch.Tensor
    uv: torch.Tensor
    face_uv: torch.Tensor
    normals_per_face: torch.Tensor
    normals_per_vertex: torch.Tensor
    chart_ids: torch.Tensor
    source_path: str = ""

    def to(self, device: torch.device) -> "MeshData":
        return replace(
            self,
            vertices=self.vertices.to(device),
            faces=self.faces.to(device),
            uv=self.uv.to(device),
            face_uv=self.face_uv.to(device),
            normals_per_face=self.normals_per_face.to(device),
            normals_per_vertex=self.normals_per_vertex.to(device),
            chart_ids=self.chart_ids.to(device),
        )


def load_mesh(path: str | Path, device: Optional[torch.device] = None) -> MeshData:
    """Load OBJ/GLB/PLY through trimesh and return torch tensors.

    FINAL_PROPOSAL C1 input comment:
        Mesh M=(V,F) and UV U are the required inputs to the baker. If U is
        missing, B1 creates a deterministic xatlas unwrap; if xatlas is not
        installed, it falls back to cylindrical UVs so setup_data stays
        offline-friendly.
    """

    import trimesh

    device = device or torch.device("cpu")
    mesh_obj = trimesh.load(str(path), force="mesh", process=True)
    if isinstance(mesh_obj, trimesh.Scene):
        mesh_obj = trimesh.util.concatenate(tuple(mesh_obj.geometry.values()))
    if mesh_obj.vertices.size == 0 or mesh_obj.faces.size == 0:
        raise ValueError(f"Mesh has no vertices/faces: {path}")
    mesh_obj.remove_unreferenced_vertices()
    vertices_np = np.asarray(mesh_obj.vertices, dtype=np.float32)
    faces_np = np.asarray(mesh_obj.faces, dtype=np.int64)
    vertices_np = _normalize_vertices(vertices_np)
    uv_np, face_uv_np = _extract_or_generate_uv(mesh_obj, vertices_np, faces_np)
    normals_face_np = np.asarray(mesh_obj.face_normals, dtype=np.float32)
    normals_vertex_np = np.asarray(mesh_obj.vertex_normals, dtype=np.float32)
    if normals_face_np.shape[0] != faces_np.shape[0]:
        normals_face_np = _compute_face_normals(vertices_np, faces_np)
    if normals_vertex_np.shape[0] != vertices_np.shape[0]:
        normals_vertex_np = _compute_vertex_normals(vertices_np, faces_np, normals_face_np)
    chart_ids = _infer_chart_ids(face_uv_np)
    return MeshData(
        vertices=torch.from_numpy(vertices_np).to(device),
        faces=torch.from_numpy(faces_np).to(device),
        uv=torch.from_numpy(uv_np.astype(np.float32)).to(device),
        face_uv=torch.from_numpy(face_uv_np.astype(np.int64)).to(device),
        normals_per_face=torch.from_numpy(normals_face_np.astype(np.float32)).to(device),
        normals_per_vertex=torch.from_numpy(normals_vertex_np.astype(np.float32)).to(device),
        chart_ids=torch.from_numpy(chart_ids.astype(np.int64)).to(device),
        source_path=str(path),
    )


def _normalize_vertices(vertices: np.ndarray) -> np.ndarray:
    center = vertices.mean(axis=0, keepdims=True)
    centered = vertices - center
    scale = np.linalg.norm(centered, axis=1).max()
    if scale < 1.0e-8:
        scale = 1.0
    return centered / scale


def _extract_or_generate_uv(mesh_obj, vertices: np.ndarray, faces: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    visual_uv = getattr(getattr(mesh_obj, "visual", None), "uv", None)
    if visual_uv is not None:
        uv = np.asarray(visual_uv, dtype=np.float32)
        if uv.ndim == 2 and uv.shape[0] == vertices.shape[0] and uv.shape[1] == 2:
            return np.mod(uv, 1.0).astype(np.float32), faces.astype(np.int64)
    try:
        import xatlas  # type: ignore

        vmapping, indices, uvs = xatlas.parametrize(vertices.astype(np.float32), faces.astype(np.uint32))
        del vmapping
        return np.asarray(uvs, dtype=np.float32).clip(0.0, 1.0), np.asarray(indices, dtype=np.int64).reshape(-1, 3)
    except Exception:
        return _cylindrical_uv(vertices), faces.astype(np.int64)


def _cylindrical_uv(vertices: np.ndarray) -> np.ndarray:
    x, y, z = vertices[:, 0], vertices[:, 1], vertices[:, 2]
    theta = np.arctan2(z, x)
    u = (theta + np.pi) / (2.0 * np.pi)
    v = (y - y.min()) / max(float(y.max() - y.min()), 1.0e-8)
    return np.stack([u, v], axis=1).astype(np.float32)


def _compute_face_normals(vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
    tri = vertices[faces]
    normal = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    norm = np.linalg.norm(normal, axis=1, keepdims=True)
    return normal / np.maximum(norm, 1.0e-8)


def _compute_vertex_normals(vertices: np.ndarray, faces: np.ndarray, face_normals: np.ndarray) -> np.ndarray:
    out = np.zeros_like(vertices)
    for face_idx, face in enumerate(faces):
        out[face] += face_normals[face_idx]
    norm = np.linalg.norm(out, axis=1, keepdims=True)
    return out / np.maximum(norm, 1.0e-8)


def _infer_chart_ids(face_uv: np.ndarray) -> np.ndarray:
    """Infer connected UV charts from shared UV edges."""

    face_count = face_uv.shape[0]
    parent = np.arange(face_count, dtype=np.int64)

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return int(x)

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    edge_to_face: dict[tuple[int, int], int] = {}
    for f_idx, fuv in enumerate(face_uv.tolist()):
        for a, b in ((fuv[0], fuv[1]), (fuv[1], fuv[2]), (fuv[2], fuv[0])):
            key = (min(a, b), max(a, b))
            if key in edge_to_face:
                union(f_idx, edge_to_face[key])
            else:
                edge_to_face[key] = f_idx
    roots = np.array([find(i) for i in range(face_count)], dtype=np.int64)
    _, chart_ids = np.unique(roots, return_inverse=True)
    return chart_ids.astype(np.int64)

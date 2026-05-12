"""Partition-independent chart-boundary curvature alignment metrics."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch

from pbr_atlas.baselines.base import BaselineAtlas
from pbr_atlas.data.mesh_loader import MeshData


@dataclass
class ChartCurvatureSummary:
    chart_count: int
    face_count: int
    mesh_edge_count: int
    chart_boundary_edge_count: int
    high_curvature_edge_count: int
    intersection_edge_count: int
    curvature_iou: float
    curvature_precision: float
    curvature_recall: float
    high_curvature_percentile: float
    high_curvature_threshold_degrees: float
    mean_boundary_dihedral_degrees: float
    mean_nonboundary_dihedral_degrees: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_atlas_npz(path: str | Path, *, atlas_size: int = 1024, padding: int = 8, name: str | None = None) -> BaselineAtlas:
    payload = np.load(path, allow_pickle=True)
    required = ("uv", "face_uv", "chart_ids")
    missing = [key for key in required if key not in payload.files]
    if missing:
        raise KeyError(f"{path} missing required atlas arrays: {missing}")
    return BaselineAtlas(
        name=name or Path(path).stem,
        uv=torch.as_tensor(payload["uv"], dtype=torch.float32),
        face_uv=torch.as_tensor(payload["face_uv"], dtype=torch.long),
        chart_ids=torch.as_tensor(payload["chart_ids"], dtype=torch.long),
        atlas_size=int(atlas_size),
        padding=int(padding),
    )


def summarize_chart_curvature_alignment(
    mesh: MeshData,
    chart_ids,
    *,
    high_percentile: float = 85.0,
    min_threshold_degrees: float = 10.0,
) -> dict[str, Any]:
    """Compare chart-boundary edges against geometry-defined high curvature.

    High-curvature edges are defined only from mesh dihedral angles. The metric
    is therefore independent of PartUV or any semantic partition.
    """

    faces = mesh.faces.detach().cpu().to(torch.long)
    normals = mesh.normals_per_face.detach().cpu().to(torch.float32)
    charts = torch.as_tensor(chart_ids, dtype=torch.long).detach().cpu().reshape(-1)
    if int(charts.numel()) != int(faces.shape[0]):
        raise ValueError(f"chart_ids face count {charts.numel()} != mesh face count {faces.shape[0]}")

    edge_to_faces: dict[tuple[int, int], list[int]] = {}
    for face_idx, face in enumerate(faces.tolist()):
        for a, b in ((face[0], face[1]), (face[1], face[2]), (face[2], face[0])):
            key = (min(int(a), int(b)), max(int(a), int(b)))
            edge_to_faces.setdefault(key, []).append(face_idx)

    chart_boundary: set[tuple[int, int]] = set()
    dihedral_edges: list[tuple[tuple[int, int], float, bool]] = []
    for edge, adjacent in edge_to_faces.items():
        if len(adjacent) != 2:
            continue
        f0, f1 = int(adjacent[0]), int(adjacent[1])
        is_boundary = int(charts[f0]) != int(charts[f1])
        if is_boundary:
            chart_boundary.add(edge)
        n0 = normals[f0]
        n1 = normals[f1]
        cos_angle = float(torch.dot(n0, n1).clamp(-1.0, 1.0).item())
        angle = float(np.degrees(np.arccos(cos_angle)))
        dihedral_edges.append((edge, angle, is_boundary))

    if dihedral_edges:
        angles = np.asarray([item[1] for item in dihedral_edges], dtype=np.float64)
        percentile_threshold = float(np.percentile(angles, float(high_percentile)))
        threshold = max(percentile_threshold, float(min_threshold_degrees))
        high_curvature = {edge for edge, angle, _ in dihedral_edges if angle >= threshold}
        if not high_curvature:
            top_idx = int(np.argmax(angles))
            high_curvature = {dihedral_edges[top_idx][0]}
    else:
        threshold = float(min_threshold_degrees)
        high_curvature = set()

    intersection = chart_boundary & high_curvature
    union = chart_boundary | high_curvature
    boundary_angles = [angle for _, angle, is_boundary in dihedral_edges if is_boundary]
    nonboundary_angles = [angle for _, angle, is_boundary in dihedral_edges if not is_boundary]

    return ChartCurvatureSummary(
        chart_count=int(torch.unique(charts).numel()) if charts.numel() else 0,
        face_count=int(faces.shape[0]),
        mesh_edge_count=int(len(edge_to_faces)),
        chart_boundary_edge_count=int(len(chart_boundary)),
        high_curvature_edge_count=int(len(high_curvature)),
        intersection_edge_count=int(len(intersection)),
        curvature_iou=float(len(intersection) / max(len(union), 1)),
        curvature_precision=float(len(intersection) / max(len(chart_boundary), 1)),
        curvature_recall=float(len(intersection) / max(len(high_curvature), 1)),
        high_curvature_percentile=float(high_percentile),
        high_curvature_threshold_degrees=float(threshold),
        mean_boundary_dihedral_degrees=float(np.mean(boundary_angles)) if boundary_angles else 0.0,
        mean_nonboundary_dihedral_degrees=float(np.mean(nonboundary_angles)) if nonboundary_angles else 0.0,
    ).to_dict()


def summarize_atlas_file(
    mesh: MeshData,
    atlas_path: str | Path,
    *,
    atlas_size: int = 1024,
    padding: int = 8,
    high_percentile: float = 85.0,
    min_threshold_degrees: float = 10.0,
) -> dict[str, Any]:
    atlas = load_atlas_npz(atlas_path, atlas_size=atlas_size, padding=padding)
    summary = summarize_chart_curvature_alignment(
        mesh,
        atlas.chart_ids,
        high_percentile=high_percentile,
        min_threshold_degrees=min_threshold_degrees,
    )
    summary["atlas_path"] = str(atlas_path)
    return summary


__all__ = [
    "ChartCurvatureSummary",
    "load_atlas_npz",
    "summarize_atlas_file",
    "summarize_chart_curvature_alignment",
]

"""Matched-control oracle reference built from area-balanced xatlas charts."""

from __future__ import annotations

import math
from typing import Any, Dict

import torch

from pbr_atlas.data.mesh_loader import MeshData

from .base import repack_existing_charts
from .xatlas_classical import XAtlasClassicalBackend


def _chart_uv_area(atlas, chart_id: int) -> float:
    face_mask = atlas.chart_ids == int(chart_id)
    if not face_mask.any():
        return 1.0
    tri = atlas.uv[atlas.face_uv[face_mask]].to(torch.float32)
    area = 0.5 * torch.abs(
        (tri[:, 1, 0] - tri[:, 0, 0]) * (tri[:, 2, 1] - tri[:, 0, 1])
        - (tri[:, 1, 1] - tri[:, 0, 1]) * (tri[:, 2, 0] - tri[:, 0, 0])
    )
    return float(area.sum().item()) if area.numel() else 1.0


class MatchedOracleBackend(XAtlasClassicalBackend):
    name = "matched_oracle"
    paper_id = "oracle_reference"

    def generate(self, mesh: MeshData, atlas_size: int, padding: int, **kw: Any):
        xatlas_atlas = super().generate(mesh, atlas_size, padding, **kw)
        if xatlas_atlas.repro_status == "failed":
            return self._failed(
                mesh,
                atlas_size=atlas_size,
                padding=padding,
                reason=f"matched_oracle requires xatlas seed atlas: {xatlas_atlas.failure_reason}",
                metadata=self._metadata(),
            )

        tri = mesh.vertices[mesh.faces].detach().to(torch.float32).cpu()
        area_3d = 0.5 * torch.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0], dim=1).norm(dim=1)
        raw_scales: Dict[int, float] = {}
        for chart in torch.unique(xatlas_atlas.chart_ids).tolist():
            mask = xatlas_atlas.chart_ids == int(chart)
            chart_area_3d = float(area_3d[mask].sum().item()) if mask.any() else 1.0
            chart_area_uv = _chart_uv_area(xatlas_atlas, int(chart))
            raw_scales[int(chart)] = math.sqrt(max(chart_area_3d, 1.0e-6) / max(chart_area_uv, 1.0e-6))
        mean_log = sum(math.log(max(value, 1.0e-6)) for value in raw_scales.values()) / max(len(raw_scales), 1)
        scales = {chart: math.exp(math.log(max(value, 1.0e-6)) - mean_log) for chart, value in raw_scales.items()}
        uv, face_uv, chart_ids = repack_existing_charts(
            xatlas_atlas.uv,
            xatlas_atlas.face_uv,
            xatlas_atlas.chart_ids,
            atlas_size=atlas_size,
            padding=padding,
            chart_scales=scales,
        )
        return self._success(
            uv=uv,
            face_uv=face_uv,
            chart_ids=chart_ids,
            atlas_size=atlas_size,
            padding=padding,
            metadata=self._metadata(seed_backend="xatlas_classical", rebalance="surface_area_over_uv_area"),
        )

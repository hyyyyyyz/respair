"""Mesh-adapted OT-UVGS capacity-allocation control."""

from __future__ import annotations

import math
from typing import Any, Dict

import torch

from pbr_atlas.data.mesh_loader import MeshData

from .base import BackendBase, chart_surface_areas, chart_visibility_scores, repack_existing_charts
from .xatlas_classical import XAtlasClassicalBackend


class OTUVGSBackend(BackendBase):
    name = "otuvgs"
    paper_id = "arXiv:2604.19127v1"

    def generate(self, mesh: MeshData, atlas_size: int, padding: int, **kw: Any):
        xatlas_backend = XAtlasClassicalBackend(self.config.get("xatlas", {}))
        base_atlas = xatlas_backend.generate(mesh, atlas_size, padding, **kw)
        if base_atlas.repro_status == "failed":
            return self._failed(
                mesh,
                atlas_size=atlas_size,
                padding=padding,
                reason=f"OT-UVGS adapted control requires xatlas seed atlas: {base_atlas.failure_reason}",
                metadata=self._metadata(),
            )
        chart_ids = base_atlas.chart_ids
        area = chart_surface_areas(mesh, chart_ids)
        visibility = chart_visibility_scores(mesh, chart_ids)
        temperature = float(self.config.get("temperature", 0.8))
        raw_scores: Dict[int, float] = {}
        for chart in area:
            raw_scores[int(chart)] = max(area[chart], 1.0e-6) * max(visibility.get(chart, 0.0), 1.0e-3)
        if not raw_scores:
            raw_scores = {0: 1.0}
        mean_log = sum(math.log(score) for score in raw_scores.values()) / len(raw_scores)
        scales = {chart: math.exp((math.log(score) - mean_log) * temperature) for chart, score in raw_scores.items()}
        uv, face_uv, packed_chart_ids = repack_existing_charts(
            base_atlas.uv,
            base_atlas.face_uv,
            chart_ids,
            atlas_size=atlas_size,
            padding=padding,
            chart_scales=scales,
        )
        return self._success(
            uv=uv,
            face_uv=face_uv,
            chart_ids=packed_chart_ids,
            atlas_size=atlas_size,
            padding=padding,
            metadata=self._metadata(seed_backend="xatlas_classical", allocation_scores=raw_scores),
        )

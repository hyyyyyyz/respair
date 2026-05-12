"""Visibility-objective parameterization attempt required by B2 guardrails."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pbr_atlas.data.mesh_loader import MeshData

from .base import (
    BackendBase,
    chart_visibility_scores,
    load_external_or_none,
    pack_chart_patches,
    project_chart_patches,
    visibility_face_groups,
)


class VisibilityParamBackend(BackendBase):
    name = "visibility_param"
    paper_id = "arXiv:2509.25094v3"

    def generate(self, mesh: MeshData, atlas_size: int, padding: int, **kw: Any):
        artifact = load_external_or_none(kw.get("external_atlas") or self.config.get("external_atlas"))
        if artifact is not None:
            return self._load_external_npz(artifact, atlas_size, padding, metadata=self._metadata(source="external_npz"))

        command = self.config.get("command")
        repo_root = self._repo_root()
        output_path = Path(kw.get("external_out") or self.config.get("external_out", "")).expanduser() if (kw.get("external_out") or self.config.get("external_out")) else None
        if command and repo_root and output_path:
            result = self._run_command(
                command.format(
                    mesh_path=mesh.source_path,
                    output_npz=str(output_path),
                    atlas_size=atlas_size,
                    padding=padding,
                ),
                cwd=repo_root,
            )
            if result.returncode == 0 and output_path.exists():
                return self._load_external_npz(output_path, atlas_size, padding, metadata=self._metadata(source="external_command"))

        groups = visibility_face_groups(mesh)
        weights = chart_visibility_scores(mesh, groups)
        max_weight = max(weights.values()) if weights else 1.0
        scales = {chart: 0.65 + 0.7 * (value / max(max_weight, 1.0e-6)) for chart, value in weights.items()}
        patches = project_chart_patches(mesh, groups, projection="axis_planar")
        uv, face_uv, chart_ids = pack_chart_patches(patches, atlas_size=atlas_size, padding=padding, chart_scales=scales)
        reason = "Explicit arXiv:2509.25094v3 attempt not locally verified; using visibility-weighted proxy control."
        return self._success(
            uv=uv,
            face_uv=face_uv,
            chart_ids=chart_ids,
            atlas_size=atlas_size,
            padding=padding,
            repro_status="partial",
            failure_reason=reason,
            metadata=self._metadata(proxy="visibility_weighted_proxy"),
        )

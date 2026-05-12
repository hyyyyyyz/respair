"""FlexPara backend.

Real reproduction of FlexPara is NOT attempted because the upstream
arXiv:2504.19210v3 reference implementation requires:
- Python 3.9 + PyTorch 1.10.1 cu111 (incompatible with our 2.7.1 cu128 stack)
- Custom CUDA ops (cdbs/CD, cdbs/EMD) compiled against PyTorch 1.10
- No shipped pretrained checkpoints; flexpara_global.pth / flexpara_multi_8.pth
  must be trained from scratch per mesh (~10K iters)

These constraints exceed the B2 budget. Logged to baseline_failure_table.py.
The PCA-grid proxy remains as repro_status="partial" with explicit
failure_reason for sanity comparisons only — NOT a paper-grade reproduction.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pbr_atlas.data.mesh_loader import MeshData

from .base import BackendBase, load_external_or_none, pack_chart_patches, pca_grid_face_groups, project_chart_patches


class FlexParaBackend(BackendBase):
    name = "flexpara"
    paper_id = "arXiv:2504.19210v3"

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

        groups = pca_grid_face_groups(mesh)
        patches = project_chart_patches(mesh, groups, projection="normal_planar")
        uv, face_uv, chart_ids = pack_chart_patches(patches, atlas_size=atlas_size, padding=padding)
        reason = (
            "FlexPara reproduction skipped: requires Python 3.9 + PyTorch 1.10.1 cu111 "
            "with custom CUDA ops + no shipped checkpoints (per-mesh training). "
            "Using PCA-grid proxy for sanity only; not a paper-grade reproduction."
        )
        return self._success(
            uv=uv,
            face_uv=face_uv,
            chart_ids=chart_ids,
            atlas_size=atlas_size,
            padding=padding,
            repro_status="partial",
            failure_reason=reason,
            metadata=self._metadata(proxy="pca_grid_proxy"),
        )

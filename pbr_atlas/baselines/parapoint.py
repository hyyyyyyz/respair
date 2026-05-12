"""ParaPoint backend placeholder."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pbr_atlas.data.mesh_loader import MeshData

from .base import BackendBase, load_external_or_none


class ParaPointBackend(BackendBase):
    name = "parapoint"
    paper_id = "arXiv:2403.10349v1"

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

        return self._failed(
            mesh,
            atlas_size=atlas_size,
            padding=padding,
            reason="ParaPoint repo/checkpoint unavailable or unverified; logged as B2 reproduction failure.",
            metadata=self._metadata(),
        )

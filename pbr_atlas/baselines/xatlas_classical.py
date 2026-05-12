"""Classical xatlas backend for B2."""

from __future__ import annotations

from typing import Any

import torch

from pbr_atlas.data.mesh_loader import MeshData

from .base import BackendBase, infer_chart_ids


class XAtlasClassicalBackend(BackendBase):
    name = "xatlas_classical"
    paper_id = "xatlas"

    def is_available(self) -> bool:
        try:
            import xatlas  # noqa: F401
        except Exception:
            return False
        return True

    def generate(self, mesh: MeshData, atlas_size: int, padding: int, **kw: Any):
        try:
            import xatlas  # type: ignore
        except Exception as exc:
            return self._failed(
                mesh,
                atlas_size=atlas_size,
                padding=padding,
                reason=f"xatlas import failed: {exc}",
                metadata=self._metadata(),
            )
        try:
            _vmapping, indices, uvs = xatlas.parametrize(
                mesh.vertices.detach().cpu().numpy().astype("float32"),
                mesh.faces.detach().cpu().numpy().astype("uint32"),
            )
            face_uv = torch.as_tensor(indices, dtype=torch.long).reshape(-1, 3)
            uv = torch.as_tensor(uvs, dtype=torch.float32)
            chart_ids = infer_chart_ids(face_uv)
            return self._success(
                uv=uv,
                face_uv=face_uv,
                chart_ids=chart_ids,
                atlas_size=atlas_size,
                padding=padding,
                metadata=self._metadata(generator="xatlas.parametrize"),
            )
        except Exception as exc:
            return self._failed(
                mesh,
                atlas_size=atlas_size,
                padding=padding,
                reason=f"xatlas parameterization failed: {exc}",
                metadata=self._metadata(),
            )

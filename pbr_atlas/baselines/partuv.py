"""PartUV backend — real subprocess invocation of upstream demo/partuv_demo.py.

Falls back to dominant-axis proxy only if real invocation fails.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, List, Optional, Tuple

import numpy as np
import torch

from pbr_atlas.data.mesh_loader import MeshData

from .base import (
    BackendBase,
    dominant_axis_face_groups,
    pack_chart_patches,
    project_chart_patches,
)


def _mesh_hash(mesh: MeshData, atlas_size: int) -> str:
    """Stable hash of (vertices, faces, atlas_size). Hex digest, 16 chars."""
    h = hashlib.sha256()
    v = mesh.vertices.detach().cpu().numpy().astype(np.float32, copy=False).tobytes()
    f = mesh.faces.detach().cpu().numpy().astype(np.int64, copy=False).tobytes()
    h.update(v)
    h.update(f)
    h.update(str(int(atlas_size)).encode("utf-8"))
    return h.hexdigest()[:16]


class PartUVBackend(BackendBase):
    name = "partuv"
    paper_id = "arXiv:2511.16659v2"

    DEFAULT_REPO = "/data/dip_1_ws/baseline_repos/PartUV"
    DEFAULT_PYTHON = "/data/conda_envs/partuv/bin/python"
    DEFAULT_CKPT = "/data/dip_1_ws/ckpts/partfield/model_objaverse.ckpt"

    def is_available(self) -> bool:
        repo = Path(self.config.get("repo_root") or self.DEFAULT_REPO)
        py = Path(self.config.get("python_bin") or self.DEFAULT_PYTHON)
        ckpt = Path(self.config.get("partfield_ckpt") or self.DEFAULT_CKPT)
        return repo.exists() and py.exists() and ckpt.exists()

    def generate(self, mesh: MeshData, atlas_size: int, padding: int, **kw: Any):
        repo = Path(kw.get("repo_root") or self.config.get("repo_root") or self.DEFAULT_REPO)
        py = Path(kw.get("python_bin") or self.config.get("python_bin") or self.DEFAULT_PYTHON)
        ckpt = Path(kw.get("partfield_ckpt") or self.config.get("partfield_ckpt") or self.DEFAULT_CKPT)

        if not (repo.exists() and py.exists() and ckpt.exists()):
            return self._fall_back_to_proxy(
                mesh, atlas_size, padding,
                f"PartUV environment incomplete (repo={repo.exists()}, python={py.exists()}, ckpt={ckpt.exists()})",
            )

        # Mesh-hash cache: skip the slow upstream pipeline when the same
        # (vertices, faces, atlas_size) was already computed.
        cache_root = Path(kw.get("cache_root") or self.config.get("cache_root") or "/data/dip_1_ws/atlases/partuv_cache")
        cache_root.mkdir(parents=True, exist_ok=True)
        digest = _mesh_hash(mesh, atlas_size)
        cache_file = cache_root / f"{digest}.npz"
        if cache_file.exists():
            try:
                payload = np.load(cache_file, allow_pickle=False)
                uv = torch.from_numpy(payload["uv"]).float()
                face_uv = torch.from_numpy(payload["face_uv"]).long()
                chart_ids = torch.from_numpy(payload["chart_ids"]).long()
                metadata = self._metadata(
                    source="real_partuv_cache",
                    cache=str(cache_file),
                    digest=digest,
                    num_uv_vertices=int(uv.shape[0]),
                    num_charts=int(chart_ids.max().item()) + 1 if chart_ids.numel() else 0,
                )
                return self._success(
                    uv=uv, face_uv=face_uv, chart_ids=chart_ids,
                    atlas_size=atlas_size, padding=padding,
                    repro_status="ok", metadata=metadata,
                )
            except Exception:
                pass  # fall through to recompute

        ckpt_link = repo / "model_objaverse.ckpt"
        if not ckpt_link.exists():
            try:
                ckpt_link.symlink_to(ckpt)
            except OSError as exc:
                return self._fall_back_to_proxy(mesh, atlas_size, padding, f"PartUV ckpt symlink failed: {exc}")

        with tempfile.TemporaryDirectory(prefix="partuv_") as tmp:
            tmp_path = Path(tmp)
            # PartUV preprocess.py rewrites output_path to <dirname(P)>/<stem>/.
            # We make the input stem and output_path stem coincide so the
            # rewrite returns the same path we created.
            stem = "input"
            input_obj = tmp_path / f"{stem}.obj"
            self._write_input_obj(mesh, input_obj)

            output_dir = tmp_path / stem
            output_dir.mkdir(parents=True, exist_ok=True)

            cmd = [
                str(py), "demo/partuv_demo.py",
                "--mesh_path", str(input_obj),
                "--output_path", str(output_dir),
                "--pack_method", "blender",
            ]
            env = os.environ.copy()
            env.setdefault("CUDA_VISIBLE_DEVICES", "1")
            try:
                proc = subprocess.run(
                    cmd, cwd=str(repo), capture_output=True, text=True, env=env, timeout=600,
                )
            except subprocess.TimeoutExpired as exc:
                return self._fall_back_to_proxy(mesh, atlas_size, padding, f"PartUV timed out: {exc}")
            except FileNotFoundError as exc:
                return self._fall_back_to_proxy(mesh, atlas_size, padding, f"PartUV launch failed: {exc}")

            uv_obj = output_dir / "final_components.obj"
            if not uv_obj.exists():
                stderr_tail = (proc.stderr or proc.stdout)[-400:].replace("\n", " | ")
                return self._fall_back_to_proxy(
                    mesh, atlas_size, padding,
                    f"PartUV did not produce final_components.obj (rc={proc.returncode}): {stderr_tail}",
                )

            try:
                uv, face_uv, chart_ids = self._parse_partuv_obj(uv_obj, mesh)
            except Exception as exc:  # parse error → fall back
                return self._fall_back_to_proxy(
                    mesh, atlas_size, padding,
                    f"PartUV OBJ parse failed: {exc}",
                )

            try:
                np.savez(
                    cache_file,
                    uv=uv.detach().cpu().numpy().astype(np.float32, copy=False),
                    face_uv=face_uv.detach().cpu().numpy().astype(np.int64, copy=False),
                    chart_ids=chart_ids.detach().cpu().numpy().astype(np.int64, copy=False),
                )
            except Exception:
                pass

            metadata = self._metadata(
                source="real_partuv_demo",
                repo=str(repo),
                ckpt=str(ckpt),
                cache=str(cache_file),
                digest=digest,
                num_uv_vertices=int(uv.shape[0]),
                num_charts=int(chart_ids.max().item()) + 1 if chart_ids.numel() else 0,
            )
            return self._success(
                uv=uv,
                face_uv=face_uv,
                chart_ids=chart_ids,
                atlas_size=atlas_size,
                padding=padding,
                repro_status="ok",
                metadata=metadata,
            )

    @staticmethod
    def _write_input_obj(mesh: MeshData, path: Path) -> None:
        verts = mesh.vertices.detach().cpu().numpy()
        faces = mesh.faces.detach().cpu().numpy()
        lines: List[str] = []
        for v in verts:
            lines.append(f"v {v[0]:.8f} {v[1]:.8f} {v[2]:.8f}\n")
        for f in faces:
            lines.append(f"f {int(f[0])+1} {int(f[1])+1} {int(f[2])+1}\n")
        path.write_text("".join(lines))

    @staticmethod
    def _parse_partuv_obj(obj_path: Path, mesh: MeshData) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        uv_list: List[Tuple[float, float]] = []
        face_uv_list: List[Tuple[int, int, int]] = []
        with obj_path.open("r") as fh:
            for raw in fh:
                line = raw.strip()
                if not line:
                    continue
                if line.startswith("vt "):
                    parts = line.split()
                    uv_list.append((float(parts[1]), float(parts[2])))
                elif line.startswith("f "):
                    parts = line.split()[1:]
                    if len(parts) != 3:
                        continue
                    indices: List[int] = []
                    for token in parts:
                        if "/" in token:
                            slash_parts = token.split("/")
                            if len(slash_parts) >= 2 and slash_parts[1]:
                                indices.append(int(slash_parts[1]) - 1)
                            else:
                                indices.append(-1)
                        else:
                            indices.append(-1)
                    if any(i < 0 for i in indices):
                        continue
                    face_uv_list.append((indices[0], indices[1], indices[2]))
        if not uv_list or not face_uv_list:
            raise ValueError("PartUV OBJ: no vt or no f lines parsed")
        if len(face_uv_list) != int(mesh.faces.shape[0]):
            raise ValueError(
                f"PartUV face count {len(face_uv_list)} != input mesh face count {int(mesh.faces.shape[0])}"
            )
        uv = torch.tensor(uv_list, dtype=torch.float32)
        face_uv = torch.tensor(face_uv_list, dtype=torch.long)
        chart_ids = PartUVBackend._uv_island_chart_ids(face_uv)
        return uv, face_uv, chart_ids

    @staticmethod
    def _uv_island_chart_ids(face_uv: torch.Tensor) -> torch.Tensor:
        """Detect UV islands via union-find on face-UV adjacency.

        Two faces share an island iff they share a UV vertex index. Returns
        per-face chart_ids consecutively renumbered from 0.
        """
        n_faces = int(face_uv.shape[0])
        parent = list(range(n_faces))

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a: int, b: int) -> None:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb

        # Map UV vertex index -> first face containing it. When another face
        # also references that UV vertex, union the two faces.
        uv_to_face: dict[int, int] = {}
        face_uv_list = face_uv.tolist()
        for fi, tri in enumerate(face_uv_list):
            for vt in tri:
                if vt in uv_to_face:
                    union(fi, uv_to_face[vt])
                else:
                    uv_to_face[vt] = fi

        roots = [find(i) for i in range(n_faces)]
        unique_roots = sorted(set(roots))
        remap = {r: i for i, r in enumerate(unique_roots)}
        chart_ids = torch.tensor([remap[r] for r in roots], dtype=torch.long)
        return chart_ids

    def _fall_back_to_proxy(self, mesh: MeshData, atlas_size: int, padding: int, reason: str):
        groups = dominant_axis_face_groups(mesh)
        patches = project_chart_patches(mesh, groups, projection="axis_planar")
        uv, face_uv, chart_ids = pack_chart_patches(patches, atlas_size=atlas_size, padding=padding)
        return self._success(
            uv=uv,
            face_uv=face_uv,
            chart_ids=chart_ids,
            atlas_size=atlas_size,
            padding=padding,
            repro_status="partial",
            failure_reason=reason,
            metadata=self._metadata(proxy="dominant_axis_part_proxy", fallback_reason=reason),
        )

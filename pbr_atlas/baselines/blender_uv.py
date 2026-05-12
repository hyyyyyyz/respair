"""Automated Blender Smart UV backend."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import torch

from pbr_atlas.data.mesh_loader import MeshData

from .base import BackendBase, infer_chart_ids

_BLENDER_HELPER = r"""
import json
import sys
from pathlib import Path

import bpy


def import_mesh(path: str):
    suffix = Path(path).suffix.lower()
    if suffix == ".obj":
        # Blender 3.4+ has bpy.ops.wm.obj_import (built-in); older versions use addon import_scene.obj
        try:
            bpy.ops.wm.obj_import(filepath=path)
        except AttributeError:
            try:
                bpy.ops.import_scene.obj(filepath=path)
            except AttributeError:
                # Old Blender requires enabling the OBJ addon explicitly
                try:
                    bpy.ops.preferences.addon_enable(module="io_scene_obj")
                except Exception:
                    pass
                bpy.ops.import_scene.obj(filepath=path)
    elif suffix in {".glb", ".gltf"}:
        bpy.ops.import_scene.gltf(filepath=path)
    elif suffix == ".ply":
        if hasattr(bpy.ops.wm, "ply_import"):
            bpy.ops.wm.ply_import(filepath=path)
        else:
            bpy.ops.import_mesh.ply(filepath=path)
    else:
        raise RuntimeError(f"Unsupported mesh suffix: {suffix}")


argv = sys.argv[sys.argv.index("--") + 1 :]
mesh_path, out_path, island_margin, angle_limit = argv[0], argv[1], float(argv[2]), float(argv[3])
bpy.ops.wm.read_factory_settings(use_empty=True)
import_mesh(mesh_path)
meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
if not meshes:
    raise RuntimeError("No mesh object imported.")
obj = meshes[0]
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.quads_convert_to_tris(quad_method="BEAUTY", ngon_method="BEAUTY")
bpy.ops.uv.smart_project(
    angle_limit=angle_limit,
    island_margin=island_margin,
    area_weight=0.0,
    correct_aspect=True,
    scale_to_bounds=True,
)
bpy.ops.object.mode_set(mode="OBJECT")
mesh = obj.data
uv_layer = mesh.uv_layers.active
if uv_layer is None:
    raise RuntimeError("Blender Smart UV did not create a UV layer.")
uv_map = {}
uvs = []
face_uv = []
for poly in mesh.polygons:
    if len(poly.loop_indices) != 3:
        continue
    indices = []
    for loop_idx in poly.loop_indices:
        uv = uv_layer.data[loop_idx].uv
        key = (round(float(uv.x), 8), round(float(uv.y), 8))
        if key not in uv_map:
            uv_map[key] = len(uvs)
            uvs.append([float(uv.x), float(uv.y)])
        indices.append(uv_map[key])
    face_uv.append(indices)
payload = {"uv": uvs, "face_uv": face_uv}
Path(out_path).write_text(json.dumps(payload), encoding="utf-8")
"""


class BlenderUVBackend(BackendBase):
    name = "blender_uv"
    paper_id = "Blender Smart UV Project"

    def is_available(self) -> bool:
        blender_bin = str(self.config.get("blender_bin", "blender"))
        return self._command_available(blender_bin)

    def generate(self, mesh: MeshData, atlas_size: int, padding: int, **kw: Any):
        blender_bin = str(kw.get("blender_bin") or self.config.get("blender_bin", "blender"))
        if not self._command_available(blender_bin):
            return self._failed(
                mesh,
                atlas_size=atlas_size,
                padding=padding,
                reason=f"Blender executable not found: {blender_bin}",
                metadata=self._metadata(),
            )
        mesh_path = Path(mesh.source_path)
        if not mesh_path.exists():
            return self._failed(
                mesh,
                atlas_size=atlas_size,
                padding=padding,
                reason=f"Mesh source path missing for Blender import: {mesh.source_path}",
                metadata=self._metadata(),
            )
        margin = float(self.config.get("island_margin", max(padding / max(atlas_size, 1), 1.0e-3)))
        angle_limit = float(self.config.get("angle_limit_deg", 66.0))
        with tempfile.TemporaryDirectory(prefix="pbr_atlas_blender_") as tmpdir:
            script_path = Path(tmpdir) / "smart_uv.py"
            out_path = Path(tmpdir) / "atlas.json"
            script_path.write_text(_BLENDER_HELPER, encoding="utf-8")
            result = self._run_command(
                " ".join(
                    [
                        blender_bin,
                        "--background",
                        "--factory-startup",
                        "--python",
                        str(script_path),
                        "--",
                        str(mesh_path),
                        str(out_path),
                        str(margin),
                        str(angle_limit),
                    ]
                )
            )
            if result.returncode != 0 or not out_path.exists():
                stderr = (result.stderr or result.stdout or "").strip()
                return self._failed(
                    mesh,
                    atlas_size=atlas_size,
                    padding=padding,
                    reason=f"Blender Smart UV failed: {stderr[:300]}",
                    metadata=self._metadata(),
                )
            payload = json.loads(out_path.read_text(encoding="utf-8"))
        uv = torch.as_tensor(payload["uv"], dtype=torch.float32)
        face_uv = torch.as_tensor(payload["face_uv"], dtype=torch.long)
        chart_ids = infer_chart_ids(face_uv)
        return self._success(
            uv=uv,
            face_uv=face_uv,
            chart_ids=chart_ids,
            atlas_size=atlas_size,
            padding=padding,
            metadata=self._metadata(generator="blender_smart_uv", island_margin=margin, angle_limit_deg=angle_limit),
        )

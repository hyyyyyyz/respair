"""Poly Haven CC0 PBR asset loader.

Loads a single mesh + authored albedo/normal/metallicRoughness PBR maps from
the gltf 2.0 bundle Polyhaven publishes for each model. Used as a real-PBR
asset proxy track (BEAST proposal #2). Multi-material assets are flattened
to a single per-face PBR sample by sampling each face from its primitive's
material, then exposed as a ``FacePBRValues`` object compatible with the
C1-C5 baker pipeline.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import numpy as np
import torch

from pbr_atlas.baker import FacePBRValues
from pbr_atlas.baker.ggx import normalize
from pbr_atlas.data.mesh_loader import MeshData


POLYHAVEN_SLUGS_DEFAULT = (
    "ArmChair_01", "Barrel_01", "Camera_01", "Chandelier_01",
    "ClassicConsole_01", "CoffeeTable_01", "Drill_01", "GreenChair_01",
    "Lantern_01", "Sofa_01", "Television_01", "Ukulele_01",
)


@dataclass
class PolyHavenAsset:
    name: str
    mesh: MeshData
    face_pbr: FacePBRValues
    materials_used: list[str]
    raw_root: Path


def _load_image_uint8(path: Path) -> np.ndarray:
    import cv2

    img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if img is None:
        raise FileNotFoundError(path)
    if img.ndim == 2:
        img = np.stack([img, img, img], axis=-1)
    else:
        img = img[..., ::-1]  # BGR -> RGB
    if img.dtype != np.uint8:
        denom = float(np.iinfo(img.dtype).max) if np.issubdtype(img.dtype, np.integer) else 1.0
        img = (img.astype(np.float32) / denom * 255).clip(0, 255).astype(np.uint8)
    return img


def _sample_texture_at_uv(image: np.ndarray, uv: np.ndarray) -> np.ndarray:
    """Bilinear sample image at uv ∈ [0,1]^2. Returns float32 [0,1] of shape [N, C]."""
    if image.dtype == np.uint8:
        img = image.astype(np.float32) / 255.0
    else:
        img = image.astype(np.float32)
    if img.ndim == 2:
        img = img[..., None]
    H, W = img.shape[:2]
    u = np.clip(uv[:, 0], 0.0, 1.0) * (W - 1)
    v = np.clip(1.0 - uv[:, 1], 0.0, 1.0) * (H - 1)
    x0 = np.floor(u).astype(np.int64)
    y0 = np.floor(v).astype(np.int64)
    x1 = np.clip(x0 + 1, 0, W - 1)
    y1 = np.clip(y0 + 1, 0, H - 1)
    fx = (u - x0).reshape(-1, 1)
    fy = (v - y0).reshape(-1, 1)
    a = img[y0, x0] * (1 - fx) * (1 - fy)
    b = img[y0, x1] * fx * (1 - fy)
    c = img[y1, x0] * (1 - fx) * fy
    d = img[y1, x1] * fx * fy
    return (a + b + c + d).astype(np.float32)


def load_polyhaven_asset(slug: str, root: str | Path, *, device: Optional[torch.device] = None) -> PolyHavenAsset:
    """Load Polyhaven gltf 2.0 model + textures into mesh + per-face PBR values.

    Args:
        slug: e.g. ``Camera_01``.
        root: dataset root, e.g. ``datasets/polyhaven_proxy/raw``.
    """
    import trimesh
    device = device or torch.device("cpu")
    root = Path(root)
    asset_dir = root / slug
    if not asset_dir.exists():
        raise FileNotFoundError(asset_dir)
    gltf_files = sorted(asset_dir.glob("*.gltf"))
    if not gltf_files:
        raise FileNotFoundError(f"no .gltf under {asset_dir}")
    gltf_path = gltf_files[0]
    scene = trimesh.load(str(gltf_path), force="scene")
    if isinstance(scene, trimesh.Trimesh):
        merged = scene
        materials_used = ["default"]
    else:
        merged = trimesh.util.concatenate([g for g in scene.geometry.values() if isinstance(g, trimesh.Trimesh)])
        materials_used = list(scene.geometry.keys())

    vertices = torch.from_numpy(merged.vertices.astype(np.float32))
    faces = torch.from_numpy(merged.faces.astype(np.int64))
    if hasattr(merged.visual, "uv") and merged.visual.uv is not None:
        uv_per_vertex = torch.from_numpy(merged.visual.uv.astype(np.float32))
    else:
        uv_per_vertex = torch.zeros((vertices.shape[0], 2), dtype=torch.float32)
    face_uv = faces.clone()
    chart_ids = torch.zeros(faces.shape[0], dtype=torch.long)
    normals_per_vertex = torch.from_numpy(merged.vertex_normals.astype(np.float32))
    normals_per_face = torch.from_numpy(merged.face_normals.astype(np.float32))

    mesh = MeshData(
        vertices=vertices.to(device),
        faces=faces.to(device),
        uv=uv_per_vertex.to(device),
        face_uv=face_uv.to(device),
        normals_per_face=normals_per_face.to(device),
        normals_per_vertex=normals_per_vertex.to(device),
        chart_ids=chart_ids.to(device),
        source_path=str(gltf_path),
    )

    gltf_json = json.loads(gltf_path.read_text())
    images = gltf_json.get("images", [])
    image_paths = [asset_dir / img.get("uri", "") for img in images]

    diffuse_img: Optional[np.ndarray] = None
    normal_img: Optional[np.ndarray] = None
    metallic_roughness_img: Optional[np.ndarray] = None
    materials = gltf_json.get("materials", [])
    if materials:
        m = materials[0]
        pbr = m.get("pbrMetallicRoughness", {})
        bc_ix = (pbr.get("baseColorTexture") or {}).get("index")
        mr_ix = (pbr.get("metallicRoughnessTexture") or {}).get("index")
        n_ix = (m.get("normalTexture") or {}).get("index")
        textures = gltf_json.get("textures", [])
        def _img_for(ix):
            if ix is None or ix >= len(textures):
                return None
            src = textures[ix].get("source")
            if src is None or src >= len(image_paths):
                return None
            p = image_paths[src]
            return _load_image_uint8(p) if p.exists() else None
        diffuse_img = _img_for(bc_ix)
        metallic_roughness_img = _img_for(mr_ix)
        normal_img = _img_for(n_ix)

    face_uv_centroids = uv_per_vertex[faces].mean(dim=1).cpu().numpy()
    n_faces = faces.shape[0]

    if diffuse_img is not None:
        albedo = _sample_texture_at_uv(diffuse_img, face_uv_centroids)
        if albedo.shape[1] >= 3:
            albedo = albedo[:, :3]
        else:
            albedo = np.repeat(albedo, 3, axis=1) if albedo.shape[1] == 1 else np.zeros((n_faces, 3), dtype=np.float32)
    else:
        albedo = np.full((n_faces, 3), 0.5, dtype=np.float32)

    if normal_img is not None:
        n_sample = _sample_texture_at_uv(normal_img, face_uv_centroids)
        if n_sample.shape[1] >= 3:
            n_sample = n_sample[:, :3] * 2.0 - 1.0
        else:
            n_sample = np.tile(np.array([0, 0, 1], dtype=np.float32), (n_faces, 1))
    else:
        n_sample = np.tile(np.array([0, 0, 1], dtype=np.float32), (n_faces, 1))

    if metallic_roughness_img is not None:
        mr = _sample_texture_at_uv(metallic_roughness_img, face_uv_centroids)
        if mr.shape[1] >= 3:
            roughness = mr[:, 1:2]
            metallic = mr[:, 2:3]
        elif mr.shape[1] == 2:
            roughness = mr[:, :1]
            metallic = mr[:, 1:2]
        else:
            roughness = mr[:, :1]
            metallic = np.zeros((n_faces, 1), dtype=np.float32)
    else:
        roughness = np.full((n_faces, 1), 0.5, dtype=np.float32)
        metallic = np.zeros((n_faces, 1), dtype=np.float32)

    face_pbr = FacePBRValues(
        albedo=torch.from_numpy(np.clip(albedo, 0.0, 1.0)).to(device),
        normal=normalize(torch.from_numpy(n_sample).to(device)),
        roughness=torch.from_numpy(np.clip(roughness, 0.02, 1.0).reshape(-1, 1)).to(device),
        metallic=torch.from_numpy(np.clip(metallic, 0.0, 1.0).reshape(-1, 1)).to(device),
    )

    return PolyHavenAsset(name=slug, mesh=mesh, face_pbr=face_pbr, materials_used=materials_used, raw_root=asset_dir)


__all__ = ["POLYHAVEN_SLUGS_DEFAULT", "PolyHavenAsset", "load_polyhaven_asset"]

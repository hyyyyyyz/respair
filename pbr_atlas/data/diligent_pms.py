"""Lambertian photometric stereo for DiLiGenT-MV captured imagery.

Given a DiLiGenT-MV asset (mesh + per-view images + per-view light directions),
this module solves for per-face Lambertian albedo and normal by accumulating
all (view, light) hits per face and least-squares fitting the lighting matrix.

This replaces the synthetic-oracle PBR face values when the supervisory target
is captured imagery. With PMS face values, the predicted render through any UV
atlas should approximate the captured imagery (modulo non-Lambertian effects),
making the residual reflect atlas defects rather than material mismatch.

Reference: classical Lambertian PMS, ``Photometric stereo'' (Woodham 1980).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
import torch

from pbr_atlas.baker import FacePBRValues
from pbr_atlas.data.diligent_mv import DiLiGenTMVAsset


@dataclass
class PMSResult:
    face_pbr: FacePBRValues
    fit_residual_per_face: torch.Tensor  # [F] mean residual after LS solve
    coverage_per_face: torch.Tensor      # [F] number of (view, light) pairs that hit
    fit_count: int
    skipped_faces: int


def _world_to_cam_dir(d_world: np.ndarray, R_w2c: np.ndarray) -> np.ndarray:
    return R_w2c @ d_world.reshape(3, 1)


def _project_face_centroids(vertices_cam: np.ndarray, faces: np.ndarray, K: np.ndarray) -> np.ndarray:
    centroids = vertices_cam[faces].mean(axis=1)
    z = centroids[:, 2:3].clip(min=1e-6)
    uv_homog = (K @ centroids.T).T
    pix = uv_homog[:, :2] / z
    return pix


def _gather_face_observations(
    asset: DiLiGenTMVAsset,
    *,
    view_indices: Optional[list[int]] = None,
    light_indices: Optional[list[int]] = None,
    min_visibility: float = 1.0,
) -> tuple[list[np.ndarray], list[np.ndarray]]:
    """Return per-face lists of light direction vectors (in mesh frame) and
    captured intensities (single channel mean) accumulated across all
    selected (view, light) pairs.

    For each face we project the centroid into each view's image plane and
    sample the captured intensity at that pixel if inside mask. This is a
    fast approximation; a per-face rasterizer would be more accurate but
    much slower.
    """
    mesh = asset.mesh
    vertices_w = mesh.vertices.detach().cpu().numpy().astype(np.float64)
    faces = mesh.faces.detach().cpu().numpy().astype(np.int64)
    n_faces = int(faces.shape[0])

    light_dirs: list[list[np.ndarray]] = [[] for _ in range(n_faces)]
    obs: list[list[float]] = [[] for _ in range(n_faces)]

    view_idx_list = view_indices if view_indices is not None else list(range(asset.num_views()))

    for vi in view_idx_list:
        view = asset.views[vi]
        K = view.intrinsic.detach().cpu().numpy().astype(np.float64)
        E = view.extrinsic.detach().cpu().numpy().astype(np.float64)
        R = E[:3, :3]
        t = E[:3, 3:4]
        cam_t = (R @ vertices_w.T + t).T
        pix = _project_face_centroids(cam_t, faces, K)
        H, W = view.image_size
        mask = view.mask.detach().cpu().numpy()
        # bilinear-sampled intensity per face per light is cheaper as nearest
        ix = np.round(pix[:, 0]).astype(np.int64)
        iy = np.round(pix[:, 1]).astype(np.int64)
        in_bounds = (ix >= 0) & (ix < W) & (iy >= 0) & (iy < H)
        ix_c = np.clip(ix, 0, W - 1); iy_c = np.clip(iy, 0, H - 1)
        face_in_mask = in_bounds & mask[iy_c, ix_c]
        # light directions in world frame (per-view per-light)
        Lw = view.light_directions_world.detach().cpu().numpy().astype(np.float64)  # [Nl,3]

        n_lights = Lw.shape[0]
        if light_indices is not None:
            li_list = list(light_indices)
        else:
            li_list = list(range(n_lights))

        # captured images at view_v indexed by light: [Nl,H,W,3]
        imgs = view.images.detach().cpu().numpy()  # already intensity-normalized
        for li in li_list:
            d_w = Lw[li] / max(np.linalg.norm(Lw[li]), 1e-8)
            img_l = imgs[li].mean(axis=-1)  # grayscale
            for fi in np.where(face_in_mask)[0]:
                pix_val = float(img_l[iy_c[fi], ix_c[fi]])
                # Keep all observations (including 0) — PMS LS handles them as "in shadow".
                # Skipping pix_val<=0 was discarding 99% of observations on dark captured imagery.
                light_dirs[fi].append(d_w.astype(np.float32))
                obs[fi].append(pix_val)

    return [np.asarray(d) if d else np.zeros((0, 3), dtype=np.float32) for d in light_dirs], \
           [np.asarray(o, dtype=np.float32) if o else np.zeros((0,), dtype=np.float32) for o in obs]


def fit_lambertian_pms(
    asset: DiLiGenTMVAsset,
    *,
    view_indices: Optional[list[int]] = None,
    light_indices: Optional[list[int]] = None,
    min_lights_per_face: int = 4,
    default_normal: tuple[float, float, float] = (0.0, 0.0, 1.0),
    default_albedo: float = 0.5,
    device: Optional[torch.device] = None,
) -> PMSResult:
    """Closed-form Lambertian PS per face: solve M @ (alb*n) = b.

    For each face with K observations: M is [K,3] light directions; b is [K]
    intensities. Solve g = (M^T M)^-1 M^T b. Albedo = ||g||, normal = g/albedo.

    Faces with fewer than ``min_lights_per_face`` valid observations fall
    back to ``(default_normal, default_albedo)``.
    """
    device = device or torch.device("cpu")
    Lw_per_face, obs_per_face = _gather_face_observations(
        asset,
        view_indices=view_indices,
        light_indices=light_indices,
    )
    n_faces = len(Lw_per_face)
    albedos = np.full((n_faces, 3), default_albedo, dtype=np.float32)
    normals = np.tile(np.asarray(default_normal, dtype=np.float32), (n_faces, 1))
    fit_residuals = np.zeros((n_faces,), dtype=np.float32)
    coverage = np.zeros((n_faces,), dtype=np.int32)
    skipped = 0
    for fi in range(n_faces):
        Lw = Lw_per_face[fi]
        b = obs_per_face[fi]
        coverage[fi] = int(b.shape[0])
        if b.shape[0] < min_lights_per_face:
            skipped += 1
            continue
        try:
            # Solve g = argmin ||Lw @ g - b||
            g, residuals, rank, _ = np.linalg.lstsq(Lw.astype(np.float64), b.astype(np.float64), rcond=None)
            alb = float(np.linalg.norm(g))
            if alb < 1e-6:
                skipped += 1
                continue
            n = (g / alb).astype(np.float32)
            albedos[fi] = float(alb)
            normals[fi] = n
            pred = Lw @ g
            err = float(np.mean((pred - b) ** 2)) if b.shape[0] else 0.0
            fit_residuals[fi] = err
        except Exception:
            skipped += 1
            continue

    albedos = np.clip(albedos, 0.0, 1.0)
    normals_t = torch.from_numpy(normals).to(device)
    normals_t = normals_t / normals_t.norm(dim=-1, keepdim=True).clamp_min(1e-6)
    albedo_t = torch.from_numpy(albedos).to(device)
    if albedo_t.ndim == 1:
        albedo_t = albedo_t.unsqueeze(-1).expand(-1, 3).contiguous()
    elif albedo_t.shape[-1] != 3:
        albedo_t = albedo_t[..., :1].expand(-1, 3).contiguous()
    roughness = torch.full((n_faces, 1), 0.5, dtype=torch.float32, device=device)
    metallic = torch.zeros((n_faces, 1), dtype=torch.float32, device=device)
    face_pbr = FacePBRValues(albedo=albedo_t, normal=normals_t, roughness=roughness, metallic=metallic)
    return PMSResult(
        face_pbr=face_pbr,
        fit_residual_per_face=torch.from_numpy(fit_residuals).to(device),
        coverage_per_face=torch.from_numpy(coverage).to(device),
        fit_count=n_faces - skipped,
        skipped_faces=skipped,
    )


__all__ = ["PMSResult", "fit_lambertian_pms"]

"""DiLiGenT-MV captured photometric stereo loader.

Provides per-asset multi-view multi-light captured imagery, camera
intrinsics/extrinsics, ground-truth mesh, mask, per-light directions
and intensities for use as a captured target signal in the C1-C5
PBR atlas repair pipeline.

Reference: Park et al., DiLiGenT-MV (https://sites.google.com/site/photometricstereodata/mv).
Five objects (Bear, Cow, Pot2, Buddha, Reading), 20 views per object,
96 lights per view, ground-truth mesh provided.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Sequence

import numpy as np
import torch

from pbr_atlas.baker import LightSpec, ViewSpec
from pbr_atlas.data.mesh_loader import MeshData, load_mesh


DILIGENT_MV_OBJECTS = ("bear", "cow", "pot2", "buddha", "reading")


@dataclass
class DiLiGenTMVView:
    """Single view: camera + 96 captured images under different lights."""

    view_index: int
    intrinsic: torch.Tensor  # 3x3
    extrinsic: torch.Tensor  # 4x4 world-to-camera
    image_size: tuple[int, int]  # (H, W)
    images: torch.Tensor  # [N_l, H, W, 3] linear, normalized by light intensity
    mask: torch.Tensor  # [H, W] bool
    light_directions_world: torch.Tensor  # [N_l, 3] unit vectors in world frame
    light_intensities: torch.Tensor  # [N_l, 3] per-light per-channel scalar


@dataclass
class DiLiGenTMVAsset:
    """Aggregate DiLiGenT-MV asset bundle."""

    name: str
    mesh: MeshData
    views: list[DiLiGenTMVView]

    def num_views(self) -> int:
        return len(self.views)

    def num_lights_per_view(self) -> int:
        return int(self.views[0].images.shape[0]) if self.views else 0


def _read_calib_results(path: Path) -> tuple[list[np.ndarray], list[np.ndarray]]:
    """Read DiLiGenT-MV ``Calib_Results.mat`` into per-view K and Rt arrays."""
    from scipy.io import loadmat

    data = loadmat(str(path), squeeze_me=True, struct_as_record=False)
    intrinsics: list[np.ndarray] = []
    extrinsics: list[np.ndarray] = []

    if "K" in data and "Rc" in data and "Tc" in data:
        K = np.asarray(data["K"], dtype=np.float64)
        Rc_all = np.asarray(data["Rc"])
        Tc_all = np.asarray(data["Tc"])
        for view_i in range(len(Rc_all)):
            R = np.asarray(Rc_all[view_i], dtype=np.float64)
            T = np.asarray(Tc_all[view_i], dtype=np.float64).reshape(3, 1)
            E = np.eye(4, dtype=np.float64)
            E[:3, :3] = R
            E[:3, 3:4] = T
            intrinsics.append(K)
            extrinsics.append(E)
        return intrinsics, extrinsics

    if "KK" in data:
        K_shared = np.asarray(data["KK"], dtype=np.float64)
        for view_i in range(1, 100):
            rc_key = f"Rc_{view_i}"
            tc_key = f"Tc_{view_i}"
            if rc_key not in data:
                break
            R = np.asarray(data[rc_key], dtype=np.float64)
            T = np.asarray(data[tc_key], dtype=np.float64).reshape(3, 1)
            E = np.eye(4, dtype=np.float64)
            E[:3, :3] = R
            E[:3, 3:4] = T
            intrinsics.append(K_shared)
            extrinsics.append(E)
        if intrinsics:
            return intrinsics, extrinsics

    for view_i in range(1, 100):
        kc_key = f"KK_{view_i}"
        rc_key = f"Rc_{view_i}"
        tc_key = f"Tc_{view_i}"
        if kc_key not in data:
            break
        K = np.asarray(data[kc_key], dtype=np.float64)
        R = np.asarray(data[rc_key], dtype=np.float64)
        T = np.asarray(data[tc_key], dtype=np.float64).reshape(3, 1)
        E = np.eye(4, dtype=np.float64)
        E[:3, :3] = R
        E[:3, 3:4] = T
        intrinsics.append(K)
        extrinsics.append(E)
    if not intrinsics:
        raise ValueError(f"Could not parse intrinsics/extrinsics from {path}")
    return intrinsics, extrinsics


def _read_text_matrix(path: Path) -> np.ndarray:
    return np.loadtxt(str(path), dtype=np.float64)


def _load_image_linear(path: Path) -> np.ndarray:
    """Load 16-bit (or 8-bit) PNG as linear float32 in [0, 1] without gamma."""
    import cv2

    img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED | cv2.IMREAD_ANYDEPTH | cv2.IMREAD_ANYCOLOR)
    if img is None:
        raise FileNotFoundError(f"failed to read {path}")
    if img.ndim == 2:
        img = np.stack([img, img, img], axis=-1)
    img = img[..., ::-1]  # BGR -> RGB
    if img.dtype == np.uint8:
        denom = 255.0
    elif img.dtype == np.uint16:
        denom = 65535.0
    else:
        denom = float(np.iinfo(img.dtype).max) if np.issubdtype(img.dtype, np.integer) else 1.0
    return (img.astype(np.float32) / denom).astype(np.float32)


def _erode_mask(mask: np.ndarray, pixels: int) -> np.ndarray:
    if pixels <= 0:
        return mask
    import cv2

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2 * pixels + 1, 2 * pixels + 1))
    return cv2.erode(mask.astype(np.uint8), kernel).astype(bool)


def _detect_view_dirs(asset_root: Path) -> list[Path]:
    candidates = sorted(p for p in asset_root.iterdir() if p.is_dir())
    view_dirs = []
    for path in candidates:
        if path.name.lower().startswith("view"):
            view_dirs.append(path)
    if not view_dirs:
        for path in candidates:
            if any((path / f).exists() for f in ("light_directions.txt", "view_01.png", "001.png")):
                view_dirs.append(path)
    return view_dirs


def load_diligent_mv_asset(
    object_name: str,
    root: str | Path,
    *,
    erode_mask_pixels: int = 2,
    saturation_threshold: float = 0.99,
    max_views: Optional[int] = None,
    max_lights: Optional[int] = None,
    decimate_faces: Optional[int] = 20000,
    device: Optional[torch.device] = None,
) -> DiLiGenTMVAsset:
    """Load one DiLiGenT-MV object with all views + lights + mesh.

    Args:
        object_name: one of ``DILIGENT_MV_OBJECTS``.
        root: dataset root containing ``bearPNG/``, ``cowPNG/``, etc.
        erode_mask_pixels: morphological erosion radius for silhouette mask.
        saturation_threshold: per-channel value above which a pixel is treated
            as saturated and excluded by zeroing the mask there.
        max_views, max_lights: caps for smoke testing.
    """
    device = device or torch.device("cpu")
    root = Path(root)
    object_lower = object_name.strip().lower()
    candidates = [root / f"{object_name}PNG", root / f"{object_lower}PNG", root / object_name, root / object_lower]
    asset_root: Optional[Path] = None
    for p in candidates:
        if p.is_dir():
            asset_root = p
            break
    if asset_root is None:
        raise FileNotFoundError(f"DiLiGenT-MV object dir not found for {object_name} under {root}")

    mesh_path: Optional[Path] = None
    for cand in [asset_root / "mesh_Gt.ply", asset_root / "mesh_Gt.obj", asset_root / "mesh.ply"]:
        if cand.exists():
            mesh_path = cand
            break
    if mesh_path is None:
        glob = list(asset_root.glob("*.ply")) + list(asset_root.glob("*.obj"))
        if glob:
            mesh_path = glob[0]
    if mesh_path is None:
        raise FileNotFoundError(f"GT mesh not found in {asset_root}")

    # DiLiGenT-MV uses mm-scale meshes (~80 units) at ~1500 mm camera distance,
    # which exceeds the baker's perspective clip range [0.05, 20]. We apply a
    # uniform scale + center so mesh sits roughly in a unit-radius region near
    # the origin while preserving the camera/light geometry. The camera
    # translation is rescaled by the same factor so projections match.
    raw_tm = None

    def _load_mesh_no_normalize(path: Path) -> "MeshData":
        """Load mesh while preserving original world-frame coordinates (DiLiGenT
        needs the raw mm-scale to match Calib_Results.mat extrinsics).
        """
        import trimesh
        from pbr_atlas.data.mesh_loader import MeshData
        tm = trimesh.load(str(path), force="mesh")
        verts = np.asarray(tm.vertices, dtype=np.float32)
        faces = np.asarray(tm.faces, dtype=np.int64)
        n_p_face = np.asarray(tm.face_normals, dtype=np.float32)
        n_p_vert = np.asarray(tm.vertex_normals, dtype=np.float32)
        H = faces.shape[0]
        return MeshData(
            vertices=torch.from_numpy(verts),
            faces=torch.from_numpy(faces),
            uv=torch.zeros((verts.shape[0], 2), dtype=torch.float32),
            face_uv=torch.from_numpy(faces.copy()),
            normals_per_face=torch.from_numpy(n_p_face),
            normals_per_vertex=torch.from_numpy(n_p_vert),
            chart_ids=torch.zeros(H, dtype=torch.long),
            source_path=str(path),
        )

    # First load raw mesh to compute scale factor
    import trimesh
    raw_tm = trimesh.load(str(mesh_path), force="mesh")
    raw_v = np.asarray(raw_tm.vertices, dtype=np.float64)
    mesh_center = raw_v.mean(axis=0)
    mesh_radius = float(np.linalg.norm(raw_v - mesh_center, axis=1).max())
    # Pick scale so camera distance after rescale is ~5 units (well inside
    # baker's [0.05, 20] perspective clip range) while mesh radius is ~0.3.
    # DiLiGenT cam distance is ~21x mesh radius. Target ~5 → scale = 5/cam_dist.
    target_cam_dist = 5.0
    estimated_cam_dist = 21.0 * mesh_radius  # rough ratio observed across DiLiGenT objects
    scene_scale = target_cam_dist / max(estimated_cam_dist, 1e-6)
    print(f"[DiLiGenT-MV] {object_name} center={mesh_center.tolist()} radius={mesh_radius:.2f} scale={scene_scale:.6f}")

    if decimate_faces:
        cache_dir = asset_root / "_cache_decimated"
        cache_dir.mkdir(exist_ok=True)
        cache_path = cache_dir / f"{mesh_path.stem}_dec{decimate_faces}.obj"
        if not cache_path.exists() or cache_path.stat().st_size > 30_000_000:
            import trimesh
            tm = trimesh.load(str(mesh_path), force="mesh")
            n_in = int(tm.faces.shape[0])
            if n_in > decimate_faces:
                ratio = max(0.001, min(0.99, 1.0 - decimate_faces / n_in))
                try:
                    import fast_simplification
                    v_out, f_out = fast_simplification.simplify(
                        np.asarray(tm.vertices, dtype=np.float32),
                        np.asarray(tm.faces, dtype=np.int32),
                        target_reduction=ratio,
                    )
                    tm = trimesh.Trimesh(vertices=v_out, faces=f_out, process=True)
                except Exception as exc:
                    raise RuntimeError(f"decimation via fast_simplification failed: {exc}")
            tm.export(cache_path)
        mesh = _load_mesh_no_normalize(cache_path)
    else:
        mesh = _load_mesh_no_normalize(mesh_path)

    # Apply uniform scale + center so mesh sits in unit-radius region.
    # Camera translations (Tc) are scaled by the same factor below.
    from dataclasses import replace as _replace
    centered_v = (mesh.vertices.cpu().numpy() - mesh_center.astype(np.float32)) * float(scene_scale)
    mesh = _replace(mesh, vertices=torch.from_numpy(centered_v.astype(np.float32)))

    calib_path: Optional[Path] = None
    for cand in [asset_root / "Calib_Results.mat", asset_root.parent / "Calib_Results.mat"]:
        if cand.exists():
            calib_path = cand
            break
    if calib_path is None:
        raise FileNotFoundError(f"Calib_Results.mat not found near {asset_root}")
    intrinsics, extrinsics = _read_calib_results(calib_path)

    # Scale extrinsics translation to match the rescaled mesh frame:
    # for original mesh point p, cam_p = R p + t. After mesh rescaling
    # p' = (p - center) * s, the same camera point should be reachable as
    # cam_p = R p' + t'   where t' = R*center + t, then scaled by s:
    # actually we want cam_p_scaled = (R p + t) * s = R (p*s) + t*s, so given
    # rescaled vertices p*s with mesh centered at origin, camera translation
    # becomes t' = (R*center + t) * s.
    rescaled_extrinsics: list[np.ndarray] = []
    for E in extrinsics:
        E_new = E.copy()
        R = E_new[:3, :3]
        t = E_new[:3, 3:4]
        t_new = (R @ mesh_center.reshape(3, 1) + t) * float(scene_scale)
        E_new[:3, 3:4] = t_new
        rescaled_extrinsics.append(E_new)
    extrinsics = rescaled_extrinsics

    view_dirs = _detect_view_dirs(asset_root)
    if not view_dirs:
        raise FileNotFoundError(f"No view sub-directories under {asset_root}")
    if max_views is not None:
        view_dirs = view_dirs[:max_views]
    if len(intrinsics) < len(view_dirs):
        raise ValueError(f"calib has {len(intrinsics)} views but found {len(view_dirs)} view dirs")

    views: list[DiLiGenTMVView] = []
    for view_i, vd in enumerate(view_dirs):
        light_dir_path = vd / "light_directions.txt"
        light_int_path = vd / "light_intensities.txt"
        mask_path = vd / "mask.png"
        if not light_dir_path.exists():
            light_dir_path = asset_root / "light_directions.txt"
        if not light_int_path.exists():
            light_int_path = asset_root / "light_intensities.txt"
        if not mask_path.exists():
            mp = list(vd.glob("mask*.png"))
            mask_path = mp[0] if mp else None
        if mask_path is None or not mask_path.exists():
            raise FileNotFoundError(f"mask.png missing for view {vd}")

        light_dirs_world = _read_text_matrix(light_dir_path)
        light_dirs_world = light_dirs_world / np.linalg.norm(light_dirs_world, axis=-1, keepdims=True).clip(1e-8)
        light_ints = _read_text_matrix(light_int_path)
        if light_ints.ndim == 1:
            light_ints = np.stack([light_ints, light_ints, light_ints], axis=-1)
        n_lights_total = light_dirs_world.shape[0]
        n_lights = n_lights_total if max_lights is None else min(max_lights, n_lights_total)

        mask = _load_image_linear(mask_path).mean(axis=-1) > 0.5
        mask = _erode_mask(mask, erode_mask_pixels)

        image_files = sorted(
            p for p in vd.iterdir()
            if p.suffix.lower() == ".png" and p.stem.isdigit()
        )
        if len(image_files) < n_lights:
            raise ValueError(f"view {vd} has {len(image_files)} numeric-named pngs but needs {n_lights}")
        image_files = image_files[:n_lights]

        imgs = []
        sat = np.zeros_like(mask, dtype=bool)
        for li, img_path in enumerate(image_files):
            img = _load_image_linear(img_path)
            if img.shape[:2] != mask.shape:
                raise ValueError(f"image {img_path} shape {img.shape} mismatches mask {mask.shape}")
            sat |= np.any(img >= saturation_threshold, axis=-1)
            inten = light_ints[li].astype(np.float32).reshape(1, 1, 3)
            normalized = img / np.maximum(inten, 1e-6)
            imgs.append(normalized)
        valid_mask = mask & ~sat
        H, W = mask.shape
        images = torch.from_numpy(np.stack(imgs, axis=0).astype(np.float32))
        view = DiLiGenTMVView(
            view_index=view_i,
            intrinsic=torch.from_numpy(intrinsics[view_i].astype(np.float32)),
            extrinsic=torch.from_numpy(extrinsics[view_i].astype(np.float32)),
            image_size=(H, W),
            images=images,
            mask=torch.from_numpy(valid_mask),
            light_directions_world=torch.from_numpy(light_dirs_world.astype(np.float32)),
            light_intensities=torch.from_numpy(light_ints.astype(np.float32)),
        )
        views.append(view)

    return DiLiGenTMVAsset(name=object_name, mesh=mesh.to(device), views=views)


def view_to_view_spec(view: DiLiGenTMVView, *, scene_target: Sequence[float] | torch.Tensor = (0.0, 0.0, 0.0)) -> ViewSpec:
    """Convert calibrated extrinsic to a ViewSpec (eye/target/up/fov_degrees).

    Camera convention: extrinsic = world->camera, OpenCV-style (x right, y down,
    z forward into scene). Eye in world is -R^T t.
    """
    K = view.intrinsic.detach().cpu().numpy().astype(np.float64)
    E = view.extrinsic.detach().cpu().numpy().astype(np.float64)
    R = E[:3, :3]
    t = E[:3, 3:4]
    eye = (-R.T @ t).reshape(3)
    look_world = R.T @ np.array([0.0, 0.0, 1.0])
    up_world = -(R.T @ np.array([0.0, 1.0, 0.0]))
    target = np.asarray(scene_target, dtype=np.float64)
    if not np.any(np.asarray(scene_target)):
        target = eye + look_world
    H, W = view.image_size
    fy = float(K[1, 1])
    fov_deg = math.degrees(2.0 * math.atan2(0.5 * H, fy))
    return ViewSpec(
        eye=torch.from_numpy(eye.astype(np.float32)),
        target=torch.from_numpy(target.astype(np.float32)),
        up=torch.from_numpy(up_world.astype(np.float32)),
        fov_degrees=fov_deg,
    )


def view_lights_to_specs(view: DiLiGenTMVView, light_indices: Sequence[int], *, unit_intensity: bool = True) -> list[LightSpec]:
    """Build LightSpec list. With unit_intensity=True, sets intensity=1.0 so the
    baker's predicted radiance lives in the same units as the light-intensity-
    normalized captured imagery (image / light_intensity)."""
    specs = []
    for li in light_indices:
        d_world = view.light_directions_world[li].detach().cpu()
        intensity = 1.0 if unit_intensity else float(view.light_intensities[li].mean().item())
        color = torch.tensor([1.0, 1.0, 1.0], dtype=torch.float32)
        specs.append(LightSpec(direction=d_world.float(), color=color, intensity=intensity))
    return specs


def captured_images_for(view: DiLiGenTMVView, light_indices: Sequence[int]) -> torch.Tensor:
    """Return tensor of captured target images at the requested light indices.

    Returned shape: ``[len(light_indices), H, W, 3]`` linear float32 in
    light-intensity-normalized space.
    """
    return view.images[list(light_indices)].clone()


def captured_mask_for(view: DiLiGenTMVView) -> torch.Tensor:
    return view.mask.clone()


__all__ = [
    "DILIGENT_MV_OBJECTS",
    "DiLiGenTMVAsset",
    "DiLiGenTMVView",
    "load_diligent_mv_asset",
    "view_to_view_spec",
    "view_lights_to_specs",
    "captured_images_for",
    "captured_mask_for",
]

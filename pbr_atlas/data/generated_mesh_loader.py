"""B7/PG generated/noisy mesh preparation helpers.

B7 prefers public generated/noisy assets when a manifest is provided, but the
default path is deterministic procedural noisy meshes. Those are real mesh
files on disk, not mocked metrics, and keep the transfer suite runnable when
network access or upstream sample URLs are unavailable.
"""

from __future__ import annotations

import json
import math
import os
import shutil
import tarfile
import urllib.request
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np

DEFAULT_B7_DATA_ROOT = Path(os.environ.get("PBR_ATLAS_B7_DATA_ROOT", "/data/dip_1_ws/datasets/B7_generated"))
DEFAULT_B7_ROBUSTNESS_ROOT = Path(
    os.environ.get("PBR_ATLAS_B7_ROBUSTNESS_ROOT", "/data/dip_1_ws/datasets/B7_robustness")
)
DEFAULT_PG_ENH1_DATA_ROOT = Path(
    os.environ.get("PBR_ATLAS_PG_ENH1_DATA_ROOT", "/data/dip_1_ws/datasets/PG_enh1_real_generated")
)

MESH_EXTS = (".obj", ".glb", ".gltf", ".ply", ".stl")
PG_ENH1_TARGET_FACE_RANGE = (3000, 30000)


@dataclass(frozen=True)
class GeneratedMeshRecord:
    asset_id: str
    mesh_path: str
    source: str
    category: str
    status: str
    seed: int
    failure_reason: str | None = None
    metadata: dict[str, object] | None = None

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["metadata"] = dict(self.metadata or {})
        return payload


@dataclass(frozen=True)
class ProceduralMeshSpec:
    asset_id: str
    primitive: str
    category: str
    seed: int
    noise_sigma: float
    wave_amplitude: float
    spike_fraction: float = 0.0
    twist: float = 0.0


DEFAULT_PROCEDURAL_SPECS: tuple[ProceduralMeshSpec, ...] = (
    ProceduralMeshSpec("proc_lumpy_ico", "icosphere", "trellis_like_lumpy", 7101, 0.045, 0.060, 0.035, 0.00),
    ProceduralMeshSpec("proc_dented_torus", "torus", "get3d_like_hollow", 7102, 0.035, 0.075, 0.000, 0.30),
    ProceduralMeshSpec("proc_crumpled_box", "box", "thingi_like_printable", 7103, 0.040, 0.045, 0.020, 0.18),
    ProceduralMeshSpec("proc_warped_cylinder", "cylinder", "sds_like_column", 7104, 0.030, 0.080, 0.010, 0.45),
    ProceduralMeshSpec("proc_twisted_cone", "cone", "sds_like_single_part", 7105, 0.030, 0.065, 0.020, 0.65),
    ProceduralMeshSpec("proc_noisy_capsule", "capsule", "generated_character_part", 7106, 0.035, 0.055, 0.015, 0.20),
    ProceduralMeshSpec("proc_ridged_sphere", "uv_sphere", "high_frequency_pbr_proxy", 7107, 0.025, 0.095, 0.000, 0.00),
    ProceduralMeshSpec("proc_pinched_ico", "icosphere", "fragmented_generated_proxy", 7108, 0.055, 0.050, 0.045, 0.35),
    ProceduralMeshSpec("proc_melty_star", "icosphere", "sds_like_melty_part", 7109, 0.065, 0.110, 0.070, 0.55),
    ProceduralMeshSpec("proc_folded_panel", "box", "generated_panel_artifact", 7110, 0.050, 0.085, 0.040, 0.35),
)


PG_PUBLIC_HF_SOURCE_SPECS: tuple[dict[str, Any], ...] = (
    {
        "source": "trellis_hf_model_repo",
        "hf_repo": "microsoft/TRELLIS-image-large",
        "hf_repo_type": "model",
        "path_keywords": ("example", "sample", "demo", "output", "glb", "mesh"),
        "category": "trellis_public_sample",
    },
    {
        "source": "trellis_hf_space",
        "hf_repo": "microsoft/TRELLIS",
        "hf_repo_type": "space",
        "path_keywords": ("example", "sample", "demo", "output", "glb", "mesh"),
        "category": "trellis_demo_output",
    },
    {
        "source": "trellis_community_hf_space",
        "hf_repo": "trellis-community/TRELLIS",
        "hf_repo_type": "space",
        "path_keywords": ("example", "sample", "demo", "output", "glb", "mesh"),
        "category": "trellis_demo_output",
    },
)

PG_PUBLIC_GITHUB_SOURCE_SPECS: tuple[dict[str, Any], ...] = (
    {
        "source": "get3d_github_demo",
        "repo": "nv-tlabs/GET3D",
        "path_keywords": ("demo", "sample", "output", "mesh", "generated"),
        "category": "get3d_public_sample",
    },
    {
        "source": "trellis_github_demo",
        "repo": "microsoft/TRELLIS",
        "path_keywords": ("demo", "sample", "output", "mesh", "generated"),
        "category": "trellis_public_sample",
    },
    {
        "source": "fantasia3d_github_demo",
        "repo": "Fantasia3D/Fantasia3D",
        "path_keywords": ("demo", "sample", "output", "mesh", "generated"),
        "category": "sds_public_output",
    },
)


@dataclass
class _ArrayMesh:
    vertices: np.ndarray
    faces: np.ndarray

    def export(self, path: str | Path) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        lines: list[str] = []
        for vertex in self.vertices:
            lines.append(f"v {vertex[0]:.8f} {vertex[1]:.8f} {vertex[2]:.8f}\n")
        for face in self.faces:
            lines.append(f"f {int(face[0]) + 1} {int(face[1]) + 1} {int(face[2]) + 1}\n")
        target.write_text("".join(lines), encoding="utf-8")

    def remove_unreferenced_vertices(self) -> None:
        used = np.unique(self.faces.reshape(-1))
        remap = np.full(int(self.vertices.shape[0]), -1, dtype=np.int64)
        remap[used] = np.arange(used.shape[0], dtype=np.int64)
        self.vertices = self.vertices[used]
        self.faces = remap[self.faces]


def default_asset_ids() -> list[str]:
    return [spec.asset_id for spec in DEFAULT_PROCEDURAL_SPECS]


def prepare_generated_mesh_set(
    data_root: str | Path = DEFAULT_B7_DATA_ROOT,
    *,
    asset_ids: Iterable[str] | None = None,
    count: int | None = None,
    manifest: str | Path | None = None,
    offline_ok: bool = True,
    force: bool = False,
) -> list[GeneratedMeshRecord]:
    """Prepare a B7 transfer set and return manifest records."""

    root = Path(data_root)
    root.mkdir(parents=True, exist_ok=True)

    requested = list(asset_ids) if asset_ids is not None else default_asset_ids()
    if count is not None:
        requested = requested[: int(count)]

    records: list[GeneratedMeshRecord] = []
    manifest_specs = _load_source_manifest(manifest or root / "B7_REMOTE_SOURCES.json")
    for asset_id in requested:
        if asset_id in manifest_specs:
            records.append(
                _prepare_manifest_asset(asset_id, manifest_specs[asset_id], root, offline_ok=offline_ok, force=force)
            )
        else:
            records.append(prepare_generated_mesh(asset_id, root, force=force))
    _write_manifest(root / "B7_GENERATED_MANIFEST.json", records)
    return records


def prepare_real_generated_mesh_set(
    data_root: str | Path = DEFAULT_PG_ENH1_DATA_ROOT,
    *,
    target_count: int = 10,
    manifest: str | Path | None = None,
    include_public_sources: bool = True,
    offline_ok: bool = True,
    force: bool = False,
) -> list[GeneratedMeshRecord]:
    """Prepare the PG-enh1 real/generated set with explicit source audit.

    The function is intentionally conservative: public-source download failures
    are materialized as failure records, and fallback meshes are marked as
    fallback rather than real generated outputs.
    """

    root = Path(data_root)
    root.mkdir(parents=True, exist_ok=True)
    failures: list[GeneratedMeshRecord] = []
    records: list[GeneratedMeshRecord] = []

    explicit_manifest = manifest or root / "PG_REAL_SOURCES.json"
    manifest_specs = _load_source_manifest(explicit_manifest)
    if manifest_specs:
        for asset_id, spec in manifest_specs.items():
            record = _prepare_manifest_asset(asset_id, spec, root, offline_ok=offline_ok, force=force)
            if record.status == "ok" and _face_count_in_range(record.mesh_path):
                records.append(record)
            else:
                failures.append(
                    _failure_record(
                        asset_id,
                        str(spec.get("source", "manifest_source")),
                        str(spec.get("category", "public_generated")),
                        record.failure_reason or _face_count_failure_reason(record.mesh_path),
                        metadata={"requested_source": dict(spec), "prepared_record": record.to_dict()},
                    )
                )
            if len(records) >= target_count:
                break

    if include_public_sources and len(records) < target_count:
        records.extend(
            _try_huggingface_public_meshes(
                root,
                needed=target_count - len(records),
                failures=failures,
                force=force,
            )
        )

    if include_public_sources and len(records) < target_count:
        records.extend(
            _try_github_public_meshes(
                root,
                needed=target_count - len(records),
                failures=failures,
                force=force,
            )
        )

    if include_public_sources and len(records) < target_count:
        records.extend(
            _try_objaverse_generated_meshes(
                root,
                needed=target_count - len(records),
                failures=failures,
                force=force,
            )
        )

    if len(records) < target_count:
        records.extend(
            _prepare_noisy_fallback_records(
                root,
                needed=target_count - len(records),
                failures=failures,
                force=force,
            )
        )

    records = records[:target_count]
    _write_manifest(root / "PG_ENH1_REAL_GENERATED_MANIFEST.json", records)
    _write_manifest(root / "PG_ENH1_SOURCE_FAILURES.json", failures)
    _write_pg_source_tables(root, records, failures)
    return records


def write_local_source_manifest(path: str | Path, records: Iterable[GeneratedMeshRecord]) -> Path:
    """Write a manifest consumable by prepare_generated_mesh_set/run_B7_transfer."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    assets: list[dict[str, Any]] = []
    for record in records:
        assets.append(
            {
                "asset_id": record.asset_id,
                "local_path": record.mesh_path,
                "source": record.source,
                "category": record.category,
                "seed": record.seed,
                "metadata": record.metadata or {},
                "prepared_status": record.status,
                "failure_reason": record.failure_reason,
            }
        )
    payload = {"version": 1, "description": "Local prepared source manifest", "assets": assets}
    tmp = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(tmp, path)
    return path


def prepare_generated_mesh(
    asset_id: str,
    data_root: str | Path = DEFAULT_B7_DATA_ROOT,
    *,
    force: bool = False,
) -> GeneratedMeshRecord:
    """Prepare one deterministic procedural B7 mesh."""

    specs = {spec.asset_id: spec for spec in DEFAULT_PROCEDURAL_SPECS}
    if asset_id not in specs:
        available = ", ".join(default_asset_ids())
        raise ValueError(f"Unknown B7 generated asset {asset_id!r}; available: {available}")
    spec = specs[asset_id]
    root = Path(data_root)
    out_dir = root / asset_id
    out_dir.mkdir(parents=True, exist_ok=True)
    mesh_path = out_dir / f"{asset_id}.obj"
    if force or not mesh_path.exists() or mesh_path.stat().st_size == 0:
        mesh = _make_procedural_mesh(spec)
        mesh.export(mesh_path)
    return GeneratedMeshRecord(
        asset_id=asset_id,
        mesh_path=str(mesh_path),
        source="procedural_noisy_fallback",
        category=spec.category,
        status="ok",
        seed=spec.seed,
        metadata={
            "primitive": spec.primitive,
            "noise_sigma": spec.noise_sigma,
            "wave_amplitude": spec.wave_amplitude,
            "spike_fraction": spec.spike_fraction,
            "twist": spec.twist,
        },
    )


def resolve_generated_mesh(asset_id: str, data_root: str | Path = DEFAULT_B7_DATA_ROOT) -> Path:
    root = Path(data_root)
    manifest_path = root / "B7_GENERATED_MANIFEST.json"
    if manifest_path.exists():
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        for item in payload.get("assets", []):
            if item.get("asset_id") == asset_id:
                path = Path(str(item["mesh_path"]))
                if path.exists():
                    return path
    path = root / asset_id / f"{asset_id}.obj"
    if path.exists():
        return path
    raise FileNotFoundError(f"B7 generated asset {asset_id!r} is not prepared under {root}")


def iter_prepared_generated_meshes(data_root: str | Path = DEFAULT_B7_DATA_ROOT) -> Iterable[Path]:
    root = Path(data_root)
    for asset_id in default_asset_ids():
        try:
            yield resolve_generated_mesh(asset_id, root)
        except FileNotFoundError:
            continue


def prepare_robustness_mesh(
    *,
    base_asset: str,
    source_mesh: str | Path,
    sigma: float,
    data_root: str | Path = DEFAULT_B7_ROBUSTNESS_ROOT,
    seed: int = 42,
    force: bool = False,
) -> GeneratedMeshRecord:
    """Cache a vertex-noise perturbation for B7 robustness sweeps."""

    import trimesh

    sigma = float(sigma)
    root = Path(data_root)
    asset_id = f"{base_asset}_noise_sigma{_level_token(sigma)}"
    out_dir = root / asset_id
    out_dir.mkdir(parents=True, exist_ok=True)
    mesh_path = out_dir / f"{asset_id}.obj"
    if force or not mesh_path.exists() or mesh_path.stat().st_size == 0:
        mesh_obj = trimesh.load(str(source_mesh), force="mesh", process=True)
        if isinstance(mesh_obj, trimesh.Scene):
            mesh_obj = trimesh.util.concatenate(tuple(mesh_obj.geometry.values()))
        vertices = _normalize_vertices(np.asarray(mesh_obj.vertices, dtype=np.float32))
        faces = np.asarray(mesh_obj.faces, dtype=np.int64)
        rng = np.random.default_rng(seed + int(round(sigma * 10000.0)))
        if sigma > 0.0:
            normals = _safe_vertex_normals(vertices, faces)
            radial = rng.normal(0.0, sigma, size=(vertices.shape[0], 1)).astype(np.float32)
            tangent = rng.normal(0.0, sigma * 0.35, size=vertices.shape).astype(np.float32)
            vertices = vertices + normals * radial + tangent
        noisy = trimesh.Trimesh(vertices=vertices, faces=faces, process=True)
        noisy.remove_unreferenced_vertices()
        noisy.export(mesh_path)
    return GeneratedMeshRecord(
        asset_id=asset_id,
        mesh_path=str(mesh_path),
        source="vertex_gaussian_robustness",
        category="spot_partuv_noise_sweep",
        status="ok",
        seed=seed,
        metadata={"base_asset": base_asset, "sigma": sigma, "source_mesh": str(source_mesh)},
    )


def _make_procedural_mesh(spec: ProceduralMeshSpec):
    rng = np.random.default_rng(spec.seed)
    mesh = _base_mesh(spec.primitive)
    vertices = _normalize_vertices(np.asarray(mesh.vertices, dtype=np.float32))
    faces = np.asarray(mesh.faces, dtype=np.int64)
    normals = _safe_vertex_normals(vertices, faces)
    phase = rng.uniform(-math.pi, math.pi, size=(3,))
    radius = np.linalg.norm(vertices, axis=1, keepdims=True)
    wave = (
        np.sin(7.0 * vertices[:, 0:1] + phase[0])
        + np.sin(11.0 * vertices[:, 1:2] + phase[1])
        + np.sin(13.0 * vertices[:, 2:3] + phase[2])
    ) / 3.0
    radial = spec.wave_amplitude * wave + rng.normal(0.0, spec.noise_sigma, size=(vertices.shape[0], 1))
    jitter = rng.normal(0.0, spec.noise_sigma * 0.25, size=vertices.shape)
    vertices = vertices + normals * radial.astype(np.float32) + jitter.astype(np.float32)
    if spec.spike_fraction > 0.0:
        count = max(1, int(round(vertices.shape[0] * spec.spike_fraction)))
        spike_idx = rng.choice(vertices.shape[0], size=count, replace=False)
        spike_scale = rng.uniform(0.10, 0.24, size=(count, 1)).astype(np.float32)
        vertices[spike_idx] += normals[spike_idx] * spike_scale
    if abs(spec.twist) > 1.0e-8:
        vertices = _twist_vertices(vertices, amount=spec.twist)
    if spec.asset_id == "proc_pinched_ico":
        vertices = _pinch(vertices, axis=1, strength=0.35)
    if spec.asset_id == "proc_ridged_sphere":
        vertices = vertices + normals * (0.045 * np.sign(np.sin(24.0 * radius))).astype(np.float32)
    out = _ArrayMesh(vertices=vertices.astype(np.float32), faces=faces.astype(np.int64))
    out.remove_unreferenced_vertices()
    return out


def _base_mesh(primitive: str):
    if primitive == "icosphere":
        return _sphere_mesh(n_lon=64, n_lat=32, radius=1.0)
    if primitive == "uv_sphere":
        return _sphere_mesh(n_lon=72, n_lat=36, radius=1.0)
    if primitive == "box":
        return _box_mesh(steps=24, extents=(1.45, 1.05, 0.95))
    if primitive == "cylinder":
        return _cylinder_mesh(radius=0.65, height=1.55, sections=96, stacks=16)
    if primitive == "cone":
        return _cone_mesh(radius=0.78, height=1.65, sections=96, stacks=16)
    if primitive == "capsule":
        mesh = _sphere_mesh(n_lon=64, n_lat=32, radius=1.0)
        mesh.vertices[:, 0] *= 0.55
        mesh.vertices[:, 2] *= 0.55
        mesh.vertices[:, 1] *= 1.25
        return mesh
    if primitive == "torus":
        return _parametric_torus()
    return _sphere_mesh(n_lon=36, n_lat=18, radius=1.0)


def _parametric_torus(major: float = 0.68, minor: float = 0.24, n_major: int = 80, n_minor: int = 24):
    vertices = []
    faces = []
    for i in range(n_major):
        u = 2.0 * math.pi * i / n_major
        for j in range(n_minor):
            v = 2.0 * math.pi * j / n_minor
            vertices.append(
                [
                    (major + minor * math.cos(v)) * math.cos(u),
                    minor * math.sin(v),
                    (major + minor * math.cos(v)) * math.sin(u),
                ]
            )
    for i in range(n_major):
        for j in range(n_minor):
            a = i * n_minor + j
            b = ((i + 1) % n_major) * n_minor + j
            c = ((i + 1) % n_major) * n_minor + (j + 1) % n_minor
            d = i * n_minor + (j + 1) % n_minor
            faces.append([a, b, d])
            faces.append([b, c, d])
    return _ArrayMesh(vertices=np.asarray(vertices, dtype=np.float32), faces=np.asarray(faces, dtype=np.int64))


def _sphere_mesh(*, n_lon: int, n_lat: int, radius: float) -> _ArrayMesh:
    vertices = []
    for lat in range(n_lat + 1):
        phi = math.pi * lat / n_lat
        y = radius * math.cos(phi)
        ring = radius * math.sin(phi)
        for lon in range(n_lon):
            theta = 2.0 * math.pi * lon / n_lon
            vertices.append([ring * math.cos(theta), y, ring * math.sin(theta)])
    faces = []
    for lat in range(n_lat):
        for lon in range(n_lon):
            a = lat * n_lon + lon
            b = lat * n_lon + (lon + 1) % n_lon
            c = (lat + 1) * n_lon + lon
            d = (lat + 1) * n_lon + (lon + 1) % n_lon
            if lat > 0:
                faces.append([a, c, b])
            if lat < n_lat - 1:
                faces.append([b, c, d])
    return _ArrayMesh(vertices=np.asarray(vertices, dtype=np.float32), faces=np.asarray(faces, dtype=np.int64))


def _box_mesh(*, steps: int, extents: tuple[float, float, float]) -> _ArrayMesh:
    ex, ey, ez = (value * 0.5 for value in extents)
    vertices: list[list[float]] = []
    faces: list[list[int]] = []

    def add_face(axis: int, sign: float) -> None:
        start = len(vertices)
        axes = [0, 1, 2]
        axes.remove(axis)
        half = [ex, ey, ez]
        for iy in range(steps + 1):
            for ix in range(steps + 1):
                coord = [0.0, 0.0, 0.0]
                coord[axis] = sign * half[axis]
                coord[axes[0]] = -half[axes[0]] + 2.0 * half[axes[0]] * ix / steps
                coord[axes[1]] = -half[axes[1]] + 2.0 * half[axes[1]] * iy / steps
                vertices.append(coord)
        for iy in range(steps):
            for ix in range(steps):
                a = start + iy * (steps + 1) + ix
                b = a + 1
                c = a + (steps + 1)
                d = c + 1
                if sign > 0:
                    faces.extend([[a, b, c], [b, d, c]])
                else:
                    faces.extend([[a, c, b], [b, c, d]])

    for axis in range(3):
        add_face(axis, 1.0)
        add_face(axis, -1.0)
    return _ArrayMesh(vertices=np.asarray(vertices, dtype=np.float32), faces=np.asarray(faces, dtype=np.int64))


def _cylinder_mesh(*, radius: float, height: float, sections: int, stacks: int) -> _ArrayMesh:
    vertices: list[list[float]] = []
    faces: list[list[int]] = []
    for stack in range(stacks + 1):
        y = -0.5 * height + height * stack / stacks
        for section in range(sections):
            theta = 2.0 * math.pi * section / sections
            vertices.append([radius * math.cos(theta), y, radius * math.sin(theta)])
    for stack in range(stacks):
        for section in range(sections):
            a = stack * sections + section
            b = stack * sections + (section + 1) % sections
            c = (stack + 1) * sections + section
            d = (stack + 1) * sections + (section + 1) % sections
            faces.extend([[a, c, b], [b, c, d]])
    bottom_center = len(vertices)
    vertices.append([0.0, -0.5 * height, 0.0])
    top_center = len(vertices)
    vertices.append([0.0, 0.5 * height, 0.0])
    top_offset = stacks * sections
    for section in range(sections):
        nxt = (section + 1) % sections
        faces.append([bottom_center, nxt, section])
        faces.append([top_center, top_offset + section, top_offset + nxt])
    return _ArrayMesh(vertices=np.asarray(vertices, dtype=np.float32), faces=np.asarray(faces, dtype=np.int64))


def _cone_mesh(*, radius: float, height: float, sections: int, stacks: int) -> _ArrayMesh:
    vertices: list[list[float]] = []
    faces: list[list[int]] = []
    for stack in range(stacks + 1):
        y = -0.5 * height + height * stack / stacks
        r = radius * (1.0 - stack / stacks)
        for section in range(sections):
            theta = 2.0 * math.pi * section / sections
            vertices.append([r * math.cos(theta), y, r * math.sin(theta)])
    for stack in range(stacks):
        for section in range(sections):
            a = stack * sections + section
            b = stack * sections + (section + 1) % sections
            c = (stack + 1) * sections + section
            d = (stack + 1) * sections + (section + 1) % sections
            if stack == stacks - 1:
                faces.append([a, c, b])
            else:
                faces.extend([[a, c, b], [b, c, d]])
    bottom_center = len(vertices)
    vertices.append([0.0, -0.5 * height, 0.0])
    for section in range(sections):
        faces.append([bottom_center, (section + 1) % sections, section])
    return _ArrayMesh(vertices=np.asarray(vertices, dtype=np.float32), faces=np.asarray(faces, dtype=np.int64))


def _normalize_vertices(vertices: np.ndarray) -> np.ndarray:
    centered = vertices - vertices.mean(axis=0, keepdims=True)
    scale = np.linalg.norm(centered, axis=1).max()
    if scale < 1.0e-8:
        scale = 1.0
    return (centered / scale).astype(np.float32)


def _safe_vertex_normals(vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
    normal = np.zeros_like(vertices, dtype=np.float32)
    tri = vertices[faces]
    face_normals = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    denom = np.linalg.norm(face_normals, axis=1, keepdims=True)
    face_normals = face_normals / np.maximum(denom, 1.0e-8)
    for face, fn in zip(faces, face_normals):
        normal[face] += fn
    norm = np.linalg.norm(normal, axis=1, keepdims=True)
    fallback = vertices / np.maximum(np.linalg.norm(vertices, axis=1, keepdims=True), 1.0e-8)
    return np.where(norm > 1.0e-8, normal / np.maximum(norm, 1.0e-8), fallback).astype(np.float32)


def _twist_vertices(vertices: np.ndarray, *, amount: float) -> np.ndarray:
    out = vertices.copy()
    y = out[:, 1]
    angle = amount * y
    cos_a = np.cos(angle)
    sin_a = np.sin(angle)
    x = out[:, 0].copy()
    z = out[:, 2].copy()
    out[:, 0] = cos_a * x - sin_a * z
    out[:, 2] = sin_a * x + cos_a * z
    return out.astype(np.float32)


def _pinch(vertices: np.ndarray, *, axis: int, strength: float) -> np.ndarray:
    out = vertices.copy()
    coord = np.abs(out[:, axis : axis + 1])
    scale = 1.0 - strength * np.exp(-coord * 8.0)
    other_axes = [idx for idx in range(3) if idx != axis]
    out[:, other_axes] *= scale
    return out.astype(np.float32)


def _level_token(value: float) -> str:
    return f"{float(value):.4f}".rstrip("0").rstrip(".").replace(".", "p") or "0"


def _load_source_manifest(path: str | Path) -> dict[str, Mapping[str, object]]:
    manifest_path = Path(path)
    if not manifest_path.exists():
        return {}
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        items = payload.get("assets", [])
    else:
        items = payload
    out: dict[str, Mapping[str, object]] = {}
    for item in items:
        if isinstance(item, Mapping) and item.get("asset_id"):
            out[str(item["asset_id"])] = item
    return out


def _prepare_manifest_asset(
    asset_id: str,
    spec: Mapping[str, object],
    data_root: Path,
    *,
    offline_ok: bool,
    force: bool,
) -> GeneratedMeshRecord:
    out_dir = data_root / asset_id
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        mesh_path = _download_or_copy_manifest_mesh(asset_id, spec, out_dir, force=force)
        return GeneratedMeshRecord(
            asset_id=asset_id,
            mesh_path=str(mesh_path),
            source=str(spec.get("source", "manifest_download")),
            category=str(spec.get("category", "public_generated")),
            status=str(spec.get("prepared_status") or spec.get("status") or "ok"),
            seed=int(spec.get("seed", 0) or 0),
            failure_reason=str(spec.get("failure_reason")) if spec.get("failure_reason") else None,
            metadata={key: value for key, value in spec.items() if key != "asset_id"},
        )
    except Exception as exc:
        if not offline_ok:
            raise
        fallback_id = str(spec.get("fallback_asset_id") or default_asset_ids()[0])
        record = prepare_generated_mesh(fallback_id, data_root, force=force)
        return GeneratedMeshRecord(
            asset_id=asset_id,
            mesh_path=record.mesh_path,
            source="procedural_noisy_fallback",
            category=str(spec.get("category", "public_generated_fallback")),
            status="partial",
            seed=record.seed,
            failure_reason=f"manifest download failed: {exc}",
            metadata={"requested_source": dict(spec), "fallback_asset_id": fallback_id},
        )


def _download_or_copy_manifest_mesh(asset_id: str, spec: Mapping[str, object], out_dir: Path, *, force: bool) -> Path:
    local_path = spec.get("local_path")
    if local_path:
        source = Path(str(local_path)).expanduser()
        if not source.exists():
            raise FileNotFoundError(source)
        target = out_dir / source.name
        if force or not target.exists():
            shutil.copy2(source, target)
        found = _find_mesh(out_dir)
        if found:
            return found
        raise FileNotFoundError(f"No mesh file found after copying {source}")

    hf_repo = spec.get("hf_repo")
    hf_filename = spec.get("hf_filename")
    if hf_repo and hf_filename:
        from huggingface_hub import hf_hub_download  # type: ignore

        path = hf_hub_download(
            repo_id=str(hf_repo),
            filename=str(hf_filename),
            repo_type=str(spec.get("hf_repo_type", "dataset")),
            local_dir=str(out_dir),
        )
        found = _find_mesh(Path(path).parent)
        if found:
            return found
        if Path(path).suffix.lower() in MESH_EXTS:
            return Path(path)
        raise FileNotFoundError(f"HuggingFace file is not a mesh: {path}")

    url = spec.get("url")
    if not url:
        raise ValueError(f"Manifest asset {asset_id} has no local_path, hf_repo/hf_filename, or url")
    filename = str(spec.get("filename") or Path(str(url)).name or f"{asset_id}.mesh")
    download_path = out_dir / filename
    if force or not download_path.exists() or download_path.stat().st_size == 0:
        request = urllib.request.Request(str(url), headers={"User-Agent": "pbr-atlas-b7/0.1"})
        with urllib.request.urlopen(request, timeout=45) as response:
            download_path.write_bytes(response.read())
    if download_path.suffix.lower() in MESH_EXTS:
        return download_path
    _extract_archive(download_path, out_dir)
    found = _find_mesh(out_dir)
    if found:
        return found
    raise FileNotFoundError(f"No mesh file found in downloaded asset {download_path}")


def _extract_archive(path: Path, out_dir: Path) -> None:
    suffixes = "".join(path.suffixes).lower()
    if suffixes.endswith(".tar.gz") or suffixes.endswith(".tgz"):
        with tarfile.open(path, "r:gz") as tf:
            _safe_extract_tar(tf, out_dir)
    elif suffixes.endswith(".zip"):
        with zipfile.ZipFile(path) as zf:
            _safe_extract_zip(zf, out_dir)
    else:
        raise ValueError(f"Unsupported archive format: {path}")


def _safe_extract_tar(tf: tarfile.TarFile, target_dir: Path) -> None:
    target_root = target_dir.resolve()
    for member in tf.getmembers():
        member_path = (target_dir / member.name).resolve()
        if not str(member_path).startswith(str(target_root)):
            raise RuntimeError(f"Unsafe tar member path: {member.name}")
    tf.extractall(target_dir)


def _safe_extract_zip(zf: zipfile.ZipFile, target_dir: Path) -> None:
    target_root = target_dir.resolve()
    for member in zf.infolist():
        member_path = (target_dir / member.filename).resolve()
        if not str(member_path).startswith(str(target_root)):
            raise RuntimeError(f"Unsafe zip member path: {member.filename}")
    zf.extractall(target_dir)


def _find_mesh(root: Path) -> Path | None:
    if not root.exists():
        return None
    for ext in MESH_EXTS:
        matches = sorted(root.rglob(f"*{ext}"))
        if matches:
            return matches[0]
    return None


def _try_huggingface_public_meshes(
    data_root: Path,
    *,
    needed: int,
    failures: list[GeneratedMeshRecord],
    force: bool,
) -> list[GeneratedMeshRecord]:
    if needed <= 0:
        return []
    try:
        from huggingface_hub import hf_hub_download, list_repo_files  # type: ignore
    except Exception as exc:
        failures.append(_failure_record("huggingface_public_sources", "huggingface_hub", "public_generated", str(exc)))
        return []

    records: list[GeneratedMeshRecord] = []
    for spec in PG_PUBLIC_HF_SOURCE_SPECS:
        if len(records) >= needed:
            break
        repo = str(spec["hf_repo"])
        repo_type = str(spec.get("hf_repo_type", "model"))
        source = str(spec["source"])
        category = str(spec.get("category", "public_generated"))
        try:
            files = list_repo_files(repo_id=repo, repo_type=repo_type)
        except Exception as exc:
            failures.append(_failure_record(repo.replace("/", "_"), source, category, f"repo listing failed: {exc}"))
            continue
        candidates = [
            filename
            for filename in files
            if Path(filename).suffix.lower() in MESH_EXTS
            and _path_has_keywords(filename, spec.get("path_keywords", ()))
        ]
        if not candidates:
            failures.append(_failure_record(repo.replace("/", "_"), source, category, "no mesh files matched public-sample filters"))
            continue
        for filename in candidates:
            if len(records) >= needed:
                break
            asset_id = _asset_id_from_source(source, filename, len(records))
            out_dir = data_root / asset_id
            out_dir.mkdir(parents=True, exist_ok=True)
            try:
                local = hf_hub_download(
                    repo_id=repo,
                    filename=filename,
                    repo_type=repo_type,
                    local_dir=str(out_dir),
                )
                mesh_path = _find_mesh(Path(local).parent) or Path(local)
                if not _face_count_in_range(mesh_path):
                    failures.append(
                        _failure_record(
                            asset_id,
                            source,
                            category,
                            _face_count_failure_reason(mesh_path),
                            metadata={"hf_repo": repo, "hf_repo_type": repo_type, "hf_filename": filename},
                        )
                    )
                    continue
                records.append(
                    GeneratedMeshRecord(
                        asset_id=asset_id,
                        mesh_path=str(mesh_path),
                        source=source,
                        category=category,
                        status="ok",
                        seed=0,
                        metadata={"hf_repo": repo, "hf_repo_type": repo_type, "hf_filename": filename},
                    )
                )
            except Exception as exc:
                failures.append(
                    _failure_record(
                        asset_id,
                        source,
                        category,
                        f"download failed: {exc}",
                        metadata={"hf_repo": repo, "hf_repo_type": repo_type, "hf_filename": filename},
                    )
                )
    return records


def _try_github_public_meshes(
    data_root: Path,
    *,
    needed: int,
    failures: list[GeneratedMeshRecord],
    force: bool,
) -> list[GeneratedMeshRecord]:
    del force
    if needed <= 0:
        return []
    records: list[GeneratedMeshRecord] = []
    for spec in PG_PUBLIC_GITHUB_SOURCE_SPECS:
        if len(records) >= needed:
            break
        repo = str(spec["repo"])
        source = str(spec["source"])
        category = str(spec.get("category", "public_generated"))
        try:
            tree = _github_repo_tree(repo)
        except Exception as exc:
            failures.append(_failure_record(repo.replace("/", "_"), source, category, f"repo tree failed: {exc}"))
            continue
        candidates = [
            item
            for item in tree
            if Path(str(item.get("path", ""))).suffix.lower() in MESH_EXTS
            and _path_has_keywords(str(item.get("path", "")), spec.get("path_keywords", ()))
        ]
        if not candidates:
            failures.append(_failure_record(repo.replace("/", "_"), source, category, "no mesh files matched public-sample filters"))
            continue
        for item in candidates:
            if len(records) >= needed:
                break
            rel_path = str(item["path"])
            asset_id = _asset_id_from_source(source, rel_path, len(records))
            out_dir = data_root / asset_id
            out_dir.mkdir(parents=True, exist_ok=True)
            mesh_path = out_dir / Path(rel_path).name
            raw_url = f"https://raw.githubusercontent.com/{repo}/HEAD/{rel_path}"
            try:
                if not mesh_path.exists() or mesh_path.stat().st_size == 0:
                    request = urllib.request.Request(raw_url, headers={"User-Agent": "pbr-atlas-pg-enh1/0.1"})
                    with urllib.request.urlopen(request, timeout=45) as response:
                        mesh_path.write_bytes(response.read())
                if not _face_count_in_range(mesh_path):
                    failures.append(
                        _failure_record(
                            asset_id,
                            source,
                            category,
                            _face_count_failure_reason(mesh_path),
                            metadata={"github_repo": repo, "path": rel_path, "url": raw_url},
                        )
                    )
                    continue
                records.append(
                    GeneratedMeshRecord(
                        asset_id=asset_id,
                        mesh_path=str(mesh_path),
                        source=source,
                        category=category,
                        status="ok",
                        seed=0,
                        metadata={"github_repo": repo, "path": rel_path, "url": raw_url},
                    )
                )
            except Exception as exc:
                failures.append(
                    _failure_record(
                        asset_id,
                        source,
                        category,
                        f"download failed: {exc}",
                        metadata={"github_repo": repo, "path": rel_path, "url": raw_url},
                    )
                )
    return records


def _try_objaverse_generated_meshes(
    data_root: Path,
    *,
    needed: int,
    failures: list[GeneratedMeshRecord],
    force: bool,
) -> list[GeneratedMeshRecord]:
    del force
    if needed <= 0:
        return []
    try:
        import objaverse  # type: ignore
    except Exception as exc:
        failures.append(_failure_record("objaverse_generated_subset", "objaverse_api", "objaverse_generated", str(exc)))
        return []

    try:
        annotations = objaverse.load_annotations()
    except Exception as exc:
        failures.append(_failure_record("objaverse_generated_subset", "objaverse_api", "objaverse_generated", f"annotation load failed: {exc}"))
        return []

    keywords = ("generated", "ai generated", "text-to-3d", "dreamfusion", "magic3d", "get3d", "trellis", "sds")
    selected: list[str] = []
    for uid, meta in list(annotations.items()):
        text = json.dumps(meta, sort_keys=True, default=str).lower()
        if any(keyword in text for keyword in keywords):
            selected.append(str(uid))
        if len(selected) >= needed * 4:
            break
    if not selected:
        failures.append(_failure_record("objaverse_generated_subset", "objaverse_api", "objaverse_generated", "no metadata matched generated/AI keywords"))
        return []

    records: list[GeneratedMeshRecord] = []
    try:
        paths = objaverse.load_objects(uids=selected, download_processes=4)
    except Exception as exc:
        failures.append(_failure_record("objaverse_generated_subset", "objaverse_api", "objaverse_generated", f"object download failed: {exc}"))
        return []

    for uid in selected:
        if len(records) >= needed:
            break
        source_path = paths.get(uid)
        if not source_path:
            continue
        asset_id = f"objaverse_ai_{uid[:10]}"
        out_dir = data_root / asset_id
        out_dir.mkdir(parents=True, exist_ok=True)
        target = out_dir / Path(str(source_path)).name
        try:
            if not target.exists() or target.stat().st_size == 0:
                shutil.copy2(source_path, target)
            if not _face_count_in_range(target):
                failures.append(
                    _failure_record(
                        asset_id,
                        "objaverse_api",
                        "objaverse_generated",
                        _face_count_failure_reason(target),
                        metadata={"uid": uid, "annotation": annotations.get(uid)},
                    )
                )
                continue
            records.append(
                GeneratedMeshRecord(
                    asset_id=asset_id,
                    mesh_path=str(target),
                    source="objaverse_api",
                    category="objaverse_generated",
                    status="ok",
                    seed=0,
                    metadata={"uid": uid, "annotation": annotations.get(uid)},
                )
            )
        except Exception as exc:
            failures.append(_failure_record(asset_id, "objaverse_api", "objaverse_generated", str(exc), metadata={"uid": uid}))
    return records


def _prepare_noisy_fallback_records(
    data_root: Path,
    *,
    needed: int,
    failures: list[GeneratedMeshRecord],
    force: bool,
) -> list[GeneratedMeshRecord]:
    if needed <= 0:
        return []
    records = _prepare_shapenet_noisy_records(data_root, needed=needed, failures=failures, force=force)
    if len(records) >= needed:
        return records[:needed]
    fallback_ids = default_asset_ids()
    for asset_id in fallback_ids:
        if len(records) >= needed:
            break
        record = prepare_generated_mesh(asset_id, data_root, force=force)
        records.append(
            GeneratedMeshRecord(
                asset_id=record.asset_id,
                mesh_path=record.mesh_path,
                source="procedural_noisy_fallback",
                category=record.category,
                status="partial",
                seed=record.seed,
                failure_reason="public generated/Objaverse downloads unavailable; using procedural noisy fallback",
                metadata=record.metadata,
            )
        )
    return records[:needed]


def _prepare_shapenet_noisy_records(
    data_root: Path,
    *,
    needed: int,
    failures: list[GeneratedMeshRecord],
    force: bool,
) -> list[GeneratedMeshRecord]:
    candidates: list[Path] = []
    search_roots = []
    env_root = os.environ.get("PBR_ATLAS_SHAPENET_ROOT")
    if env_root:
        search_roots.append(Path(env_root))
    search_roots.extend([data_root.parent / "shapenet_oracle_300", data_root.parent / "ShapeNet", data_root.parent / "shapenet"])
    for root in search_roots:
        if not str(root) or not root.exists():
            continue
        for ext in MESH_EXTS:
            candidates.extend(sorted(root.rglob(f"*{ext}")))
        if candidates:
            break
    if not candidates:
        failures.append(_failure_record("shapenet_noisy_fallback", "local_shapenet", "fallback_noisy", "no local ShapeNet mesh root found"))
        return []

    records: list[GeneratedMeshRecord] = []
    for idx, source_mesh in enumerate(candidates[: needed * 3]):
        if len(records) >= needed:
            break
        asset_id = f"shapenet_noisy_{idx:02d}"
        out_dir = data_root / asset_id
        out_dir.mkdir(parents=True, exist_ok=True)
        target = out_dir / f"{asset_id}.obj"
        try:
            if force or not target.exists() or target.stat().st_size == 0:
                _export_noisy_copy(source_mesh, target, seed=8200 + idx)
            if not _face_count_in_range(target):
                failures.append(
                    _failure_record(
                        asset_id,
                        "local_shapenet",
                        "fallback_noisy",
                        _face_count_failure_reason(target),
                        metadata={"source_mesh": str(source_mesh)},
                    )
                )
                continue
            records.append(
                GeneratedMeshRecord(
                    asset_id=asset_id,
                    mesh_path=str(target),
                    source="local_shapenet_noisy_fallback",
                    category="fallback_noisy",
                    status="partial",
                    seed=8200 + idx,
                    failure_reason="public generated downloads unavailable; using noisy local ShapeNet fallback",
                    metadata={"source_mesh": str(source_mesh), "noise_sigma": 0.015},
                )
            )
        except Exception as exc:
            failures.append(_failure_record(asset_id, "local_shapenet", "fallback_noisy", str(exc), metadata={"source_mesh": str(source_mesh)}))
    return records


def _export_noisy_copy(source_mesh: Path, target: Path, *, seed: int) -> None:
    import trimesh

    mesh_obj = trimesh.load(str(source_mesh), force="mesh", process=True)
    if isinstance(mesh_obj, trimesh.Scene):
        mesh_obj = trimesh.util.concatenate(tuple(mesh_obj.geometry.values()))
    vertices = _normalize_vertices(np.asarray(mesh_obj.vertices, dtype=np.float32))
    faces = np.asarray(mesh_obj.faces, dtype=np.int64)
    rng = np.random.default_rng(seed)
    normals = _safe_vertex_normals(vertices, faces)
    vertices = vertices + normals * rng.normal(0.0, 0.015, size=(vertices.shape[0], 1)).astype(np.float32)
    noisy = trimesh.Trimesh(vertices=vertices, faces=faces, process=True)
    noisy.remove_unreferenced_vertices()
    target.parent.mkdir(parents=True, exist_ok=True)
    noisy.export(target)


def _github_repo_tree(repo: str) -> list[dict[str, Any]]:
    api_url = f"https://api.github.com/repos/{repo}/git/trees/HEAD?recursive=1"
    request = urllib.request.Request(api_url, headers={"User-Agent": "pbr-atlas-pg-enh1/0.1"})
    with urllib.request.urlopen(request, timeout=45) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return [item for item in payload.get("tree", []) if item.get("type") == "blob"]


def _path_has_keywords(path: str, keywords: Iterable[str]) -> bool:
    lowered = path.lower()
    return any(str(keyword).lower() in lowered for keyword in keywords)


def _asset_id_from_source(source: str, path: str, index: int) -> str:
    stem = Path(path).stem.lower()
    clean = "".join(ch if ch.isalnum() else "_" for ch in f"{source}_{stem}")[:48].strip("_")
    return f"{clean}_{index:02d}" if clean else f"{source}_{index:02d}"


def _mesh_face_count(path: str | Path) -> int | None:
    path = Path(path)
    if path.suffix.lower() == ".obj":
        try:
            count = 0
            with path.open("r", encoding="utf-8", errors="ignore") as handle:
                for raw in handle:
                    if raw.startswith("f "):
                        count += 1
            if count > 0:
                return count
        except Exception:
            pass
    try:
        import trimesh

        mesh_obj = trimesh.load(str(path), force="mesh", process=False)
        if isinstance(mesh_obj, trimesh.Scene):
            mesh_obj = trimesh.util.concatenate(tuple(mesh_obj.geometry.values()))
        return int(np.asarray(mesh_obj.faces).shape[0])
    except Exception:
        return None


def _face_count_in_range(path: str | Path) -> bool:
    face_count = _mesh_face_count(path)
    if face_count is None:
        return False
    lo, hi = PG_ENH1_TARGET_FACE_RANGE
    return lo <= face_count <= hi


def _face_count_failure_reason(path: str | Path) -> str:
    face_count = _mesh_face_count(path)
    lo, hi = PG_ENH1_TARGET_FACE_RANGE
    if face_count is None:
        return "mesh could not be loaded for face-count validation"
    return f"face_count={face_count} outside requested range [{lo}, {hi}]"


def _failure_record(
    asset_id: str,
    source: str,
    category: str,
    reason: str,
    *,
    metadata: Mapping[str, Any] | None = None,
) -> GeneratedMeshRecord:
    return GeneratedMeshRecord(
        asset_id=asset_id,
        mesh_path="",
        source=source,
        category=category,
        status="failed",
        seed=0,
        failure_reason=reason,
        metadata=dict(metadata or {}),
    )


def _write_pg_source_tables(
    root: Path,
    records: list[GeneratedMeshRecord],
    failures: list[GeneratedMeshRecord],
) -> None:
    lines = [
        "# PG-enh1 Generated Source Table",
        "",
        "| Asset | Source | Category | Status | Faces | Mesh | Note |",
        "|---|---|---|---|---:|---|---|",
    ]
    for record in records:
        lines.append(
            "| {asset} | {source} | {category} | {status} | {faces} | {mesh} | {note} |".format(
                asset=record.asset_id,
                source=record.source,
                category=record.category,
                status=record.status,
                faces=_mesh_face_count(record.mesh_path) or "-",
                mesh=record.mesh_path,
                note=record.failure_reason or "-",
            )
        )
    if not records:
        lines.append("| - | - | - | - | - | - | no prepared assets |")
    (root / "PG_ENH1_SOURCE_TABLE.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    failure_lines = [
        "# PG-enh1 Source Failure Table",
        "",
        "| Asset / Probe | Source | Category | Failure Reason |",
        "|---|---|---|---|",
    ]
    for record in failures:
        failure_lines.append(
            f"| {record.asset_id} | {record.source} | {record.category} | {record.failure_reason or '-'} |"
        )
    if not failures:
        failure_lines.append("| - | - | - | no source failures recorded |")
    (root / "PG_ENH1_SOURCE_FAILURE_TABLE.md").write_text("\n".join(failure_lines) + "\n", encoding="utf-8")


def _write_manifest(path: Path, records: list[GeneratedMeshRecord]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "description": "B7 generated/noisy mesh cache manifest",
        "assets": [record.to_dict() for record in records],
    }
    tmp = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(tmp, path)

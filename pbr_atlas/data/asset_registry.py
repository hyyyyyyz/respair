"""Small B1 sample asset registry with offline-friendly fallbacks."""

from __future__ import annotations

import os
import tarfile
import urllib.request
import zipfile
from pathlib import Path
from typing import Iterable

DEFAULT_DATA_ROOT = Path(os.environ.get("PBR_ATLAS_DATA_ROOT", "/data/dip_1_ws/datasets/sample"))

BUNNY_URL = "http://graphics.stanford.edu/data/3Dscanrep/bunnyrep/bunny_reduced.tar.gz"
SPOT_URL = "https://www.cs.cmu.edu/~kmcrane/Projects/ModelRepository/spot.zip"


def resolve_asset(asset: str, data_root: str | Path = DEFAULT_DATA_ROOT) -> Path:
    """Return the expected local mesh path for a B1 asset."""

    root = Path(data_root)
    aliases = {"objaverse_sample": "objaverse", "objaverse1": "objaverse"}
    asset = aliases.get(asset, asset)
    candidates = {
        "bunny": _find_mesh(root / "bunny"),
        "spot": _find_mesh(root / "spot"),
        "objaverse": _find_mesh(root / "objaverse"),
    }
    if asset not in candidates:
        raise ValueError(f"Unknown B1 asset {asset!r}; expected bunny, spot, or objaverse")
    path = candidates[asset]
    if path is None:
        raise FileNotFoundError(f"Asset {asset!r} is not prepared under {root}")
    return path


def prepare_asset(asset: str, data_root: str | Path = DEFAULT_DATA_ROOT, offline_ok: bool = True) -> Path:
    """Prepare a single B1 sample asset.

    B1 registry comment:
        The sample set is intentionally tiny: Stanford bunny, Spot cow, and one
        optional Objaverse GLB. Failed downloads fall back to generated
        trimesh primitives with xatlas/cylindrical UVs added by mesh_loader.
    """

    aliases = {"objaverse_sample": "objaverse", "objaverse1": "objaverse"}
    asset = aliases.get(asset, asset)
    root = Path(data_root)
    root.mkdir(parents=True, exist_ok=True)
    if asset == "bunny":
        return _prepare_download_or_fallback("bunny", root / "bunny", BUNNY_URL, "bunny_reduced.tar.gz", "icosphere", offline_ok)
    if asset == "spot":
        return _prepare_download_or_fallback("spot", root / "spot", SPOT_URL, "spot.zip", "box", offline_ok)
    if asset == "objaverse":
        return _prepare_objaverse(root / "objaverse", offline_ok)
    raise ValueError(f"Unknown B1 asset {asset!r}")


def prepare_all(data_root: str | Path = DEFAULT_DATA_ROOT, offline_ok: bool = True) -> list[Path]:
    return [prepare_asset(asset, data_root, offline_ok=offline_ok) for asset in ("bunny", "spot", "objaverse")]


def _prepare_download_or_fallback(
    name: str,
    target_dir: Path,
    url: str,
    archive_name: str,
    primitive: str,
    offline_ok: bool,
) -> Path:
    target_dir.mkdir(parents=True, exist_ok=True)
    existing = _find_mesh(target_dir)
    if existing is not None:
        return existing
    archive = target_dir / archive_name
    try:
        _download(url, archive)
        _extract_archive(archive, target_dir)
        found = _find_mesh(target_dir)
        if found is not None:
            return found
    except Exception:
        if not offline_ok:
            raise
    return _write_primitive(target_dir / f"{name}_fallback.obj", primitive)


def _prepare_objaverse(target_dir: Path, offline_ok: bool) -> Path:
    target_dir.mkdir(parents=True, exist_ok=True)
    existing = _find_mesh(target_dir)
    if existing is not None:
        return existing
    try:
        from huggingface_hub import hf_hub_download  # type: ignore

        # A tiny public GLB-like sample path cannot be guaranteed stable across
        # Objaverse mirrors, so this is intentionally best-effort. The fallback
        # keeps B1 deterministic when the network or token is unavailable.
        path = hf_hub_download(
            repo_id="allenai/objaverse",
            filename="glbs/000-000/000a52e0c1614bd68a234d3f1fbfca55.glb",
            repo_type="dataset",
            local_dir=str(target_dir),
        )
        return Path(path)
    except Exception:
        if not offline_ok:
            raise
    return _write_primitive(target_dir / "objaverse_fallback.obj", "cylinder")


def _download(url: str, path: Path) -> None:
    if path.exists() and path.stat().st_size > 0:
        return
    request = urllib.request.Request(url, headers={"User-Agent": "pbr-atlas-b1/0.1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        path.write_bytes(response.read())


def _extract_archive(archive: Path, target_dir: Path) -> None:
    suffixes = "".join(archive.suffixes)
    if suffixes.endswith(".tar.gz") or suffixes.endswith(".tgz"):
        with tarfile.open(archive, "r:gz") as tf:
            _safe_extract_tar(tf, target_dir)
    elif suffixes.endswith(".zip"):
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(target_dir)
    else:
        raise ValueError(f"Unsupported archive: {archive}")


def _safe_extract_tar(tf: tarfile.TarFile, target_dir: Path) -> None:
    target_root = target_dir.resolve()
    for member in tf.getmembers():
        member_path = (target_dir / member.name).resolve()
        if not str(member_path).startswith(str(target_root)):
            raise RuntimeError(f"Unsafe tar member path: {member.name}")
    tf.extractall(target_dir)


def _find_mesh(root: Path) -> Path | None:
    if not root.exists():
        return None
    for ext in ("*.obj", "*.glb", "*.ply", "*.stl"):
        matches = sorted(root.rglob(ext))
        if matches:
            return matches[0]
    return None


def _write_primitive(path: Path, primitive: str) -> Path:
    import trimesh

    path.parent.mkdir(parents=True, exist_ok=True)
    if primitive == "icosphere":
        mesh = trimesh.creation.icosphere(subdivisions=3, radius=1.0)
    elif primitive == "cylinder":
        mesh = trimesh.creation.cylinder(radius=0.65, height=1.5, sections=48)
    else:
        mesh = trimesh.creation.box(extents=(1.4, 0.9, 1.1))
    mesh.export(path)
    return path


def iter_prepared_assets(data_root: str | Path = DEFAULT_DATA_ROOT) -> Iterable[Path]:
    for asset in ("bunny", "spot", "objaverse"):
        try:
            yield resolve_asset(asset, data_root)
        except FileNotFoundError:
            continue


"""Storage-safe JSON / NPZ / PNG / text helpers for B1 outputs."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import numpy as np
import torch


def ensure_dir(path: str | Path) -> Path:
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _json_default(value: Any):
    if isinstance(value, torch.Tensor):
        value = value.detach().cpu()
        if value.ndim == 0:
            return value.item()
        return value.tolist()
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def atomic_write_json(path: str | Path, payload: dict[str, Any], indent: int = 2) -> Path:
    path = Path(path)
    ensure_dir(path.parent)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=indent, sort_keys=True, default=_json_default), encoding="utf-8")
    os.replace(tmp, path)
    return path


def save_npz(path: str | Path, **arrays: Any) -> Path:
    path = Path(path)
    ensure_dir(path.parent)
    np_arrays = {}
    for key, value in arrays.items():
        if isinstance(value, torch.Tensor):
            value = value.detach().cpu().numpy()
        np_arrays[key] = np.asarray(value)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "wb") as handle:
        np.savez_compressed(handle, **np_arrays)
    os.replace(tmp, path)
    return path


def write_text(path: str | Path, text: str) -> Path:
    path = Path(path)
    ensure_dir(path.parent)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)
    return path


def save_png(path: str | Path, image: np.ndarray) -> Path:
    import imageio.v3 as iio

    path = Path(path)
    ensure_dir(path.parent)
    image_u8 = np.clip(image * 255.0, 0.0, 255.0).astype(np.uint8)
    iio.imwrite(path, image_u8)
    return path


def directory_size_mb(path: str | Path) -> float:
    path = Path(path)
    total = 0
    if not path.exists():
        return 0.0
    for file in path.rglob("*"):
        if file.is_file():
            total += file.stat().st_size
    return total / (1024.0 * 1024.0)


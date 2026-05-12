"""Chart/part semantic-preservation metrics for PG-enh2."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np


def chart_part_purity(chart_ids, part_ids) -> tuple[float, list[float]]:
    """Per-chart majority-part fraction, averaged over charts."""

    chart = _as_int_array(chart_ids)
    part = _as_int_array(part_ids)
    _check_same_faces(chart, part)
    purities: list[float] = []
    for chart_id in np.unique(chart):
        mask = chart == chart_id
        values = part[mask]
        if values.size == 0:
            continue
        _, counts = np.unique(values, return_counts=True)
        purities.append(float(counts.max() / values.size))
    return (float(np.mean(purities)) if purities else 0.0), purities


def weighted_chart_part_purity(chart_ids, part_ids) -> float:
    """Face-weighted majority-part fraction over all charts."""

    chart = _as_int_array(chart_ids)
    part = _as_int_array(part_ids)
    _check_same_faces(chart, part)
    numerator = 0
    for chart_id in np.unique(chart):
        values = part[chart == chart_id]
        if values.size == 0:
            continue
        _, counts = np.unique(values, return_counts=True)
        numerator += int(counts.max())
    return float(numerator / max(int(chart.size), 1))


def chart_part_entropy(chart_ids, part_ids) -> tuple[float, list[float]]:
    """Mean normalized part entropy inside each chart; lower is cleaner."""

    chart = _as_int_array(chart_ids)
    part = _as_int_array(part_ids)
    _check_same_faces(chart, part)
    n_parts = max(int(np.unique(part).size), 1)
    denom = math.log(max(n_parts, 2))
    entropies: list[float] = []
    for chart_id in np.unique(chart):
        values = part[chart == chart_id]
        if values.size == 0:
            continue
        _, counts = np.unique(values, return_counts=True)
        probs = counts.astype(np.float64) / float(counts.sum())
        entropy = -float(np.sum(probs * np.log(np.maximum(probs, 1.0e-12)))) / denom
        entropies.append(entropy)
    return (float(np.mean(entropies)) if entropies else 0.0), entropies


def normalized_mutual_information(chart_ids, part_ids) -> float:
    """Symmetric NMI between chart ids and reference part ids."""

    chart = _as_int_array(chart_ids)
    part = _as_int_array(part_ids)
    _check_same_faces(chart, part)
    if chart.size == 0:
        return 0.0
    _, chart_inv = np.unique(chart, return_inverse=True)
    _, part_inv = np.unique(part, return_inverse=True)
    n_chart = int(chart_inv.max()) + 1
    n_part = int(part_inv.max()) + 1
    joint = np.zeros((n_chart, n_part), dtype=np.float64)
    np.add.at(joint, (chart_inv, part_inv), 1.0)
    joint /= float(chart.size)
    chart_prob = joint.sum(axis=1)
    part_prob = joint.sum(axis=0)
    nz = joint > 0.0
    mi = float(np.sum(joint[nz] * np.log(joint[nz] / (chart_prob[:, None] * part_prob[None, :])[nz])))
    h_chart = _entropy(chart_prob)
    h_part = _entropy(part_prob)
    denom = math.sqrt(max(h_chart * h_part, 1.0e-12))
    return float(mi / denom)


def load_chart_ids(path: str | Path) -> np.ndarray:
    payload = np.load(path, allow_pickle=True)
    if "chart_ids" not in payload.files:
        raise KeyError(f"{path} does not contain chart_ids")
    return _as_int_array(payload["chart_ids"])


def part_ids_from_hierarchy(path: str | Path, face_count: int) -> np.ndarray:
    """Load flexible PartUV-style hierarchy JSON leaf faces as per-face ids."""

    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    leaves = _hierarchy_leaves(payload)
    part_ids = np.full(face_count, -1, dtype=np.int64)
    for part_idx, leaf in enumerate(leaves):
        faces = leaf.get("faces") or leaf.get("face_indices") or leaf.get("face_ids") or []
        for face_idx in faces:
            idx = int(face_idx)
            if 0 <= idx < face_count:
                part_ids[idx] = part_idx
    if np.any(part_ids < 0):
        missing = np.flatnonzero(part_ids < 0)
        part_ids[missing] = np.arange(missing.size, dtype=np.int64) + len(leaves)
    return part_ids


def summarize_chart_part_overlap(chart_ids, part_ids) -> dict[str, Any]:
    mean_purity, purities = chart_part_purity(chart_ids, part_ids)
    mean_entropy, entropies = chart_part_entropy(chart_ids, part_ids)
    return {
        "chart_count": int(np.unique(_as_int_array(chart_ids)).size),
        "part_count": int(np.unique(_as_int_array(part_ids)).size),
        "face_count": int(_as_int_array(chart_ids).size),
        "purity_mean": mean_purity,
        "purity_weighted": weighted_chart_part_purity(chart_ids, part_ids),
        "purity_min": float(min(purities)) if purities else 0.0,
        "purity_per_chart": purities,
        "entropy_mean": mean_entropy,
        "entropy_max": float(max(entropies)) if entropies else 0.0,
        "nmi": normalized_mutual_information(chart_ids, part_ids),
    }


def _hierarchy_leaves(node: Any) -> list[dict[str, Any]]:
    if isinstance(node, list):
        leaves: list[dict[str, Any]] = []
        for item in node:
            leaves.extend(_hierarchy_leaves(item))
        return leaves
    if not isinstance(node, dict):
        return []
    children = node.get("children") or node.get("parts") or []
    if children:
        return _hierarchy_leaves(children)
    if any(key in node for key in ("faces", "face_indices", "face_ids")):
        return [node]
    return []


def _as_int_array(values) -> np.ndarray:
    return np.asarray(values, dtype=np.int64).reshape(-1)


def _check_same_faces(chart: np.ndarray, part: np.ndarray) -> None:
    if chart.shape[0] != part.shape[0]:
        raise ValueError(f"chart_ids face count {chart.shape[0]} != part_ids face count {part.shape[0]}")


def _entropy(prob: np.ndarray) -> float:
    prob = prob[prob > 0.0]
    return -float(np.sum(prob * np.log(prob)))

"""Matplotlib helpers for B6 qualitative figures."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, Mapping, Sequence

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.patches import Rectangle


def as_numpy(value) -> np.ndarray:
    """Convert tensors/lists/arrays to a CPU numpy array."""

    if value is None:
        return np.asarray([])
    if hasattr(value, "detach"):
        value = value.detach().cpu().numpy()
    return np.asarray(value)


def load_atlas_npz(path: str | Path) -> dict[str, np.ndarray]:
    arrays = np.load(path, allow_pickle=True)
    return {key: arrays[key] for key in arrays.files}


def load_residual_npz(path: str | Path) -> dict[str, np.ndarray]:
    arrays = np.load(path, allow_pickle=True)
    return {key: arrays[key] for key in arrays.files}


def setup_atlas_axis(ax, title: str | None = None) -> None:
    ax.set_aspect("equal")
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.set_xticks([])
    ax.set_yticks([])
    if title:
        ax.set_title(title, fontsize=10, pad=6)
    for spine in ax.spines.values():
        spine.set_linewidth(0.6)
        spine.set_color("#404040")


def draw_empty_panel(ax, title: str, message: str) -> None:
    setup_atlas_axis(ax, title)
    ax.text(0.5, 0.5, message, ha="center", va="center", fontsize=9, color="#555555", wrap=True)


def face_polygons(uv: np.ndarray, face_uv: np.ndarray) -> list[np.ndarray]:
    uv = as_numpy(uv).astype(np.float32, copy=False)
    face_uv = as_numpy(face_uv).astype(np.int64, copy=False)
    if uv.size == 0 or face_uv.size == 0:
        return []
    valid = np.all((face_uv >= 0) & (face_uv < len(uv)), axis=1)
    return [uv[tri] for tri in face_uv[valid]]


def _face_values(values: Sequence[float] | np.ndarray | None, face_count: int) -> np.ndarray:
    if values is None:
        return np.zeros(face_count, dtype=np.float32)
    out = as_numpy(values).astype(np.float32, copy=False).reshape(-1)
    if out.size < face_count:
        padded = np.zeros(face_count, dtype=np.float32)
        padded[: out.size] = out
        return padded
    return out[:face_count]


def draw_uv_heatmap(
    ax,
    uv: np.ndarray,
    face_uv: np.ndarray,
    values: Sequence[float] | np.ndarray | None = None,
    *,
    chart_ids: Sequence[int] | np.ndarray | None = None,
    title: str | None = None,
    cmap: str = "inferno",
    edge_alpha: float = 0.18,
) -> None:
    """Draw a UV atlas as per-face colored triangles."""

    polygons = face_polygons(uv, face_uv)
    setup_atlas_axis(ax, title)
    if not polygons:
        ax.text(0.5, 0.5, "missing atlas", ha="center", va="center", fontsize=9, color="#555555")
        return

    values_arr = _face_values(values, len(polygons))
    vmax = float(np.quantile(values_arr, 0.98)) if np.any(values_arr > 0) else 1.0
    vmax = max(vmax, 1.0e-8)
    norm = matplotlib.colors.Normalize(vmin=0.0, vmax=vmax)
    collection = PolyCollection(
        polygons,
        array=values_arr,
        cmap=cmap,
        norm=norm,
        edgecolors=(0.08, 0.08, 0.08, edge_alpha),
        linewidths=0.12,
    )
    ax.add_collection(collection)
    if chart_ids is not None:
        draw_chart_bound_boxes(ax, uv, face_uv, chart_ids, color="#202020", linewidth=0.35, alpha=0.35)


def chart_bounds(uv: np.ndarray, face_uv: np.ndarray, chart_ids: Sequence[int] | np.ndarray) -> dict[int, tuple[float, float, float, float]]:
    uv = as_numpy(uv).astype(np.float32, copy=False)
    face_uv = as_numpy(face_uv).astype(np.int64, copy=False)
    chart_ids = as_numpy(chart_ids).astype(np.int64, copy=False).reshape(-1)
    out: dict[int, tuple[float, float, float, float]] = {}
    if uv.size == 0 or face_uv.size == 0 or chart_ids.size == 0:
        return out
    for chart in sorted(np.unique(chart_ids).tolist()):
        mask = chart_ids == int(chart)
        if not np.any(mask):
            continue
        ids = np.unique(face_uv[mask].reshape(-1))
        ids = ids[(ids >= 0) & (ids < len(uv))]
        if ids.size == 0:
            continue
        pts = uv[ids]
        lo = pts.min(axis=0)
        hi = pts.max(axis=0)
        out[int(chart)] = (float(lo[0]), float(lo[1]), float(hi[0]), float(hi[1]))
    return out


def draw_chart_bound_boxes(
    ax,
    uv: np.ndarray,
    face_uv: np.ndarray,
    chart_ids: Sequence[int] | np.ndarray,
    *,
    color: str = "#1f2937",
    linewidth: float = 0.8,
    alpha: float = 0.8,
) -> None:
    for x0, y0, x1, y1 in chart_bounds(uv, face_uv, chart_ids).values():
        ax.add_patch(
            Rectangle(
                (x0, y0),
                max(x1 - x0, 1.0e-5),
                max(y1 - y0, 1.0e-5),
                fill=False,
                edgecolor=color,
                linewidth=linewidth,
                alpha=alpha,
            )
        )


def draw_chart_overlay(
    ax,
    uv: np.ndarray,
    face_uv: np.ndarray,
    chart_ids: Sequence[int] | np.ndarray,
    highlight_charts: Iterable[int],
    *,
    color: str = "#d62728",
    linewidth: float = 1.8,
    label_charts: bool = False,
) -> None:
    highlights = {int(chart) for chart in highlight_charts}
    bounds = chart_bounds(uv, face_uv, chart_ids)
    for chart in sorted(highlights):
        if chart not in bounds:
            continue
        x0, y0, x1, y1 = bounds[chart]
        ax.add_patch(
            Rectangle(
                (x0, y0),
                max(x1 - x0, 1.0e-5),
                max(y1 - y0, 1.0e-5),
                fill=False,
                edgecolor=color,
                linewidth=linewidth,
            )
        )
        if label_charts:
            ax.text(x0, y1, str(chart), fontsize=6, color=color, va="bottom", ha="left")


def draw_allocation_bars(
    ax,
    allocations: Sequence[float] | np.ndarray | Mapping[str, float] | None,
    *,
    chart_scales: Mapping[str, float] | Mapping[int, float] | None = None,
    edited_charts: Iterable[int] = (),
    title: str | None = None,
    max_bars: int = 24,
) -> None:
    """Draw C3 texel budget bars, highlighting edited charts."""

    ax.clear()
    if title:
        ax.set_title(title, fontsize=10, pad=6)
    edited = {int(chart) for chart in edited_charts}
    if allocations is None:
        ax.text(0.5, 0.5, "missing allocation", ha="center", va="center", fontsize=9, color="#555555")
        ax.set_axis_off()
        return
    if isinstance(allocations, Mapping):
        pairs = [(int(k), float(v)) for k, v in allocations.items()]
    else:
        arr = as_numpy(allocations).reshape(-1)
        pairs = [(idx, float(value)) for idx, value in enumerate(arr.tolist())]
    if not pairs:
        ax.text(0.5, 0.5, "missing allocation", ha="center", va="center", fontsize=9, color="#555555")
        ax.set_axis_off()
        return
    pairs = sorted(pairs, key=lambda item: item[1], reverse=True)[:max_bars]
    labels = [str(chart) for chart, _ in pairs]
    values = np.asarray([value for _, value in pairs], dtype=np.float32)
    colors = ["#d62728" if chart in edited else "#4c78a8" for chart, _ in pairs]
    y = np.arange(len(pairs))
    ax.barh(y, values / max(float(values.max()), 1.0e-8), color=colors, height=0.72)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=6)
    ax.invert_yaxis()
    ax.set_xlim(0.0, 1.05)
    ax.set_xlabel("relative texels", fontsize=8)
    ax.tick_params(axis="x", labelsize=7)
    ax.grid(axis="x", color="#dddddd", linewidth=0.4)
    if chart_scales:
        scale_map = {int(k): float(v) for k, v in chart_scales.items()}
        for yi, (chart, _) in enumerate(pairs):
            if chart in scale_map:
                ax.text(1.02, yi, f"{scale_map[chart]:.2f}x", va="center", fontsize=6, color="#555555")


def draw_seam_map(
    ax,
    uv: np.ndarray,
    face_uv: np.ndarray,
    chart_ids: Sequence[int] | np.ndarray,
    seam_edges: Sequence[Sequence[int]] | np.ndarray | None = None,
    seam_values: Sequence[float] | np.ndarray | None = None,
    *,
    title: str | None = None,
) -> None:
    """Draw seam links in UV space using face-centroid connections."""

    draw_uv_heatmap(ax, uv, face_uv, None, chart_ids=chart_ids, title=title, cmap="Greys", edge_alpha=0.08)
    face_uv = as_numpy(face_uv).astype(np.int64, copy=False)
    uv = as_numpy(uv).astype(np.float32, copy=False)
    seams = as_numpy(seam_edges).astype(np.int64, copy=False) if seam_edges is not None else np.empty((0, 2), dtype=np.int64)
    if seams.ndim != 2 or seams.shape[1] != 2 or face_uv.size == 0 or uv.size == 0:
        return
    centroids = uv[face_uv.clip(0, max(len(uv) - 1, 0))].mean(axis=1)
    valid = np.all((seams >= 0) & (seams < len(centroids)), axis=1)
    seams = seams[valid]
    if seams.size == 0:
        return
    segments = np.stack([centroids[seams[:, 0]], centroids[seams[:, 1]]], axis=1)
    values = _face_values(seam_values, len(segments))
    vmax = float(np.quantile(values, 0.98)) if np.any(values > 0) else 1.0
    collection = LineCollection(
        segments,
        array=values,
        cmap="magma",
        norm=matplotlib.colors.Normalize(vmin=0.0, vmax=max(vmax, 1.0e-8)),
        linewidths=0.55,
        alpha=0.95,
    )
    ax.add_collection(collection)


def metric_text(metrics: Mapping[str, object] | None, *, prefix: str = "") -> str:
    if not metrics:
        return f"{prefix}PSNR -\nSSIM -"
    psnr = _safe_metric(metrics, "psnr")
    ssim = _safe_metric(metrics, "ssim")
    return f"{prefix}PSNR {psnr}\nSSIM {ssim}"


def draw_metric_box(ax, text: str, *, loc: tuple[float, float] = (0.03, 0.97)) -> None:
    ax.text(
        loc[0],
        loc[1],
        text,
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=7,
        color="#111111",
        bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "edgecolor": "#cccccc", "alpha": 0.88},
    )


def save_figure_pair(fig, output_stem: str | Path, *, dpi: int = 220) -> tuple[Path, Path]:
    stem = Path(output_stem)
    stem.parent.mkdir(parents=True, exist_ok=True)
    png = stem.with_suffix(".png")
    pdf = stem.with_suffix(".pdf")
    fig.savefig(png, dpi=dpi, bbox_inches="tight")
    fig.savefig(pdf, bbox_inches="tight")
    return png, pdf


def _safe_metric(metrics: Mapping[str, object], key: str) -> str:
    value = metrics.get(key)
    if value is None:
        return "-"
    if value == "inf":
        return "inf"
    try:
        return f"{float(value):.3f}"
    except Exception:
        return str(value)


__all__ = [
    "as_numpy",
    "chart_bounds",
    "draw_allocation_bars",
    "draw_chart_bound_boxes",
    "draw_chart_overlay",
    "draw_empty_panel",
    "draw_metric_box",
    "draw_seam_map",
    "draw_uv_heatmap",
    "face_polygons",
    "load_atlas_npz",
    "load_residual_npz",
    "metric_text",
    "save_figure_pair",
    "setup_atlas_axis",
]

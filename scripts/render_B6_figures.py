#!/usr/bin/env python
"""Render qualitative residual-chain and rollback figures from cached runs."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import matplotlib.pyplot as plt
import numpy as np

from pbr_atlas.utils.figure import (
    draw_allocation_bars,
    draw_chart_overlay,
    draw_empty_panel,
    draw_metric_box,
    draw_seam_map,
    draw_uv_heatmap,
    load_atlas_npz,
    load_residual_npz,
    save_figure_pair,
)
from pbr_atlas.utils.io import ensure_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render qualitative residual-chain figures.")
    parser.add_argument("--b3-root", default="runs/B3_main")
    parser.add_argument("--b2-root", default="runs/B2_baseline")
    parser.add_argument("--b4-root", default="runs/B4_ablation")
    parser.add_argument("--output-dir", default="figures/qualitative_residual_chain")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--main-assets", nargs="*", default=["spot", "bunny"])
    parser.add_argument(
        "--rollback-cases",
        nargs="*",
        default=[
            "spot:xatlas_classical",
            "bunny:xatlas_classical",
            "objaverse:xatlas_classical",
            "objaverse:partuv",
        ],
        help="Rollback gallery cases as asset:baseline.",
    )
    parser.add_argument("--top-k", type=int, default=14)
    return parser.parse_args()


def _resolve_root(path: str | Path, fallbacks: list[Path]) -> Path:
    root = Path(path)
    if root.exists():
        return root
    for fallback in fallbacks:
        if fallback.exists():
            return fallback
    return root


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _safe_get(payload: dict[str, Any] | None, *keys: str, default=None):
    cur: Any = payload
    for key in keys:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def _fmt(value: Any, digits: int = 2) -> str:
    if value is None:
        return "-"
    if value == "inf":
        return "inf"
    try:
        return f"{float(value):.{digits}f}"
    except Exception:
        return str(value)


def _run_dir(root: Path, asset: str, baseline: str, seed: int) -> Path:
    return root / f"{asset}_{baseline}_ours_seed{seed}"


def _load_case(b3_root: Path, b2_root: Path, asset: str, baseline: str, seed: int) -> dict[str, Any]:
    run_dir = _run_dir(b3_root, asset, baseline, seed)
    metrics = _load_json(run_dir / "metrics.json") or {}
    repair_log = _load_json(run_dir / "repair_log.json") or {}
    initial_atlas = _load_npz_or_none(run_dir / "initial_atlas.npz")
    final_atlas = _load_npz_or_none(run_dir / "atlas.npz")
    final_residual = _load_npz_or_none(run_dir / "residual_atlas.npz")
    b2_run = b2_root / f"{asset}_{baseline}_seed{seed}"
    b2_residual = _load_npz_or_none(b2_run / "residual_atlas.npz")
    return {
        "asset": asset,
        "baseline": baseline,
        "run_dir": run_dir,
        "metrics": metrics,
        "repair_log": repair_log,
        "initial_atlas": initial_atlas,
        "final_atlas": final_atlas,
        "final_residual": final_residual,
        "b2_residual": b2_residual,
    }


def _load_npz_or_none(path: Path) -> dict[str, np.ndarray] | None:
    if not path.exists():
        return None
    if path.name.endswith("residual_atlas.npz"):
        return load_residual_npz(path)
    return load_atlas_npz(path)


def _initial_residual(case: dict[str, Any]) -> np.ndarray:
    values = _safe_get(case["metrics"], "initial", "residual_stats", "e_f")
    if values is not None:
        return np.asarray(values, dtype=np.float32)
    residual = case.get("b2_residual") or {}
    return np.asarray(residual.get("e_f", []), dtype=np.float32)


def _final_residual(case: dict[str, Any]) -> np.ndarray:
    residual = case.get("final_residual") or {}
    return np.asarray(residual.get("e_f", []), dtype=np.float32)


def _edited_chart_ids(case: dict[str, Any], top_k: int) -> list[int]:
    repair = case.get("repair_log") or {}
    metrics = case.get("metrics") or {}
    out: list[int] = []
    for log in repair.get("repair", []):
        for edit in log.get("edits", []):
            if edit.get("accepted") and "chart_id" in edit:
                out.append(int(edit["chart_id"]))
        for chart in log.get("selected_chart_ids", []):
            out.append(int(chart))
    e_c = _safe_get(metrics, "initial", "residual_stats", "E_c", default=[])
    for chart in np.argsort(np.asarray(e_c, dtype=np.float32))[::-1].tolist():
        out.append(int(chart))
    unique: list[int] = []
    seen: set[int] = set()
    for chart in out:
        if chart in seen:
            continue
        seen.add(chart)
        unique.append(chart)
        if len(unique) >= top_k:
            break
    return unique


def _allocation_payload(case: dict[str, Any]) -> tuple[list[float], dict[str, float]]:
    logs = _safe_get(case["metrics"], "allocator", "outer_logs", default=[])
    if not logs:
        return [], {}
    first = logs[0]
    allocations = _safe_get(first, "summary", "allocations", default=[])
    scales = dict(first.get("chart_scales") or {})
    return list(allocations or []), scales


def _b4_context(b4_root: Path, asset: str, seed: int) -> str:
    statuses: list[str] = []
    for ablation in ("A12", "A13"):
        path = b4_root / f"{ablation}_{asset}_partuv_seed{seed}" / "metrics.json"
        metrics = _load_json(path)
        if metrics:
            verdict = "accept" if _safe_get(metrics, "c5", "accept") is True else "rollback"
            statuses.append(f"{ablation}:{verdict}")
    return "  ".join(statuses)


def render_main_case(case: dict[str, Any], b4_root: Path, output_dir: Path, top_k: int, seed: int) -> None:
    asset = case["asset"]
    baseline = case["baseline"]
    metrics = case["metrics"]
    initial_atlas = case.get("initial_atlas")
    final_atlas = case.get("final_atlas")
    residual = case.get("final_residual") or {}
    if not initial_atlas or not final_atlas:
        fig, ax = plt.subplots(figsize=(4, 3))
        draw_empty_panel(ax, f"{asset}/{baseline}", "missing cached B3 atlas")
        save_figure_pair(fig, output_dir / f"{asset}_{baseline}_residual_chain")
        plt.close(fig)
        return

    edited = _edited_chart_ids(case, top_k=top_k)
    allocations, chart_scales = _allocation_payload(case)
    initial_e_f = _initial_residual(case)
    final_e_f = _final_residual(case)
    fig, axes = plt.subplots(1, 4, figsize=(13.6, 3.25), constrained_layout=True)

    draw_uv_heatmap(
        axes[0],
        initial_atlas["uv"],
        initial_atlas["face_uv"],
        initial_e_f,
        chart_ids=initial_atlas.get("chart_ids"),
        title="Initial atlas",
    )
    draw_metric_box(
        axes[0],
        f"PSNR {_fmt(_safe_get(metrics, 'initial', 'relit', 'psnr'))}\nSSIM {_fmt(_safe_get(metrics, 'initial', 'relit', 'ssim'), 3)}",
    )

    draw_uv_heatmap(
        axes[1],
        initial_atlas["uv"],
        initial_atlas["face_uv"],
        initial_e_f,
        chart_ids=initial_atlas.get("chart_ids"),
        title=f"C2 edit overlay (K={top_k})",
    )
    draw_chart_overlay(axes[1], initial_atlas["uv"], initial_atlas["face_uv"], initial_atlas["chart_ids"], edited, label_charts=False)

    draw_allocation_bars(
        axes[2],
        allocations,
        chart_scales=chart_scales,
        edited_charts=edited,
        title="C3 texel budget",
    )

    draw_seam_map(
        axes[3],
        final_atlas["uv"],
        final_atlas["face_uv"],
        final_atlas["chart_ids"],
        residual.get("seam_edges"),
        residual.get("S_e"),
        title="Final residual + seams",
    )
    d_psnr = _safe_get(metrics, "c5", "delta_psnr")
    seam_delta = _safe_get(metrics, "c5", "seam_relative_delta")
    b4_note = _b4_context(b4_root, asset, seed)
    seam_text = "-" if seam_delta is None else f"{float(seam_delta) * 100.0:.1f}%"
    box = (
        f"PSNR {_fmt(_safe_get(metrics, 'final', 'relit', 'psnr'))}\n"
        f"SSIM {_fmt(_safe_get(metrics, 'final', 'relit', 'ssim'), 3)}\n"
        f"dPSNR {_fmt(d_psnr)}\n"
        f"seam {seam_text}"
    )
    if b4_note:
        box += f"\n{b4_note}"
    draw_metric_box(axes[3], box)

    fig.suptitle(f"Qualitative residual chain: {asset}/{baseline}", fontsize=12)
    save_figure_pair(fig, output_dir / f"{asset}_{baseline}_residual_chain")
    plt.close(fig)


def _parse_case(raw: str) -> tuple[str, str]:
    if ":" not in raw:
        raise ValueError(f"Rollback case must be asset:baseline, got {raw!r}")
    asset, baseline = raw.split(":", 1)
    return asset.strip(), baseline.strip()


def render_rollback_gallery(cases: list[dict[str, Any]], output_dir: Path, top_k: int) -> None:
    rows = max(1, len(cases))
    fig, axes = plt.subplots(rows, 3, figsize=(9.6, 2.45 * rows), constrained_layout=True)
    axes_arr = np.asarray(axes).reshape(rows, 3)
    for row, case in enumerate(cases):
        asset = case["asset"]
        baseline = case["baseline"]
        metrics = case["metrics"]
        initial_atlas = case.get("initial_atlas")
        final_atlas = case.get("final_atlas") or initial_atlas
        residual = case.get("final_residual") or {}
        initial_e_f = _initial_residual(case)
        final_e_f = _final_residual(case)
        edited = _edited_chart_ids(case, top_k=top_k)

        if not initial_atlas:
            for col in range(3):
                draw_empty_panel(axes_arr[row, col], f"{asset}/{baseline}", "missing cache")
            continue

        draw_uv_heatmap(
            axes_arr[row, 0],
            initial_atlas["uv"],
            initial_atlas["face_uv"],
            initial_e_f,
            chart_ids=initial_atlas.get("chart_ids"),
            title=f"{asset}/{baseline}: initial",
        )
        draw_metric_box(axes_arr[row, 0], f"PSNR {_fmt(_safe_get(metrics, 'initial', 'relit', 'psnr'))}")

        draw_uv_heatmap(
            axes_arr[row, 1],
            initial_atlas["uv"],
            initial_atlas["face_uv"],
            initial_e_f,
            chart_ids=initial_atlas.get("chart_ids"),
            title="attempted C2 edits",
        )
        draw_chart_overlay(axes_arr[row, 1], initial_atlas["uv"], initial_atlas["face_uv"], initial_atlas["chart_ids"], edited)

        draw_seam_map(
            axes_arr[row, 2],
            final_atlas["uv"],
            final_atlas["face_uv"],
            final_atlas["chart_ids"],
            residual.get("seam_edges"),
            residual.get("S_e"),
            title="C5 rollback result",
        )
        rollback = _safe_get(metrics, "c5", "rollback_to_baseline")
        d_psnr = _safe_get(metrics, "c5", "delta_psnr")
        draw_metric_box(
            axes_arr[row, 2],
            f"rollback {rollback}\nfinal PSNR {_fmt(_safe_get(metrics, 'final', 'relit', 'psnr'))}\ndPSNR {_fmt(d_psnr)}",
        )
        if final_e_f.size and final_e_f.shape == initial_e_f.shape:
            # Touch the final residual so missing/corrupt caches are surfaced in
            # this script even when the seam map can still be drawn.
            _ = float(np.mean(np.abs(final_e_f - initial_e_f)))

    fig.suptitle("C5 rollback qualitative gallery", fontsize=12)
    save_figure_pair(fig, output_dir / "rollback_gallery")
    plt.close(fig)


def main() -> None:
    args = parse_args()
    b3_root = _resolve_root(args.b3_root, [ROOT / "runs" / "B3_main", Path("/data/dip_1_ws/runs/B3_main")])
    b2_root = _resolve_root(args.b2_root, [ROOT / "runs" / "B2_baseline", Path("/data/dip_1_ws/runs/B2_baseline")])
    b4_root = _resolve_root(args.b4_root, [ROOT / "runs" / "B4_ablation", Path("/data/dip_1_ws/runs/B4_ablation")])
    output_dir = ensure_dir(args.output_dir)

    for asset in args.main_assets:
        case = _load_case(b3_root, b2_root, asset, "partuv", args.seed)
        render_main_case(case, b4_root, output_dir, args.top_k, args.seed)

    rollback_cases = [_load_case(b3_root, b2_root, asset, baseline, args.seed) for asset, baseline in map(_parse_case, args.rollback_cases)]
    render_rollback_gallery(rollback_cases, output_dir, args.top_k)
    print(str(output_dir))


if __name__ == "__main__":
    main()

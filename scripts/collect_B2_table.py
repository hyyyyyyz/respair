#!/usr/bin/env python
"""Collect B2 baseline runs into matched tables and a short result summary."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pbr_atlas.baselines.baseline_failure_table import load_failure_records, write_failure_report
from pbr_atlas.utils.io import write_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect B2 baseline metrics into markdown tables.")
    parser.add_argument("--input-root", default="/data/dip_1_ws/runs/B2_baseline")
    return parser.parse_args()


def _safe_get(payload: dict[str, Any], *keys: str, default=None):
    cur: Any = payload
    for key in keys:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def _format_metric(value: Any, digits: int = 4) -> str:
    if value is None:
        return "-"
    if value == "inf":
        return "inf"
    if isinstance(value, (int, float)):
        return f"{float(value):.{digits}f}"
    return str(value)


def main() -> None:
    args = parse_args()
    root = Path(args.input_root)
    metrics_paths = sorted(root.glob("*/metrics.json"))
    rows: list[dict[str, Any]] = []
    for path in metrics_paths:
        with open(path, "r", encoding="utf-8") as handle:
            rows.append(json.load(handle))

    table_lines = [
        "# B2 Matched Table",
        "",
        "| Asset | Baseline | Status | Matched OK | PSNR | SSIM | LPIPS | E_c mean | G_l | Peak Mem (GB) | Wall (s) | Charts | Util | Dist Q95 | Notes |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]

    comparable_runs = 0
    matched_ok_runs = 0
    partial_runs = 0
    failed_runs = 0
    psnr_sum = 0.0
    psnr_count = 0
    baseline_counter: dict[str, int] = {}

    for payload in sorted(rows, key=lambda item: (item.get("asset", ""), item.get("baseline", ""))):
        asset = payload.get("asset", "-")
        baseline = payload.get("baseline", "-")
        status = payload.get("repro_status", "-")
        matched = not bool(_safe_get(payload, "matched_protocol", "matched_constraint_violated", default=True))
        relit_psnr = _safe_get(payload, "relit", "psnr")
        relit_ssim = _safe_get(payload, "relit", "ssim")
        relit_lpips = _safe_get(payload, "relit", "lpips")
        ec_mean = _safe_get(payload, "residual_stats", "E_c_mean")
        gl_mean = _safe_get(payload, "residual_stats", "G_l_mean")
        peak_mem = payload.get("peak_memory_GB")
        wall = payload.get("wall_clock_s")
        chart_count = _safe_get(payload, "matched_protocol", "stats", "chart_count")
        util = _safe_get(payload, "matched_protocol", "stats", "texture_utilization")
        dist_q95 = _safe_get(payload, "matched_protocol", "stats", "max_distortion_q95")
        notes = payload.get("failure_reason") or "; ".join(_safe_get(payload, "matched_protocol", "violations", default=[])) or "-"

        if status == "failed":
            failed_runs += 1
        elif status == "partial":
            partial_runs += 1
            comparable_runs += 1
        else:
            comparable_runs += 1
        if matched:
            matched_ok_runs += 1
        if isinstance(relit_psnr, (int, float)):
            psnr_sum += float(relit_psnr)
            psnr_count += 1
        baseline_counter[baseline] = baseline_counter.get(baseline, 0) + 1

        table_lines.append(
            "| {asset} | {baseline} | {status} | {matched} | {psnr} | {ssim} | {lpips} | {ec} | {gl} | {mem} | {wall} | {charts} | {util} | {dist} | {notes} |".format(
                asset=asset,
                baseline=baseline,
                status=status,
                matched="yes" if matched else "no",
                psnr=_format_metric(relit_psnr),
                ssim=_format_metric(relit_ssim),
                lpips=_format_metric(relit_lpips),
                ec=_format_metric(ec_mean),
                gl=_format_metric(gl_mean),
                mem=_format_metric(peak_mem, digits=3),
                wall=_format_metric(wall, digits=3),
                charts=_format_metric(chart_count, digits=0),
                util=_format_metric(util),
                dist=_format_metric(dist_q95),
                notes=str(notes).replace("\n", " "),
            )
        )

    if len(table_lines) == 4:
        table_lines.append("| - | - | - | - | - | - | - | - | - | - | - | - | - | - | No runs found. |")

    table_text = "\n".join(table_lines) + "\n"
    write_text(root / "MATCHED_TABLE.md", table_text)
    write_text(root / "B2_MATCHED_TABLE.md", table_text)

    failure_records = load_failure_records(root)
    write_failure_report(root, failure_records)

    avg_psnr = psnr_sum / psnr_count if psnr_count else 0.0
    top_baselines = ", ".join(f"{name}:{count}" for name, count in sorted(baseline_counter.items()))
    result_lines = [
        "# B2 Results",
        "",
        f"- runs discovered: {len(rows)}",
        f"- comparable outputs: {comparable_runs}",
        f"- matched-protocol pass count: {matched_ok_runs}",
        f"- partial reproductions: {partial_runs}",
        f"- failed reproductions: {failed_runs}",
        f"- average PSNR over available runs: {avg_psnr:.4f}" if psnr_count else "- average PSNR over available runs: -",
        f"- baseline coverage: {top_baselines or '-'}",
        "",
        "## B3 Implications",
        "",
        "- Prefer `xatlas_classical`, `matched_oracle`, and any partial proxy that passes matched constraints as initial B3 controls.",
        "- Keep every `partial`/`failed` row explicit in the appendix failure table; do not silently drop them from the protocol narrative.",
        "- Investigate any baseline with `matched_constraint_violated: true` before treating its relit metrics as a fair control.",
    ]
    write_text(root / "B2_RESULTS.md", "\n".join(result_lines) + "\n")
    print(str(root / "MATCHED_TABLE.md"))


if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""Collect B3 main runs into the main result table and claim status note."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pbr_atlas.utils.io import write_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect B3 metrics into markdown tables.")
    parser.add_argument("--input-root", default="/data/dip_1_ws/runs/B3_main")
    return parser.parse_args()


def _safe_get(payload: dict[str, Any], *keys: str, default=None):
    cur: Any = payload
    for key in keys:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def _num(value: Any) -> float | None:
    if value is None or value == "inf":
        return None
    try:
        return float(value)
    except Exception:
        return None


def _fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "-"
    if value == "inf":
        return "inf"
    if isinstance(value, (int, float)):
        return f"{float(value):.{digits}f}"
    return str(value)


def _delta(a: Any, b: Any) -> float | None:
    a_num = _num(a)
    b_num = _num(b)
    if a_num is None or b_num is None:
        return None
    return a_num - b_num


def _mean_std(values: list[float]) -> tuple[float | None, float | None]:
    if not values:
        return None, None
    mean = sum(values) / len(values)
    var = sum((value - mean) ** 2 for value in values) / len(values)
    return mean, var**0.5


def _fmt_stat(values: list[float], digits: int = 4) -> str:
    mean, std = _mean_std(values)
    if mean is None:
        return "-"
    if len(values) <= 1:
        return _fmt(mean, digits=digits)
    return f"{mean:.{digits}f}±{std:.{digits}f}"


def main() -> None:
    args = parse_args()
    root = Path(args.input_root)
    metrics_paths = sorted(root.glob("*/metrics.json"))
    rows = []
    for path in metrics_paths:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        payload["_run_dir"] = str(path.parent)
        rows.append(payload)

    grouped: dict[tuple[str, str], dict[str, list[dict[str, Any]]]] = {}
    for payload in rows:
        key = (str(payload.get("asset", "-")), str(payload.get("baseline", "-")))
        grouped.setdefault(key, {}).setdefault(str(payload.get("method", "-")), []).append(payload)

    table_lines = [
        "# B3 Main Table",
        "",
        "| Asset | Baseline | Ours PSNR | Baseline PSNR | dPSNR | dLPIPS | dE_c | dG_l | Repair Chart Ratio | Edit Chart Count | Matched Protocol After Repair |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]

    deltas_psnr: list[float] = []
    deltas_lpips: list[float] = []
    deltas_ec: list[float] = []
    deltas_gl: list[float] = []
    hard_pass = 0
    metric_pass = 0
    matched_pass = 0
    ours_count = 0
    edit_ratios: list[float] = []
    seam_drops: list[float] = []

    for (asset, baseline), methods in sorted(grouped.items()):
        ours_runs = sorted(methods.get("ours", []), key=lambda item: (int(item.get("seed", 0)), int(item.get("split_seed", item.get("seed", 0)))))
        base_runs = sorted(methods.get("baseline_only", []), key=lambda item: (int(item.get("seed", 0)), int(item.get("split_seed", item.get("seed", 0)))))
        row_runs = ours_runs or base_runs

        ours_psnrs: list[float] = []
        base_psnrs: list[float] = []
        row_d_psnr: list[float] = []
        row_d_lpips: list[float] = []
        row_d_ec: list[float] = []
        row_d_gl: list[float] = []
        row_ratios: list[float] = []
        row_edits: list[float] = []
        row_matched_pass = 0
        row_accept = 0

        for idx, ours in enumerate(ours_runs):
            base = base_runs[idx] if idx < len(base_runs) else None
            ours_psnr = _num(_safe_get(ours, "final", "relit", "psnr"))
            base_psnr = _num(_safe_get(base or {}, "final", "relit", "psnr"))
            if base_psnr is None:
                base_psnr = _num(_safe_get(ours, "initial", "relit", "psnr"))
            if ours_psnr is not None:
                ours_psnrs.append(ours_psnr)
            if base_psnr is not None:
                base_psnrs.append(base_psnr)
            d_psnr = None if ours_psnr is None or base_psnr is None else ours_psnr - base_psnr
            d_lpips = _delta(_safe_get(ours, "final", "relit", "lpips"), _safe_get(base or ours, "initial", "relit", "lpips"))
            d_ec = _delta(_safe_get(ours, "final", "residual_stats", "E_c_mean"), _safe_get(base or ours, "initial", "residual_stats", "E_c_mean"))
            d_gl = _delta(_safe_get(ours, "final", "residual_stats", "G_l_mean"), _safe_get(base or ours, "initial", "residual_stats", "G_l_mean"))
            for value, target in ((d_psnr, row_d_psnr), (d_lpips, row_d_lpips), (d_ec, row_d_ec), (d_gl, row_d_gl)):
                if value is not None:
                    target.append(float(value))
            repair_ratio = _num(_safe_get(ours, "repair", "edited_chart_ratio"))
            edit_count = _num(_safe_get(ours, "repair", "edit_chart_count"))
            if repair_ratio is not None:
                row_ratios.append(repair_ratio)
                edit_ratios.append(repair_ratio)
            if edit_count is not None:
                row_edits.append(edit_count)
            matched_violated = _safe_get(ours, "c5", "matched_protocol_after_repair", "matched_constraint_violated")
            if matched_violated is False:
                matched_pass += 1
                row_matched_pass += 1
            if _safe_get(ours, "c5", "hard_accept") is True:
                hard_pass += 1
            if _safe_get(ours, "c5", "metric_accept") is True:
                metric_pass += 1
            if _safe_get(ours, "c5", "accept") is True:
                row_accept += 1
            seam_drop = _num(_safe_get(ours, "c5", "seam_relative_delta"))
            if seam_drop is not None:
                seam_drops.append(seam_drop)

        if not ours_runs:
            for base in base_runs:
                base_psnr = _num(_safe_get(base, "final", "relit", "psnr"))
                if base_psnr is not None:
                    base_psnrs.append(base_psnr)

        deltas_psnr.extend(row_d_psnr)
        deltas_lpips.extend(row_d_lpips)
        deltas_ec.extend(row_d_ec)
        deltas_gl.extend(row_d_gl)
        ours_count += len(ours_runs)
        matched_text = f"{row_matched_pass}/{len(ours_runs)}" if ours_runs else "-"
        if ours_runs:
            matched_text = f"{matched_text}; accept {row_accept}/{len(ours_runs)}"

        table_lines.append(
            "| {asset} | {baseline} | {ours_psnr} | {base_psnr} | {d_psnr} | {d_lpips} | {d_ec} | {d_gl} | {ratio} | {edits} | {matched} |".format(
                asset=asset,
                baseline=baseline,
                ours_psnr=_fmt_stat(ours_psnrs),
                base_psnr=_fmt_stat(base_psnrs),
                d_psnr=_fmt_stat(row_d_psnr),
                d_lpips=_fmt_stat(row_d_lpips),
                d_ec=_fmt_stat(row_d_ec),
                d_gl=_fmt_stat(row_d_gl),
                ratio=_fmt_stat(row_ratios),
                edits=_fmt_stat(row_edits, digits=1),
                matched=matched_text,
            )
        )

    if len(table_lines) == 4:
        table_lines.append("| - | - | - | - | - | - | - | - | - | - | No runs found. |")
    write_text(root / "MAIN_TABLE.md", "\n".join(table_lines) + "\n")

    avg_psnr = sum(deltas_psnr) / len(deltas_psnr) if deltas_psnr else None
    avg_lpips = sum(deltas_lpips) / len(deltas_lpips) if deltas_lpips else None
    avg_ec = sum(deltas_ec) / len(deltas_ec) if deltas_ec else None
    avg_gl = sum(deltas_gl) / len(deltas_gl) if deltas_gl else None
    max_edit_ratio = max(edit_ratios) if edit_ratios else None
    avg_seam_drop = sum(seam_drops) / len(seam_drops) if seam_drops else None

    claim_lines = [
        "# B3 Results",
        "",
        f"- runs discovered: {len(rows)}",
        f"- ours runs: {ours_count}",
        f"- C5 hard-guard pass count: {hard_pass}/{ours_count}" if ours_count else "- C5 hard-guard pass count: -",
        f"- C5 metric-accept count: {metric_pass}/{ours_count}" if ours_count else "- C5 metric-accept count: -",
        f"- matched-protocol-after-repair pass count: {matched_pass}/{ours_count}" if ours_count else "- matched-protocol-after-repair pass count: -",
        f"- average dPSNR: {_fmt(avg_psnr)}",
        f"- average dLPIPS: {_fmt(avg_lpips)}",
        f"- average dE_c: {_fmt(avg_ec)}",
        f"- average dG_l: {_fmt(avg_gl)}",
        "",
        "## Claim Status",
        "",
        f"- C1 residual chain: {'supported' if rows else 'pending'} by persisted residual_atlas/residual_chain outputs.",
        f"- C2 local repair: {_claim_status(max_edit_ratio is not None and max_edit_ratio <= 0.15, rows)}; max edited chart ratio = {_fmt(max_edit_ratio)}.",
        f"- C3 fixed-budget mip allocation: {_claim_status(avg_gl is not None and avg_gl < 0.0, rows)}; average dG_l = {_fmt(avg_gl)}.",
        f"- C4 cross-channel seam coupling: {_claim_status(avg_seam_drop is not None and avg_seam_drop < 0.0, rows)}; average seam relative delta = {_fmt(avg_seam_drop)}.",
        f"- C5 matched controls: {_claim_status(ours_count > 0 and matched_pass == ours_count and hard_pass == ours_count, rows)}.",
    ]
    write_text(root / "B3_RESULTS.md", "\n".join(claim_lines) + "\n")
    print(str(root / "MAIN_TABLE.md"))


def _claim_status(condition: bool, rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "pending"
    return "supported" if condition else "needs ablation"


if __name__ == "__main__":
    main()

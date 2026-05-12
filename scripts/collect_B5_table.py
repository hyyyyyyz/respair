#!/usr/bin/env python
"""Collect B5 strict matched-control runs into paper-facing markdown tables."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pbr_atlas.ablations.b5_strict_matched import B5_CONDITIONS
from pbr_atlas.utils.io import ensure_dir, write_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect B5 matched-control metrics.")
    parser.add_argument("--input-root", default="/data/dip_1_ws/runs/B5_matched")
    parser.add_argument("--b3-root", default="runs/B3_main")
    parser.add_argument("--output-root", default=None)
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


def _num(value: Any) -> float | None:
    if value is None or value == "inf":
        return None
    try:
        return float(value)
    except Exception:
        return None


def _fmt(value: Any, digits: int = 4) -> str:
    value_num = _num(value)
    if value == "inf":
        return "inf"
    if value_num is None:
        return "-"
    return f"{value_num:.{digits}f}"


def _delta(a: Any, b: Any) -> float | None:
    a_num = _num(a)
    b_num = _num(b)
    if a_num is None or b_num is None:
        return None
    return a_num - b_num


def _load_b3(b3_root: Path, asset: str, seed: int = 42) -> dict[str, Any] | None:
    candidates = [
        b3_root / f"{asset}_partuv_ours_seed{seed}" / "metrics.json",
        ROOT / "runs" / "B3_main" / f"{asset}_partuv_ours_seed{seed}" / "metrics.json",
        Path("/data/dip_1_ws/runs/B3_main") / f"{asset}_partuv_ours_seed{seed}" / "metrics.json",
    ]
    for path in candidates:
        payload = _load_json(path)
        if payload:
            return payload
    return None


def _c5_verdict(metrics: dict[str, Any] | None) -> str:
    if not metrics:
        return "missing"
    c5 = metrics.get("c5", {})
    if metrics.get("repro_status") == "failed":
        return "repro-failed"
    if c5.get("accept") is True:
        return "accept"
    if c5.get("rollback_to_baseline") is True:
        return "rollback"
    if c5.get("hard_accept") is False:
        return "hard-fail"
    if c5.get("metric_accept") is False:
        return "metric-fail"
    return "-"


def _matched_ok(metrics: dict[str, Any] | None) -> str:
    if not metrics:
        return "-"
    value = _safe_get(metrics, "c5", "b5_strict", "matched_ok")
    if value is None:
        value = _safe_get(metrics, "c5", "hard_accept")
    if value is None:
        return "-"
    return "yes" if bool(value) else "no"


def _index_metrics(root: Path) -> dict[tuple[str, str], dict[str, Any]]:
    out: dict[tuple[str, str], dict[str, Any]] = {}
    for path in sorted(root.glob("*/metrics.json")):
        payload = _load_json(path)
        if not payload:
            continue
        condition = str(payload.get("condition") or _safe_get(payload, "c5", "b5_strict", "id") or "")
        asset = str(payload.get("asset") or "")
        if not condition or not asset:
            continue
        payload["_run_dir"] = str(path.parent)
        out[(asset, condition)] = payload
    return out


def main() -> None:
    args = parse_args()
    root = _resolve_root(args.input_root, [ROOT / "runs" / "B5_matched"])
    b3_root = _resolve_root(args.b3_root, [ROOT / "runs" / "B3_main", Path("/data/dip_1_ws/runs/B3_main")])
    output_root = Path(args.output_root) if args.output_root else root
    ensure_dir(output_root)

    metrics_by_case = _index_metrics(root)
    table_lines = [
        "# B5 Strict Matched-Control Table",
        "",
        "| Asset | Condition | ours_PSNR | dPSNR vs ACCEPT | matched_OK | c5_verdict | Gain vs initial | Strict violations |",
        "|---|---|---:|---:|---|---|---:|---|",
    ]
    result_lines = [
        "# B5 Results",
        "",
        f"- runs discovered: {len(metrics_by_case)}",
        "",
        "## Expected-Control Check",
        "",
    ]

    pass_gain = 0
    evaluated_gain = 0
    matched_yes = 0
    expected_rows = 0

    for asset in ("spot", "bunny"):
        b3 = _load_b3(b3_root, asset)
        b3_accept = _safe_get(b3, "final", "relit", "psnr")
        for condition_id, spec in B5_CONDITIONS.items():
            expected_rows += 1
            metrics = metrics_by_case.get((asset, condition_id))
            final_psnr = _safe_get(metrics, "final", "relit", "psnr")
            initial_psnr = _safe_get(metrics, "initial", "relit", "psnr")
            d_accept = _delta(final_psnr, b3_accept)
            gain = _delta(final_psnr, initial_psnr)
            matched = _matched_ok(metrics)
            matched_yes += int(matched == "yes")
            if gain is not None:
                evaluated_gain += 1
                pass_gain += int(gain >= 0.3)
            violations = _safe_get(metrics, "c5", "b5_strict", "violations", default=[])
            if isinstance(violations, list):
                violations_text = "; ".join(str(v) for v in violations) or "-"
            else:
                violations_text = str(violations)
            table_lines.append(
                f"| {asset} | {condition_id} {spec.name} | {_fmt(final_psnr)} | {_fmt(d_accept)} | "
                f"{matched} | {_c5_verdict(metrics)} | {_fmt(gain)} | {violations_text} |"
            )
            result_lines.append(
                f"- {asset}/{condition_id}: matched={matched}, verdict={_c5_verdict(metrics)}, "
                f"gain_vs_initial={_fmt(gain)}, d_vs_B3_ACCEPT={_fmt(d_accept)}."
            )

    if expected_rows == 0:
        table_lines.append("| - | - | - | - | - | - | - | No B5 conditions configured. |")

    result_lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- matched OK count: {matched_yes}/{expected_rows}",
            f"- gain >= +0.3 dB count: {pass_gain}/{evaluated_gain}" if evaluated_gain else "- gain >= +0.3 dB count: -",
            "",
            "## Expected Reference",
            "",
        ]
    )
    for condition_id, spec in B5_CONDITIONS.items():
        result_lines.append(f"- {condition_id}: {spec.expected}")

    write_text(output_root / "B5_TABLE.md", "\n".join(table_lines) + "\n")
    write_text(output_root / "B5_RESULTS.md", "\n".join(result_lines) + "\n")
    print(str(output_root / "B5_TABLE.md"))


if __name__ == "__main__":
    main()

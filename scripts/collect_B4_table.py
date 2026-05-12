#!/usr/bin/env python
"""Collect B4 ablation runs into markdown tables."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pbr_atlas.ablations.common import EXPECTED_DELTAS
from pbr_atlas.utils.io import write_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect B4 ablation metrics.")
    parser.add_argument("--input-root", default="runs/B4_ablation")
    parser.add_argument("--b3-root", default="runs/B3_main")
    return parser.parse_args()


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
    if value_num is None:
        return "-"
    return f"{value_num:.{digits}f}"


def _delta(a: Any, b: Any) -> float | None:
    a_num = _num(a)
    b_num = _num(b)
    if a_num is None or b_num is None:
        return None
    return a_num - b_num


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_b3(root: Path, asset: str, baseline: str, seed: int) -> dict[str, Any] | None:
    direct = root / f"{asset}_{baseline}_ours_seed{seed}" / "metrics.json"
    if direct.exists():
        return _load_json(direct)
    matches = sorted(root.glob(f"{asset}_{baseline}_ours_seed*/metrics.json"))
    return _load_json(matches[0]) if matches else None


def _c5_verdict(metrics: dict[str, Any]) -> str:
    c5 = metrics.get("c5", {})
    if c5.get("accept") is True:
        return "accept"
    if c5.get("rollback_to_baseline") is True:
        return "rollback"
    if c5.get("hard_accept") is False:
        return "hard-fail"
    if c5.get("metric_accept") is False:
        return "metric-fail"
    return "-"


def _matched_ok(metrics: dict[str, Any]) -> str:
    control = _safe_get(metrics, "c5", "matched_control", "hard_constraint_ok")
    if control is not None:
        return "yes" if control else "no"
    violated = _safe_get(metrics, "c5", "matched_protocol_after_repair", "matched_constraint_violated")
    if violated is None:
        return "-"
    return "no" if violated else "yes"


def _direction_ok(ablation: str, delta_vs_ours: float | None) -> bool | None:
    if delta_vs_ours is None:
        return None
    if ablation in {"A1", "A2", "A3", "A4", "A5", "A6", "A7", "A18"}:
        return delta_vs_ours <= 0.0
    if ablation in {"A8", "A9"}:
        return True
    return delta_vs_ours >= -0.05


def main() -> None:
    args = parse_args()
    root = Path(args.input_root)
    b3_root = Path(args.b3_root)
    metrics_paths = sorted(root.glob("*/metrics.json"))
    rows: list[dict[str, Any]] = []
    for path in metrics_paths:
        payload = _load_json(path)
        if not payload:
            continue
        payload["_run_dir"] = str(path.parent)
        rows.append(payload)

    table = [
        "# B4 Ablation Table",
        "",
        "| Ablation | Variant | Case (asset/baseline) | PSNR | dPSNR vs ours | dGain from B3 | C5 verdict | matched OK | Expected delta |",
        "|---|---|---|---:|---:|---:|---|---|---|",
    ]
    direction_total = 0
    direction_ok = 0
    matched_yes = 0

    for metrics in sorted(rows, key=lambda item: (str(item.get("ablation", "")), str(item.get("asset", "")), str(item.get("baseline", "")), str(item.get("ablation_variant") or ""))):
        ablation = str(metrics.get("ablation", "-"))
        asset = str(metrics.get("asset", "-"))
        baseline = str(metrics.get("baseline", "-"))
        seed = int(metrics.get("seed", 42))
        variant = metrics.get("ablation_variant") or "-"
        final_psnr = _safe_get(metrics, "final", "relit", "psnr")
        initial_psnr = _safe_get(metrics, "initial", "relit", "psnr")
        b3 = _load_b3(b3_root, asset, baseline, seed)
        b3_final = _safe_get(b3 or {}, "final", "relit", "psnr")
        b3_initial = _safe_get(b3 or {}, "initial", "relit", "psnr")
        d_vs_ours = _delta(final_psnr, b3_final)
        d_gain = None
        if _delta(final_psnr, initial_psnr) is not None and _delta(b3_final, b3_initial) is not None:
            d_gain = _delta(final_psnr, initial_psnr) - _delta(b3_final, b3_initial)
        ok = _direction_ok(ablation, d_vs_ours)
        if ok is not None:
            direction_total += 1
            direction_ok += int(ok)
        matched = _matched_ok(metrics)
        matched_yes += int(matched == "yes")
        table.append(
            f"| {ablation} | {variant} | {asset}/{baseline} | {_fmt(final_psnr)} | {_fmt(d_vs_ours)} | {_fmt(d_gain)} | "
            f"{_c5_verdict(metrics)} | {matched} | {metrics.get('expected_delta') or EXPECTED_DELTAS.get(ablation, '-')} |"
        )

    if not rows:
        table.append("| - | - | - | - | - | - | - | - | No runs found. |")

    write_text(root / "B4_TABLE.md", "\n".join(table) + "\n")
    results = [
        "# B4 Results",
        "",
        f"- runs discovered: {len(rows)}",
        f"- expected-direction pass count: {direction_ok}/{direction_total}" if direction_total else "- expected-direction pass count: -",
        f"- matched OK count: {matched_yes}/{len(rows)}" if rows else "- matched OK count: -",
        "",
        "## Expected Delta Reference",
        "",
    ]
    for ablation_id in [f"A{i}" for i in range(1, 19)]:
        results.append(f"- {ablation_id}: {EXPECTED_DELTAS[ablation_id]}")
    write_text(root / "B4_RESULTS.md", "\n".join(results) + "\n")
    print(str(root / "B4_TABLE.md"))


if __name__ == "__main__":
    main()


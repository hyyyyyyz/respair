#!/usr/bin/env python
"""Collect B7 transfer and robustness runs into markdown tables."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pbr_atlas.utils.io import ensure_dir, write_text  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect B7 transfer/robustness metrics.")
    parser.add_argument("--transfer-root", default="/data/dip_1_ws/runs/B7_transfer")
    parser.add_argument("--robustness-root", default="/data/dip_1_ws/runs/B7_robustness")
    parser.add_argument("--output-root", default=None, help="Defaults to --transfer-root.")
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
    return str(metrics.get("repro_status") or "-")


def _metrics(root: Path, block: str | None = None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(root.glob("*/metrics.json")):
        payload = _load_json(path)
        if not payload:
            continue
        if block and payload.get("block") != block:
            continue
        payload["_run_dir"] = str(path.parent)
        rows.append(payload)
    return rows


def _transfer_outputs(root: Path) -> tuple[list[str], list[str], dict[str, float | int | None]]:
    rows = _metrics(root, "B7_transfer")
    grouped: dict[tuple[str, str], dict[str, dict[str, Any]]] = {}
    for payload in rows:
        asset = str(payload.get("generated_asset") or payload.get("asset") or "-")
        baseline = str(payload.get("baseline") or "-")
        method = str(payload.get("method") or "-")
        grouped.setdefault((asset, baseline), {})[method] = payload

    table_lines = [
        "# B7 Generated Transfer Table",
        "",
        "| Generated Mesh | Source | Baseline | Baseline PSNR | Ours PSNR | dPSNR | c5_verdict | repro_status | Failure / Note |",
        "|---|---|---|---:|---:|---:|---|---|---|",
    ]
    failure_lines = [
        "# B7 Failure Table",
        "",
        "| Generated Mesh | Method | Baseline | repro_status | Failure Reason | Run Dir |",
        "|---|---|---|---|---|---|",
    ]

    evaluated = 0
    pass_plus3 = 0
    pass_plan = 0
    deltas: list[float] = []

    for (asset, baseline), methods in sorted(grouped.items()):
        ours = methods.get("ours")
        base = methods.get("baseline_only")
        row_source = ours or base or {}
        source = _safe_get(row_source, "generated_mesh", "source", default="-")
        base_psnr = _safe_get(base, "final", "relit", "psnr")
        if base_psnr is None:
            base_psnr = _safe_get(row_source, "initial", "relit", "psnr")
        ours_psnr = _safe_get(ours, "final", "relit", "psnr")
        d_psnr = _delta(ours_psnr, base_psnr)
        if d_psnr is not None:
            evaluated += 1
            deltas.append(d_psnr)
            pass_plus3 += int(d_psnr > 3.0)
            pass_plan += int(d_psnr >= 0.3)
        note = _safe_get(ours or base, "failure_reason", default="-")
        table_lines.append(
            f"| {asset} | {source} | {baseline} | {_fmt(base_psnr)} | {_fmt(ours_psnr)} | {_fmt(d_psnr)} | "
            f"{_c5_verdict(ours)} | {row_source.get('repro_status', '-')} | {note or '-'} |"
        )

    if not grouped:
        table_lines.append("| - | - | - | - | - | - | missing | - | No B7 transfer runs found. |")

    for payload in rows:
        status = str(payload.get("repro_status") or "-")
        if status == "ok":
            continue
        failure_lines.append(
            "| {asset} | {method} | {baseline} | {status} | {reason} | {run_dir} |".format(
                asset=payload.get("generated_asset") or payload.get("asset") or "-",
                method=payload.get("method") or "-",
                baseline=payload.get("baseline") or "-",
                status=status,
                reason=payload.get("failure_reason") or "-",
                run_dir=payload.get("_run_dir") or "-",
            )
        )
    if len(failure_lines) == 4:
        failure_lines.append("| - | - | - | - | No transfer failures or partial reproductions found. | - |")

    stats = {
        "transfer_rows": len(rows),
        "transfer_pairs": len(grouped),
        "transfer_evaluated": evaluated,
        "transfer_pass_plus3": pass_plus3,
        "transfer_pass_plan": pass_plan,
        "transfer_avg_dpsnr": sum(deltas) / len(deltas) if deltas else None,
    }
    return table_lines, failure_lines, stats


def _reference_level(sweep: str) -> float:
    if sweep == "noise":
        return 0.0
    if sweep == "view":
        return 4.0
    if sweep == "light":
        return 4.0
    return 0.0


def _is_mild(sweep: str, level: float) -> bool:
    if sweep == "noise":
        return 0.0 < level <= 0.02
    if sweep == "view":
        return level in {4.0, 6.0}
    if sweep == "light":
        return level in {2.0, 4.0}
    return False


def _robustness_outputs(root: Path) -> tuple[list[str], dict[str, float | int | None]]:
    rows = _metrics(root, "B7_robustness")
    table_lines = [
        "# B7 Robustness Table",
        "",
        "| Sweep | Level | Asset | Method | PSNR | Ref PSNR | Drop | c5_verdict | repro_status |",
        "|---|---:|---|---|---:|---:|---:|---|---|",
    ]
    by_key: dict[tuple[str, str, str, str], dict[float, dict[str, Any]]] = {}
    for payload in rows:
        robustness = payload.get("robustness") or {}
        sweep = str(robustness.get("sweep") or "-")
        level_num = _num(robustness.get("level"))
        if level_num is None:
            continue
        asset = str(payload.get("asset") or "-")
        baseline = str(payload.get("baseline") or "-")
        method = str(payload.get("method") or "-")
        by_key.setdefault((sweep, asset, baseline, method), {})[float(level_num)] = payload

    mild_evaluated = 0
    mild_pass = 0
    drops: list[float] = []
    for (sweep, asset, baseline, method), levels in sorted(by_key.items()):
        ref = levels.get(_reference_level(sweep))
        if ref is None and levels:
            ref = levels[sorted(levels.keys())[0]]
        ref_psnr = _safe_get(ref, "final", "relit", "psnr")
        for level, payload in sorted(levels.items()):
            psnr = _safe_get(payload, "final", "relit", "psnr")
            drop = _delta(ref_psnr, psnr)
            if drop is not None:
                drops.append(drop)
                if method == "ours" and _is_mild(sweep, level):
                    mild_evaluated += 1
                    mild_pass += int(drop < 2.0)
            table_lines.append(
                f"| {sweep} | {_fmt(level)} | {asset}/{baseline} | {method} | {_fmt(psnr)} | {_fmt(ref_psnr)} | "
                f"{_fmt(drop)} | {_c5_verdict(payload)} | {payload.get('repro_status', '-')} |"
            )

    if not by_key:
        table_lines.append("| - | - | - | - | - | - | - | missing | No B7 robustness runs found. |")

    stats = {
        "robustness_rows": len(rows),
        "robustness_cases": sum(len(levels) for levels in by_key.values()),
        "robustness_mild_evaluated": mild_evaluated,
        "robustness_mild_pass": mild_pass,
        "robustness_avg_drop": sum(drops) / len(drops) if drops else None,
    }
    return table_lines, stats


def main() -> None:
    args = parse_args()
    transfer_root = _resolve_root(args.transfer_root, [ROOT / "runs" / "B7_transfer"])
    robustness_root = _resolve_root(args.robustness_root, [ROOT / "runs" / "B7_robustness"])
    output_root = Path(args.output_root) if args.output_root else transfer_root
    ensure_dir(output_root)

    transfer_table, failure_table, transfer_stats = _transfer_outputs(transfer_root)
    robustness_table, robustness_stats = _robustness_outputs(robustness_root)

    write_text(transfer_root / "B7_TABLE.md", "\n".join(transfer_table) + "\n")
    write_text(transfer_root / "B7_FAILURE_TABLE.md", "\n".join(failure_table) + "\n")
    ensure_dir(robustness_root)
    write_text(robustness_root / "B7_ROBUSTNESS_TABLE.md", "\n".join(robustness_table) + "\n")

    evaluated = int(transfer_stats["transfer_evaluated"] or 0)
    pass_plus3 = int(transfer_stats["transfer_pass_plus3"] or 0)
    pass_plan = int(transfer_stats["transfer_pass_plan"] or 0)
    mild_eval = int(robustness_stats["robustness_mild_evaluated"] or 0)
    mild_pass = int(robustness_stats["robustness_mild_pass"] or 0)
    plus3_fraction = (pass_plus3 / evaluated) if evaluated else None
    plan_fraction = (pass_plan / evaluated) if evaluated else None
    mild_fraction = (mild_pass / mild_eval) if mild_eval else None

    result_lines = [
        "# B7 Results",
        "",
        "## Generated Transfer vs Brief",
        "",
        f"- transfer run rows discovered: {transfer_stats['transfer_rows']}",
        f"- generated mesh/baseline pairs evaluated: {evaluated}",
        f"- brief target dPSNR > +3 dB on >=50% meshes: {pass_plus3}/{evaluated} ({_fmt(plus3_fraction, 2)})",
        f"- EXPERIMENT_PLAN weaker target dPSNR >= +0.3 dB: {pass_plan}/{evaluated} ({_fmt(plan_fraction, 2)})",
        f"- average transfer dPSNR: {_fmt(transfer_stats['transfer_avg_dpsnr'])}",
        "",
        "## Robustness vs Brief",
        "",
        f"- robustness rows discovered: {robustness_stats['robustness_rows']}",
        f"- mild perturbation PSNR drop < 2 dB: {mild_pass}/{mild_eval} ({_fmt(mild_fraction, 2)})",
        f"- average robustness PSNR drop: {_fmt(robustness_stats['robustness_avg_drop'])}",
        "",
        "## Verdict",
        "",
        f"- transfer_plus3_target: {'supported' if plus3_fraction is not None and plus3_fraction >= 0.5 else 'pending/unsupported'}",
        f"- transfer_plan_target: {'supported' if plan_fraction is not None and plan_fraction >= 0.5 else 'pending/unsupported'}",
        f"- robustness_mild_target: {'supported' if mild_fraction is not None and mild_fraction >= 1.0 else 'pending/unsupported'}",
        "",
        f"- transfer table: {transfer_root / 'B7_TABLE.md'}",
        f"- robustness table: {robustness_root / 'B7_ROBUSTNESS_TABLE.md'}",
        f"- failure table: {transfer_root / 'B7_FAILURE_TABLE.md'}",
    ]
    write_text(output_root / "B7_RESULTS.md", "\n".join(result_lines) + "\n")
    print(str(transfer_root / "B7_TABLE.md"))


if __name__ == "__main__":
    main()

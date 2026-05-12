#!/usr/bin/env python
"""PG-enh3 robustness sweep for bunny and warped cylinder."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pbr_atlas.utils.io import atomic_write_json, ensure_dir, write_text  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run PG-enh3 robustness grid.")
    parser.add_argument("--assets", default="bunny,proc_warped_cylinder")
    parser.add_argument("--sweeps", default="noise,view,light")
    parser.add_argument("--baseline", default="partuv")
    parser.add_argument("--method", default="ours")
    parser.add_argument("--config", default="configs/B7_robustness.yaml")
    parser.add_argument("--output-root", default="/data/dip_1_ws/runs/PG_enh3_robust")
    parser.add_argument("--data-root", default=None)
    parser.add_argument("--generated-data-root", default=None)
    parser.add_argument("--robustness-data-root", default=None)
    parser.add_argument("--gpu", type=int, default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--no-lpips", action="store_true")
    parser.add_argument("--force-setup", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--collect-only", action="store_true")
    return parser.parse_args()


def _items(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _run_command(args: argparse.Namespace, asset: str, sweep: str) -> None:
    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "run_B7_robustness.py"),
        "--asset",
        asset,
        "--baseline",
        args.baseline,
        "--method",
        args.method,
        "--sweep",
        sweep,
        "--config",
        args.config,
        "--output-root",
        args.output_root,
    ]
    if args.data_root:
        cmd += ["--data-root", args.data_root]
    if args.generated_data_root:
        cmd += ["--generated-data-root", args.generated_data_root]
    if args.robustness_data_root:
        cmd += ["--robustness-data-root", args.robustness_data_root]
    if args.gpu is not None:
        cmd += ["--gpu", str(args.gpu)]
    if args.seed is not None:
        cmd += ["--seed", str(args.seed)]
    if args.no_lpips:
        cmd.append("--no-lpips")
    if args.force_setup:
        cmd.append("--force-setup")
    if args.dry_run:
        cmd.append("--dry-run")
    subprocess.run(cmd, check=True)


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _num(value: Any) -> float | None:
    if value is None or value == "inf":
        return None
    try:
        return float(value)
    except Exception:
        return None


def _fmt(value: Any, digits: int = 3) -> str:
    value = _num(value)
    return "-" if value is None else f"{value:.{digits}f}"


def _c5(metrics: dict[str, Any]) -> str:
    if metrics.get("repro_status") == "failed":
        return "failed"
    c5 = metrics.get("c5", {})
    if c5.get("accept") is True:
        return "accept"
    if c5.get("rollback_to_baseline") is True:
        return "rollback"
    return str(metrics.get("repro_status") or "-")


def _reference_level(sweep: str) -> float:
    return 0.0 if sweep == "noise" else 4.0


def _collect(output_root: Path) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for path in sorted(output_root.glob("*/metrics.json")):
        metrics = _load_json(path)
        if not metrics or metrics.get("block") != "B7_robustness":
            continue
        robustness = metrics.get("robustness") or {}
        rows.append(
            {
                "run_dir": str(path.parent),
                "asset": metrics.get("asset"),
                "baseline": metrics.get("baseline"),
                "method": metrics.get("method"),
                "sweep": robustness.get("sweep"),
                "level": robustness.get("level"),
                "psnr": ((metrics.get("final") or {}).get("relit") or {}).get("psnr"),
                "c5": _c5(metrics),
                "repro_status": metrics.get("repro_status"),
            }
        )
    ref: dict[tuple[str, str], float | None] = {}
    for row in rows:
        key = (str(row["asset"]), str(row["sweep"]))
        if float(row["level"]) == _reference_level(str(row["sweep"])):
            ref[key] = _num(row["psnr"])
    for row in rows:
        ref_psnr = ref.get((str(row["asset"]), str(row["sweep"])))
        psnr = _num(row["psnr"])
        row["ref_psnr"] = ref_psnr
        row["drop_vs_ref"] = None if ref_psnr is None or psnr is None else ref_psnr - psnr
    return {"rows": rows}


def _markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# PG-enh3 Robustness Table",
        "",
        "| Asset | Sweep | Level | PSNR | Ref PSNR | Drop | C5 | Status |",
        "|---|---|---:|---:|---:|---:|---|---|",
    ]
    for row in payload["rows"]:
        lines.append(
            "| {asset} | {sweep} | {level} | {psnr} | {ref} | {drop} | {c5} | {status} |".format(
                asset=row["asset"],
                sweep=row["sweep"],
                level=_fmt(row["level"], 4),
                psnr=_fmt(row["psnr"]),
                ref=_fmt(row["ref_psnr"]),
                drop=_fmt(row["drop_vs_ref"]),
                c5=row["c5"],
                status=row["repro_status"],
            )
        )
    if not payload["rows"]:
        lines.append("| - | - | - | - | - | - | missing | no PG-enh3 runs found |")
    return "\n".join(lines) + "\n"


def _results(payload: dict[str, Any]) -> str:
    rows = payload["rows"]
    assets = sorted({str(row["asset"]) for row in rows})
    lines = ["# PG-enh3 Robustness Results", ""]
    for asset in assets:
        asset_rows = [row for row in rows if row["asset"] == asset]
        rollback_noise = [
            row for row in asset_rows if row["sweep"] == "noise" and row["c5"] == "rollback" and _num(row["level"]) not in (None, 0.0)
        ]
        max_drop = max([_num(row["drop_vs_ref"]) or 0.0 for row in asset_rows], default=0.0)
        lines.append(f"- {asset}: {len(asset_rows)} rows, max drop {_fmt(max_drop)}, nonzero-noise rollbacks {len(rollback_noise)}")
    if not assets:
        lines.append("- no completed rows")
    return "\n".join(lines) + "\n"


def _latex(payload: dict[str, Any]) -> str:
    rows = payload["rows"]
    lines = [
        "\\begin{table}[t]",
        "\\centering",
        "\\caption{Extended robustness on bunny and warped cylinder. Drop is measured against $\\sigma=0$ for noise and four held-out views/lights for view/light sweeps.}",
        "\\label{tab:pg-robust-extended}",
        "\\begin{tabular}{llrrr}",
        "\\toprule",
        "Asset & Sweep & Level & PSNR & Drop \\\\",
        "\\midrule",
    ]
    for row in rows:
        asset = str(row["asset"]).replace("_", "\\_")
        lines.append(f"{asset} & {row['sweep']} & {_fmt(row['level'], 2)} & {_fmt(row['psnr'], 2)} & {_fmt(row['drop_vs_ref'], 2)} \\\\")
    if not rows:
        lines.append("\\multicolumn{5}{c}{No completed PG-enh3 rows.} \\\\")
    lines.extend(["\\bottomrule", "\\end{tabular}", "\\end{table}"])
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    output_root = ensure_dir(args.output_root)
    if not args.collect_only:
        for asset in _items(args.assets):
            for sweep in _items(args.sweeps):
                _run_command(args, asset, sweep)
    payload = _collect(output_root)
    atomic_write_json(output_root / "PG_ENH3_RESULTS.json", payload)
    write_text(output_root / "PG_ENH3_TABLE.md", _markdown(payload))
    write_text(output_root / "PG_ENH3_RESULTS.md", _results(payload))
    write_text(ROOT / "paper" / "tables" / "table8_robust_extended.tex", _latex(payload))
    print(str(output_root / "PG_ENH3_TABLE.md"))


if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""PG-enh1 real/public generated mesh transfer evaluation."""

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

from pbr_atlas.data.generated_mesh_loader import (  # noqa: E402
    DEFAULT_PG_ENH1_DATA_ROOT,
    prepare_real_generated_mesh_set,
    write_local_source_manifest,
)
from pbr_atlas.utils.io import atomic_write_json, ensure_dir, write_text  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run PG-enh1 real generated mesh evaluation.")
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--data-root", default=str(DEFAULT_PG_ENH1_DATA_ROOT))
    parser.add_argument("--output-root", default="/data/dip_1_ws/runs/PG_enh1_real_generated")
    parser.add_argument("--config", default="configs/B7_transfer.yaml")
    parser.add_argument("--source-manifest", default=None)
    parser.add_argument("--baseline", default="partuv")
    parser.add_argument("--method", default="all")
    parser.add_argument("--gpu", type=int, default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--no-lpips", action="store_true")
    parser.add_argument("--force-setup", action="store_true")
    parser.add_argument("--no-public-sources", dest="include_public_sources", action="store_false")
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--collect-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def _run_transfer(args: argparse.Namespace, asset_id: str, manifest: Path) -> None:
    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "run_B7_transfer.py"),
        "--asset",
        asset_id,
        "--baseline",
        args.baseline,
        "--method",
        args.method,
        "--config",
        args.config,
        "--output-root",
        args.output_root,
        "--data-root",
        args.data_root,
        "--manifest",
        str(manifest),
    ]
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


def _c5(metrics: dict[str, Any] | None) -> str:
    if not metrics:
        return "missing"
    if metrics.get("repro_status") == "failed":
        return "failed"
    c5 = metrics.get("c5", {})
    if c5.get("accept") is True:
        return "accept"
    if c5.get("rollback_to_baseline") is True:
        return "rollback"
    return str(metrics.get("repro_status") or "-")


def _collect(output_root: Path) -> dict[str, Any]:
    grouped: dict[str, dict[str, dict[str, Any]]] = {}
    for path in sorted(output_root.glob("*/metrics.json")):
        payload = _load_json(path)
        if not payload:
            continue
        asset = str(payload.get("generated_asset") or payload.get("asset") or path.parent.name)
        method = str(payload.get("method") or "-")
        grouped.setdefault(asset, {})[method] = payload

    rows: list[dict[str, Any]] = []
    for asset, methods in sorted(grouped.items()):
        ours = methods.get("ours")
        base = methods.get("baseline_only")
        source_record = ((ours or base or {}).get("generated_mesh") or {})
        base_psnr = ((base or {}).get("final") or {}).get("relit", {}).get("psnr")
        if base_psnr is None:
            base_psnr = ((ours or {}).get("initial") or {}).get("relit", {}).get("psnr")
        ours_psnr = ((ours or {}).get("final") or {}).get("relit", {}).get("psnr")
        base_num = _num(base_psnr)
        ours_num = _num(ours_psnr)
        delta = None if base_num is None or ours_num is None else ours_num - base_num
        rows.append(
            {
                "asset": asset,
                "source": source_record.get("source", "-"),
                "category": source_record.get("category", "-"),
                "source_status": source_record.get("status", "-"),
                "baseline_psnr": base_psnr,
                "ours_psnr": ours_psnr,
                "delta_psnr": delta,
                "c5": _c5(ours),
                "repro_status": (ours or base or {}).get("repro_status", "-"),
                "failure_reason": (ours or base or {}).get("failure_reason") or source_record.get("failure_reason") or "-",
                "mesh_path": source_record.get("mesh_path", "-"),
            }
        )
    accepts = sum(1 for row in rows if row["c5"] == "accept")
    return {"rows": rows, "accepts": accepts, "evaluated": len(rows), "trigger_rate": accepts / len(rows) if rows else None}


def _markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# PG-enh1 Real Generated Transfer Table",
        "",
        "| Asset | Source | Source Status | Baseline PSNR | Ours PSNR | dPSNR | C5 | Repro | Note |",
        "|---|---|---|---:|---:|---:|---|---|---|",
    ]
    for row in payload["rows"]:
        lines.append(
            "| {asset} | {source} | {status} | {base} | {ours} | {delta} | {c5} | {repro} | {note} |".format(
                asset=row["asset"],
                source=row["source"],
                status=row["source_status"],
                base=_fmt(row["baseline_psnr"]),
                ours=_fmt(row["ours_psnr"]),
                delta=_fmt(row["delta_psnr"]),
                c5=row["c5"],
                repro=row["repro_status"],
                note=row["failure_reason"],
            )
        )
    if not payload["rows"]:
        lines.append("| - | - | - | - | - | - | missing | - | no PG-enh1 runs found |")
    lines.extend(
        [
            "",
            f"- evaluated pairs: {payload['evaluated']}",
            f"- accept / trigger rate: {payload['accepts']}/{payload['evaluated']} ({_fmt(payload['trigger_rate'], 2)})",
        ]
    )
    return "\n".join(lines) + "\n"


def _results(payload: dict[str, Any]) -> str:
    rows = payload["rows"]
    real_rows = [row for row in rows if row["source_status"] == "ok"]
    fallback_rows = [row for row in rows if row["source_status"] != "ok"]
    lines = [
        "# PG-enh1 Real Generated Results",
        "",
        f"- completed rows: {len(rows)}",
        f"- public-source rows: {len(real_rows)}",
        f"- fallback rows: {len(fallback_rows)}",
        f"- accepted by C5: {payload['accepts']}/{payload['evaluated']}",
    ]
    return "\n".join(lines) + "\n"


def _latex(payload: dict[str, Any]) -> str:
    lines = [
        "\\begin{table}[t]",
        "\\centering",
        "\\caption{PG-enh1 generated/noisy transfer. Public-source download failures are not hidden; fallback rows are marked by source status.}",
        "\\label{tab:pg-real-generated}",
        "\\begin{tabular}{lrrrr}",
        "\\toprule",
        "Asset & Base PSNR & Ours PSNR & $\\Delta$PSNR & C5 \\\\",
        "\\midrule",
    ]
    for row in payload["rows"]:
        asset = str(row["asset"]).replace("_", "\\_")
        lines.append(f"{asset} & {_fmt(row['baseline_psnr'], 2)} & {_fmt(row['ours_psnr'], 2)} & {_fmt(row['delta_psnr'], 2)} & {row['c5']} \\\\")
    if not payload["rows"]:
        lines.append("\\multicolumn{5}{c}{No completed PG-enh1 rows.} \\\\")
    lines.extend(["\\bottomrule", "\\end{tabular}", "\\end{table}"])
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    data_root = ensure_dir(args.data_root)
    output_root = ensure_dir(args.output_root)
    if not args.collect_only:
        records = prepare_real_generated_mesh_set(
            data_root=data_root,
            target_count=args.count,
            manifest=args.source_manifest,
            include_public_sources=args.include_public_sources,
            force=args.force_setup,
        )
        local_manifest = write_local_source_manifest(data_root / "PG_ENH1_LOCAL_SOURCES.json", records)
        if args.prepare_only:
            print(str(local_manifest))
            return
        for record in records:
            _run_transfer(args, record.asset_id, local_manifest)
    payload = _collect(output_root)
    atomic_write_json(output_root / "PG_ENH1_RESULTS.json", payload)
    write_text(output_root / "PG_ENH1_TABLE.md", _markdown(payload))
    write_text(output_root / "PG_ENH1_RESULTS.md", _results(payload))
    write_text(ROOT / "paper" / "tables" / "table6_real_generated.tex", _latex(payload))
    print(str(output_root / "PG_ENH1_TABLE.md"))


if __name__ == "__main__":
    main()

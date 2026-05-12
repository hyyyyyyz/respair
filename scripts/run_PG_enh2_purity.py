#!/usr/bin/env python
"""PG-enh2 chart-part purity evaluation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pbr_atlas.baselines import create_backend  # noqa: E402
from pbr_atlas.data.generated_mesh_loader import default_asset_ids  # noqa: E402
from pbr_atlas.data.mesh_loader import load_mesh  # noqa: E402
from pbr_atlas.eval.chart_purity import (  # noqa: E402
    load_chart_ids,
    part_ids_from_hierarchy,
    summarize_chart_part_overlap,
)
from pbr_atlas.utils.io import atomic_write_json, ensure_dir, save_npz, write_text  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run PG-enh2 chart-part purity evaluation.")
    parser.add_argument("--b3-root", default="runs/B3_main")
    parser.add_argument("--b7-root", default="runs/B7_transfer")
    parser.add_argument("--output-root", default="runs/PG_enh2_purity")
    parser.add_argument("--paper-table", default="paper/tables/table7_purity.tex")
    parser.add_argument("--atlas-size", type=int, default=1024)
    parser.add_argument("--padding", type=int, default=4)
    parser.add_argument("--assets", default="spot,bunny,objaverse")
    parser.add_argument("--generated-assets", default=",".join(default_asset_ids()[:8]))
    parser.add_argument("--include-generated", action="store_true", default=True)
    parser.add_argument("--no-generated", dest="include_generated", action="store_false")
    return parser.parse_args()


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _atlas_path(run_dir: Path, name: str) -> Path | None:
    path = run_dir / name
    return path if path.exists() else None


def _run_dir(root: Path, run_id: str) -> Path:
    return root / run_id


def _reference_part_ids(partuv_run: Path) -> tuple[np.ndarray, str]:
    partuv_initial = _atlas_path(partuv_run, "initial_atlas.npz")
    if partuv_initial is None:
        raise FileNotFoundError(partuv_run / "initial_atlas.npz")
    chart_ids = load_chart_ids(partuv_initial)
    for name in ("hierarchy.json", "partuv_hierarchy.json", "leaf_hierarchy.json"):
        candidate = partuv_run / name
        if candidate.exists():
            return part_ids_from_hierarchy(candidate, int(chart_ids.shape[0])), str(candidate)
    return chart_ids, "partuv_chart_proxy"


def _summarize(label: str, chart_path: Path, part_ids: np.ndarray) -> dict[str, Any]:
    chart_ids = load_chart_ids(chart_path)
    summary = summarize_chart_part_overlap(chart_ids, part_ids)
    summary["label"] = label
    summary["atlas_path"] = str(chart_path)
    return summary


def _compute_xatlas_for_mesh(asset_id: str, mesh_path: str, output_root: Path, *, atlas_size: int, padding: int) -> Path:
    target = output_root / "xatlas_cache" / f"{asset_id}_xatlas.npz"
    if target.exists():
        return target
    mesh = load_mesh(mesh_path)
    atlas = create_backend("xatlas_classical", {}).generate(mesh, atlas_size, padding)
    if atlas.repro_status == "failed":
        raise RuntimeError(atlas.failure_reason or "xatlas failed")
    save_npz(target, uv=atlas.uv, face_uv=atlas.face_uv, chart_ids=atlas.chart_ids)
    return target


def _b3_case(asset: str, b3_root: Path) -> dict[str, Path]:
    return {
        "partuv_run": _run_dir(b3_root, f"{asset}_partuv_ours_seed42"),
        "xatlas_initial": _run_dir(b3_root, f"{asset}_xatlas_classical_ours_seed42") / "initial_atlas.npz",
        "partuv_initial": _run_dir(b3_root, f"{asset}_partuv_ours_seed42") / "initial_atlas.npz",
        "ours_final": _run_dir(b3_root, f"{asset}_partuv_ours_seed42") / "atlas.npz",
    }


def _generated_case(asset: str, b7_root: Path, output_root: Path, *, atlas_size: int, padding: int) -> dict[str, Path]:
    run = _run_dir(b7_root, f"{asset}_partuv_ours_seed42")
    metrics = _load_json(run / "metrics.json") or {}
    mesh_path = str(metrics.get("mesh_path") or "")
    if not mesh_path:
        raise FileNotFoundError(f"missing mesh_path in {run / 'metrics.json'}")
    return {
        "partuv_run": run,
        "xatlas_initial": _compute_xatlas_for_mesh(asset, mesh_path, output_root, atlas_size=atlas_size, padding=padding),
        "partuv_initial": run / "initial_atlas.npz",
        "ours_final": run / "atlas.npz",
    }


def _case_row(asset: str, source_group: str, paths: dict[str, Path]) -> dict[str, Any]:
    part_ids, part_source = _reference_part_ids(paths["partuv_run"])
    required = ["xatlas_initial", "partuv_initial", "ours_final"]
    missing = [str(paths[name]) for name in required if not paths[name].exists()]
    if missing:
        return {
            "asset": asset,
            "source_group": source_group,
            "status": "missing",
            "missing": missing,
            "part_source": part_source,
        }
    xatlas = _summarize("xatlas", paths["xatlas_initial"], part_ids)
    partuv = _summarize("partuv", paths["partuv_initial"], part_ids)
    ours = _summarize("ours_after_repair", paths["ours_final"], part_ids)
    return {
        "asset": asset,
        "source_group": source_group,
        "status": "ok",
        "part_source": part_source,
        "face_count": int(part_ids.shape[0]),
        "xatlas": xatlas,
        "partuv": partuv,
        "ours_after_repair": ours,
        "delta_ours_vs_partuv": float(ours["purity_mean"] - partuv["purity_mean"]),
        "delta_partuv_vs_xatlas": float(partuv["purity_mean"] - xatlas["purity_mean"]),
    }


def _fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return "-"
    try:
        return f"{float(value):.{digits}f}"
    except Exception:
        return "-"


def _markdown(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# PG-enh2 Chart-Part Purity",
        "",
        "| Asset | Group | Part Source | Faces | xatlas Purity | PartUV Purity | Ours Purity | xatlas Entropy | Ours- PartUV | Status |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        if row.get("status") != "ok":
            lines.append(
                f"| {row.get('asset')} | {row.get('source_group')} | {row.get('part_source', '-')} | - | - | - | - | - | - | missing: {row.get('missing', [])} |"
            )
            continue
        lines.append(
            "| {asset} | {group} | {part_source} | {faces} | {xpur} | {ppur} | {opur} | {xent} | {delta} | ok |".format(
                asset=row["asset"],
                group=row["source_group"],
                part_source=row["part_source"],
                faces=row["face_count"],
                xpur=_fmt(row["xatlas"]["purity_mean"]),
                ppur=_fmt(row["partuv"]["purity_mean"]),
                opur=_fmt(row["ours_after_repair"]["purity_mean"]),
                xent=_fmt(row["xatlas"]["entropy_mean"]),
                delta=_fmt(row["delta_ours_vs_partuv"], 4),
            )
        )
    return "\n".join(lines) + "\n"


def _latex(rows: list[dict[str, Any]]) -> str:
    ok_rows = [row for row in rows if row.get("status") == "ok"]
    lines = [
        "\\begin{table}[t]",
        "\\centering",
        "\\scriptsize",
        "\\caption{Chart--part purity using PartUV leaf charts as the reference partition. Higher purity and lower entropy indicate better preservation of part structure.}",
        "\\label{tab:pg-purity}",
        "\\begin{tabular}{@{}lcccc@{}}",
        "\\toprule",
        "Asset & xatlas & PartUV & Ours & xatlas ent. \\\\",
        "\\midrule",
    ]
    for row in ok_rows:
        label = str(row["asset"]).replace("_", "\\_")
        lines.append(
            f"{label} & {_fmt(row['xatlas']['purity_mean'], 2)} & {_fmt(row['partuv']['purity_mean'], 2)} & "
            f"{_fmt(row['ours_after_repair']['purity_mean'], 2)} & {_fmt(row['xatlas']['entropy_mean'], 2)} \\\\"
        )
    if not ok_rows:
        lines.append("\\multicolumn{5}{c}{No completed PG-enh2 rows.} \\\\")
    lines.extend(["\\bottomrule", "\\end{tabular}", "\\end{table}"])
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    b3_root = Path(args.b3_root)
    b7_root = Path(args.b7_root)
    output_root = ensure_dir(args.output_root)
    rows: list[dict[str, Any]] = []

    for asset in [item.strip() for item in args.assets.split(",") if item.strip()]:
        try:
            rows.append(_case_row(asset, "B3_anchor", _b3_case(asset, b3_root)))
        except Exception as exc:
            rows.append({"asset": asset, "source_group": "B3_anchor", "status": "failed", "missing": [str(exc)]})

    if args.include_generated:
        for asset in [item.strip() for item in args.generated_assets.split(",") if item.strip()]:
            try:
                paths = _generated_case(asset, b7_root, output_root, atlas_size=args.atlas_size, padding=args.padding)
                rows.append(_case_row(asset, "B7_procedural", paths))
            except Exception as exc:
                rows.append({"asset": asset, "source_group": "B7_procedural", "status": "failed", "missing": [str(exc)]})

    write_text(output_root / "PURITY_TABLE.md", _markdown(rows))
    atomic_write_json(output_root / "purity_metrics.json", {"rows": rows})
    write_text(args.paper_table, _latex(rows))
    print(str(output_root / "PURITY_TABLE.md"))


if __name__ == "__main__":
    main()

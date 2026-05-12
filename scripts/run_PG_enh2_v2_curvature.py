#!/usr/bin/env python
"""PG-enh2-v2 chart-boundary curvature editability evaluation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pbr_atlas.baselines import create_backend  # noqa: E402
from pbr_atlas.data import prepare_asset  # noqa: E402
from pbr_atlas.data.mesh_loader import load_mesh  # noqa: E402
from pbr_atlas.eval.chart_curvature import summarize_atlas_file  # noqa: E402
from pbr_atlas.utils.io import atomic_write_json, ensure_dir, save_npz, write_text  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run chart-boundary curvature alignment evaluation.")
    parser.add_argument("--b3-root", default="runs/B3_main")
    parser.add_argument("--real-root", default="runs/PG_enh1_real_v2")
    parser.add_argument("--output-root", default="runs/PG_enh2_v2_curvature")
    parser.add_argument("--paper-table", default="paper/tables/table10_curvature.tex")
    parser.add_argument("--data-root", default=None)
    parser.add_argument("--assets", default="spot,bunny,objaverse,ts_animal")
    parser.add_argument("--atlas-size", type=int, default=1024)
    parser.add_argument("--padding", type=int, default=8)
    parser.add_argument("--high-percentile", type=float, default=85.0)
    parser.add_argument("--min-threshold-degrees", type=float, default=10.0)
    return parser.parse_args()


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _find_runs(asset: str, roots: list[Path], *, baseline: str = "partuv", method: str = "ours") -> list[Path]:
    runs: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        patterns = [f"{asset}_{baseline}_{method}_seed*"]
        for pattern in patterns:
            runs.extend(path for path in root.glob(pattern) if path.is_dir())
    return sorted(dict.fromkeys(runs))


def _first_existing(paths: list[Path]) -> Path | None:
    for path in paths:
        if path.exists():
            return path
    return None


def _mesh_path_for_asset(asset: str, runs: list[Path], data_root: Path | None) -> Path:
    for run in runs:
        metrics = _load_json(run / "metrics.json") or {}
        candidates = [
            metrics.get("mesh_path"),
            (metrics.get("generated_mesh") or {}).get("mesh_path") if isinstance(metrics.get("generated_mesh"), dict) else None,
        ]
        for candidate in candidates:
            if candidate and Path(str(candidate)).exists():
                return Path(str(candidate))
    if asset in {"spot", "bunny", "objaverse", "objaverse_sample"}:
        return prepare_asset(asset, data_root=data_root or Path("datasets/sample"), offline_ok=True)
    raise FileNotFoundError(f"Could not resolve mesh path for {asset}; checked {len(runs)} run dirs")


def _compute_xatlas(asset: str, mesh_path: Path, output_root: Path, *, atlas_size: int, padding: int) -> Path:
    target = output_root / "xatlas_cache" / f"{asset}_xatlas.npz"
    if target.exists():
        return target
    mesh = load_mesh(mesh_path)
    atlas = create_backend("xatlas_classical", {}).generate(mesh, atlas_size, padding)
    if atlas.repro_status == "failed":
        raise RuntimeError(atlas.failure_reason or f"xatlas failed for {asset}")
    save_npz(target, uv=atlas.uv, face_uv=atlas.face_uv, chart_ids=atlas.chart_ids)
    return target


def _atlas_paths(asset: str, b3_root: Path, roots: list[Path], output_root: Path, mesh_path: Path, *, atlas_size: int, padding: int) -> dict[str, list[Path]]:
    partuv_runs = _find_runs(asset, roots, baseline="partuv", method="ours")
    xatlas_runs = _find_runs(asset, [b3_root], baseline="xatlas_classical", method="ours")
    xatlas_paths = [run / "initial_atlas.npz" for run in xatlas_runs if (run / "initial_atlas.npz").exists()]
    if not xatlas_paths:
        xatlas_paths = [_compute_xatlas(asset, mesh_path, output_root, atlas_size=atlas_size, padding=padding)]
    return {
        "xatlas": xatlas_paths,
        "partuv": [run / "initial_atlas.npz" for run in partuv_runs if (run / "initial_atlas.npz").exists()],
        "ours": [run / "atlas.npz" for run in partuv_runs if (run / "atlas.npz").exists()],
    }


def _mean_std(values: list[float]) -> tuple[float | None, float | None]:
    if not values:
        return None, None
    mean = sum(values) / len(values)
    var = sum((value - mean) ** 2 for value in values) / len(values)
    return mean, var**0.5


def _summarize_label(asset: str, label: str, mesh_path: Path, atlas_paths: list[Path], args: argparse.Namespace) -> dict[str, Any]:
    if not atlas_paths:
        return {"asset": asset, "label": label, "status": "missing", "runs": []}
    mesh = load_mesh(mesh_path)
    runs = []
    for path in atlas_paths:
        try:
            summary = summarize_atlas_file(
                mesh,
                path,
                atlas_size=args.atlas_size,
                padding=args.padding,
                high_percentile=args.high_percentile,
                min_threshold_degrees=args.min_threshold_degrees,
            )
            summary.update({"status": "ok", "atlas_path": str(path)})
        except Exception as exc:
            summary = {"status": "failed", "atlas_path": str(path), "error": str(exc)}
        runs.append(summary)
    ok = [item for item in runs if item.get("status") == "ok"]
    ious = [float(item["curvature_iou"]) for item in ok]
    precs = [float(item["curvature_precision"]) for item in ok]
    recalls = [float(item["curvature_recall"]) for item in ok]
    boundary_angles = [float(item["mean_boundary_dihedral_degrees"]) for item in ok]
    iou_mean, iou_std = _mean_std(ious)
    prec_mean, prec_std = _mean_std(precs)
    recall_mean, recall_std = _mean_std(recalls)
    angle_mean, angle_std = _mean_std(boundary_angles)
    return {
        "asset": asset,
        "label": label,
        "status": "ok" if ok else "failed",
        "run_count": len(ok),
        "curvature_iou_mean": iou_mean,
        "curvature_iou_std": iou_std,
        "curvature_precision_mean": prec_mean,
        "curvature_precision_std": prec_std,
        "curvature_recall_mean": recall_mean,
        "curvature_recall_std": recall_std,
        "boundary_dihedral_mean": angle_mean,
        "boundary_dihedral_std": angle_std,
        "runs": runs,
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
        "# PG-enh2-v2 Chart Curvature Alignment",
        "",
        "| Asset | xatlas IoU | PartUV IoU | Ours IoU | xatlas Prec | PartUV Prec | Ours Prec | Ours n |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    by_asset: dict[str, dict[str, dict[str, Any]]] = {}
    for row in rows:
        by_asset.setdefault(str(row["asset"]), {})[str(row["label"])] = row
    for asset, labels in sorted(by_asset.items()):
        xatlas = labels.get("xatlas", {})
        partuv = labels.get("partuv", {})
        ours = labels.get("ours", {})
        lines.append(
            "| {asset} | {xiou} | {piou} | {oiou} | {xprec} | {pprec} | {oprec} | {n} |".format(
                asset=asset,
                xiou=_fmt(xatlas.get("curvature_iou_mean")),
                piou=_fmt(partuv.get("curvature_iou_mean")),
                oiou=_fmt(ours.get("curvature_iou_mean")),
                xprec=_fmt(xatlas.get("curvature_precision_mean")),
                pprec=_fmt(partuv.get("curvature_precision_mean")),
                oprec=_fmt(ours.get("curvature_precision_mean")),
                n=ours.get("run_count", 0),
            )
        )
    return "\n".join(lines) + "\n"


def _latex(rows: list[dict[str, Any]]) -> str:
    by_asset: dict[str, dict[str, dict[str, Any]]] = {}
    for row in rows:
        by_asset.setdefault(str(row["asset"]), {})[str(row["label"])] = row
    lines = [
        "\\begin{table}[t]",
        "\\centering",
        "\\scriptsize",
        "\\caption{Partition-independent chart-boundary curvature alignment. High-curvature edges are defined from mesh dihedral angles, not from PartUV labels. Higher IoU/precision means chart seams better coincide with geometry-defined part-like boundaries.}",
        "\\label{tab:curvature_alignment}",
        "\\begin{tabular}{@{}lrrrr@{}}",
        "\\toprule",
        "Asset & xatlas IoU & PartUV IoU & Ours IoU & Ours precision \\\\",
        "\\midrule",
    ]
    for asset, labels in sorted(by_asset.items()):
        xatlas = labels.get("xatlas", {})
        partuv = labels.get("partuv", {})
        ours = labels.get("ours", {})
        asset_label = asset.replace("_", "\\_")
        x_iou = _fmt(xatlas.get('curvature_iou_mean'), 2)
        p_iou = _fmt(partuv.get('curvature_iou_mean'), 2)
        o_iou = _fmt(ours.get('curvature_iou_mean'), 2)
        o_prec = _fmt(ours.get('curvature_precision_mean'), 2)
        lines.append(
            f"{asset_label} & {x_iou} & {p_iou} & {o_iou} & {o_prec} \\\\"
        )
    if not by_asset:
        lines.append("\\multicolumn{5}{c}{No completed curvature rows.} \\\\")
    lines.extend(["\\bottomrule", "\\end{tabular}", "\\end{table}"])
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    b3_root = Path(args.b3_root)
    real_root = Path(args.real_root)
    output_root = ensure_dir(args.output_root)
    data_root = Path(args.data_root) if args.data_root else None
    roots = [b3_root, real_root]
    rows: list[dict[str, Any]] = []
    for asset in [item.strip() for item in args.assets.split(",") if item.strip()]:
        runs = _find_runs(asset, roots, baseline="partuv", method="ours") + _find_runs(
            asset, [b3_root], baseline="xatlas_classical", method="ours"
        )
        try:
            mesh_path = _mesh_path_for_asset(asset, runs, data_root)
            paths = _atlas_paths(
                asset,
                b3_root,
                roots,
                output_root,
                mesh_path,
                atlas_size=args.atlas_size,
                padding=args.padding,
            )
            for label in ("xatlas", "partuv", "ours"):
                rows.append(_summarize_label(asset, label, mesh_path, paths[label], args))
        except Exception as exc:
            rows.append({"asset": asset, "label": "all", "status": "failed", "error": str(exc), "runs": []})
    write_text(output_root / "CURVATURE_TABLE.md", _markdown(rows))
    atomic_write_json(output_root / "curvature_metrics.json", {"rows": rows})
    write_text(args.paper_table, _latex(rows))
    print(str(output_root / "CURVATURE_TABLE.md"))


if __name__ == "__main__":
    main()

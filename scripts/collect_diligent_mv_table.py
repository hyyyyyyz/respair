#!/usr/bin/env python
"""Aggregate DiLiGenT-MV W1 runs into a captured-target table with bootstrap CIs.

For each (object, baseline, method) cell, collect across split seeds:
- mean ± std PSNR
- 95% bootstrap CI on the mean
- accept count / n_seeds
- mean wall-clock

Output: paper-ready table12_diligent_main.tex + JSON dump for downstream stats.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Iterable

import numpy as np


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--root", default="runs/W1_diligent_mv")
    p.add_argument("--objects", default="bear,cow,pot2,buddha,reading")
    p.add_argument("--baselines", default="xatlas_classical,blender_uv,partuv")
    p.add_argument("--methods", default="baseline_only,ours")
    p.add_argument("--seeds", default="0,1,2,3,4")
    p.add_argument("--bootstrap-iters", type=int, default=2000)
    p.add_argument("--out-tex", default="paper/tables/table13_diligent_mv.tex")
    p.add_argument("--out-md", default="DILIGENT_MV_SUMMARY.md")
    p.add_argument("--out-json", default="runs/W1_diligent_mv/diligent_mv_metrics.json")
    return p.parse_args()


def _bootstrap_mean_ci(values: np.ndarray, *, n_iter: int, seed: int = 0, alpha: float = 0.05) -> tuple[float, float]:
    if len(values) == 0:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    n = len(values)
    means = np.empty(n_iter, dtype=np.float64)
    for k in range(n_iter):
        idx = rng.integers(0, n, n)
        means[k] = float(values[idx].mean())
    return float(np.percentile(means, 100 * alpha / 2)), float(np.percentile(means, 100 * (1 - alpha / 2)))


def _load_seed(root: Path, asset: str, baseline: str, method: str, seed: int) -> dict | None:
    run_id = f"{asset}_{baseline}_{method}_split{seed}_seed{seed}"
    path = root / run_id / "metrics.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())


def _collect_cell(root: Path, asset: str, baseline: str, method: str, seeds: Iterable[int]) -> dict:
    init_psnrs: list[float] = []
    final_psnrs: list[float] = []
    accepts = 0
    walls: list[float] = []
    rows: list[dict] = []
    for s in seeds:
        d = _load_seed(root, asset, baseline, method, s)
        if d is None:
            rows.append({"seed": s, "status": "missing"})
            continue
        ip = d.get("initial", {}).get("relit", {}).get("psnr")
        fp = d.get("final", {}).get("relit", {}).get("psnr")
        rb = bool(d.get("rolled_back", True))
        if ip is None or fp is None:
            rows.append({"seed": s, "status": "incomplete"})
            continue
        init_psnrs.append(float(ip))
        final_psnrs.append(float(fp))
        if not rb:
            accepts += 1
        walls.append(float(d.get("wall_clock_s", 0.0)))
        rows.append({"seed": s, "status": "ok", "init": ip, "final": fp, "rolled_back": rb, "wall_s": walls[-1]})

    if init_psnrs:
        deltas = np.array(final_psnrs) - np.array(init_psnrs)
        ip_arr = np.array(init_psnrs)
        fp_arr = np.array(final_psnrs)
        ci_lo, ci_hi = _bootstrap_mean_ci(deltas, n_iter=2000, seed=hash((asset, baseline, method)) & 0xffff)
    else:
        deltas = np.array([])
        ip_arr = np.array([])
        fp_arr = np.array([])
        ci_lo, ci_hi = float("nan"), float("nan")

    return {
        "asset": asset,
        "baseline": baseline,
        "method": method,
        "n": len(init_psnrs),
        "init_mean": float(ip_arr.mean()) if ip_arr.size else float("nan"),
        "init_std": float(ip_arr.std(ddof=0)) if ip_arr.size else float("nan"),
        "final_mean": float(fp_arr.mean()) if fp_arr.size else float("nan"),
        "final_std": float(fp_arr.std(ddof=0)) if fp_arr.size else float("nan"),
        "delta_mean": float(deltas.mean()) if deltas.size else float("nan"),
        "delta_ci95_lo": ci_lo,
        "delta_ci95_hi": ci_hi,
        "accepts": accepts,
        "wall_mean_s": float(np.mean(walls)) if walls else 0.0,
        "rows": rows,
    }


def _fmt(v: float, digits: int = 2) -> str:
    if math.isnan(v):
        return "-"
    return f"{v:.{digits}f}"


def _latex(rows: list[dict]) -> str:
    lines = [
        "\\begin{table*}[t]",
        "\\centering",
        "\\scriptsize",
        "\\caption{DiLiGenT-MV captured-target evaluation. Five objects $\\times$ baselines $\\times$ method, $n$ split seeds. PSNR is on the held-out test split (disjoint from proposal/gate). Mean $\\pm$ std reported with 95\\% bootstrap CI on $\\Delta$.}",
        "\\label{tab:diligent_mv}",
        "\\begin{tabular}{@{}llrrrrl@{}}",
        "\\toprule",
        "Asset & Baseline / method & n & Init PSNR & Final PSNR & $\\Delta$ (95\\% CI) & Accept \\\\",
        "\\midrule",
    ]
    by_asset: dict[str, list[dict]] = {}
    for r in rows:
        by_asset.setdefault(r["asset"], []).append(r)
    for asset, cells in sorted(by_asset.items()):
        for cell in cells:
            label = f"{cell['baseline'].replace('_classical','')} / {cell['method']}"
            label = label.replace("_", "\\_")
            init = f"{_fmt(cell['init_mean'])}$\\pm${_fmt(cell['init_std'])}" if cell["n"] else "-"
            final = f"{_fmt(cell['final_mean'])}$\\pm${_fmt(cell['final_std'])}" if cell["n"] else "-"
            delta = f"{_fmt(cell['delta_mean'])} [{_fmt(cell['delta_ci95_lo'])}, {_fmt(cell['delta_ci95_hi'])}]" if cell["n"] else "-"
            asset_label = asset.replace("_", "\\_")
            lines.append(f"{asset_label} & {label} & {cell['n']} & {init} & {final} & {delta} & {cell['accepts']}/{cell['n']} \\\\")
    lines.extend(["\\bottomrule", "\\end{tabular}", "\\end{table*}", ""])
    return "\n".join(lines)


def _markdown(rows: list[dict]) -> str:
    lines = [
        "# DiLiGenT-MV captured-target results",
        "",
        "| Asset | Baseline | Method | n | Init | Final | Δ (CI95) | Accept | Wall (s) |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        init = f"{_fmt(r['init_mean'])}±{_fmt(r['init_std'])}" if r["n"] else "-"
        final = f"{_fmt(r['final_mean'])}±{_fmt(r['final_std'])}" if r["n"] else "-"
        delta = f"{_fmt(r['delta_mean'])} [{_fmt(r['delta_ci95_lo'])}, {_fmt(r['delta_ci95_hi'])}]" if r["n"] else "-"
        lines.append(f"| {r['asset']} | {r['baseline']} | {r['method']} | {r['n']} | {init} | {final} | {delta} | {r['accepts']}/{r['n']} | {_fmt(r['wall_mean_s'], 0)} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    root = Path(args.root)
    assets = [a.strip() for a in args.objects.split(",") if a.strip()]
    baselines = [b.strip() for b in args.baselines.split(",") if b.strip()]
    methods = [m.strip() for m in args.methods.split(",") if m.strip()]
    seeds = [int(s) for s in args.seeds.split(",") if s.strip()]
    rows = []
    for asset in assets:
        for bl in baselines:
            for m in methods:
                rows.append(_collect_cell(root, asset, bl, m, seeds))
    Path(args.out_md).write_text(_markdown(rows))
    Path(args.out_tex).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out_tex).write_text(_latex(rows))
    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out_json).write_text(json.dumps({"rows": rows}, indent=2))
    print(f"Wrote {args.out_md} / {args.out_tex} / {args.out_json}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Aggregate A1 multi-seed B3 split runs into mean ± std summary."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Iterable


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--root", default="/data/dip_1_ws/runs/A1_split")
    p.add_argument("--cases", default="spot:xatlas_classical,spot:partuv,bunny:partuv,objaverse:xatlas_classical,ts_animal:partuv")
    p.add_argument("--seeds", default="42,1234,9999")
    p.add_argument("--out-tex", default="paper/tables/table11_a1_split.tex")
    p.add_argument("--out-md", default="A1_SPLIT_SUMMARY.md")
    return p.parse_args()


def _mean_std(xs: list[float]) -> tuple[float, float]:
    n = len(xs)
    if n == 0:
        return float("nan"), float("nan")
    mu = sum(xs) / n
    var = sum((x - mu) ** 2 for x in xs) / n
    return mu, math.sqrt(var)


def _fmt(mu: float, sigma: float, digits: int = 2) -> str:
    if math.isnan(mu):
        return "-"
    return f"{mu:.{digits}f}$\\pm${sigma:.{digits}f}"


def _label_for(asset: str, baseline: str) -> str:
    pretty_asset = asset.replace("_", "\\_")
    pretty_base = {"xatlas_classical": "xatlas", "partuv": "PartUV"}.get(baseline, baseline)
    return f"{pretty_asset} & {pretty_base}"


def _collect(root: Path, asset: str, baseline: str, seeds: Iterable[int]) -> dict:
    initial, final, deltas, verdicts = [], [], [], []
    rows = []
    for seed in seeds:
        run_id = f"{asset}_{baseline}_ours_split{seed}"
        m_path = root / run_id / "metrics.json"
        if not m_path.exists():
            rows.append({"seed": seed, "status": "missing", "path": str(m_path)})
            continue
        m = json.loads(m_path.read_text())
        ip = m.get("initial", {}).get("relit", {}).get("psnr")
        fp = m.get("final", {}).get("relit", {}).get("psnr")
        c5 = m.get("c5") or {}
        v = "accept" if c5.get("accept") else "rollback"
        if ip is None or fp is None:
            rows.append({"seed": seed, "status": "incomplete"})
            continue
        initial.append(float(ip))
        final.append(float(fp))
        deltas.append(float(fp) - float(ip))
        verdicts.append(v)
        rows.append({"seed": seed, "init": ip, "final": fp, "delta": fp - ip, "c5": v})
    accept_n = sum(1 for v in verdicts if v == "accept")
    return {
        "asset": asset,
        "baseline": baseline,
        "n_runs": len(initial),
        "init": _mean_std(initial),
        "final": _mean_std(final),
        "delta": _mean_std(deltas),
        "accept_count": accept_n,
        "verdicts": verdicts,
        "rows": rows,
    }


def main() -> None:
    args = parse_args()
    root = Path(args.root)
    cases = [tuple(c.split(":")) for c in args.cases.split(",") if c.strip()]
    seeds = [int(s) for s in args.seeds.split(",") if s.strip()]
    summaries = [_collect(root, a, b, seeds) for a, b in cases]

    md = ["# A1 Split-Seed Summary", "",
          "| Asset | Baseline | n | Init PSNR | Final PSNR | $\\Delta$Final | Accept rate |",
          "|---|---|---:|---:|---:|---:|---:|"]
    for s in summaries:
        md.append(
            f"| {s['asset']} | {s['baseline']} | {s['n_runs']} "
            f"| {_fmt(*s['init'])} | {_fmt(*s['final'])} | {_fmt(*s['delta'])} "
            f"| {s['accept_count']}/{s['n_runs']} |"
        )
    Path(args.out_md).write_text("\n".join(md) + "\n")

    tex = [
        "\\begin{table}[t]",
        "\\centering",
        "\\scriptsize",
        "\\caption{A1 structural rerun: proposal/gate/test 3-split with multi-seed (n=" + str(len(seeds)) + "). Headline PSNR is on the held-out test split only; candidate search and C5 use disjoint splits. PSNR is mean$\\pm$std over split seeds.}",
        "\\label{tab:a1_split}",
        "\\begin{tabular}{@{}llrrrrl@{}}",
        "\\toprule",
        "Asset & Baseline & n & Init PSNR & Final PSNR & $\\Delta$Final & Accept \\\\",
        "\\midrule",
    ]
    for s in summaries:
        if s["n_runs"] == 0:
            tex.append(f"{_label_for(s['asset'], s['baseline'])} & 0 & - & - & - & - \\\\")
            continue
        delta_mu = s['delta'][0]
        sign = "\\textbf{" if delta_mu > 0.5 else ""
        close = "}" if delta_mu > 0.5 else ""
        tex.append(
            f"{_label_for(s['asset'], s['baseline'])} & {s['n_runs']} "
            f"& {_fmt(*s['init'])} & {_fmt(*s['final'])} "
            f"& {sign}{_fmt(*s['delta'])}{close} "
            f"& {s['accept_count']}/{s['n_runs']} \\\\"
        )
    tex.extend(["\\bottomrule", "\\end{tabular}", "\\end{table}", ""])
    Path(args.out_tex).write_text("\n".join(tex))

    print("Wrote", args.out_md, "and", args.out_tex)
    for s in summaries:
        print(f"  {s['asset']}/{s['baseline']}: n={s['n_runs']} init={_fmt(*s['init'])} final={_fmt(*s['final'])} accept={s['accept_count']}/{s['n_runs']}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""Run B1 twice with the same seed and compare e_f / E_c / G_l."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="B1 metric determinism check.")
    parser.add_argument("--asset", default="bunny", choices=["bunny", "spot", "objaverse", "objaverse_sample"])
    parser.add_argument("--gpu", type=int, default=None)
    parser.add_argument("--config", default="configs/B1_sanity.yaml")
    parser.add_argument("--output-root", default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--tolerance", type=float, default=1.0e-4)
    parser.add_argument("--keep-lpips", action="store_true", help="Do not skip LPIPS during determinism runs.")
    return parser.parse_args()


def load_config(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _run_once(args: argparse.Namespace, run_id: str, output_root: Path) -> Path:
    cmd = [
        sys.executable,
        str(Path(__file__).with_name("run_B1.py")),
        "--asset",
        args.asset,
        "--config",
        args.config,
        "--output-root",
        str(output_root),
        "--run-id",
        run_id,
    ]
    if args.gpu is not None:
        cmd.extend(["--gpu", str(args.gpu)])
    if args.seed is not None:
        cmd.extend(["--seed", str(args.seed)])
    if not args.keep_lpips:
        cmd.append("--no-lpips")
    env = os.environ.copy()
    subprocess.run(cmd, check=True, env=env)
    return output_root / run_id / "metrics.json"


def _load_field(path: Path, name: str) -> np.ndarray:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return np.asarray(payload["residual_stats"][name], dtype=np.float64)


def _max_abs_diff(path_a: Path, path_b: Path, name: str) -> float:
    a = _load_field(path_a, name)
    b = _load_field(path_b, name)
    if a.shape != b.shape:
        return float("inf")
    if a.size == 0:
        return 0.0
    return float(np.max(np.abs(a - b)))


def main() -> None:
    args = parse_args()
    cfg = load_config(args.config)
    output_root = Path(args.output_root or cfg.get("output_root", "/data/dip_1_ws/runs/B1_sanity"))
    seed = int(args.seed if args.seed is not None else cfg.get("seed", 42))
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_a = f"determinism_{stamp}_{args.asset}_seed{seed}_a"
    run_b = f"determinism_{stamp}_{args.asset}_seed{seed}_b"
    path_a = _run_once(args, run_a, output_root)
    path_b = _run_once(args, run_b, output_root)
    diffs = {
        "e_f": _max_abs_diff(path_a, path_b, "e_f"),
        "E_c": _max_abs_diff(path_a, path_b, "E_c"),
        "G_l": _max_abs_diff(path_a, path_b, "G_l"),
    }
    passed = all(value <= args.tolerance for value in diffs.values())
    report = {
        "asset": args.asset,
        "seed": seed,
        "tolerance": args.tolerance,
        "passed": passed,
        "diffs": diffs,
        "run_a": str(path_a.parent),
        "run_b": str(path_b.parent),
    }
    output_root.mkdir(parents=True, exist_ok=True)
    report_path = output_root / f"determinism_{stamp}_{args.asset}_seed{seed}.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    if not passed:
        raise SystemExit(f"Determinism check failed: {diffs}")
    print(f"PASS {json.dumps(diffs, sort_keys=True)}")


if __name__ == "__main__":
    main()


#!/usr/bin/env python
"""Run B5 strict matched-control experiments through the B3 pipeline."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pbr_atlas.ablations.b5_strict_matched import (
    B5_CONDITIONS,
    annotate_metrics,
    make_layout_preserving_repack,
    normalize_condition_id,
    patch_c5_guard,
    patch_config,
)
from pbr_atlas.ablations.common import deep_merge, load_npz_atlas, sync_matched_atlas_size
from pbr_atlas.utils.io import atomic_write_json, write_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run B5 strict matched-control experiments.")
    parser.add_argument("--condition", default=None, help="B5.1..B5.5, B5_1..B5_5, or 1..5.")
    parser.add_argument("--asset", default=None, choices=["spot", "bunny"])
    parser.add_argument("--baseline", default="partuv", choices=["partuv"])
    parser.add_argument("--config", default=None)
    parser.add_argument("--baseline-run", default=None, help="B3 run dir containing initial_atlas.npz.")
    parser.add_argument("--gpu", type=int, default=None)
    parser.add_argument("--output-root", default=None)
    parser.add_argument("--data-root", default=None)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--no-lpips", action="store_true")
    parser.add_argument("--all", action="store_true", help="Run spot+bunny for all five B5 conditions.")
    parser.add_argument("--collect", action="store_true", help="Collect B5_TABLE.md after running.")
    return parser.parse_args()


def _load_yaml(path: str | Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_config(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    payload = _load_yaml(path)
    parent = payload.pop("inherits", None)
    if parent:
        parent_path = (path.parent / parent).resolve()
        payload = deep_merge(load_config(parent_path), payload)
    return payload


def _condition_config_path(condition_id: str) -> Path:
    suffix = condition_id.split(".")[1]
    return ROOT / "configs" / "B5" / f"B5_{suffix}.yaml"


def _find_baseline_run(args: argparse.Namespace, cfg: dict[str, Any], seed: int) -> Path | None:
    if args.baseline_run:
        run = Path(args.baseline_run)
        if not (run / "initial_atlas.npz").exists():
            raise FileNotFoundError(f"--baseline-run missing initial_atlas.npz: {run}")
        return run

    run_id = f"{args.asset}_{args.baseline}_ours_seed{seed}"
    roots = [
        Path(cfg.get("b3_output_root", "runs/B3_main")),
        ROOT / "runs" / "B3_main",
        Path("/data/dip_1_ws/runs/B3_main"),
    ]
    for root in roots:
        run = root / run_id
        if (run / "initial_atlas.npz").exists():
            return run
    return None


def _patch_cached_baseline(args: argparse.Namespace, cfg: dict[str, Any], baseline_run: Path | None) -> None:
    if baseline_run is None:
        return
    import pbr_atlas.baselines as baselines_pkg

    original_create_backend = baselines_pkg.create_backend
    cached_path = baseline_run / "initial_atlas.npz"

    def create_backend(name: str, config=None):
        backend = original_create_backend(name, config)
        if name != args.baseline:
            return backend
        backend_name = str(name)

        class CachedInitialAtlasBackend:
            name = backend_name

            def is_available(self) -> bool:
                return True

            def generate(self, mesh, atlas_size: int, padding: int, **kw):
                del mesh, kw
                atlas = load_npz_atlas(cached_path, name=backend_name, atlas_size=int(atlas_size), padding=int(padding))
                metadata = {**dict(atlas.metadata), "cached_b3_run": str(baseline_run)}
                return atlas.__class__(
                    name=atlas.name,
                    uv=atlas.uv,
                    face_uv=atlas.face_uv,
                    chart_ids=atlas.chart_ids,
                    atlas_size=atlas.atlas_size,
                    padding=atlas.padding,
                    metadata=metadata,
                    repro_status=atlas.repro_status,
                    failure_reason=atlas.failure_reason,
                )

        return CachedInitialAtlasBackend()

    baselines_pkg.create_backend = create_backend


def _apply_runtime_patches(condition_id: str, cfg: dict[str, Any]) -> None:
    import scripts.run_B3 as b3

    b3._c5_guard = patch_c5_guard(b3._c5_guard, condition_id, cfg)

    if cfg.get("b5_strict", {}).get("freeze_repack_layout"):
        import pbr_atlas.baselines.base as base_pkg
        import pbr_atlas.method.chart_repair as chart_repair_pkg

        wrapped = make_layout_preserving_repack(base_pkg.repack_existing_charts)
        base_pkg.repack_existing_charts = wrapped
        chart_repair_pkg.repack_existing_charts = wrapped


def _write_temp_config(cfg: dict[str, Any]) -> Path:
    handle = tempfile.NamedTemporaryFile("w", suffix=".yaml", prefix="B5_resolved_", delete=False)
    with handle:
        yaml.safe_dump(cfg, handle, sort_keys=False)
    return Path(handle.name)


def _run_id(args: argparse.Namespace, condition_id: str, seed: int) -> str:
    if args.run_id:
        return args.run_id
    return f"{condition_id.replace('.', '_')}_{args.asset}_{args.baseline}_seed{seed}"


def _c5_verdict(metrics: dict[str, Any]) -> str:
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


def _enrich_metrics(run_dir: Path, args: argparse.Namespace, condition_id: str, cfg: dict[str, Any], baseline_run: Path | None) -> None:
    metrics_path = run_dir / "metrics.json"
    if not metrics_path.exists():
        return
    with open(metrics_path, "r", encoding="utf-8") as handle:
        metrics = json.load(handle)
    metrics = annotate_metrics(metrics, condition_id, cfg)
    metrics["baseline_run"] = str(baseline_run) if baseline_run else None
    atomic_write_json(metrics_path, metrics)

    final_psnr = metrics.get("final", {}).get("relit", {}).get("psnr")
    initial_psnr = metrics.get("initial", {}).get("relit", {}).get("psnr")
    matched_ok = metrics.get("c5", {}).get("b5_strict", {}).get("matched_ok")
    summary = (
        "# B5 Strict Matched Summary\n\n"
        f"- condition: {condition_id}\n"
        f"- condition name: {metrics.get('condition_name')}\n"
        f"- asset: {args.asset}\n"
        f"- baseline: {args.baseline}\n"
        f"- initial PSNR: {initial_psnr}\n"
        f"- final PSNR: {final_psnr}\n"
        f"- matched OK: {matched_ok}\n"
        f"- C5 verdict: {_c5_verdict(metrics)}\n"
        f"- rollback to baseline: {metrics.get('c5', {}).get('rollback_to_baseline')}\n"
    )
    write_text(run_dir / "summary.md", summary)


def _run_one(args: argparse.Namespace) -> Path:
    if not args.condition:
        raise ValueError("--condition is required unless --all is used")
    if not args.asset:
        raise ValueError("--asset is required unless --all is used")

    condition_id = normalize_condition_id(args.condition)
    config_path = Path(args.config) if args.config else _condition_config_path(condition_id)
    cfg = load_config(config_path)
    cfg = patch_config(cfg, condition_id)
    cfg = sync_matched_atlas_size(cfg)
    if args.output_root:
        cfg["output_root"] = args.output_root
    if args.data_root:
        cfg["data_root"] = args.data_root
    seed = int(args.seed if args.seed is not None else cfg.get("seed", 42))
    if args.seed is not None:
        cfg["seed"] = seed

    baseline_run = _find_baseline_run(args, cfg, seed)
    _patch_cached_baseline(args, cfg, baseline_run)
    _apply_runtime_patches(condition_id, cfg)

    run_id = _run_id(args, condition_id, seed)
    resolved_config = _write_temp_config(cfg)
    output_root = str(cfg.get("output_root", "/data/dip_1_ws/runs/B5_matched"))

    import scripts.run_B3 as b3

    argv = [
        "run_B3.py",
        "--asset",
        args.asset,
        "--baseline",
        args.baseline,
        "--method",
        "ours",
        "--config",
        str(resolved_config),
        "--output-root",
        output_root,
        "--run-id",
        run_id,
    ]
    if args.gpu is not None:
        argv += ["--gpu", str(args.gpu)]
    if args.no_lpips:
        argv += ["--no-lpips"]
    old_argv = sys.argv[:]
    try:
        sys.argv = argv
        b3.main()
    finally:
        sys.argv = old_argv

    run_dir = Path(output_root) / run_id
    _enrich_metrics(run_dir, args, condition_id, cfg, baseline_run)
    print(str(run_dir))
    return run_dir


def _run_all(args: argparse.Namespace) -> None:
    script = Path(__file__).resolve()
    output_root = args.output_root
    for condition_id in B5_CONDITIONS:
        for asset in ("spot", "bunny"):
            cmd = [sys.executable, str(script), "--condition", condition_id, "--asset", asset, "--baseline", args.baseline]
            if output_root:
                cmd += ["--output-root", output_root]
            if args.data_root:
                cmd += ["--data-root", args.data_root]
            if args.gpu is not None:
                cmd += ["--gpu", str(args.gpu)]
            if args.seed is not None:
                cmd += ["--seed", str(args.seed)]
            if args.no_lpips:
                cmd += ["--no-lpips"]
            subprocess.run(cmd, check=True)
    if args.collect:
        collect_cmd = [sys.executable, str(ROOT / "scripts" / "collect_B5_table.py")]
        if output_root:
            collect_cmd += ["--input-root", output_root]
        subprocess.run(collect_cmd, check=True)


def main() -> None:
    args = parse_args()
    if args.all:
        _run_all(args)
        return
    run_dir = _run_one(args)
    if args.collect:
        collect_cmd = [sys.executable, str(ROOT / "scripts" / "collect_B5_table.py"), "--input-root", str(run_dir.parent)]
        subprocess.run(collect_cmd, check=True)


if __name__ == "__main__":
    main()

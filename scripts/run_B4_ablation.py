#!/usr/bin/env python
"""Run one B4 ablation by applying a non-destructive patch to the B3 pipeline."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from dataclasses import replace
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pbr_atlas.ablations import load_patch_module
from pbr_atlas.ablations.common import coerce_variant, deep_merge, load_npz_atlas, sync_matched_atlas_size
from pbr_atlas.utils.io import atomic_write_json, write_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one B4 design-choice ablation.")
    parser.add_argument("--ablation", required=True, choices=[f"A{i}" for i in range(1, 19)])
    parser.add_argument("--asset", required=True, choices=["spot", "bunny", "objaverse", "objaverse_sample"])
    parser.add_argument("--baseline", required=True, choices=["xatlas_classical", "partuv", "blender_uv", "matched_oracle"])
    parser.add_argument("--config", default=None)
    parser.add_argument("--baseline-run", default=None, help="B3 run dir containing initial_atlas.npz.")
    parser.add_argument("--variant", default=None, help="Named sweep variant for A14-A18.")
    parser.add_argument("--gpu", type=int, default=None)
    parser.add_argument("--output-root", default=None)
    parser.add_argument("--data-root", default=None)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--no-lpips", action="store_true")
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


def _find_baseline_run(args: argparse.Namespace, cfg: dict[str, Any], seed: int) -> Path | None:
    if args.baseline_run:
        run = Path(args.baseline_run)
        if not (run / "initial_atlas.npz").exists():
            raise FileNotFoundError(f"--baseline-run missing initial_atlas.npz: {run}")
        return run
    run_id = f"{args.asset}_{args.baseline}_ours_seed{seed}"
    candidates = [
        Path(cfg.get("b3_output_root", "runs/B3_main")) / run_id,
        ROOT / "runs" / "B3_main" / run_id,
        Path("/data/dip_1_ws/runs/B3_main") / run_id,
    ]
    for run in candidates:
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
                return replace(atlas, metadata={**dict(atlas.metadata), "cached_b3_run": str(baseline_run)})

        return CachedInitialAtlasBackend()

    baselines_pkg.create_backend = create_backend


def _apply_runtime_patches(args: argparse.Namespace, cfg: dict[str, Any], patch_module) -> None:
    import pbr_atlas.method as method_pkg
    import scripts.run_B3 as b3

    ablation = cfg.get("ablation", {})
    repairer = ablation.get("repairer")
    if repairer in {"distortion_only", "noop", "global_reunwrap"}:
        # Patch BOTH method_pkg AND run_B3 module namespace because run_B3
        # `from pbr_atlas.method import LocalChartRepair` creates a local binding
        # that won't see method_pkg.LocalChartRepair reassignment.
        patched = patch_module.patch(method_pkg.LocalChartRepair)
        method_pkg.LocalChartRepair = patched
        b3.LocalChartRepair = patched

    if ablation.get("allocator") == "uniform":
        patched = patch_module.patch(method_pkg.MipAwareAllocator)
        method_pkg.MipAwareAllocator = patched
        b3.MipAwareAllocator = patched

    if ablation.get("seam_loss") == "rgb_only":
        patched = patch_module.patch(method_pkg.CrossChannelSeamLoss)
        method_pkg.CrossChannelSeamLoss = patched
        b3.CrossChannelSeamLoss = patched

    if ablation.get("rgb_only_baker"):
        b3._evaluate_atlas = patch_module.patch(b3._evaluate_atlas)

    matched_control = ablation.get("matched_control")
    if matched_control:
        from pbr_atlas.ablations.matched_controls import patch_c5_guard

        b3._c5_guard = patch_c5_guard(b3._c5_guard, str(args.ablation).upper(), cfg)

    brdf_model = cfg.get("brdf", {}).get("model")
    if brdf_model:
        from pbr_atlas.ablations.sweeps import apply_brdf_model

        apply_brdf_model(str(brdf_model))

    light_type = cfg.get("lights", {}).get("type")
    if light_type:
        from pbr_atlas.ablations.sweeps import apply_light_type

        apply_light_type(str(light_type))


def _write_temp_config(cfg: dict[str, Any]) -> Path:
    handle = tempfile.NamedTemporaryFile("w", suffix=".yaml", prefix="B4_resolved_", delete=False)
    with handle:
        yaml.safe_dump(cfg, handle, sort_keys=False)
    return Path(handle.name)


def _run_id(args: argparse.Namespace, cfg: dict[str, Any], seed: int) -> str:
    if args.run_id:
        return args.run_id
    variant = cfg.get("ablation", {}).get("variant")
    prefix = f"{args.ablation}_{variant}" if variant else args.ablation
    return f"{prefix}_{args.asset}_{args.baseline}_seed{seed}"


def _enrich_metrics(run_dir: Path, args: argparse.Namespace, cfg: dict[str, Any], baseline_run: Path | None) -> None:
    metrics_path = run_dir / "metrics.json"
    if not metrics_path.exists():
        return
    with open(metrics_path, "r", encoding="utf-8") as handle:
        metrics = json.load(handle)
    patch_module = load_patch_module(args.ablation)
    metrics["block"] = "B4_ablation"
    metrics["ablation"] = args.ablation
    metrics["ablation_name"] = cfg.get("ablation", {}).get("name")
    metrics["ablation_mechanism"] = cfg.get("ablation", {}).get("mechanism")
    metrics["ablation_variant"] = cfg.get("ablation", {}).get("variant")
    metrics["expected_delta"] = cfg.get("ablation", {}).get("expected_delta")
    metrics["baseline_run"] = str(baseline_run) if baseline_run else None
    metrics["resolved_ablation_config"] = cfg.get("ablation", {})
    if hasattr(patch_module, "annotate_metrics"):
        metrics = patch_module.annotate_metrics(metrics)
    if cfg.get("ablation", {}).get("per_channel_uv"):
        metrics.setdefault("ablation_checks", {})["single_uv_ready"] = False
    atomic_write_json(metrics_path, metrics)

    summary = (
        "# B4 Ablation Summary\n\n"
        f"- ablation: {args.ablation}\n"
        f"- variant: {metrics.get('ablation_variant') or '-'}\n"
        f"- asset: {args.asset}\n"
        f"- baseline: {args.baseline}\n"
        f"- expected delta: {metrics.get('expected_delta')}\n"
        f"- initial PSNR: {metrics.get('initial', {}).get('relit', {}).get('psnr')}\n"
        f"- final PSNR: {metrics.get('final', {}).get('relit', {}).get('psnr')}\n"
        f"- C5 accept: {metrics.get('c5', {}).get('accept')}\n"
        f"- C5 rollback to baseline: {metrics.get('c5', {}).get('rollback_to_baseline')}\n"
    )
    write_text(run_dir / "summary.md", summary)


def main() -> None:
    args = parse_args()
    config_path = Path(args.config or f"configs/B4_ablations/{args.ablation}.yaml")
    cfg = load_config(config_path)
    cfg.setdefault("ablation", {})["id"] = args.ablation
    patch_module = load_patch_module(args.ablation)
    cfg = patch_module.patch(cfg)
    cfg = coerce_variant(cfg, args.variant)
    cfg = sync_matched_atlas_size(cfg)
    if args.output_root:
        cfg["output_root"] = args.output_root
    else:
        cfg.setdefault("output_root", "runs/B4_ablation")
    if args.data_root:
        cfg["data_root"] = args.data_root
    seed = int(args.seed if args.seed is not None else cfg.get("seed", 42))
    if args.seed is not None:
        cfg["seed"] = seed

    baseline_run = _find_baseline_run(args, cfg, seed)
    _patch_cached_baseline(args, cfg, baseline_run)
    _apply_runtime_patches(args, cfg, patch_module)

    run_id = _run_id(args, cfg, seed)
    resolved_config = _write_temp_config(cfg)
    output_root = str(cfg.get("output_root", "runs/B4_ablation"))

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
    _enrich_metrics(run_dir, args, cfg, baseline_run)
    print(str(run_dir))


if __name__ == "__main__":
    main()

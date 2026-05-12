#!/usr/bin/env python
"""Run B7 generated-mesh transfer cases through the B3 pipeline."""

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

from pbr_atlas.ablations.common import deep_merge, sync_matched_atlas_size  # noqa: E402
from pbr_atlas.data.generated_mesh_loader import (  # noqa: E402
    DEFAULT_B7_DATA_ROOT,
    GeneratedMeshRecord,
    default_asset_ids,
    prepare_generated_mesh_set,
)
from pbr_atlas.utils.io import atomic_write_json, ensure_dir, write_text  # noqa: E402


BASELINE_CHOICES = ["xatlas_classical", "partuv", "blender_uv", "matched_oracle"]
METHOD_CHOICES = ["ours", "baseline_only", "all"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run B7 generated transfer experiments.")
    parser.add_argument("--asset", default="all", help="B7 generated asset id or 'all'.")
    parser.add_argument("--baseline", default="partuv", choices=BASELINE_CHOICES)
    parser.add_argument("--method", default="all", choices=METHOD_CHOICES)
    parser.add_argument("--config", default="configs/B7_transfer.yaml")
    parser.add_argument("--gpu", type=int, default=None)
    parser.add_argument("--output-root", default=None)
    parser.add_argument("--data-root", default=None, help="B7 generated mesh cache root.")
    parser.add_argument("--manifest", default=None, help="Optional B7 remote/local source manifest.")
    parser.add_argument("--count", type=int, default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--force-setup", action="store_true")
    parser.add_argument("--no-lpips", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--collect", action="store_true", help="Run collect_B7_table.py after runs finish.")
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


def _write_temp_config(cfg: dict[str, Any]) -> Path:
    handle = tempfile.NamedTemporaryFile("w", suffix=".yaml", prefix="B7_transfer_resolved_", delete=False)
    with handle:
        yaml.safe_dump(cfg, handle, sort_keys=False)
    return Path(handle.name)


def _methods(method_arg: str) -> list[str]:
    if method_arg == "all":
        return ["baseline_only", "ours"]
    return [method_arg]


def _run_id(asset_id: str, baseline: str, method: str, seed: int) -> str:
    return f"{asset_id}_{baseline}_{method}_seed{seed}"


def _patch_prepare_asset(mesh_path: Path):
    import pbr_atlas.data as data_pkg

    original = data_pkg.prepare_asset

    def prepare_asset(asset: str, data_root=None, offline_ok: bool = True):  # noqa: ARG001
        return mesh_path

    data_pkg.prepare_asset = prepare_asset
    return data_pkg, original


def _failure_metrics(
    run_dir: Path,
    *,
    record: GeneratedMeshRecord,
    baseline: str,
    method: str,
    seed: int,
    exc: BaseException,
) -> None:
    ensure_dir(run_dir)
    payload = {
        "block": "B7_transfer",
        "asset": record.asset_id,
        "generated_asset": record.asset_id,
        "baseline": baseline,
        "method": method,
        "seed": seed,
        "mesh_path": record.mesh_path,
        "generated_mesh": record.to_dict(),
        "repro_status": "failed",
        "failure_reason": f"{type(exc).__name__}: {exc}",
    }
    atomic_write_json(run_dir / "metrics.json", payload)
    write_text(
        run_dir / "summary.md",
        "# B7 Transfer Summary\n\n"
        f"- asset: {record.asset_id}\n"
        f"- baseline: {baseline}\n"
        f"- method: {method}\n"
        "- repro_status: failed\n"
        f"- failure_reason: {payload['failure_reason']}\n",
    )


def _enrich_metrics(
    run_dir: Path,
    *,
    record: GeneratedMeshRecord,
    b3_asset_alias: str,
    baseline: str,
    method: str,
    cfg: dict[str, Any],
) -> None:
    metrics_path = run_dir / "metrics.json"
    if not metrics_path.exists():
        return
    with open(metrics_path, "r", encoding="utf-8") as handle:
        metrics = json.load(handle)
    metrics["block"] = "B7_transfer"
    metrics["asset"] = record.asset_id
    metrics["generated_asset"] = record.asset_id
    metrics["b3_asset_alias"] = b3_asset_alias
    metrics["baseline"] = baseline
    metrics["method"] = method
    metrics["mesh_path"] = record.mesh_path
    metrics["generated_mesh"] = record.to_dict()
    metrics["b7_expected"] = dict(cfg.get("b7_transfer", {}))
    atomic_write_json(metrics_path, metrics)

    final_psnr = metrics.get("final", {}).get("relit", {}).get("psnr")
    initial_psnr = metrics.get("initial", {}).get("relit", {}).get("psnr")
    summary = (
        "# B7 Transfer Summary\n\n"
        f"- asset: {record.asset_id}\n"
        f"- source: {record.source}\n"
        f"- mesh: {record.mesh_path}\n"
        f"- baseline: {baseline}\n"
        f"- method: {method}\n"
        f"- repro_status: {metrics.get('repro_status')}\n"
        f"- initial PSNR: {initial_psnr}\n"
        f"- final PSNR: {final_psnr}\n"
        f"- C5 accept: {metrics.get('c5', {}).get('accept')}\n"
        f"- C5 rollback to baseline: {metrics.get('c5', {}).get('rollback_to_baseline')}\n"
    )
    write_text(run_dir / "summary.md", summary)


def _run_one(
    *,
    record: GeneratedMeshRecord,
    method: str,
    args: argparse.Namespace,
    cfg: dict[str, Any],
    seed: int,
    resolved_config: Path,
    output_root: Path,
) -> Path:
    b7_cfg = cfg.get("b7_transfer", {})
    b3_asset_alias = str(b7_cfg.get("asset_alias_for_b3", "objaverse_sample"))
    run_id = _run_id(record.asset_id, args.baseline, method, seed)
    run_dir = output_root / run_id
    if args.dry_run:
        print(f"DRY\t{run_id}\t{record.mesh_path}")
        return run_dir

    data_pkg, original_prepare = _patch_prepare_asset(Path(record.mesh_path))
    import scripts.run_B3 as b3

    argv = [
        "run_B3.py",
        "--asset",
        b3_asset_alias,
        "--baseline",
        args.baseline,
        "--method",
        method,
        "--config",
        str(resolved_config),
        "--output-root",
        str(output_root),
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
    except Exception as exc:
        _failure_metrics(run_dir, record=record, baseline=args.baseline, method=method, seed=seed, exc=exc)
    finally:
        sys.argv = old_argv
        data_pkg.prepare_asset = original_prepare

    _enrich_metrics(run_dir, record=record, b3_asset_alias=b3_asset_alias, baseline=args.baseline, method=method, cfg=cfg)
    print(str(run_dir))
    return run_dir


def main() -> None:
    args = parse_args()
    cfg = sync_matched_atlas_size(load_config(args.config))
    b7_cfg = cfg.get("b7_transfer", {})
    if args.output_root:
        cfg["output_root"] = args.output_root
    output_root = Path(cfg.get("output_root", "/data/dip_1_ws/runs/B7_transfer"))
    if args.data_root:
        cfg["data_root"] = args.data_root
    data_root = Path(args.data_root or cfg.get("data_root", DEFAULT_B7_DATA_ROOT))
    seed = int(args.seed if args.seed is not None else cfg.get("seed", 42))
    cfg["seed"] = seed

    if args.asset == "all":
        cfg_assets = b7_cfg.get("assets")
        asset_ids = [str(item) for item in cfg_assets] if cfg_assets else default_asset_ids()
    else:
        asset_ids = [args.asset]
    count = args.count if args.count is not None else b7_cfg.get("generated_count")
    records = prepare_generated_mesh_set(
        data_root=data_root,
        asset_ids=asset_ids,
        count=int(count) if count else None,
        manifest=args.manifest,
        offline_ok=True,
        force=args.force_setup,
    )

    cfg["data_root"] = str(data_root)
    cfg["output_root"] = str(output_root)
    resolved_config = _write_temp_config(cfg)

    for record in records:
        for method in _methods(args.method):
            _run_one(
                record=record,
                method=method,
                args=args,
                cfg=cfg,
                seed=seed,
                resolved_config=resolved_config,
                output_root=output_root,
            )

    if args.collect and not args.dry_run:
        robustness_root = Path(cfg.get("b7_transfer", {}).get("robustness_root", output_root.parent / "B7_robustness"))
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "collect_B7_table.py"),
                "--transfer-root",
                str(output_root),
                "--robustness-root",
                str(robustness_root),
            ],
            check=True,
        )


if __name__ == "__main__":
    main()

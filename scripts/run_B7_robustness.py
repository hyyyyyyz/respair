#!/usr/bin/env python
"""Run B7 robustness sweeps on spot/PartUV through the B3 pipeline."""

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
from pbr_atlas.data.asset_registry import DEFAULT_DATA_ROOT, prepare_asset as prepare_b1_asset  # noqa: E402
from pbr_atlas.data.generated_mesh_loader import (  # noqa: E402
    DEFAULT_B7_DATA_ROOT,
    DEFAULT_B7_ROBUSTNESS_ROOT,
    GeneratedMeshRecord,
    default_asset_ids,
    prepare_generated_mesh,
    prepare_robustness_mesh,
)
from pbr_atlas.utils.io import atomic_write_json, ensure_dir, write_text  # noqa: E402


SWEEP_CHOICES = ["noise", "view", "light", "all"]
METHOD_CHOICES = ["ours", "baseline_only", "all"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run B7 robustness sweeps.")
    parser.add_argument("--sweep", default="all", choices=SWEEP_CHOICES)
    parser.add_argument("--level", default=None, help="Single sigma/view-holdout/light-holdout level.")
    parser.add_argument("--asset", default="spot", help="Asset name (built-in or procedural prefixed proc_*)")
    parser.add_argument("--baseline", default="partuv", choices=["partuv"])
    parser.add_argument("--method", default="ours", choices=METHOD_CHOICES)
    parser.add_argument("--config", default="configs/B7_robustness.yaml")
    parser.add_argument("--gpu", type=int, default=None)
    parser.add_argument("--output-root", default=None)
    parser.add_argument("--data-root", default=None, help="B1 sample mesh root.")
    parser.add_argument("--generated-data-root", default=None, help="B7/PG generated mesh cache root.")
    parser.add_argument("--robustness-data-root", default=None, help="B7 vertex-noise mesh cache root.")
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
    handle = tempfile.NamedTemporaryFile("w", suffix=".yaml", prefix="B7_robustness_resolved_", delete=False)
    with handle:
        yaml.safe_dump(cfg, handle, sort_keys=False)
    return Path(handle.name)


def _level_token(value: str | float | int) -> str:
    if isinstance(value, str):
        try:
            value = float(value)
        except ValueError:
            return value.replace(".", "p")
    if float(value).is_integer():
        return str(int(value))
    return f"{float(value):.4f}".rstrip("0").rstrip(".").replace(".", "p")


def _methods(method_arg: str) -> list[str]:
    if method_arg == "all":
        return ["baseline_only", "ours"]
    return [method_arg]


def _sweep_levels(args: argparse.Namespace, cfg: dict[str, Any]) -> list[tuple[str, float | int]]:
    b7_cfg = cfg.get("b7_robustness", {})
    sweeps = ["noise", "view", "light"] if args.sweep == "all" else [args.sweep]
    out: list[tuple[str, float | int]] = []
    for sweep in sweeps:
        if args.level is not None:
            level: float | int = float(args.level) if sweep == "noise" else int(args.level)
            out.append((sweep, level))
            continue
        if sweep == "noise":
            out.extend((sweep, float(level)) for level in b7_cfg.get("noise_sigmas", [0.0, 0.01, 0.02, 0.05]))
        elif sweep == "view":
            out.extend((sweep, int(level)) for level in b7_cfg.get("view_holdouts", [4, 6, 8, 12]))
        elif sweep == "light":
            out.extend((sweep, int(level)) for level in b7_cfg.get("light_holdouts", [2, 4, 6, 8]))
    return out


def _run_id(sweep: str, level: float | int, asset: str, baseline: str, method: str, seed: int) -> str:
    label = "sigma" if sweep == "noise" else "holdout"
    return f"{sweep}_{label}{_level_token(level)}_{asset}_{baseline}_{method}_seed{seed}"


def _is_generated_asset(asset: str) -> bool:
    return asset not in {"spot", "bunny", "objaverse", "objaverse_sample"} or asset in set(default_asset_ids())


def _b3_asset_alias(asset: str) -> str:
    return "objaverse_sample" if _is_generated_asset(asset) else asset


def _patch_prepare_asset(mesh_path: Path):
    import pbr_atlas.data as data_pkg

    original = data_pkg.prepare_asset

    def prepare_asset(asset: str, data_root=None, offline_ok: bool = True):  # noqa: ARG001
        return mesh_path

    data_pkg.prepare_asset = prepare_asset
    return data_pkg, original


def _case_config(cfg: dict[str, Any], *, sweep: str, level: float | int, output_root: Path, data_root: Path, seed: int) -> dict[str, Any]:
    case_cfg = deep_merge(cfg, {})
    case_cfg["output_root"] = str(output_root)
    case_cfg["data_root"] = str(data_root)
    case_cfg["seed"] = seed
    if sweep == "view":
        case_cfg.setdefault("views", {})["holdout"] = int(level)
    if sweep == "light":
        case_cfg.setdefault("lights", {})["holdout"] = int(level)
    case_cfg["b7_robustness_case"] = {"sweep": sweep, "level": float(level) if sweep == "noise" else int(level)}
    return sync_matched_atlas_size(case_cfg)


def _failure_metrics(
    run_dir: Path,
    *,
    args: argparse.Namespace,
    sweep: str,
    level: float | int,
    method: str,
    seed: int,
    record: GeneratedMeshRecord | None,
    exc: BaseException,
) -> None:
    ensure_dir(run_dir)
    payload = {
        "block": "B7_robustness",
        "asset": args.asset,
        "baseline": args.baseline,
        "method": method,
        "seed": seed,
        "robustness": {"sweep": sweep, "level": level},
        "robustness_mesh": record.to_dict() if record else None,
        "repro_status": "failed",
        "failure_reason": f"{type(exc).__name__}: {exc}",
    }
    atomic_write_json(run_dir / "metrics.json", payload)
    write_text(
        run_dir / "summary.md",
        "# B7 Robustness Summary\n\n"
        f"- asset: {args.asset}\n"
        f"- sweep: {sweep}\n"
        f"- level: {level}\n"
        f"- baseline: {args.baseline}\n"
        f"- method: {method}\n"
        "- repro_status: failed\n"
        f"- failure_reason: {payload['failure_reason']}\n",
    )


def _enrich_metrics(
    run_dir: Path,
    *,
    args: argparse.Namespace,
    sweep: str,
    level: float | int,
    method: str,
    record: GeneratedMeshRecord | None,
    cfg: dict[str, Any],
) -> None:
    metrics_path = run_dir / "metrics.json"
    if not metrics_path.exists():
        return
    with open(metrics_path, "r", encoding="utf-8") as handle:
        metrics = json.load(handle)
    metrics["block"] = "B7_robustness"
    metrics["asset"] = args.asset
    metrics["baseline"] = args.baseline
    metrics["method"] = method
    metrics["robustness"] = {
        "sweep": sweep,
        "level": float(level) if sweep == "noise" else int(level),
        "noise_sigma": float(level) if sweep == "noise" else None,
        "view_holdout": int(level) if sweep == "view" else metrics.get("views", {}).get("holdout"),
        "light_holdout": int(level) if sweep == "light" else metrics.get("lights", {}).get("holdout"),
    }
    if record:
        metrics["robustness_mesh"] = record.to_dict()
        metrics["robustness_asset"] = record.asset_id
        metrics["mesh_path"] = record.mesh_path
    metrics["b7_expected"] = dict(cfg.get("b7_robustness", {}))
    atomic_write_json(metrics_path, metrics)

    final_psnr = metrics.get("final", {}).get("relit", {}).get("psnr")
    summary = (
        "# B7 Robustness Summary\n\n"
        f"- asset: {args.asset}\n"
        f"- sweep: {sweep}\n"
        f"- level: {level}\n"
        f"- baseline: {args.baseline}\n"
        f"- method: {method}\n"
        f"- repro_status: {metrics.get('repro_status')}\n"
        f"- final PSNR: {final_psnr}\n"
        f"- C5 accept: {metrics.get('c5', {}).get('accept')}\n"
        f"- C5 rollback to baseline: {metrics.get('c5', {}).get('rollback_to_baseline')}\n"
    )
    write_text(run_dir / "summary.md", summary)


def _run_one(
    *,
    args: argparse.Namespace,
    cfg: dict[str, Any],
    sweep: str,
    level: float | int,
    method: str,
    seed: int,
    output_root: Path,
    data_root: Path,
    generated_data_root: Path,
    robustness_data_root: Path,
) -> Path:
    record: GeneratedMeshRecord | None = None
    base_record: GeneratedMeshRecord | None = None
    source_mesh: Path | None = None
    if _is_generated_asset(args.asset) and not args.dry_run:
        base_record = prepare_generated_mesh(args.asset, data_root=generated_data_root, force=args.force_setup)
        source_mesh = Path(base_record.mesh_path)
    elif not args.dry_run:
        source_mesh = prepare_b1_asset(args.asset, data_root=data_root, offline_ok=True)

    if sweep == "noise" and not args.dry_run:
        assert source_mesh is not None
        record = prepare_robustness_mesh(
            base_asset=args.asset,
            source_mesh=source_mesh,
            sigma=float(level),
            data_root=robustness_data_root,
            seed=seed,
            force=args.force_setup,
        )
    run_id = _run_id(sweep, level, args.asset, args.baseline, method, seed)
    run_dir = output_root / run_id
    case_cfg = _case_config(cfg, sweep=sweep, level=level, output_root=output_root, data_root=data_root, seed=seed)
    resolved_config = _write_temp_config(case_cfg)

    if args.dry_run:
        mesh_text = record.mesh_path if record else "base_asset"
        print(f"DRY\t{run_id}\t{mesh_text}")
        return run_dir

    data_pkg = None
    original_prepare = None
    patch_record = record or base_record
    if patch_record is not None:
        data_pkg, original_prepare = _patch_prepare_asset(Path(patch_record.mesh_path))

    import scripts.run_B3 as b3

    argv = [
        "run_B3.py",
        "--asset",
        _b3_asset_alias(args.asset),
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
        _failure_metrics(run_dir, args=args, sweep=sweep, level=level, method=method, seed=seed, record=record, exc=exc)
    finally:
        sys.argv = old_argv
        if data_pkg is not None and original_prepare is not None:
            data_pkg.prepare_asset = original_prepare

    _enrich_metrics(run_dir, args=args, sweep=sweep, level=level, method=method, record=record or base_record, cfg=cfg)
    print(str(run_dir))
    return run_dir


def main() -> None:
    args = parse_args()
    cfg = sync_matched_atlas_size(load_config(args.config))
    if args.output_root:
        cfg["output_root"] = args.output_root
    output_root = Path(cfg.get("output_root", "/data/dip_1_ws/runs/B7_robustness"))
    data_root = Path(args.data_root or cfg.get("data_root", DEFAULT_DATA_ROOT))
    b7_cfg = cfg.get("b7_robustness", {})
    robustness_data_root = Path(
        args.robustness_data_root or b7_cfg.get("robustness_data_root", DEFAULT_B7_ROBUSTNESS_ROOT)
    )
    generated_data_root = Path(args.generated_data_root or b7_cfg.get("generated_data_root", DEFAULT_B7_DATA_ROOT))
    seed = int(args.seed if args.seed is not None else cfg.get("seed", 42))
    cfg["seed"] = seed

    for sweep, level in _sweep_levels(args, cfg):
        for method in _methods(args.method):
            _run_one(
                args=args,
                cfg=cfg,
                sweep=sweep,
                level=level,
                method=method,
                seed=seed,
                output_root=output_root,
                data_root=data_root,
                generated_data_root=generated_data_root,
                robustness_data_root=robustness_data_root,
            )

    if args.collect and not args.dry_run:
        transfer_root = Path(cfg.get("b7_robustness", {}).get("transfer_root", output_root.parent / "B7_transfer"))
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "collect_B7_table.py"),
                "--transfer-root",
                str(transfer_root),
                "--robustness-root",
                str(output_root),
                "--output-root",
                str(transfer_root),
            ],
            check=True,
        )


if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""B2 baseline reproduction entrypoint."""

from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a single B2 baseline evaluation.")
    parser.add_argument("--asset", required=True, choices=["bunny", "spot", "objaverse", "objaverse_sample"])
    parser.add_argument(
        "--baseline",
        required=True,
        choices=[
            "xatlas_classical",
            "blender_uv",
            "partuv",
            "flexpara",
            "otuvgs",
            "flatten_anything",
            "parapoint",
            "visibility_param",
            "matched_oracle",
        ],
    )
    parser.add_argument("--gpu", type=int, default=None, help="CUDA device index before visibility remapping.")
    parser.add_argument("--config", default="configs/B2_matched.yaml")
    parser.add_argument("--output-root", default=None)
    parser.add_argument("--data-root", default=None)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--atlas-resolution", type=int, default=None)
    parser.add_argument("--render-resolution", type=int, default=None)
    parser.add_argument("--precision", default=None, choices=["fp32", "float32", "fp16", "float16", "bf16", "bfloat16"])
    parser.add_argument("--no-lpips", action="store_true")
    return parser.parse_args()


def load_config(path: str | Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _metric_or_none(value):
    if value is None:
        return None
    if value == float("inf"):
        return "inf"
    return float(value)


def _round_list(tensor, digits: int = 8) -> list[float]:
    values = tensor.detach().to("cpu").flatten().tolist()
    return [round(float(v), digits) for v in values]


def _failure_summary(asset: str, baseline: str, reason: str, matched_violations: list[str]) -> str:
    lines = [
        "# B2 Baseline Summary",
        "",
        f"- asset: {asset}",
        f"- baseline: {baseline}",
        "- repro_status: failed",
        f"- failure_reason: {reason}",
    ]
    if matched_violations:
        lines.append(f"- matched_violations: {matched_violations}")
    return "\n".join(lines) + "\n"


def _format_placeholders(node: Any, values: dict[str, Any]) -> Any:
    if isinstance(node, str):
        try:
            return node.format(**values)
        except Exception:
            return node
    if isinstance(node, dict):
        return {key: _format_placeholders(value, values) for key, value in node.items()}
    if isinstance(node, list):
        return [_format_placeholders(value, values) for value in node]
    return node


def main() -> None:
    args = parse_args()
    if args.gpu is not None:
        os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpu)

    import torch

    from pbr_atlas.baker import DifferentiablePBRBaker, create_synthetic_oracle_maps, make_lights, make_orbit_views, sample_face_pbr_from_maps
    from pbr_atlas.baker.residual import compute_residual_attribution
    from pbr_atlas.baselines import BACKEND_REGISTRY, clone_mesh_with_atlas, create_backend
    from pbr_atlas.baselines.base import BaselineAtlas
    from pbr_atlas.baselines.baseline_failure_table import FailureRecord, record_failure, write_failure_report
    from pbr_atlas.baselines.matched_protocol import MatchedProtocolConfig, enforce
    from pbr_atlas.data import prepare_asset
    from pbr_atlas.data.mesh_loader import load_mesh
    from pbr_atlas.eval.metrics import image_metrics, normal_angular_error, per_channel_mae
    from pbr_atlas.eval.residual_attribution import residual_localization_hit_rate
    from pbr_atlas.utils import atomic_write_json, directory_size_mb, ensure_dir, save_npz, save_residual_atlas_png, set_global_seed, write_text

    cfg = load_config(args.config)
    seed = int(args.seed if args.seed is not None else cfg.get("seed", 42))
    atlas_resolution = int(args.atlas_resolution or cfg.get("atlas_resolution", cfg.get("matched_protocol", {}).get("atlas_size", 1024)))
    render_resolution = int(args.render_resolution or cfg.get("render_resolution", 256))
    precision = args.precision or cfg.get("precision", "bf16")
    output_root = Path(args.output_root or cfg.get("output_root", "/data/dip_1_ws/runs/B2_baseline"))
    run_id = args.run_id or f"{args.asset}_{args.baseline}_seed{seed}"
    run_dir = ensure_dir(output_root / run_id)
    data_root = Path(args.data_root or cfg.get("data_root", "/data/dip_1_ws/datasets/sample"))
    vis_resolution = int(cfg.get("visualization_resolution", min(atlas_resolution, 1024)))
    matched_cfg = MatchedProtocolConfig.from_mapping(cfg.get("matched_protocol"))
    padding = int(matched_cfg.padding)

    set_global_seed(seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats()
    started = time.time()

    mesh_path = prepare_asset(args.asset, data_root=data_root, offline_ok=True)
    mesh = load_mesh(mesh_path, device=device)

    baker = DifferentiablePBRBaker(
        atlas_resolution=atlas_resolution,
        render_resolution=render_resolution,
        precision=precision,
        gradient_checkpointing=bool(cfg.get("gradient_checkpointing", True)),
        device=device,
    )

    baseline_cfg = _format_placeholders(
        dict(cfg.get("baselines", {})),
        {
            "asset": args.asset if args.asset != "objaverse_sample" else "objaverse",
            "baseline": args.baseline,
            "seed": seed,
            "atlas_size": atlas_resolution,
            "padding": padding,
            "output_root": str(output_root),
        },
    )
    xatlas_reference = create_backend("xatlas_classical", baseline_cfg.get("xatlas_classical", {})).generate(mesh, atlas_resolution, padding)
    if xatlas_reference.repro_status == "failed":
        xatlas_reference = BaselineAtlas(
            name="xatlas_reference_fallback",
            uv=mesh.uv.detach().cpu(),
            face_uv=mesh.face_uv.detach().cpu(),
            chart_ids=mesh.chart_ids.detach().cpu(),
            atlas_size=atlas_resolution,
            padding=padding,
            metadata={"warning": "xatlas baseline unavailable; fell back to input mesh UV."},
            repro_status="partial",
            failure_reason="xatlas reference unavailable",
        )

    oracle_reference_backend = create_backend("matched_oracle", baseline_cfg.get("matched_oracle", {}))
    oracle_reference = oracle_reference_backend.generate(mesh, atlas_resolution, padding)
    if oracle_reference.repro_status == "failed":
        oracle_reference = xatlas_reference

    baseline_backend = create_backend(args.baseline, baseline_cfg.get(args.baseline, {}))
    candidate_atlas = (
        xatlas_reference
        if args.baseline == "xatlas_classical"
        else oracle_reference
        if args.baseline == "matched_oracle"
        else baseline_backend.generate(mesh, atlas_resolution, padding)
    )

    matched_report = enforce(mesh, candidate_atlas, xatlas_reference, matched_cfg)
    save_npz(
        run_dir / "atlas.npz",
        uv=candidate_atlas.uv,
        face_uv=candidate_atlas.face_uv,
        chart_ids=candidate_atlas.chart_ids,
    )

    base_metrics = {
        "block": "B2_baseline",
        "asset": args.asset,
        "baseline": args.baseline,
        "paper_id": candidate_atlas.metadata.get("paper_id"),
        "seed": seed,
        "device": str(device),
        "precision": precision,
        "atlas_resolution": atlas_resolution,
        "padding": padding,
        "mesh_path": str(mesh_path),
        "repro_status": candidate_atlas.repro_status,
        "failure_reason": candidate_atlas.failure_reason,
        "baseline_metadata": candidate_atlas.metadata,
        "matched_protocol": matched_report.to_dict(),
        "outputs": {
            "metrics": str(run_dir / "metrics.json"),
            "atlas_npz": str(run_dir / "atlas.npz"),
            "residual_npz": str(run_dir / "residual_atlas.npz"),
            "residual_png": str(run_dir / "residual_atlas.png"),
            "summary": str(run_dir / "summary.md"),
        },
    }

    if candidate_atlas.repro_status == "failed":
        metrics = dict(base_metrics)
        atomic_write_json(run_dir / "metrics.json", metrics)
        write_text(run_dir / "summary.md", _failure_summary(args.asset, args.baseline, candidate_atlas.failure_reason or "unknown failure", matched_report.violations))
        record_failure(
            output_root,
            FailureRecord(
                baseline=args.baseline,
                asset=args.asset,
                repro_status="failed",
                reason=candidate_atlas.failure_reason or "unknown failure",
                paper_id=str(candidate_atlas.metadata.get("paper_id") or ""),
                run_dir=str(run_dir),
            ),
        )
        write_failure_report(output_root)
        print(str(run_dir))
        return

    candidate_mesh = clone_mesh_with_atlas(mesh, candidate_atlas, device=device)
    oracle_mesh = clone_mesh_with_atlas(mesh, oracle_reference, device=device)
    oracle_maps = create_synthetic_oracle_maps(atlas_resolution, seed=seed, device=device)
    face_values = sample_face_pbr_from_maps(oracle_mesh, oracle_maps)
    oracle_baked_maps = baker.bake(oracle_mesh, face_values)
    candidate_baked_maps = baker.bake(candidate_mesh, face_values)

    view_cfg = cfg.get("views", {})
    light_cfg = cfg.get("lights", {})
    holdout_views = int(view_cfg.get("holdout", 4))
    holdout_lights = int(light_cfg.get("holdout", 4))
    all_views = make_orbit_views(int(view_cfg.get("train", 6)) + holdout_views, device=device)
    all_lights = make_lights(int(light_cfg.get("train", 4)) + holdout_lights, device=device)
    views = all_views[-holdout_views:] if holdout_views else all_views
    lights = all_lights[-holdout_lights:] if holdout_lights else all_lights

    pred_render = baker.render(candidate_mesh, candidate_baked_maps, views, lights)
    target_render = baker.render(oracle_mesh, oracle_baked_maps, views, lights)
    relit_metrics = image_metrics(pred_render.images, target_render.images, compute_lpips=not args.no_lpips)

    pbr_mae = per_channel_mae(
        {
            "albedo": candidate_baked_maps.albedo,
            "roughness": candidate_baked_maps.roughness,
            "metallic": candidate_baked_maps.metallic,
        },
        {
            "albedo": oracle_baked_maps.albedo,
            "roughness": oracle_baked_maps.roughness,
            "metallic": oracle_baked_maps.metallic,
        },
    )
    pbr_mae["normal_angular_error_deg"] = normal_angular_error(candidate_baked_maps.normal, oracle_baked_maps.normal)

    residual = compute_residual_attribution(
        pred=pred_render.images,
        target=target_render.images,
        face_ids=pred_render.face_ids,
        alpha=pred_render.alpha,
        mesh=candidate_mesh,
        maps=candidate_baked_maps,
        chart_ids=candidate_mesh.chart_ids,
        mip_levels=int(cfg.get("mip_levels", 4)),
    )

    artifact_mask = torch.zeros(candidate_mesh.faces.shape[0], dtype=torch.bool, device=device)
    if residual.seam_edges.numel() > 0:
        artifact_mask[residual.seam_edges.reshape(-1)] = True
    hit_rate = residual_localization_hit_rate(residual.e_f, artifact_mask, top_fraction=0.2)

    save_npz(
        run_dir / "residual_atlas.npz",
        e_f=residual.e_f,
        E_c=residual.E_c,
        S_e=residual.seam_residual,
        seam_edges=residual.seam_edges,
        G_l=residual.G_l,
    )
    save_residual_atlas_png(run_dir / "residual_atlas.png", candidate_mesh, residual.e_f, resolution=vis_resolution)

    peak_memory_gb = 0.0
    if device.type == "cuda":
        peak_memory_gb = float(torch.cuda.max_memory_allocated() / (1024.0**3))
    wall_clock_s = time.time() - started

    metrics = dict(base_metrics)
    metrics.update(
        {
            "relit": {key: _metric_or_none(value) for key, value in relit_metrics.items()},
            "pbr_channel": pbr_mae,
            "residual_stats": {
                "e_f": _round_list(residual.e_f),
                "E_c": _round_list(residual.E_c),
                "G_l": _round_list(residual.G_l),
                "e_f_mean": float(residual.e_f.mean().detach().cpu()) if residual.e_f.numel() else 0.0,
                "E_c_mean": float(residual.E_c.mean().detach().cpu()) if residual.E_c.numel() else 0.0,
                "G_l_mean": float(residual.G_l.mean().detach().cpu()) if residual.G_l.numel() else 0.0,
                "seam_residual_mean": float(residual.seam_residual.mean().detach().cpu()) if residual.seam_residual.numel() else 0.0,
                "residual_top20_seam_hit_rate": hit_rate,
            },
            "peak_memory_GB": peak_memory_gb,
            "wall_clock_s": wall_clock_s,
        }
    )
    atomic_write_json(run_dir / "metrics.json", metrics)
    output_size_mb = directory_size_mb(run_dir)
    metrics["storage"] = {"output_size_MB": output_size_mb}
    atomic_write_json(run_dir / "metrics.json", metrics)

    if candidate_atlas.repro_status != "ok":
        record_failure(
            output_root,
            FailureRecord(
                baseline=args.baseline,
                asset=args.asset,
                repro_status=candidate_atlas.repro_status,
                reason=candidate_atlas.failure_reason or "partial reproduction",
                paper_id=str(candidate_atlas.metadata.get("paper_id") or ""),
                run_dir=str(run_dir),
                notes="proxy output generated",
            ),
        )
        write_failure_report(output_root)

    summary = (
        "# B2 Baseline Summary\n\n"
        f"- asset: {args.asset}\n"
        f"- baseline: {args.baseline}\n"
        f"- repro_status: {candidate_atlas.repro_status}\n"
        f"- matched_constraint_violated: {matched_report.matched_constraint_violated}\n"
        f"- matched_violations: {matched_report.violations}\n"
        f"- relit PSNR: {metrics['relit']['psnr']}\n"
        f"- relit SSIM: {metrics['relit']['ssim']}\n"
        f"- LPIPS: {metrics['relit']['lpips']}\n"
        f"- E_c mean: {metrics['residual_stats']['E_c_mean']:.8f}\n"
        f"- G_l mean: {metrics['residual_stats']['G_l_mean']:.8f}\n"
        f"- peak memory GB: {peak_memory_gb:.3f}\n"
        f"- wall clock s: {wall_clock_s:.3f}\n"
    )
    write_text(run_dir / "summary.md", summary)
    print(str(run_dir))


if __name__ == "__main__":
    main()

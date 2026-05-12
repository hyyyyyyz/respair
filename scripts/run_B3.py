#!/usr/bin/env python
"""B3 main anchor runner: C1 baseline bake + C2/C3/C4 repair pipeline."""

from __future__ import annotations

import argparse
import os
import sys
import time
from dataclasses import replace
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one B3 main-method evaluation.")
    parser.add_argument("--asset", required=True, help="Asset name (built-in or procedural/generated registered via patch_prepare_asset)")
    parser.add_argument("--baseline", required=True, choices=["xatlas_classical", "partuv", "blender_uv", "matched_oracle"])
    parser.add_argument("--method", default="ours", choices=["ours", "baseline_only"])
    parser.add_argument("--config", default="configs/B3_main.yaml")
    parser.add_argument("--gpu", type=int, default=None, help="CUDA device index before visibility remapping.")
    parser.add_argument("--output-root", default=None)
    parser.add_argument("--data-root", default=None)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--split-seed", type=int, default=None, help="Seed for disjoint proposal/gate/test view-light splits.")
    parser.add_argument("--atlas-resolution", type=int, default=None)
    parser.add_argument("--render-resolution", type=int, default=None)
    parser.add_argument("--precision", default=None, choices=["fp32", "float32", "fp16", "float16", "bf16", "bfloat16"])
    parser.add_argument("--no-lpips", action="store_true")
    return parser.parse_args()


def load_config(path: str | Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


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


def _metric_or_none(value: Any):
    if value is None:
        return None
    if value == float("inf"):
        return "inf"
    return float(value)


def _round_list(tensor, digits: int = 8) -> list[float]:
    values = tensor.detach().to("cpu").flatten().tolist()
    return [round(float(v), digits) for v in values]


def _numeric(value: Any) -> float | None:
    if value is None or value == "inf":
        return None
    try:
        return float(value)
    except Exception:
        return None


def _repair_config_from_mapping(payload: dict[str, Any]):
    from pbr_atlas.method import RepairConfig

    fields = RepairConfig.__dataclass_fields__
    return RepairConfig(**{key: value for key, value in dict(payload or {}).items() if key in fields})


def _split_counts(
    mapping: dict[str, Any],
    *,
    legacy_train: str,
    legacy_holdout: str,
    default_proposal: int,
    default_gate: int,
    default_test: int,
) -> dict[str, int]:
    """Read A1 split counts, with backward compatibility for train/holdout configs."""

    if any(key in mapping for key in ("proposal", "gate", "test")):
        return {
            "proposal": int(mapping.get("proposal", mapping.get(legacy_train, default_proposal))),
            "gate": int(mapping.get("gate", mapping.get(legacy_holdout, default_gate))),
            "test": int(mapping.get("test", mapping.get(legacy_holdout, default_test))),
        }
    train = int(mapping.get(legacy_train, default_proposal))
    holdout = int(mapping.get(legacy_holdout, default_gate))
    return {"proposal": train, "gate": holdout, "test": int(mapping.get("test", default_test if legacy_holdout not in mapping else holdout))}


def _residual_stats(residual) -> dict[str, Any]:
    return {
        "e_f": _round_list(residual.e_f),
        "E_c": _round_list(residual.E_c),
        "G_l": _round_list(residual.G_l),
        "e_f_mean": float(residual.e_f.mean().detach().cpu()) if residual.e_f.numel() else 0.0,
        "e_f_max": float(residual.e_f.max().detach().cpu()) if residual.e_f.numel() else 0.0,
        "E_c_mean": float(residual.E_c.mean().detach().cpu()) if residual.E_c.numel() else 0.0,
        "G_l_mean": float(residual.G_l.mean().detach().cpu()) if residual.G_l.numel() else 0.0,
        "seam_residual_mean": float(residual.seam_residual.mean().detach().cpu()) if residual.seam_residual.numel() else 0.0,
    }


def _evaluate_atlas(
    *,
    baker,
    mesh,
    atlas,
    face_values,
    target_mesh,
    target_maps,
    target_images,
    views,
    lights,
    mip_levels: int,
    compute_lpips: bool,
    seam_loss_fn,
) -> dict[str, Any]:
    import torch

    from pbr_atlas.baker.residual import compute_residual_attribution
    from pbr_atlas.baselines import clone_mesh_with_atlas
    from pbr_atlas.eval.metrics import image_metrics, normal_angular_error, per_channel_mae
    from pbr_atlas.method import channel_seam_metrics

    with torch.no_grad():
        candidate_mesh = clone_mesh_with_atlas(mesh, atlas, device=baker.device)
        maps = baker.bake(candidate_mesh, face_values)
        pred_render = baker.render(candidate_mesh, maps, views, lights)
    relit_metrics = image_metrics(pred_render.images, target_images, compute_lpips=compute_lpips)
    pbr_mae = per_channel_mae(
        {
            "albedo": maps.albedo,
            "roughness": maps.roughness,
            "metallic": maps.metallic,
        },
        {
            "albedo": target_maps.albedo,
            "roughness": target_maps.roughness,
            "metallic": target_maps.metallic,
        },
    )
    pbr_mae["normal_angular_error_deg"] = normal_angular_error(maps.normal, target_maps.normal)
    residual = compute_residual_attribution(
        pred=pred_render.images,
        target=target_images,
        face_ids=pred_render.face_ids,
        alpha=pred_render.alpha,
        mesh=candidate_mesh,
        maps=maps,
        chart_ids=candidate_mesh.chart_ids,
        mip_levels=int(mip_levels),
    )
    seam_loss = seam_loss_fn(maps, candidate_mesh, candidate_mesh.chart_ids)
    return {
        "mesh": candidate_mesh,
        "maps": maps,
        "pred_images": pred_render.images,
        "relit": {key: _metric_or_none(value) for key, value in relit_metrics.items()},
        "pbr_channel": pbr_mae,
        "residual": residual,
        "residual_stats": _residual_stats(residual),
        "c4": {
            "loss": float(seam_loss.detach().cpu()),
            **channel_seam_metrics(maps, candidate_mesh, candidate_mesh.chart_ids),
        },
    }


def _c5_guard(
    *,
    mesh,
    baseline_atlas,
    candidate_atlas,
    initial_eval: dict[str, Any],
    final_eval: dict[str, Any],
    matched_cfg,
    c5_cfg: dict[str, Any],
) -> dict[str, Any]:
    from pbr_atlas.baselines.matched_protocol import compute_atlas_stats

    base_stats = compute_atlas_stats(mesh, baseline_atlas, raster_resolution=matched_cfg.raster_resolution)
    cand_stats = compute_atlas_stats(mesh, candidate_atlas, raster_resolution=matched_cfg.raster_resolution)
    chart_delta = int(cand_stats.chart_count - base_stats.chart_count)
    max_chart_delta = max(1, int(base_stats.chart_count * float(matched_cfg.chart_count_window) + 0.999))
    distortion_limit = float(base_stats.max_distortion_q95 + float(c5_cfg.get("distortion_tail_epsilon", 3.0)))

    violations: list[str] = []
    if int(candidate_atlas.atlas_size) != int(baseline_atlas.atlas_size):
        violations.append("atlas_size_changed")
    if int(candidate_atlas.padding) != int(baseline_atlas.padding):
        violations.append("padding_changed")
    if abs(chart_delta) > max_chart_delta:
        violations.append(f"chart_delta={chart_delta} exceeds {max_chart_delta}")
    if cand_stats.max_distortion_q95 > distortion_limit:
        violations.append(f"distortion_q95={cand_stats.max_distortion_q95:.4f} exceeds {distortion_limit:.4f}")

    initial_psnr = _numeric(initial_eval["relit"].get("psnr"))
    final_psnr = _numeric(final_eval["relit"].get("psnr"))
    delta_psnr = None if initial_psnr is None or final_psnr is None else final_psnr - initial_psnr
    initial_seam = float(initial_eval["residual_stats"].get("seam_residual_mean", 0.0))
    final_seam = float(final_eval["residual_stats"].get("seam_residual_mean", 0.0))
    seam_relative_delta = 0.0 if initial_seam <= 1.0e-8 else (final_seam - initial_seam) / initial_seam
    delta_psnr_min = float(c5_cfg.get("delta_psnr_min", 0.3))
    seam_drop_min = float(c5_cfg.get("seam_residual_drop_min", 0.12))
    metric_accept = (delta_psnr is not None and delta_psnr >= delta_psnr_min) and (seam_relative_delta <= -seam_drop_min)
    hard_accept = not violations
    return {
        "hard_accept": hard_accept,
        "metric_accept": bool(metric_accept),
        "accept": bool(hard_accept and metric_accept),
        "violations": violations,
        "delta_psnr": delta_psnr,
        "seam_relative_delta": seam_relative_delta,
        "chart_count_delta": chart_delta,
        "chart_count_delta_limit": max_chart_delta,
        "distortion_q95": cand_stats.max_distortion_q95,
        "distortion_q95_limit": distortion_limit,
        "baseline_stats": base_stats.to_dict(),
        "candidate_stats": cand_stats.to_dict(),
    }


def _failure_summary(asset: str, baseline: str, method: str, reason: str) -> str:
    return (
        "# B3 Main Summary\n\n"
        f"- asset: {asset}\n"
        f"- baseline: {baseline}\n"
        f"- method: {method}\n"
        "- repro_status: failed\n"
        f"- failure_reason: {reason}\n"
    )


def main() -> None:
    args = parse_args()
    if args.gpu is not None:
        os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpu)

    import torch

    from pbr_atlas.baker import DifferentiablePBRBaker, make_view_light_splits, sample_face_pbr_from_maps
    from pbr_atlas.baselines import clone_mesh_with_atlas, create_backend
    from pbr_atlas.baselines.base import BaselineAtlas, repack_existing_charts
    from pbr_atlas.baselines.matched_protocol import MatchedProtocolConfig, enforce
    from pbr_atlas.data import generate_synthetic_oracle_pbr, prepare_asset
    from pbr_atlas.data.mesh_loader import load_mesh
    from pbr_atlas.method import (
        CrossChannelSeamLoss,
        LocalChartRepair,
        MipAwareAllocator,
        allocation_to_chart_scales,
        estimate_face_pbr_frequency,
        estimate_face_visibility,
    )
    from pbr_atlas.utils import (
        atomic_write_json,
        directory_size_mb,
        ensure_dir,
        save_npz,
        save_residual_atlas_png,
        save_residual_chain_png,
        set_global_seed,
        write_text,
    )

    cfg = load_config(args.config)
    seed = int(args.seed if args.seed is not None else cfg.get("seed", 42))
    split_seed = int(args.split_seed if args.split_seed is not None else cfg.get("split_seed", seed))
    atlas_resolution = int(args.atlas_resolution or cfg.get("atlas_resolution", 1024))
    render_resolution = int(args.render_resolution or cfg.get("render_resolution", 256))
    precision = args.precision or cfg.get("precision", "bf16")
    output_root = Path(args.output_root or cfg.get("output_root", "/data/dip_1_ws/runs/B3_main"))
    run_id = args.run_id or f"{args.asset}_{args.baseline}_{args.method}_seed{seed}_split{split_seed}"
    run_dir = ensure_dir(output_root / run_id)
    data_root = Path(args.data_root or cfg.get("data_root", "/data/dip_1_ws/datasets/sample"))
    vis_resolution = int(cfg.get("visualization_resolution", min(atlas_resolution, 1024)))
    mip_levels = int(cfg.get("mip_levels", 4))
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
            metadata={"warning": "xatlas reference unavailable; fell back to input mesh UV."},
            repro_status="partial",
            failure_reason="xatlas reference unavailable",
        )

    oracle_reference = create_backend("matched_oracle", baseline_cfg.get("matched_oracle", {})).generate(mesh, atlas_resolution, padding)
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
    save_npz(run_dir / "initial_atlas.npz", uv=candidate_atlas.uv, face_uv=candidate_atlas.face_uv, chart_ids=candidate_atlas.chart_ids)

    base_metrics = {
        "block": "B3_main",
        "asset": args.asset,
        "baseline": args.baseline,
        "method": args.method,
        "seed": seed,
        "split_seed": split_seed,
        "device": str(device),
        "precision": precision,
        "atlas_resolution": atlas_resolution,
        "render_resolution": render_resolution,
        "padding": padding,
        "mesh_path": str(mesh_path),
        "repro_status": candidate_atlas.repro_status,
        "failure_reason": candidate_atlas.failure_reason,
        "baseline_metadata": candidate_atlas.metadata,
        "matched_protocol_initial": matched_report.to_dict(),
    }
    if candidate_atlas.repro_status == "failed":
        metrics = dict(base_metrics)
        atomic_write_json(run_dir / "metrics.json", metrics)
        write_text(run_dir / "summary.md", _failure_summary(args.asset, args.baseline, args.method, candidate_atlas.failure_reason or "unknown failure"))
        print(str(run_dir))
        return

    view_cfg = cfg.get("views", {})
    light_cfg = cfg.get("lights", {})
    split_counts = {
        "views": _split_counts(
            dict(view_cfg),
            legacy_train="train",
            legacy_holdout="holdout",
            default_proposal=6,
            default_gate=4,
            default_test=4,
        ),
        "lights": _split_counts(
            dict(light_cfg),
            legacy_train="train",
            legacy_holdout="holdout",
            default_proposal=4,
            default_gate=4,
            default_test=4,
        ),
    }
    splits = make_view_light_splits(split_counts["views"], split_counts["lights"], split_seed=split_seed, device=device)
    proposal_views, proposal_lights = splits.proposal.views, splits.proposal.lights
    gate_views, gate_lights = splits.gate.views, splits.gate.lights
    test_views, test_lights = splits.test.views, splits.test.lights
    base_metrics["splits"] = splits.to_metadata()

    oracle_cfg = cfg.get("oracle_pbr", {})
    oracle_maps = generate_synthetic_oracle_pbr(
        mesh,
        seed=seed,
        pattern=str(oracle_cfg.get("pattern", "voronoi_albedo+smooth_normal+region_roughness")),
        resolution=atlas_resolution,
        num_voronoi_seeds=int(oracle_cfg.get("num_voronoi_seeds", 16)),
        device=device,
    )
    oracle_mesh = clone_mesh_with_atlas(mesh, oracle_reference, device=device)
    face_values = sample_face_pbr_from_maps(oracle_mesh, oracle_maps)
    with torch.no_grad():
        oracle_baked_maps = baker.bake(oracle_mesh, face_values)
        proposal_target_render = baker.render(oracle_mesh, oracle_baked_maps, proposal_views, proposal_lights)
        gate_target_render = baker.render(oracle_mesh, oracle_baked_maps, gate_views, gate_lights)
        test_target_render = baker.render(oracle_mesh, oracle_baked_maps, test_views, test_lights)

    seam_loss_fn = CrossChannelSeamLoss(cfg.get("seam_loss", {}).get("channel_weights", {}))
    initial_proposal_eval = _evaluate_atlas(
        baker=baker,
        mesh=mesh,
        atlas=candidate_atlas,
        face_values=face_values,
        target_mesh=oracle_mesh,
        target_maps=oracle_baked_maps,
        target_images=proposal_target_render.images,
        views=proposal_views,
        lights=proposal_lights,
        mip_levels=mip_levels,
        compute_lpips=not args.no_lpips,
        seam_loss_fn=seam_loss_fn,
    )
    initial_gate_eval = _evaluate_atlas(
        baker=baker,
        mesh=mesh,
        atlas=candidate_atlas,
        face_values=face_values,
        target_mesh=oracle_mesh,
        target_maps=oracle_baked_maps,
        target_images=gate_target_render.images,
        views=gate_views,
        lights=gate_lights,
        mip_levels=mip_levels,
        compute_lpips=not args.no_lpips,
        seam_loss_fn=seam_loss_fn,
    )
    initial_test_eval = _evaluate_atlas(
        baker=baker,
        mesh=mesh,
        atlas=candidate_atlas,
        face_values=face_values,
        target_mesh=oracle_mesh,
        target_maps=oracle_baked_maps,
        target_images=test_target_render.images,
        views=test_views,
        lights=test_lights,
        mip_levels=mip_levels,
        compute_lpips=not args.no_lpips,
        seam_loss_fn=seam_loss_fn,
    )

    current_atlas = candidate_atlas
    current_proposal_eval = initial_proposal_eval
    current_gate_eval = initial_gate_eval
    repair_logs: list[dict[str, Any]] = []
    allocation_logs: list[dict[str, Any]] = []
    c5_history: list[dict[str, Any]] = []

    if args.method == "ours":
        repair_cfg_payload = dict(cfg.get("repair", {}))
        outer_iters = int(repair_cfg_payload.get("outer_iters", 3))
        repair_cfg = _repair_config_from_mapping(repair_cfg_payload)
        allocator_cfg = dict(cfg.get("allocator", {}))
        allocator = MipAwareAllocator(
            atlas_size=atlas_resolution,
            w_mip=float(allocator_cfg.get("w_mip", 1.0)),
            w_vis=float(allocator_cfg.get("w_vis", 0.5)),
            w_freq=float(allocator_cfg.get("w_freq", 0.5)),
            w_residual=float(allocator_cfg.get("w_residual", 1.0)),
            temperature=float(allocator_cfg.get("temperature", 1.0)),
            min_texel_fraction=float(allocator_cfg.get("min_texel_fraction", 0.05)),
        )
        for outer_idx in range(max(1, outer_iters)):
            repairer = LocalChartRepair(repair_cfg)
            repaired_atlas, repair_log = repairer.repair(
                baker,
                mesh,
                current_atlas,
                oracle_maps,
                current_proposal_eval["residual"],
                proposal_views=proposal_views,
                proposal_lights=proposal_lights,
            )
            repair_logs.append({"outer_iter": outer_idx, **repair_log.to_dict()})

            repaired_proposal_eval = _evaluate_atlas(
                baker=baker,
                mesh=mesh,
                atlas=repaired_atlas,
                face_values=face_values,
                target_mesh=oracle_mesh,
                target_maps=oracle_baked_maps,
                target_images=proposal_target_render.images,
                views=proposal_views,
                lights=proposal_lights,
                mip_levels=mip_levels,
                compute_lpips=not args.no_lpips,
                seam_loss_fn=seam_loss_fn,
            )
            view_visibility = estimate_face_visibility(repaired_proposal_eval["mesh"], proposal_views)
            pbr_frequency = estimate_face_pbr_frequency(repaired_proposal_eval["mesh"], repaired_proposal_eval["maps"])
            allocation = allocator.allocate(repaired_atlas, repaired_proposal_eval["residual"], view_visibility, pbr_frequency)
            chart_scales = allocation_to_chart_scales(repaired_atlas, allocation)
            alloc_uv, alloc_face_uv, alloc_chart_ids = repack_existing_charts(
                repaired_atlas.uv,
                repaired_atlas.face_uv,
                repaired_atlas.chart_ids,
                atlas_size=atlas_resolution,
                padding=padding,
                chart_scales=chart_scales,
            )
            allocated_atlas = replace(
                repaired_atlas,
                name=f"{repaired_atlas.name}_c3_alloc",
                uv=alloc_uv,
                face_uv=alloc_face_uv,
                chart_ids=alloc_chart_ids,
                metadata={
                    **dict(repaired_atlas.metadata),
                    "c3_allocated": True,
                    "c3_chart_scales": chart_scales,
                },
            )
            allocated_proposal_eval = _evaluate_atlas(
                baker=baker,
                mesh=mesh,
                atlas=allocated_atlas,
                face_values=face_values,
                target_mesh=oracle_mesh,
                target_maps=oracle_baked_maps,
                target_images=proposal_target_render.images,
                views=proposal_views,
                lights=proposal_lights,
                mip_levels=mip_levels,
                compute_lpips=not args.no_lpips,
                seam_loss_fn=seam_loss_fn,
            )
            allocated_gate_eval = _evaluate_atlas(
                baker=baker,
                mesh=mesh,
                atlas=allocated_atlas,
                face_values=face_values,
                target_mesh=oracle_mesh,
                target_maps=oracle_baked_maps,
                target_images=gate_target_render.images,
                views=gate_views,
                lights=gate_lights,
                mip_levels=mip_levels,
                compute_lpips=not args.no_lpips,
                seam_loss_fn=seam_loss_fn,
            )
            allocation_logs.append(
                {
                    "outer_iter": outer_idx,
                    "summary": allocator.last_summary.to_dict() if allocator.last_summary else {},
                    "chart_scales": chart_scales,
                    "c4_loss": allocated_proposal_eval["c4"]["loss"],
                    "split": "proposal",
                }
            )
            guard = _c5_guard(
                mesh=mesh,
                baseline_atlas=candidate_atlas,
                candidate_atlas=allocated_atlas,
                initial_eval=initial_gate_eval,
                final_eval=allocated_gate_eval,
                matched_cfg=matched_cfg,
                c5_cfg=dict(cfg.get("c5_guard", {})),
            )
            c5_history.append({"outer_iter": outer_idx, "split": "gate", **guard})
            # C5 deployment gate: only accept if BOTH hard guard (matched-protocol)
            # AND metric guard (delta-PSNR / seam improvement) are satisfied.
            # FINAL_PROPOSAL §C5: rollback if accept=False.
            if not guard["accept"]:
                break
            current_atlas = allocated_atlas
            current_proposal_eval = allocated_proposal_eval
            current_gate_eval = allocated_gate_eval

    final_atlas = current_atlas
    final_proposal_eval = current_proposal_eval
    final_gate_eval = current_gate_eval
    final_test_eval = _evaluate_atlas(
        baker=baker,
        mesh=mesh,
        atlas=final_atlas,
        face_values=face_values,
        target_mesh=oracle_mesh,
        target_maps=oracle_baked_maps,
        target_images=test_target_render.images,
        views=test_views,
        lights=test_lights,
        mip_levels=mip_levels,
        compute_lpips=not args.no_lpips,
        seam_loss_fn=seam_loss_fn,
    )
    matched_after_repair = enforce(mesh, final_atlas, xatlas_reference, matched_cfg)
    final_guard = _c5_guard(
        mesh=mesh,
        baseline_atlas=candidate_atlas,
        candidate_atlas=final_atlas,
        initial_eval=initial_gate_eval,
        final_eval=final_gate_eval,
        matched_cfg=matched_cfg,
        c5_cfg=dict(cfg.get("c5_guard", {})),
    )
    # If even the initial outer iter was rejected, current_atlas == baseline_atlas
    # and current_*_eval == initial_*_eval, so final == initial automatically.
    # Track explicit rollback flag for honest reporting.
    c5_rollback = (final_atlas is candidate_atlas) or (current_atlas is candidate_atlas)

    save_npz(run_dir / "atlas.npz", uv=final_atlas.uv, face_uv=final_atlas.face_uv, chart_ids=final_atlas.chart_ids)
    save_npz(
        run_dir / "residual_atlas.npz",
        e_f=final_test_eval["residual"].e_f,
        E_c=final_test_eval["residual"].E_c,
        S_e=final_test_eval["residual"].seam_residual,
        seam_edges=final_test_eval["residual"].seam_edges,
        G_l=final_test_eval["residual"].G_l,
    )
    save_npz(
        run_dir / "residual_proposal_atlas.npz",
        e_f=final_proposal_eval["residual"].e_f,
        E_c=final_proposal_eval["residual"].E_c,
        S_e=final_proposal_eval["residual"].seam_residual,
        seam_edges=final_proposal_eval["residual"].seam_edges,
        G_l=final_proposal_eval["residual"].G_l,
    )
    save_residual_atlas_png(run_dir / "residual_atlas.png", final_test_eval["mesh"], final_test_eval["residual"].e_f, resolution=vis_resolution)
    save_residual_atlas_png(run_dir / "residual_initial.png", initial_test_eval["mesh"], initial_test_eval["residual"].e_f, resolution=vis_resolution)
    save_residual_chain_png(
        run_dir / "residual_chain.png",
        [(initial_test_eval["mesh"], initial_test_eval["residual"].e_f), (final_test_eval["mesh"], final_test_eval["residual"].e_f)],
        resolution=vis_resolution,
    )

    accepted_edits = sum(1 for log in repair_logs for edit in log.get("edits", []) if edit.get("accepted"))
    initial_chart_count = int(final_guard["baseline_stats"]["chart_count"])
    peak_memory_gb = 0.0
    if device.type == "cuda":
        peak_memory_gb = float(torch.cuda.max_memory_allocated() / (1024.0**3))
    wall_clock_s = time.time() - started

    metrics = dict(base_metrics)
    metrics.update(
        {
            "repro_status": "ok" if candidate_atlas.repro_status == "ok" else candidate_atlas.repro_status,
            "relit": final_test_eval["relit"],
            "pbr_channel": final_test_eval["pbr_channel"],
            "residual_stats": final_test_eval["residual_stats"],
            "initial": {
                "split": "test",
                "relit": initial_test_eval["relit"],
                "pbr_channel": initial_test_eval["pbr_channel"],
                "residual_stats": initial_test_eval["residual_stats"],
                "c4": initial_test_eval["c4"],
            },
            "final": {
                "split": "test",
                "relit": final_test_eval["relit"],
                "pbr_channel": final_test_eval["pbr_channel"],
                "residual_stats": final_test_eval["residual_stats"],
                "c4": final_test_eval["c4"],
            },
            "proposal": {
                "initial": {
                    "relit": initial_proposal_eval["relit"],
                    "pbr_channel": initial_proposal_eval["pbr_channel"],
                    "residual_stats": initial_proposal_eval["residual_stats"],
                    "c4": initial_proposal_eval["c4"],
                },
                "final": {
                    "relit": final_proposal_eval["relit"],
                    "pbr_channel": final_proposal_eval["pbr_channel"],
                    "residual_stats": final_proposal_eval["residual_stats"],
                    "c4": final_proposal_eval["c4"],
                },
            },
            "gate": {
                "initial": {
                    "relit": initial_gate_eval["relit"],
                    "pbr_channel": initial_gate_eval["pbr_channel"],
                    "residual_stats": initial_gate_eval["residual_stats"],
                    "c4": initial_gate_eval["c4"],
                },
                "final": {
                    "relit": final_gate_eval["relit"],
                    "pbr_channel": final_gate_eval["pbr_channel"],
                    "residual_stats": final_gate_eval["residual_stats"],
                    "c4": final_gate_eval["c4"],
                },
            },
            "repair": {
                "enabled": args.method == "ours",
                "outer_logs": repair_logs,
                "edit_chart_count": accepted_edits,
                "edited_chart_ratio": float(accepted_edits) / float(max(initial_chart_count, 1)),
                "chart_count_delta": final_guard["chart_count_delta"],
            },
            "allocator": {
                "enabled": args.method == "ours",
                "outer_logs": allocation_logs,
            },
            "c4_seam": {
                "initial": initial_test_eval["c4"],
                "final": final_test_eval["c4"],
            },
            "c5": {
                **final_guard,
                "history": c5_history,
                "matched_protocol_after_repair": matched_after_repair.to_dict(),
                "rollback_to_baseline": bool(c5_rollback),
            },
            "peak_memory_GB": peak_memory_gb,
            "wall_clock_s": wall_clock_s,
            "outputs": {
                "metrics": str(run_dir / "metrics.json"),
                "atlas_npz": str(run_dir / "atlas.npz"),
                "residual_npz": str(run_dir / "residual_atlas.npz"),
                "residual_proposal_npz": str(run_dir / "residual_proposal_atlas.npz"),
                "residual_png": str(run_dir / "residual_atlas.png"),
                "residual_chain_png": str(run_dir / "residual_chain.png"),
                "summary": str(run_dir / "summary.md"),
                "repair_log": str(run_dir / "repair_log.json"),
            },
        }
    )
    atomic_write_json(run_dir / "repair_log.json", {"repair": repair_logs, "allocator": allocation_logs, "c5": c5_history})
    atomic_write_json(run_dir / "metrics.json", metrics)
    output_size_mb = directory_size_mb(run_dir)
    metrics["storage"] = {"output_size_MB": output_size_mb}
    atomic_write_json(run_dir / "metrics.json", metrics)

    summary = (
        "# B3 Main Summary\n\n"
        f"- asset: {args.asset}\n"
        f"- baseline: {args.baseline}\n"
        f"- method: {args.method}\n"
        f"- repro_status: {metrics['repro_status']}\n"
        f"- split seed: {split_seed}\n"
        f"- initial PSNR (test): {initial_test_eval['relit'].get('psnr')}\n"
        f"- final PSNR (test): {final_test_eval['relit'].get('psnr')}\n"
        f"- LPIPS (test): {final_test_eval['relit'].get('lpips')}\n"
        f"- gate delta PSNR: {final_guard['delta_psnr']}\n"
        f"- E_c mean (test): {final_test_eval['residual_stats']['E_c_mean']:.8f}\n"
        f"- G_l mean (test): {final_test_eval['residual_stats']['G_l_mean']:.8f}\n"
        f"- C4 seam loss (test): {final_test_eval['c4']['loss']:.8f}\n"
        f"- edited chart ratio: {metrics['repair']['edited_chart_ratio']:.6f}\n"
        f"- C5 hard accept: {final_guard['hard_accept']}\n"
        f"- C5 metric accept: {final_guard['metric_accept']}\n"
        f"- C5 rollback to baseline: {bool(c5_rollback)}\n"
        f"- matched after repair violated: {matched_after_repair.matched_constraint_violated}\n"
        f"- peak memory GB: {peak_memory_gb:.3f}\n"
        f"- wall clock s: {wall_clock_s:.3f}\n"
    )
    write_text(run_dir / "summary.md", summary)
    print(str(run_dir))


if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""DiLiGenT-MV captured-target runner for the C1-C5 atlas repair pipeline.

This is a slim wrapper that reuses the same baking, repair, and gate
helpers as ``run_B3.py``, but feeds in CAPTURED imagery as the target
signal instead of synthetic oracle renders. For the first pass we use
synthetic oracle face PBR values to drive baking; future revisions will
replace those with photometric-stereo estimates.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import torch
import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pbr_atlas.baker import (
    DifferentiablePBRBaker,
    make_view_light_splits,
    sample_face_pbr_from_maps,
)
from pbr_atlas.baker.captured_target import build_captured_split, captured_split_to_render_output
from pbr_atlas.baselines import clone_mesh_with_atlas, create_backend
from pbr_atlas.data import generate_synthetic_oracle_pbr
from pbr_atlas.data.diligent_mv import (
    DILIGENT_MV_OBJECTS,
    load_diligent_mv_asset,
    view_lights_to_specs,
    view_to_view_spec,
)
import importlib.util
_run_b3_spec = importlib.util.spec_from_file_location("_run_b3_helpers", str(ROOT / "scripts" / "run_B3.py"))
_run_b3 = importlib.util.module_from_spec(_run_b3_spec)
sys.modules["_run_b3_helpers"] = _run_b3
_run_b3_spec.loader.exec_module(_run_b3)
_evaluate_atlas = _run_b3._evaluate_atlas
_repair_config_from_mapping = _run_b3._repair_config_from_mapping
_c5_guard = _run_b3._c5_guard

from pbr_atlas.method.chart_repair import LocalChartRepair
from pbr_atlas.method.texel_alloc import MipAwareAllocator
from pbr_atlas.method.seam_coupling import CrossChannelSeamLoss
from pbr_atlas.utils.io import atomic_write_json, ensure_dir, save_npz


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--asset", required=True, choices=list(DILIGENT_MV_OBJECTS))
    p.add_argument("--baseline", default="xatlas_classical", choices=["xatlas_classical", "blender_uv", "partuv"])
    p.add_argument("--method", default="ours", choices=["ours", "baseline_only"])
    p.add_argument("--config", default="configs/B3_main.yaml")
    p.add_argument("--root", default="datasets/diligent_mv/extracted/DiLiGenT-MV/mvpmsData")
    p.add_argument("--output-root", default="runs/W1_diligent_mv")
    p.add_argument("--run-id", default=None)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--split-seed", type=int, default=42)
    p.add_argument("--max-views", type=int, default=None, help="Cap views for smoke")
    p.add_argument("--max-lights", type=int, default=None, help="Cap lights for smoke")
    p.add_argument("--no-lpips", action="store_true")
    p.add_argument("--use-pms", action="store_true", help="Replace synthetic oracle face_values with Lambertian PMS fit on captured imagery")
    p.add_argument("--render-resolution", type=int, default=256)
    p.add_argument("--proposal-views", type=int, default=10)
    p.add_argument("--gate-views", type=int, default=5)
    p.add_argument("--test-views", type=int, default=5)
    p.add_argument("--proposal-lights", type=int, default=48)
    p.add_argument("--gate-lights", type=int, default=24)
    p.add_argument("--test-lights", type=int, default=24)
    return p.parse_args()


def _make_view_indices(n_views: int, *, proposal: int, gate: int, test: int, seed: int) -> dict[str, list[int]]:
    g = torch.Generator().manual_seed(seed)
    perm = torch.randperm(n_views, generator=g).tolist()
    if proposal + gate + test > n_views:
        raise ValueError(f"Need {proposal+gate+test} views, only {n_views} available")
    out = {
        "proposal": perm[:proposal],
        "gate": perm[proposal:proposal + gate],
        "test": perm[proposal + gate:proposal + gate + test],
    }
    return out


def _make_light_indices(n_lights: int, *, proposal: int, gate: int, test: int, seed: int) -> dict[str, list[int]]:
    g = torch.Generator().manual_seed(seed + 1)
    perm = torch.randperm(n_lights, generator=g).tolist()
    if proposal + gate + test > n_lights:
        raise ValueError(f"Need {proposal+gate+test} lights, only {n_lights} available")
    return {
        "proposal": perm[:proposal],
        "gate": perm[proposal:proposal + gate],
        "test": perm[proposal + gate:proposal + gate + test],
    }


def _flatten_view_light_specs(asset, view_idx_list: list[int], light_idx_list: list[int]):
    """Return distinct ViewSpecs and LightSpecs for the (V, L) Cartesian product.

    Baker.render() iterates views x lights internally, so we return one
    ViewSpec per view and one LightSpec per light index (using view 0 as
    the canonical source for light directions).
    """
    views = [view_to_view_spec(asset.views[vi]) for vi in view_idx_list]
    canonical_view = asset.views[view_idx_list[0]] if view_idx_list else asset.views[0]
    lights = view_lights_to_specs(canonical_view, list(light_idx_list))
    return views, lights


def main() -> None:
    args = parse_args()
    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8")) or {}
    started = time.time()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    asset = load_diligent_mv_asset(
        args.asset,
        args.root,
        max_views=args.max_views,
        max_lights=args.max_lights,
        device=device,
    )
    n_views = asset.num_views()
    n_lights = asset.num_lights_per_view()

    view_idx = _make_view_indices(
        n_views,
        proposal=min(args.proposal_views, n_views),
        gate=min(args.gate_views, max(1, n_views - args.proposal_views)),
        test=min(args.test_views, max(1, n_views - args.proposal_views - args.gate_views)),
        seed=args.split_seed,
    )
    light_idx = _make_light_indices(
        n_lights,
        proposal=min(args.proposal_lights, n_lights),
        gate=min(args.gate_lights, max(1, n_lights - args.proposal_lights)),
        test=min(args.test_lights, max(1, n_lights - args.proposal_lights - args.gate_lights)),
        seed=args.split_seed,
    )

    atlas_resolution = int(cfg.get("atlas_resolution", 1024))
    padding = int(cfg.get("padding", 8))
    baker = DifferentiablePBRBaker(
        atlas_resolution=atlas_resolution,
        render_resolution=args.render_resolution,
        precision=str(cfg.get("precision", "bf16")),
        gradient_checkpointing=False,
        device=device,
    )

    mesh = asset.mesh.to(device)
    backend = create_backend(args.baseline, cfg.get("baselines", {}).get(args.baseline, {}))
    candidate_atlas = backend.generate(mesh, atlas_resolution, padding)
    if candidate_atlas.repro_status == "failed":
        raise RuntimeError(f"baseline {args.baseline} failed: {candidate_atlas.failure_reason}")

    xatlas_ref = create_backend("xatlas_classical", {}).generate(mesh, atlas_resolution, padding)
    oracle_mesh = clone_mesh_with_atlas(mesh, xatlas_ref, device=device)
    if args.use_pms:
        from pbr_atlas.data.diligent_pms import fit_lambertian_pms
        # Use proposal-split lights so we don't leak gate/test info into the prior.
        pms_result = fit_lambertian_pms(
            asset,
            view_indices=view_idx["proposal"] + view_idx["gate"],
            light_indices=light_idx["proposal"],
            device=device,
        )
        face_values = pms_result.face_pbr
        oracle_maps = generate_synthetic_oracle_pbr(
            mesh, seed=args.seed, resolution=atlas_resolution, device=device,
        )  # kept for residual_atlas oracle reference; not used in baking
        print(f"  PMS fit: {pms_result.fit_count}/{pms_result.fit_count + pms_result.skipped_faces} faces, mean residual {pms_result.fit_residual_per_face.mean().item():.4f}")
    else:
        # Synthetic oracle face values for the baker (default); captured imagery is target.
        oracle_maps = generate_synthetic_oracle_pbr(
            mesh, seed=args.seed, resolution=atlas_resolution, device=device,
        )
        face_values = sample_face_pbr_from_maps(oracle_mesh, oracle_maps)

    proposal_views, proposal_lights = _flatten_view_light_specs(asset, view_idx["proposal"], light_idx["proposal"])
    gate_views, gate_lights = _flatten_view_light_specs(asset, view_idx["gate"], light_idx["gate"])
    test_views, test_lights = _flatten_view_light_specs(asset, view_idx["test"], light_idx["test"])

    proposal_split = build_captured_split(asset, view_idx["proposal"], light_idx["proposal"], render_resolution=args.render_resolution)
    gate_split = build_captured_split(asset, view_idx["gate"], light_idx["gate"], render_resolution=args.render_resolution)
    test_split = build_captured_split(asset, view_idx["test"], light_idx["test"], render_resolution=args.render_resolution)
    proposal_target = captured_split_to_render_output(proposal_split, device=device)
    gate_target = captured_split_to_render_output(gate_split, device=device)
    test_target = captured_split_to_render_output(test_split, device=device)

    seam_loss_fn = CrossChannelSeamLoss(cfg.get("seam_loss", {}).get("channel_weights", {}))
    mip_levels = int(cfg.get("mip_levels", 4))
    with torch.no_grad():
        oracle_baked = baker.bake(oracle_mesh, face_values)
    initial_proposal_eval = _evaluate_atlas(
        baker=baker, mesh=mesh, atlas=candidate_atlas, face_values=face_values,
        target_mesh=oracle_mesh, target_maps=oracle_baked,
        target_images=proposal_target.images,
        views=proposal_views, lights=proposal_lights,
        mip_levels=mip_levels, compute_lpips=not args.no_lpips, seam_loss_fn=seam_loss_fn,
    )
    initial_test_eval = _evaluate_atlas(
        baker=baker, mesh=mesh, atlas=candidate_atlas, face_values=face_values,
        target_mesh=oracle_mesh, target_maps=oracle_baked,
        target_images=test_target.images,
        views=test_views, lights=test_lights,
        mip_levels=mip_levels, compute_lpips=not args.no_lpips, seam_loss_fn=seam_loss_fn,
    )

    from pbr_atlas.baselines.matched_protocol import MatchedProtocolConfig
    matched_cfg = MatchedProtocolConfig.from_mapping(cfg.get("matched_protocol"))
    final_atlas = candidate_atlas
    final_test_eval = initial_test_eval
    repair_logs: list[dict[str, Any]] = []
    c5_rollback = True

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
        current_atlas = candidate_atlas
        current_proposal_eval = initial_proposal_eval
        for outer_idx in range(max(1, outer_iters)):
            repairer = LocalChartRepair(repair_cfg)
            repaired_atlas, log = repairer.repair(
                baker, mesh, current_atlas, oracle_maps,
                current_proposal_eval["residual"],
                proposal_views=proposal_views, proposal_lights=proposal_lights,
            )
            log_dict = log.to_dict() if hasattr(log, "to_dict") else dict(log)
            log_dict["outer_iter"] = outer_idx
            repair_logs.append(log_dict)
            cand_proposal_eval = _evaluate_atlas(
                baker=baker, mesh=mesh, atlas=repaired_atlas, face_values=face_values,
                target_mesh=oracle_mesh, target_maps=oracle_baked,
                target_images=proposal_target.images,
                views=proposal_views, lights=proposal_lights,
                mip_levels=mip_levels, compute_lpips=not args.no_lpips, seam_loss_fn=seam_loss_fn,
            )
            cand_gate_eval = _evaluate_atlas(
                baker=baker, mesh=mesh, atlas=repaired_atlas, face_values=face_values,
                target_mesh=oracle_mesh, target_maps=oracle_baked,
                target_images=gate_target.images,
                views=gate_views, lights=gate_lights,
                mip_levels=mip_levels, compute_lpips=not args.no_lpips, seam_loss_fn=seam_loss_fn,
            )
            initial_gate_eval = _evaluate_atlas(
                baker=baker, mesh=mesh, atlas=current_atlas, face_values=face_values,
                target_mesh=oracle_mesh, target_maps=oracle_baked,
                target_images=gate_target.images,
                views=gate_views, lights=gate_lights,
                mip_levels=mip_levels, compute_lpips=not args.no_lpips, seam_loss_fn=seam_loss_fn,
            )
            guard = _c5_guard(
                mesh=mesh,
                baseline_atlas=candidate_atlas,  # always against original baseline (matches run_B3 semantics)
                candidate_atlas=repaired_atlas,
                initial_eval=initial_gate_eval, final_eval=cand_gate_eval,
                matched_cfg=matched_cfg,
                c5_cfg=dict(cfg.get("c5_guard", {})),
            )
            guard["outer_iter"] = outer_idx
            if guard.get("accept"):
                current_atlas = repaired_atlas
                current_proposal_eval = cand_proposal_eval
                c5_rollback = False
            else:
                break

        final_atlas = current_atlas
        final_test_eval = _evaluate_atlas(
            baker=baker, mesh=mesh, atlas=final_atlas, face_values=face_values,
            target_mesh=oracle_mesh, target_maps=oracle_baked,
            target_images=test_target.images,
            views=test_views, lights=test_lights,
            mip_levels=mip_levels, compute_lpips=not args.no_lpips, seam_loss_fn=seam_loss_fn,
        )

    run_id = args.run_id or f"{args.asset}_{args.baseline}_{args.method}_split{args.split_seed}_seed{args.seed}"
    run_dir = ensure_dir(Path(args.output_root) / run_id)

    save_npz(run_dir / "atlas.npz", uv=final_atlas.uv, face_uv=final_atlas.face_uv, chart_ids=final_atlas.chart_ids)
    save_npz(run_dir / "initial_atlas.npz", uv=candidate_atlas.uv, face_uv=candidate_atlas.face_uv, chart_ids=candidate_atlas.chart_ids)

    metrics = {
        "asset": args.asset,
        "baseline": args.baseline,
        "method": args.method,
        "block": "W1_diligent_mv",
        "device": str(device),
        "atlas_resolution": atlas_resolution,
        "padding": padding,
        "render_resolution": args.render_resolution,
        "split_seed": args.split_seed,
        "seed": args.seed,
        "splits": {
            "proposal_views": view_idx["proposal"],
            "gate_views": view_idx["gate"],
            "test_views": view_idx["test"],
            "proposal_lights": light_idx["proposal"],
            "gate_lights": light_idx["gate"],
            "test_lights": light_idx["test"],
        },
        "initial": {
            "relit": {
                "psnr": initial_test_eval["relit"]["psnr"],
                "ssim": initial_test_eval["relit"]["ssim"],
                "lpips": initial_test_eval["relit"].get("lpips"),
            },
        },
        "final": {
            "relit": {
                "psnr": final_test_eval["relit"]["psnr"],
                "ssim": final_test_eval["relit"]["ssim"],
                "lpips": final_test_eval["relit"].get("lpips"),
            },
        },
        "rolled_back": c5_rollback,
        "wall_clock_s": time.time() - started,
        "peak_memory_GB": float(torch.cuda.max_memory_allocated() / (1024.0**3)) if device.type == "cuda" else 0.0,
        "repair_logs": repair_logs,
    }
    atomic_write_json(run_dir / "metrics.json", metrics)
    print(f"  init psnr={initial_test_eval['relit']['psnr']:.3f}  final psnr={final_test_eval['relit']['psnr']:.3f}  rollback={c5_rollback}")
    print(f"Wrote {run_dir / 'metrics.json'}")


if __name__ == "__main__":
    main()

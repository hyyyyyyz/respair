#!/usr/bin/env python
"""W3 Polyhaven CC0 PBR external-validity track.

For each Polyhaven model with authored PBR maps, treat the authored
(albedo / normal / metallicRoughness) values as the oracle face PBR and
run the C1-C5 pipeline against renders of those values as the target.

The expectation is that authored PBR + held-out HDRI relighting produces
a more diverse residual structure than the synthetic voronoi oracle, so
PartUV-initialized atlases on some Polyhaven assets will show
residual-backed atlas leverage.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import time
from dataclasses import replace
from pathlib import Path

import torch
import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pbr_atlas.baker import DifferentiablePBRBaker, make_view_light_splits
from pbr_atlas.baselines import clone_mesh_with_atlas, create_backend
from pbr_atlas.baselines.matched_protocol import MatchedProtocolConfig
from pbr_atlas.data.polyhaven import POLYHAVEN_SLUGS_DEFAULT, load_polyhaven_asset
from pbr_atlas.method.texel_alloc import MipAwareAllocator
from pbr_atlas.method.chart_repair import LocalChartRepair
from pbr_atlas.method.seam_coupling import CrossChannelSeamLoss
from pbr_atlas.utils.io import atomic_write_json, ensure_dir, save_npz

_run_b3_spec = importlib.util.spec_from_file_location("_run_b3_helpers", str(ROOT / "scripts" / "run_B3.py"))
_run_b3 = importlib.util.module_from_spec(_run_b3_spec)
sys.modules["_run_b3_helpers"] = _run_b3
_run_b3_spec.loader.exec_module(_run_b3)
_evaluate_atlas = _run_b3._evaluate_atlas
_repair_config_from_mapping = _run_b3._repair_config_from_mapping
_c5_guard = _run_b3._c5_guard


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--slug", required=True)
    p.add_argument("--baseline", default="partuv", choices=["xatlas_classical", "partuv", "blender_uv"])
    p.add_argument("--method", default="ours", choices=["baseline_only", "ours"])
    p.add_argument("--config", default="configs/B7_transfer.yaml")
    p.add_argument("--root", default="/data/dip_1_ws/datasets/polyhaven_proxy/raw")
    p.add_argument("--output-root", default="/data/dip_1_ws/runs/W3_polyhaven")
    p.add_argument("--run-id", default=None)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--split-seed", type=int, default=42)
    p.add_argument("--no-lpips", action="store_true")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8")) or {}
    started = time.time()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    asset = load_polyhaven_asset(args.slug, args.root, device=device)
    mesh = asset.mesh
    face_values = asset.face_pbr

    atlas_resolution = int(cfg.get("atlas_resolution", 1024))
    padding = int(cfg.get("padding", 8))
    baker = DifferentiablePBRBaker(
        atlas_resolution=atlas_resolution,
        render_resolution=int(cfg.get("render_resolution", 256)),
        precision=str(cfg.get("precision", "bf16")),
        gradient_checkpointing=False,
        device=device,
    )

    backend = create_backend(args.baseline, cfg.get("baselines", {}).get(args.baseline, {}))
    candidate_atlas = backend.generate(mesh, atlas_resolution, padding)
    if candidate_atlas.repro_status == "failed":
        raise RuntimeError(f"baseline {args.baseline} failed: {candidate_atlas.failure_reason}")

    xatlas_ref = create_backend("xatlas_classical", {}).generate(mesh, atlas_resolution, padding)
    oracle_mesh = clone_mesh_with_atlas(mesh, xatlas_ref, device=device)

    splits = make_view_light_splits({"proposal": 6, "gate": 4, "test": 4}, {"proposal": 4, "gate": 4, "test": 4}, split_seed=args.split_seed, device=device)
    proposal_views, proposal_lights = splits.proposal.views, splits.proposal.lights
    gate_views, gate_lights = splits.gate.views, splits.gate.lights
    test_views, test_lights = splits.test.views, splits.test.lights

    with torch.no_grad():
        oracle_baked = baker.bake(oracle_mesh, face_values)
        proposal_target = baker.render(oracle_mesh, oracle_baked, proposal_views, proposal_lights)
        gate_target = baker.render(oracle_mesh, oracle_baked, gate_views, gate_lights)
        test_target = baker.render(oracle_mesh, oracle_baked, test_views, test_lights)

    seam_loss_fn = CrossChannelSeamLoss(cfg.get("seam_loss", {}).get("channel_weights", {}))
    mip_levels = int(cfg.get("mip_levels", 4))

    matched_cfg = MatchedProtocolConfig.from_mapping(cfg.get("matched_protocol"))

    def eval_atlas(atlas, target_images, views, lights):
        return _evaluate_atlas(
            baker=baker, mesh=mesh, atlas=atlas, face_values=face_values,
            target_mesh=oracle_mesh, target_maps=oracle_baked,
            target_images=target_images, views=views, lights=lights,
            mip_levels=mip_levels, compute_lpips=not args.no_lpips,
            seam_loss_fn=seam_loss_fn,
        )

    initial_proposal_eval = eval_atlas(candidate_atlas, proposal_target.images, proposal_views, proposal_lights)
    initial_test_eval = eval_atlas(candidate_atlas, test_target.images, test_views, test_lights)

    final_atlas = candidate_atlas
    final_test_eval = initial_test_eval
    c5_rollback = True
    repair_logs: list = []

    if args.method == "ours":
        repair_cfg_payload = dict(cfg.get("repair", {}))
        outer_iters = int(repair_cfg_payload.get("outer_iters", 3))
        repair_cfg = _repair_config_from_mapping(repair_cfg_payload)
        current_atlas = candidate_atlas
        current_proposal_eval = initial_proposal_eval
        for outer_idx in range(max(1, outer_iters)):
            repairer = LocalChartRepair(repair_cfg)
            repaired_atlas, log = repairer.repair(
                baker, mesh, current_atlas, oracle_baked,
                current_proposal_eval["residual"],
                proposal_views=proposal_views, proposal_lights=proposal_lights,
            )
            cand_proposal_eval = eval_atlas(repaired_atlas, proposal_target.images, proposal_views, proposal_lights)
            cand_gate_eval = eval_atlas(repaired_atlas, gate_target.images, gate_views, gate_lights)
            initial_gate_eval = eval_atlas(current_atlas, gate_target.images, gate_views, gate_lights)
            guard = _c5_guard(
                mesh=mesh, baseline_atlas=candidate_atlas, candidate_atlas=repaired_atlas,
                initial_eval=initial_gate_eval, final_eval=cand_gate_eval,
                matched_cfg=matched_cfg, c5_cfg=dict(cfg.get("c5_guard", {})),
            )
            log_dict = log.to_dict() if hasattr(log, "to_dict") else dict(log)
            log_dict["outer_iter"] = outer_idx
            log_dict["guard"] = guard
            repair_logs.append(log_dict)
            if guard.get("accept"):
                current_atlas = repaired_atlas
                current_proposal_eval = cand_proposal_eval
                c5_rollback = False
            else:
                break
        final_atlas = current_atlas
        final_test_eval = eval_atlas(final_atlas, test_target.images, test_views, test_lights)

    run_id = args.run_id or f"{args.slug}_{args.baseline}_{args.method}_seed{args.seed}"
    run_dir = ensure_dir(Path(args.output_root) / run_id)
    save_npz(run_dir / "atlas.npz", uv=final_atlas.uv, face_uv=final_atlas.face_uv, chart_ids=final_atlas.chart_ids)
    save_npz(run_dir / "initial_atlas.npz", uv=candidate_atlas.uv, face_uv=candidate_atlas.face_uv, chart_ids=candidate_atlas.chart_ids)
    metrics = {
        "slug": args.slug, "baseline": args.baseline, "method": args.method,
        "block": "W3_polyhaven", "device": str(device),
        "atlas_resolution": atlas_resolution, "padding": padding,
        "render_resolution": int(cfg.get("render_resolution", 256)),
        "seed": args.seed, "split_seed": args.split_seed,
        "materials_used": asset.materials_used,
        "initial": {"relit": {k: v for k, v in initial_test_eval["relit"].items()}},
        "final": {"relit": {k: v for k, v in final_test_eval["relit"].items()}},
        "rolled_back": c5_rollback,
        "wall_clock_s": time.time() - started,
        "repair_logs": repair_logs,
    }
    atomic_write_json(run_dir / "metrics.json", metrics)
    init_p = initial_test_eval["relit"]["psnr"]; final_p = final_test_eval["relit"]["psnr"]
    print(f"  init={init_p:.3f}  final={final_p:.3f}  delta={final_p-init_p:+.3f}  rb={c5_rollback}")
    print(f"Wrote {run_dir / 'metrics.json'}")


if __name__ == "__main__":
    main()

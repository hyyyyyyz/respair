#!/usr/bin/env python
"""Target-signal confound test (BEAST proposal #5).

Rules out the reviewer worry that the residual repair is reacting to
material-prediction noise rather than UV atlas defects. We construct four
controlled regimes per asset:

  Regime A (UV-only defect):     bad initial atlas + clean oracle PBR
  Regime B (material-only noise): clean initial atlas + noisy oracle PBR
  Regime C (mixed):              bad initial atlas + noisy oracle PBR
  Regime D (control, no defect): clean initial atlas + clean oracle PBR

Success criterion: C5 accepts in A (gain), rolls back in B and D (no
atlas leverage), and behavior in C is dominated by whichever defect is
larger. If C5 accepts in B, the residual repair is responding to material
noise rather than UV defects, which would invalidate the deployment claim.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
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
    FacePBRValues,
    make_view_light_splits,
    sample_face_pbr_from_maps,
)
from pbr_atlas.baselines import clone_mesh_with_atlas, create_backend
from pbr_atlas.data import generate_synthetic_oracle_pbr, prepare_asset
from pbr_atlas.method.allocator import MipAwareAllocator
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


REGIMES = ("A_uv_only", "B_material_only", "C_mixed", "D_control")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--asset", default="spot")
    p.add_argument("--config", default="configs/B3_main.yaml")
    p.add_argument("--data-root", default="datasets/sample")
    p.add_argument("--output-root", default="runs/target_signal_confound")
    p.add_argument("--seeds", default="0,1,2,3,4")
    p.add_argument("--regimes", default=",".join(REGIMES))
    p.add_argument("--material-sigma", type=float, default=0.10, help="std-dev of per-face PBR noise (in [0,1] units)")
    p.add_argument("--no-lpips", action="store_true")
    return p.parse_args()


def _perturb_face_values(face_values: FacePBRValues, sigma: float, seed: int) -> FacePBRValues:
    """Add gaussian noise to each PBR channel per face. Clamps albedo/rough to [0,1]."""
    if sigma <= 0:
        return face_values
    g = torch.Generator(device=face_values.albedo.device).manual_seed(seed)
    def add(x: torch.Tensor, lo: float, hi: float) -> torch.Tensor:
        noise = torch.randn(x.shape, generator=g, device=x.device, dtype=x.dtype) * sigma
        return (x + noise).clamp(lo, hi)
    return FacePBRValues(
        albedo=add(face_values.albedo, 0.0, 1.0),
        normal=torch.nn.functional.normalize(add(face_values.normal, -1.0, 1.0), dim=-1),
        roughness=add(face_values.roughness, 0.02, 1.0),
        metallic=add(face_values.metallic, 0.0, 1.0),
    )


def _bad_atlas(mesh, atlas_resolution: int, padding: int) -> Any:
    """Construct a deliberately bad initial atlas: dominant-axis 6-chart proxy.

    Used as the 'UV defect' condition. Falls back to whatever blender_uv
    backend produces if dominant fails.
    """
    backend = create_backend("blender_uv", {})
    out = backend.generate(mesh, atlas_resolution, padding)
    if out.repro_status == "failed":
        out = create_backend("xatlas_classical", {}).generate(mesh, atlas_resolution, padding)
    return out


def _good_atlas(mesh, atlas_resolution: int, padding: int) -> Any:
    return create_backend("xatlas_classical", {}).generate(mesh, atlas_resolution, padding)


def _run_one(regime: str, *, asset: str, seed: int, args: argparse.Namespace, cfg: dict[str, Any], device: torch.device) -> dict[str, Any]:
    started = time.time()
    atlas_resolution = int(cfg.get("atlas_resolution", 1024))
    padding = int(cfg.get("padding", 8))

    baker = DifferentiablePBRBaker(
        atlas_resolution=atlas_resolution,
        render_resolution=int(cfg.get("render_resolution", 256)),
        precision=str(cfg.get("precision", "bf16")),
        gradient_checkpointing=False,
        device=device,
    )
    mesh_path = prepare_asset(asset, data_root=Path(args.data_root), offline_ok=True)
    from pbr_atlas.data.mesh_loader import load_mesh
    mesh = load_mesh(mesh_path).to(device)

    use_bad_atlas = regime in ("A_uv_only", "C_mixed")
    use_noisy_material = regime in ("B_material_only", "C_mixed")

    candidate_atlas = _bad_atlas(mesh, atlas_resolution, padding) if use_bad_atlas else _good_atlas(mesh, atlas_resolution, padding)
    xatlas_ref = _good_atlas(mesh, atlas_resolution, padding)
    oracle_mesh = clone_mesh_with_atlas(mesh, xatlas_ref, device=device)
    oracle_maps = generate_synthetic_oracle_pbr(mesh, seed=seed, resolution=atlas_resolution, device=device)
    face_values_clean = sample_face_pbr_from_maps(oracle_mesh, oracle_maps)
    if use_noisy_material:
        face_values = _perturb_face_values(face_values_clean, sigma=args.material_sigma, seed=seed * 7919 + hash(regime) % 1000)
    else:
        face_values = face_values_clean

    splits = make_view_light_splits({"proposal": 6, "gate": 4, "test": 4}, {"proposal": 4, "gate": 4, "test": 4}, split_seed=seed, device=device)
    proposal_views, proposal_lights = splits.proposal.views, splits.proposal.lights
    gate_views, gate_lights = splits.gate.views, splits.gate.lights
    test_views, test_lights = splits.test.views, splits.test.lights

    with torch.no_grad():
        oracle_baked = baker.bake(oracle_mesh, face_values_clean)
        proposal_target = baker.render(oracle_mesh, oracle_baked, proposal_views, proposal_lights)
        gate_target = baker.render(oracle_mesh, oracle_baked, gate_views, gate_lights)
        test_target = baker.render(oracle_mesh, oracle_baked, test_views, test_lights)

    seam_loss_fn = CrossChannelSeamLoss(cfg.get("seam_loss", {}).get("channel_weights", {}))
    mip_levels = int(cfg.get("mip_levels", 4))

    initial_proposal_eval = _evaluate_atlas(
        baker=baker, mesh=mesh, atlas=candidate_atlas, face_values=face_values,
        target_mesh=oracle_mesh, target_maps=oracle_baked,
        target_images=proposal_target.images,
        views=proposal_views, lights=proposal_lights,
        mip_levels=mip_levels, compute_lpips=not args.no_lpips, seam_loss_fn=seam_loss_fn,
    )
    initial_gate_eval = _evaluate_atlas(
        baker=baker, mesh=mesh, atlas=candidate_atlas, face_values=face_values,
        target_mesh=oracle_mesh, target_maps=oracle_baked,
        target_images=gate_target.images,
        views=gate_views, lights=gate_lights,
        mip_levels=mip_levels, compute_lpips=not args.no_lpips, seam_loss_fn=seam_loss_fn,
    )
    initial_test_eval = _evaluate_atlas(
        baker=baker, mesh=mesh, atlas=candidate_atlas, face_values=face_values,
        target_mesh=oracle_mesh, target_maps=oracle_baked,
        target_images=test_target.images,
        views=test_views, lights=test_lights,
        mip_levels=mip_levels, compute_lpips=not args.no_lpips, seam_loss_fn=seam_loss_fn,
    )

    repair_cfg_payload = dict(cfg.get("repair", {}))
    outer_iters = int(repair_cfg_payload.get("outer_iters", 3))
    repair_cfg = _repair_config_from_mapping(repair_cfg_payload)
    matched_cfg = dict(cfg.get("matched_protocol", {}))
    current_atlas = candidate_atlas
    current_proposal_eval = initial_proposal_eval
    rolled_back = True
    accepted_iters = 0
    for outer_idx in range(max(1, outer_iters)):
        repairer = LocalChartRepair(repair_cfg)
        repaired_atlas, _ = repairer.repair(
            baker, mesh, current_atlas, oracle_maps,
            current_proposal_eval["residual"],
            proposal_views=proposal_views, proposal_lights=proposal_lights,
        )
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
        guard = _c5_guard(
            mesh=mesh, baseline_atlas=current_atlas, candidate_atlas=repaired_atlas,
            initial_eval=initial_gate_eval, final_eval=cand_gate_eval,
            matched_cfg=matched_cfg,
            c5_cfg=dict(cfg.get("c5_guard", {})),
        )
        if guard.get("accept"):
            current_atlas = repaired_atlas
            current_proposal_eval = cand_proposal_eval
            rolled_back = False
            accepted_iters += 1
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

    return {
        "asset": asset,
        "regime": regime,
        "use_bad_atlas": use_bad_atlas,
        "use_noisy_material": use_noisy_material,
        "material_sigma": args.material_sigma if use_noisy_material else 0.0,
        "seed": seed,
        "init_psnr": initial_test_eval["relit"]["psnr"],
        "final_psnr": final_test_eval["relit"]["psnr"],
        "delta_psnr": final_test_eval["relit"]["psnr"] - initial_test_eval["relit"]["psnr"],
        "rolled_back": rolled_back,
        "accepted_iters": accepted_iters,
        "wall_clock_s": time.time() - started,
    }


def main() -> None:
    args = parse_args()
    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8")) or {}
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    seeds = [int(s) for s in args.seeds.split(",") if s.strip()]
    regimes = [r.strip() for r in args.regimes.split(",") if r.strip()]
    out_root = ensure_dir(args.output_root)
    rows: list[dict[str, Any]] = []
    for regime in regimes:
        for seed in seeds:
            tag = f"{args.asset}_{regime}_seed{seed}"
            print(f"  start {tag}")
            try:
                row = _run_one(regime, asset=args.asset, seed=seed, args=args, cfg=cfg, device=device)
            except Exception as exc:
                row = {"asset": args.asset, "regime": regime, "seed": seed, "status": "failed", "error": str(exc)}
            row["tag"] = tag
            rows.append(row)
            print(f"    {tag}: init={row.get('init_psnr', 'na'):.2f} final={row.get('final_psnr', 'na'):.2f} delta={row.get('delta_psnr', 'na'):.2f} rb={row.get('rolled_back', 'na')}" if "init_psnr" in row else f"    {tag}: FAILED {row.get('error')}")
    atomic_write_json(out_root / "confound_metrics.json", {"rows": rows})
    print(f"Wrote {out_root / 'confound_metrics.json'}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""B1 sanity entrypoint: mesh + UV -> bake -> relight -> residual atlas."""

from __future__ import annotations

import argparse
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run B1 Oracle Baker sanity.")
    parser.add_argument("--asset", default=None, choices=["bunny", "spot", "objaverse", "objaverse_sample"])
    parser.add_argument("--gpu", type=int, default=None, help="CUDA device index before visibility remapping.")
    parser.add_argument("--config", default="configs/B1_sanity.yaml")
    parser.add_argument("--output-root", default=None)
    parser.add_argument("--data-root", default=None)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--atlas-resolution", type=int, default=None)
    parser.add_argument("--render-resolution", type=int, default=None)
    parser.add_argument("--precision", default=None, choices=["fp32", "float32", "fp16", "float16", "bf16", "bfloat16"])
    parser.add_argument("--no-lpips", action="store_true", help="Skip LPIPS if a fast determinism run is desired.")
    return parser.parse_args()


def load_config(path: str | Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _round_list(tensor, digits: int = 8) -> list[float]:
    values = tensor.detach().to("cpu").flatten().tolist()
    return [round(float(v), digits) for v in values]


def _metric_or_none(value):
    if value is None:
        return None
    if value == float("inf"):
        return "inf"
    return float(value)


def main() -> None:
    args = parse_args()
    if args.gpu is not None:
        os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpu)

    import torch

    from pbr_atlas.baker import (
        DifferentiablePBRBaker,
        make_lights,
        make_orbit_views,
        PBRMaps,
        sample_face_pbr_from_maps,
    )
    from pbr_atlas.baker.residual import compute_residual_attribution
    from pbr_atlas.data import generate_synthetic_oracle_pbr, prepare_asset
    from pbr_atlas.data.mesh_loader import load_mesh
    from pbr_atlas.eval.metrics import image_metrics, normal_angular_error, per_channel_mae
    from pbr_atlas.eval.residual_attribution import residual_localization_hit_rate
    from pbr_atlas.utils import atomic_write_json, directory_size_mb, ensure_dir, save_npz, save_residual_atlas_png, set_global_seed, write_text

    cfg = load_config(args.config)
    seed = int(args.seed if args.seed is not None else cfg.get("seed", 42))
    asset = args.asset or cfg.get("asset", "bunny")
    atlas_resolution = int(args.atlas_resolution or cfg.get("atlas_resolution", 1024))
    render_resolution = int(args.render_resolution or cfg.get("render_resolution", 256))
    precision = args.precision or cfg.get("precision", "bf16")
    output_root = Path(args.output_root or cfg.get("output_root", "/data/dip_1_ws/runs/B1_sanity"))
    run_id = args.run_id or f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{asset}_seed{seed}"
    run_dir = ensure_dir(output_root / run_id)
    data_root = Path(args.data_root or cfg.get("data_root", "/data/dip_1_ws/datasets/sample"))
    vis_resolution = int(cfg.get("visualization_resolution", min(atlas_resolution, 1024)))

    set_global_seed(seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats()
    started = time.time()

    mesh_path = prepare_asset(asset, data_root=data_root, offline_ok=True)
    mesh = load_mesh(mesh_path, device=device)

    baker = DifferentiablePBRBaker(
        atlas_resolution=atlas_resolution,
        render_resolution=render_resolution,
        precision=precision,
        gradient_checkpointing=bool(cfg.get("gradient_checkpointing", True)),
        device=device,
    )

    # FINAL_PROPOSAL C1 oracle comment:
    # If real PBR is absent, B1 creates synthetic T_k^* and samples per-face
    # P_k(f); baker.bake then approximates T_k(t)=sum_f w_{t,f}P_k(f)/(sum_f w_{t,f}+eps).
    oracle_cfg = cfg.get("oracle_pbr", {})
    oracle_maps = generate_synthetic_oracle_pbr(
        mesh,
        seed=seed,
        pattern=str(oracle_cfg.get("pattern", "voronoi_albedo+smooth_normal+region_roughness")),
        resolution=atlas_resolution,
        num_voronoi_seeds=int(oracle_cfg.get("num_voronoi_seeds", 16)),
        device=device,
    )
    face_values = sample_face_pbr_from_maps(mesh, oracle_maps)
    baked_maps = baker.bake(mesh, face_values)

    view_cfg = cfg.get("views", {})
    light_cfg = cfg.get("lights", {})
    train_views = int(view_cfg.get("train", 6))
    holdout_views = int(view_cfg.get("holdout", 4))
    train_lights = int(light_cfg.get("train", 4))
    holdout_lights = int(light_cfg.get("holdout", 4))
    all_views = make_orbit_views(train_views + holdout_views, device=device)
    all_lights = make_lights(train_lights + holdout_lights, device=device)
    train_view_specs = all_views[:train_views]
    train_light_specs = all_lights[:train_lights]
    views = all_views[train_views:]
    lights = all_lights[train_lights:]

    # FINAL_PROPOSAL C1 render residual comment:
    # L_render sums rho_1(I_hat-I*) + beta(1-SSIM)/2 + gamma LPIPS over
    # held-out V_ho x L_ho. B1 reports the constituent metrics without training.
    pred_render = baker.render(mesh, baked_maps, views, lights)
    target_render = baker.render(mesh, oracle_maps, views, lights)
    metrics_img = image_metrics(pred_render.images, target_render.images, compute_lpips=not args.no_lpips)
    train_metrics_img = {}
    if train_view_specs and train_light_specs:
        train_pred_render = baker.render(mesh, baked_maps, train_view_specs, train_light_specs)
        train_target_render = baker.render(mesh, oracle_maps, train_view_specs, train_light_specs)
        train_metrics_img = image_metrics(train_pred_render.images, train_target_render.images, compute_lpips=not args.no_lpips)

    backward_metrics = {"enabled": bool(cfg.get("backward_check", True)), "loss": None, "all_grads_finite": None}
    if backward_metrics["enabled"]:
        # B1 forward/backward sanity comment:
        # C1 is differentiable through R_pbr. We verify one held-out pair can
        # backpropagate d mean(|I_hat-I*|) / d T_k without storing render buffers.
        grad_maps = PBRMaps(
            albedo=baked_maps.albedo.detach().clone().requires_grad_(True),
            normal=baked_maps.normal.detach().clone().requires_grad_(True),
            roughness=baked_maps.roughness.detach().clone().requires_grad_(True),
            metallic=baked_maps.metallic.detach().clone().requires_grad_(True),
            face_ids=baked_maps.face_ids,
        )
        grad_render = baker.render(mesh, grad_maps, views[:1], lights[:1])
        backward_loss = (grad_render.images - target_render.images[:1]).abs().mean()
        backward_loss.backward()
        grads = [grad_maps.albedo.grad, grad_maps.normal.grad, grad_maps.roughness.grad, grad_maps.metallic.grad]
        backward_metrics = {
            "enabled": True,
            "loss": float(backward_loss.detach().cpu()),
            "all_grads_finite": bool(all(g is not None and torch.isfinite(g).all().item() for g in grads)),
        }

    pbr_mae = per_channel_mae(
        {
            "albedo": baked_maps.albedo,
            "roughness": baked_maps.roughness,
            "metallic": baked_maps.metallic,
        },
        {
            "albedo": oracle_maps.albedo,
            "roughness": oracle_maps.roughness,
            "metallic": oracle_maps.metallic,
        },
    )
    pbr_mae["normal_angular_error_deg"] = normal_angular_error(baked_maps.normal, oracle_maps.normal)

    residual = compute_residual_attribution(
        pred=pred_render.images,
        target=target_render.images,
        face_ids=pred_render.face_ids,
        alpha=pred_render.alpha,
        mesh=mesh,
        maps=baked_maps,
        chart_ids=mesh.chart_ids,
        mip_levels=int(cfg.get("mip_levels", 4)),
    )

    artifact_mask = torch.zeros(mesh.faces.shape[0], dtype=torch.bool, device=device)
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
    save_residual_atlas_png(run_dir / "residual_atlas.png", mesh, residual.e_f, resolution=vis_resolution)

    peak_memory_gb = 0.0
    if device.type == "cuda":
        peak_memory_gb = float(torch.cuda.max_memory_allocated() / (1024.0**3))
    wall_clock_s = time.time() - started

    metrics = {
        "block": "B1_sanity",
        "asset": asset,
        "mesh_path": str(mesh_path),
        "seed": seed,
        "device": str(device),
        "precision": precision,
        "atlas_resolution": atlas_resolution,
        "render_resolution": render_resolution,
        "views": {"train": train_views, "holdout": holdout_views},
        "lights": {"train": train_lights, "holdout": holdout_lights},
        "relit_train": {key: _metric_or_none(value) for key, value in train_metrics_img.items()},
        "relit": {key: _metric_or_none(value) for key, value in metrics_img.items()},
        "pbr_channel": pbr_mae,
        "backward_check": backward_metrics,
        "residual_stats": {
            "e_f": _round_list(residual.e_f),
            "E_c": _round_list(residual.E_c),
            "G_l": _round_list(residual.G_l),
            "e_f_mean": float(residual.e_f.mean().detach().cpu()),
            "e_f_max": float(residual.e_f.max().detach().cpu()) if residual.e_f.numel() else 0.0,
            "E_c_mean": float(residual.E_c.mean().detach().cpu()) if residual.E_c.numel() else 0.0,
            "seam_residual_mean": float(residual.seam_residual.mean().detach().cpu()) if residual.seam_residual.numel() else 0.0,
            "residual_top20_seam_hit_rate": hit_rate,
        },
        "peak_memory_GB": peak_memory_gb,
        "wall_clock_s": wall_clock_s,
        "outputs": {
            "metrics": str(run_dir / "metrics.json"),
            "residual_npz": str(run_dir / "residual_atlas.npz"),
            "residual_png": str(run_dir / "residual_atlas.png"),
            "summary": str(run_dir / "summary.md"),
        },
    }
    atomic_write_json(run_dir / "metrics.json", metrics)
    output_size_mb = directory_size_mb(run_dir)
    metrics["storage"] = {
        "output_size_MB": output_size_mb,
        "persistent_asset_budget_MB": 200.0,
        "storage_safe": output_size_mb < 200.0,
    }
    atomic_write_json(run_dir / "metrics.json", metrics)
    summary = (
        f"# B1 Sanity Summary\n\n"
        f"- asset: {asset}\n"
        f"- seed: {seed}\n"
        f"- relit PSNR: {metrics['relit']['psnr']}\n"
        f"- relit SSIM: {metrics['relit']['ssim']}\n"
        f"- LPIPS: {metrics['relit']['lpips']}\n"
        f"- max e_f: {metrics['residual_stats']['e_f_max']:.8f}\n"
        f"- G_l: {metrics['residual_stats']['G_l']}\n"
        f"- peak memory GB: {peak_memory_gb:.3f}\n"
        f"- output size MB: {output_size_mb:.3f}\n"
    )
    write_text(run_dir / "summary.md", summary)
    print(str(run_dir))


if __name__ == "__main__":
    main()

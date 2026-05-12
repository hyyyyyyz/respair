#!/usr/bin/env python
"""Render DiLiGenT-MV captured before/after relit comparison panels.

For each DiLiGenT object (Bear, Cow, Pot2, Buddha, Reading), pick one
test-split (view, light) pair and render:

  Captured (reference) | Initial atlas render | Init error | Repaired render | Ours error

with a shared inferno colorbar and yellow-boxed zoom inset on each panel.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import replace
from pathlib import Path
from typing import Optional

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
import torch
import matplotlib.pyplot as plt
import torch.nn.functional as F

from pbr_atlas.baker import DifferentiablePBRBaker, sample_face_pbr_from_maps
from pbr_atlas.baker.captured_target import build_captured_split, captured_split_to_render_output
from pbr_atlas.baselines import clone_mesh_with_atlas, create_backend
from pbr_atlas.data import generate_synthetic_oracle_pbr
from pbr_atlas.data.diligent_mv import (
    load_diligent_mv_asset,
    view_lights_to_specs,
    view_to_view_spec,
)
from pbr_atlas.utils.io import ensure_dir


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--cases",
        default=(
            "bear:/data/dip_1_ws/runs/W1_diligent_mv/bear_xatlas_classical_ours_split0_seed0,"
            "cow:/data/dip_1_ws/runs/W1_diligent_mv/cow_xatlas_classical_ours_split0_seed0,"
            "pot2:/data/dip_1_ws/runs/W1_diligent_mv/pot2_xatlas_classical_ours_split0_seed0,"
            "buddha:/data/dip_1_ws/runs/W1_diligent_mv/buddha_xatlas_classical_ours_split0_seed0,"
            "reading:/data/dip_1_ws/runs/W1_diligent_mv/reading_xatlas_classical_ours_split0_seed0"
        ),
    )
    p.add_argument("--diligent-root", default="/data/dip_1_ws/datasets/diligent_mv/extracted/DiLiGenT-MV/mvpmsData")
    p.add_argument("--output-dir", default="figures/visual_evidence_diligent")
    p.add_argument("--atlas-resolution", type=int, default=1024)
    p.add_argument("--render-resolution", type=int, default=512)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--err-vmax", type=float, default=0.4)
    p.add_argument("--zoom-size", type=int, default=96)
    p.add_argument("--zoom-frac", type=float, default=0.36)
    p.add_argument("--decimate-faces", type=int, default=20000)
    return p.parse_args()


def _swap_atlas(mesh, npz_path: Path, device: torch.device):
    arrays = np.load(npz_path, allow_pickle=True)
    uv = torch.as_tensor(arrays["uv"], dtype=torch.float32, device=device)
    face_uv = torch.as_tensor(arrays["face_uv"], dtype=torch.long, device=device)
    if "chart_ids" in arrays.files:
        chart_ids = torch.as_tensor(arrays["chart_ids"], dtype=torch.long, device=device)
    else:
        chart_ids = torch.zeros(int(face_uv.shape[0]), dtype=torch.long, device=device)
    return replace(mesh, uv=uv, face_uv=face_uv, chart_ids=chart_ids)


def _to_rgb(image: torch.Tensor) -> np.ndarray:
    img = image.detach().cpu().clamp(0, 1).numpy()
    if img.ndim == 4:
        img = img[0]
    if img.shape[-1] == 1:
        img = np.repeat(img, 3, axis=-1)
    return img


def _brighten(img: np.ndarray, gamma: float = 0.6, gain: float = 5.0) -> np.ndarray:
    """Captured DiLiGenT images are very dark (intensity-normalized). Boost for paper."""
    out = np.clip(img * gain, 0, 1)
    return np.clip(out ** gamma, 0, 1)


def _add_zoom_inset(ax, image_or_err, bbox, *, kind, cmap=None, vmin=0.0, vmax=1.0, frac=0.36):
    from matplotlib.patches import Rectangle
    y0, y1, x0, x1 = bbox
    rect = Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, edgecolor="#FFFF55", linewidth=1.2)
    ax.add_patch(rect)
    inset = ax.inset_axes([1.0 - frac, 1.0 - frac, frac, frac])
    crop = image_or_err[y0:y1, x0:x1]
    if kind == "rgb":
        inset.imshow(crop)
    else:
        inset.imshow(crop, cmap=cmap, vmin=vmin, vmax=vmax)
    inset.set_xticks([]); inset.set_yticks([])
    for spine in inset.spines.values():
        spine.set_edgecolor("#FFFF55"); spine.set_linewidth(1.2)


def _resize_capture(img_hw3: torch.Tensor, target: int) -> torch.Tensor:
    chw = img_hw3.permute(2, 0, 1).unsqueeze(0)
    out = F.interpolate(chw, size=(target, target), mode="bilinear", align_corners=False, antialias=True)
    return out.squeeze(0).permute(1, 2, 0).contiguous()


def _render_case(asset_name: str, run_dir: Path, args, device: torch.device) -> Optional[dict]:
    metrics_path = run_dir / "metrics.json"
    if not metrics_path.exists():
        print(f"  SKIP {asset_name}: no metrics.json at {metrics_path}")
        return None
    metrics = json.loads(metrics_path.read_text())
    splits = metrics.get("splits", {})
    test_view = (splits.get("test_views") or [0])[0]
    test_light = (splits.get("test_lights") or [0])[0]
    seed = int(metrics.get("seed", 0))

    asset = load_diligent_mv_asset(
        asset_name, args.diligent_root,
        max_views=None, max_lights=None,
        decimate_faces=args.decimate_faces, device=device,
    )
    base_mesh = asset.mesh
    init_mesh = _swap_atlas(base_mesh, run_dir / "initial_atlas.npz", device)
    final_mesh = _swap_atlas(base_mesh, run_dir / "atlas.npz", device)

    captured_split = build_captured_split(asset, [test_view], [test_light], render_resolution=args.render_resolution)
    captured_target = captured_split_to_render_output(captured_split, device=device)

    view_specs = [view_to_view_spec(asset.views[test_view])]
    light_specs = view_lights_to_specs(asset.views[test_view], [test_light])

    oracle_maps = generate_synthetic_oracle_pbr(base_mesh, seed=seed, resolution=args.atlas_resolution, device=device)
    xatlas_ref = create_backend("xatlas_classical", {}).generate(base_mesh, args.atlas_resolution, 8)
    oracle_mesh = clone_mesh_with_atlas(base_mesh, xatlas_ref, device=device)
    face_values = sample_face_pbr_from_maps(oracle_mesh, oracle_maps)

    baker = DifferentiablePBRBaker(
        atlas_resolution=args.atlas_resolution,
        render_resolution=args.render_resolution,
        precision="bf16", device=device,
    )
    init_baked = baker.bake(init_mesh, face_values)
    final_baked = baker.bake(final_mesh, face_values)
    with torch.no_grad():
        init_render = baker.render(init_mesh, init_baked, view_specs, light_specs).images
        final_render = baker.render(final_mesh, final_baked, view_specs, light_specs).images

    captured_img = _to_rgb(captured_target.images[0])
    init_img = _to_rgb(init_render[0])
    final_img = _to_rgb(final_render[0])
    init_err = np.abs(init_img - captured_img).mean(axis=-1)
    final_err = np.abs(final_img - captured_img).mean(axis=-1)

    H, W = init_err.shape
    half = max(8, args.zoom_size // 2)
    if half * 2 < min(H, W):
        flat_idx = int(np.argmax(init_err))
        cy, cx = divmod(flat_idx, init_err.shape[1])
        cy = int(np.clip(cy, half, H - half))
        cx = int(np.clip(cx, half, W - half))
        zoom_bbox = (cy - half, cy + half, cx - half, cx + half)
    else:
        zoom_bbox = None

    return {
        "asset": asset_name,
        "captured": _brighten(captured_img),
        "init": _brighten(init_img),
        "final": _brighten(final_img),
        "init_err_raw": init_err,
        "final_err_raw": final_err,
        "zoom_bbox": zoom_bbox,
        "init_psnr": metrics.get("initial", {}).get("relit", {}).get("psnr"),
        "final_psnr": metrics.get("final", {}).get("relit", {}).get("psnr"),
    }


def _compose(panels: list[dict], output_dir: Path, args) -> None:
    ensure_dir(output_dir)
    n = len(panels)
    fig, axes = plt.subplots(n, 5, figsize=(15, 3 * n + 0.5))
    if n == 1:
        axes = axes[None, :]
    titles = ["Captured (reference)", "Initial render", "Init error", "Repaired render", "Ours error"]
    cmap = plt.get_cmap("inferno")
    err_im_handle = None
    for r, panel in enumerate(panels):
        items = [
            ("rgb", panel["captured"]),
            ("rgb", panel["init"]),
            ("err", panel["init_err_raw"]),
            ("rgb", panel["final"]),
            ("err", panel["final_err_raw"]),
        ]
        bbox = panel.get("zoom_bbox")
        for c, (kind, img) in enumerate(items):
            ax = axes[r, c]
            if kind == "rgb":
                ax.imshow(img)
            else:
                handle = ax.imshow(img, cmap=cmap, vmin=0.0, vmax=args.err_vmax)
                if err_im_handle is None:
                    err_im_handle = handle
            ax.set_xticks([]); ax.set_yticks([])
            if r == 0:
                ax.set_title(titles[c], fontsize=10)
            if bbox is not None:
                _add_zoom_inset(ax, img, bbox, kind=kind, cmap=cmap, vmin=0.0, vmax=args.err_vmax, frac=args.zoom_frac)
        ip = panel["init_psnr"]; fp = panel["final_psnr"]
        delta_str = f"  +{fp-ip:.1f} dB" if (ip is not None and fp is not None) else ""
        axes[r, 0].set_ylabel(f"{panel['asset']}{delta_str}", fontsize=10)
    plt.tight_layout(rect=[0, 0.04, 1, 1])
    if err_im_handle is not None:
        cax = fig.add_axes([0.25, 0.02, 0.5, 0.014])
        cbar = fig.colorbar(err_im_handle, cax=cax, orientation="horizontal")
        cbar.set_label(f"absolute error vs captured (per-pixel mean RGB), shared scale 0--{args.err_vmax}", fontsize=9)
        cbar.ax.tick_params(labelsize=8)
    out_pdf = output_dir / "fig8_diligent_visual.pdf"
    out_png = output_dir / "fig8_diligent_visual.png"
    fig.savefig(out_pdf, bbox_inches="tight", dpi=200)
    fig.savefig(out_png, bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"Saved: {out_pdf}\nSaved: {out_png}")


def main() -> None:
    args = parse_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    panels = []
    for token in args.cases.split(","):
        if not token.strip():
            continue
        asset, run_dir = token.split(":", 1)
        try:
            panel = _render_case(asset.strip(), Path(run_dir.strip()), args, device)
        except Exception as exc:
            import traceback; traceback.print_exc()
            print(f"  FAILED {asset}: {exc}")
            panel = None
        if panel is not None:
            panels.append(panel)
            print(f"  rendered {asset}")
    if panels:
        _compose(panels, Path(args.output_dir), args)


if __name__ == "__main__":
    main()

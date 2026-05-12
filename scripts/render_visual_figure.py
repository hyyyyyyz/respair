#!/usr/bin/env python
"""Render before/after held-out relit comparison panels for accepted cases.

For each provided run dir, re-bake PBR maps under both the initial and the
repaired atlas using the SAME oracle PBR (matched seed), render the test split
view/light pair, and save side-by-side PNG panels.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import replace
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
import torch
import matplotlib.pyplot as plt

from pbr_atlas.baker import DifferentiablePBRBaker, make_view_light_splits, sample_face_pbr_from_maps
from pbr_atlas.baselines import clone_mesh_with_atlas, create_backend
from pbr_atlas.data import generate_synthetic_oracle_pbr, prepare_asset
from pbr_atlas.data.mesh_loader import MeshData, load_mesh
from pbr_atlas.utils.io import ensure_dir


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--cases",
        default=(
            "spot:/data/dip_1_ws/runs/B3_main/spot_partuv_ours_seed42,"
            "bunny:/data/dip_1_ws/runs/B3_main/bunny_partuv_ours_seed42,"
            "warped_cylinder:/data/dip_1_ws/runs/B7_transfer/proc_warped_cylinder_partuv_ours_seed42,"
            "ts_animal:/data/dip_1_ws/runs/PG_enh1_real_v2/ts_animal_partuv_ours_seed42,"
            "f3d_animal:/data/dip_1_ws/runs/PG_enh1_real_v2/f3d_animal_partuv_ours_seed42"
        ),
    )
    p.add_argument("--err-vmax", type=float, default=0.4, help="Shared error colorbar maximum")
    p.add_argument("--zoom-size", type=int, default=96, help="Side length (px) for the auto-zoom inset; 0 disables")
    p.add_argument("--zoom-frac", type=float, default=0.36, help="Inset axes fractional size relative to its parent")
    p.add_argument("--output-dir", default="figures/visual_evidence")
    p.add_argument("--atlas-resolution", type=int, default=1024)
    p.add_argument("--render-resolution", type=int, default=512)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--split-seed", type=int, default=42)
    p.add_argument("--view-idx", type=int, default=0)
    p.add_argument("--light-idx", type=int, default=0)
    return p.parse_args()


def _resolve_mesh(asset: str, run_dir: Path) -> Path:
    metrics = json.loads((run_dir / "metrics.json").read_text())
    mp = metrics.get("mesh_path")
    if mp and Path(mp).exists():
        return Path(mp)
    if asset in {"spot", "bunny", "objaverse", "objaverse_sample"}:
        return prepare_asset(asset, data_root=Path("datasets/sample"), offline_ok=True)
    raise FileNotFoundError(f"Cannot resolve mesh for {asset}")


def _swap_atlas(mesh: MeshData, npz_path: Path, device: torch.device) -> MeshData:
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


def _err_heatmap(err: np.ndarray, vmax: float) -> np.ndarray:
    err = np.clip(err / max(vmax, 1e-6), 0, 1)
    cmap = plt.get_cmap("inferno")
    return cmap(err)[..., :3]


def _brighten(img: np.ndarray, gamma: float = 0.7, gain: float = 1.4) -> np.ndarray:
    """Apply a mild gamma + gain so dark renders are readable in print."""
    out = np.clip(img * gain, 0, 1)
    return np.clip(out ** gamma, 0, 1)


def _render_case(asset: str, run_dir: Path, args: argparse.Namespace, device: torch.device) -> dict:
    mesh_path = _resolve_mesh(asset, run_dir)
    base_mesh = load_mesh(mesh_path).to(device)

    init_mesh = _swap_atlas(base_mesh, run_dir / "initial_atlas.npz", device)
    final_mesh = _swap_atlas(base_mesh, run_dir / "atlas.npz", device)

    oracle_atlas = create_backend("matched_oracle", {}).generate(base_mesh, args.atlas_resolution, 8)
    if oracle_atlas.repro_status == "failed":
        oracle_atlas = create_backend("xatlas_classical", {}).generate(base_mesh, args.atlas_resolution, 8)
    oracle_mesh = clone_mesh_with_atlas(base_mesh, oracle_atlas, device=device)

    xatlas_baseline_atlas = create_backend("xatlas_classical", {}).generate(base_mesh, args.atlas_resolution, 8)
    if xatlas_baseline_atlas.repro_status == "failed":
        xatlas_mesh = init_mesh
    else:
        xatlas_mesh = clone_mesh_with_atlas(base_mesh, xatlas_baseline_atlas, device=device)

    oracle = generate_synthetic_oracle_pbr(
        base_mesh, seed=args.seed, resolution=args.atlas_resolution, device=device
    )
    splits = make_view_light_splits({"proposal": 6, "gate": 4, "test": 4}, {"proposal": 4, "gate": 4, "test": 4}, split_seed=args.split_seed, device=device)
    test_views = splits.test.views[args.view_idx:args.view_idx + 1]
    test_lights = splits.test.lights[args.light_idx:args.light_idx + 1]

    baker = DifferentiablePBRBaker(
        atlas_resolution=args.atlas_resolution,
        render_resolution=args.render_resolution,
        precision="bf16",
        device=device,
    )

    face_values = sample_face_pbr_from_maps(oracle_mesh, oracle)
    oracle_baked = baker.bake(oracle_mesh, face_values)
    init_baked = baker.bake(init_mesh, face_values)
    final_baked = baker.bake(final_mesh, face_values)
    xatlas_baked = baker.bake(xatlas_mesh, face_values)

    with torch.no_grad():
        ref = baker.render(oracle_mesh, oracle_baked, test_views, test_lights).images
        init_render = baker.render(init_mesh, init_baked, test_views, test_lights).images
        final_render = baker.render(final_mesh, final_baked, test_views, test_lights).images
        xatlas_render = baker.render(xatlas_mesh, xatlas_baked, test_views, test_lights).images

    ref_img = _to_rgb(ref[0])
    init_img = _to_rgb(init_render[0])
    final_img = _to_rgb(final_render[0])
    xatlas_img = _to_rgb(xatlas_render[0])
    init_err_raw = np.abs(init_img - ref_img).mean(axis=-1)
    final_err_raw = np.abs(final_img - ref_img).mean(axis=-1)
    xatlas_err_raw = np.abs(xatlas_img - ref_img).mean(axis=-1)

    H, W = ref_img.shape[:2]
    half = max(8, args.zoom_size // 2)
    if half * 2 < min(H, W) and args.zoom_size > 0:
        # Find centroid of high-error pixels in init_err_raw (bias toward seams).
        flat_idx = int(np.argmax(init_err_raw))
        cy, cx = divmod(flat_idx, init_err_raw.shape[1])
        cy = int(np.clip(cy, half, H - half))
        cx = int(np.clip(cx, half, W - half))
        zoom_bbox = (cy - half, cy + half, cx - half, cx + half)
    else:
        zoom_bbox = None

    return {
        "asset": asset,
        "ref": _brighten(ref_img),
        "init": _brighten(init_img),
        "final": _brighten(final_img),
        "xatlas": _brighten(xatlas_img),
        "init_err_raw": init_err_raw,
        "final_err_raw": final_err_raw,
        "xatlas_err_raw": xatlas_err_raw,
        "zoom_bbox": zoom_bbox,
    }


def _add_zoom_inset(ax, image_or_err, bbox, *, kind: str, cmap=None, vmin=0.0, vmax=1.0, frac=0.36) -> None:
    """Overlay a small inset showing the zoomed bbox on top-right of axes.

    bbox: (y0, y1, x0, x1) in source-image pixel coordinates.
    """
    from matplotlib.patches import Rectangle

    y0, y1, x0, x1 = bbox
    H_src = image_or_err.shape[0]
    W_src = image_or_err.shape[1]
    # Outline on the parent axes
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
        spine.set_edgecolor("#FFFF55")
        spine.set_linewidth(1.2)


def _compose(panels: list[dict], output_dir: Path, err_vmax: float, zoom_frac: float) -> None:
    ensure_dir(output_dir)
    n = len(panels)
    fig, axes = plt.subplots(n, 7, figsize=(21, 3 * n + 0.4))
    if n == 1:
        axes = axes[None, :]
    titles = [
        "Reference", "Initial PartUV", "Init error",
        "Repaired (ours)", "Ours error",
        "xatlas baseline", "xatlas error",
    ]
    cmap = plt.get_cmap("inferno")
    err_im_handle = None
    for r, panel in enumerate(panels):
        items = [
            ("rgb", panel["ref"]),
            ("rgb", panel["init"]),
            ("err", panel["init_err_raw"]),
            ("rgb", panel["final"]),
            ("err", panel["final_err_raw"]),
            ("rgb", panel["xatlas"]),
            ("err", panel["xatlas_err_raw"]),
        ]
        bbox = panel.get("zoom_bbox")
        for c, (kind, img) in enumerate(items):
            ax = axes[r, c]
            if kind == "rgb":
                ax.imshow(img)
            else:
                handle = ax.imshow(img, cmap=cmap, vmin=0.0, vmax=err_vmax)
                if err_im_handle is None:
                    err_im_handle = handle
            ax.set_xticks([]); ax.set_yticks([])
            if r == 0:
                ax.set_title(titles[c], fontsize=10)
            if bbox is not None:
                _add_zoom_inset(
                    ax, img, bbox,
                    kind=kind, cmap=cmap, vmin=0.0, vmax=err_vmax, frac=zoom_frac,
                )
        axes[r, 0].set_ylabel(panel["asset"], fontsize=10)
    plt.tight_layout(rect=[0, 0.04, 1, 1])
    if err_im_handle is not None:
        cax = fig.add_axes([0.25, 0.02, 0.5, 0.014])
        cbar = fig.colorbar(err_im_handle, cax=cax, orientation="horizontal")
        cbar.set_label(f"absolute error (per-pixel mean over RGB), shared scale 0--{err_vmax}", fontsize=9)
        cbar.ax.tick_params(labelsize=8)
    out_pdf = output_dir / "fig7_visual_comparison.pdf"
    out_png = output_dir / "fig7_visual_comparison.png"
    fig.savefig(out_pdf, bbox_inches="tight", dpi=200)
    fig.savefig(out_png, bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"Saved: {out_pdf}")
    print(f"Saved: {out_png}")


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    cases = []
    for token in args.cases.split(","):
        if not token.strip():
            continue
        asset, run_dir = token.split(":", 1)
        cases.append((asset.strip(), Path(run_dir.strip())))
    panels: list[dict] = []
    for asset, run_dir in cases:
        try:
            panel = _render_case(asset, run_dir, args, device)
            panels.append(panel)
            print(f"  rendered {asset}")
        except Exception as exc:
            import traceback
            traceback.print_exc()
            print(f"  FAILED {asset}: {exc}")
    if panels:
        _compose(panels, output_dir, args.err_vmax, args.zoom_frac)


if __name__ == "__main__":
    main()

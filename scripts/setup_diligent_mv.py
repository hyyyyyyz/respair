#!/usr/bin/env python
"""Inspect and verify a DiLiGenT-MV install.

Reports per-object: mesh face count, view count, light count, image shape,
mask area, sample camera/light intrinsics. Catches loader bugs before launching
the full grid.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pbr_atlas.data.diligent_mv import (  # noqa: E402
    DILIGENT_MV_OBJECTS,
    captured_images_for,
    captured_mask_for,
    load_diligent_mv_asset,
    view_lights_to_specs,
    view_to_view_spec,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--root", default="datasets/diligent_mv/extracted/DiLiGenT-MV/mvpmsData")
    p.add_argument("--objects", nargs="*", default=list(DILIGENT_MV_OBJECTS))
    p.add_argument("--max-lights", type=int, default=4, help="Smoke load N lights only")
    p.add_argument("--decimate-faces", type=int, default=20000, help="Decimate GT mesh to N faces; 0 disables")
    p.add_argument("--out-json", default="datasets/diligent_mv/processed/setup_audit.json")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    audit = {"root": str(args.root), "objects": {}}
    for name in args.objects:
        try:
            asset = load_diligent_mv_asset(
                name, args.root,
                max_lights=args.max_lights,
                decimate_faces=int(args.decimate_faces) if args.decimate_faces > 0 else None,
            )
            view0 = asset.views[0]
            view_spec = view_to_view_spec(view0)
            light_specs = view_lights_to_specs(view0, list(range(min(2, view0.images.shape[0]))))
            target_imgs = captured_images_for(view0, [0])
            mask = captured_mask_for(view0)
            audit["objects"][name] = {
                "status": "ok",
                "mesh_faces": int(asset.mesh.faces.shape[0]),
                "mesh_verts": int(asset.mesh.vertices.shape[0]),
                "num_views": asset.num_views(),
                "lights_per_view_loaded": int(view0.images.shape[0]),
                "image_h": int(view0.image_size[0]),
                "image_w": int(view0.image_size[1]),
                "mask_active_pixels": int(mask.sum().item()),
                "view0_eye": view_spec.eye.tolist(),
                "view0_fov_degrees": view_spec.fov_degrees,
                "light0_dir": light_specs[0].direction.tolist(),
                "light0_intensity": light_specs[0].intensity,
                "target_image_min": float(target_imgs.min().item()),
                "target_image_max": float(target_imgs.max().item()),
                "target_image_mean": float(target_imgs.mean().item()),
            }
            print(f"  OK {name}: {asset.mesh.faces.shape[0]} faces, {asset.num_views()} views, {view0.images.shape[0]} lights loaded; img mean={target_imgs.mean().item():.4f}")
        except Exception as exc:
            audit["objects"][name] = {"status": "failed", "error": str(exc)}
            print(f"  FAIL {name}: {exc}")
    out = Path(args.out_json)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(audit, indent=2))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()

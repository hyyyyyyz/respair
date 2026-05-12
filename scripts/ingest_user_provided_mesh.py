#!/usr/bin/env python3
"""Ingest user-downloaded real generated meshes into the PG-enh1 evaluation pipeline.

Usage:
  python scripts/ingest_user_provided_mesh.py \
    --source-dir ~/Downloads/pg_real_generated \
    --target-root /data/dip_1_ws/datasets/pg_real_generated \
    --manifest configs/pg_real_meshes.json

Manifest format (configs/pg_real_meshes.json), one entry per mesh:
  [
    {"file": "trellis_chair.glb", "asset_id": "trellis_chair", "source": "TRELLIS", "category": "trellis_furniture"},
    {"file": "get3d_car_001.obj", "asset_id": "get3d_car_001", "source": "GET3D", "category": "get3d_vehicle"},
    {"file": "dreamfusion_owl.obj", "asset_id": "dreamfusion_owl", "source": "DreamFusion", "category": "sds_animal"}
  ]

If no manifest is provided, asset_id = filename stem and source/category = "user_provided".
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

MESH_EXTS = {".obj", ".glb", ".gltf", ".ply", ".stl"}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--source-dir", required=True, help="Local directory with downloaded meshes (e.g. ~/Downloads/pg_real_generated)")
    p.add_argument("--target-root", default="/data/dip_1_ws/datasets/pg_real_generated", help="Server-side dataset root")
    p.add_argument("--server", default="server2", help="SSH alias for the GPU server")
    p.add_argument("--manifest", default=None, help="Optional JSON manifest with per-file metadata")
    p.add_argument("--upload", action="store_true", help="rsync to server after ingest")
    p.add_argument("--no-upload", dest="upload", action="store_false")
    p.set_defaults(upload=True)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    source_dir = Path(args.source_dir).expanduser().resolve()
    if not source_dir.exists():
        raise SystemExit(f"source-dir does not exist: {source_dir}")

    manifest_path = Path(args.manifest).expanduser() if args.manifest else None
    manifest_lookup: dict[str, dict[str, str]] = {}
    if manifest_path and manifest_path.exists():
        for entry in json.loads(manifest_path.read_text()):
            manifest_lookup[entry["file"]] = entry

    candidates = sorted(p for p in source_dir.rglob("*") if p.suffix.lower() in MESH_EXTS)
    if not candidates:
        raise SystemExit(f"No mesh files in {source_dir} (recognized: {sorted(MESH_EXTS)})")

    target_root = Path(args.target_root)
    local_stage = Path("/tmp/pg_real_generated_stage")
    if local_stage.exists():
        shutil.rmtree(local_stage)
    local_stage.mkdir(parents=True)

    records = []
    for src in candidates:
        meta = manifest_lookup.get(src.name, {})
        asset_id = meta.get("asset_id", src.stem.replace(" ", "_"))
        source = meta.get("source", "user_provided")
        category = meta.get("category", "user_provided")

        asset_dir = local_stage / asset_id
        asset_dir.mkdir(exist_ok=True)
        dst = asset_dir / f"{asset_id}{src.suffix.lower()}"
        shutil.copy(src, dst)
        records.append({
            "asset_id": asset_id,
            "mesh_path": str(target_root / asset_id / dst.name),
            "source": source,
            "category": category,
            "status": "ok",
            "seed": 42,
            "failure_reason": None,
            "metadata": {"original_filename": src.name},
        })
        print(f"staged {asset_id} ← {src.name} (source={source}, category={category})")

    manifest_out = local_stage / "PG_REAL_MESHES_MANIFEST.json"
    manifest_out.write_text(json.dumps(records, indent=2))
    print(f"\nstaged {len(records)} meshes to {local_stage}")
    print(f"manifest: {manifest_out}")

    if args.upload:
        print(f"\nrsync → {args.server}:{target_root}/")
        subprocess.run(["ssh", args.server, f"mkdir -p {target_root}"], check=True)
        subprocess.run([
            "rsync", "-avz", "--delete",
            f"{local_stage}/",
            f"{args.server}:{target_root}/",
        ], check=True)
        print("upload complete")
        print(f"\nNext: ssh {args.server} 'cd ~/dip_1_ws && python scripts/run_PG_enh1_real_generated.py --output-root /data/dip_1_ws/runs/PG_enh1_real_v2 --source-manifest {target_root}/PG_REAL_MESHES_MANIFEST.json'")


if __name__ == "__main__":
    main()

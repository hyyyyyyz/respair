#!/usr/bin/env python3
"""Fetch real high-quality meshes for PG-enh1 set C, no manual download needed.

Sources:
1. Polyhaven free PBR-quality models (artist-built, noisy real-world topology)
2. Objaverse via huggingface API (curated diverse mesh subset)

Outputs to /data/dip_1_ws/datasets/pg_real_meshes/ (alongside set A).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

OUT_ROOT = Path("/data/dip_1_ws/datasets/pg_real_meshes")
OUT_ROOT.mkdir(parents=True, exist_ok=True)

# Polyhaven: high-quality artist-built meshes with PBR materials.
# Direct download URLs (no auth, public CC0).
# Format: https://dl.polyhaven.org/file/ph-assets/Models/{fmt}/{res}/{slug}/{slug}_{res}.{fmt}
POLYHAVEN_PICKS = [
    ("teddy_bear", "creature_plush"),
    ("garden_chair", "object_chair"),
    ("food_kiwi_01", "object_organic"),
    ("rocking_chair_01", "object_chair"),
    ("camping_chair", "object_chair"),
    ("vintage_camera", "object_device"),
    ("rocking_horse", "creature_toy"),
    ("rotary_telephone", "object_device"),
]

POLYHAVEN_URL_TEMPLATES = [
    "https://dl.polyhaven.org/file/ph-assets/Models/glb/1k/{slug}/{slug}_1k.glb",
    "https://dl.polyhaven.org/file/ph-assets/Models/gltf/1k/{slug}/{slug}_1k.gltf",
]


def fetch_polyhaven(slug: str, category: str, manifest_records: list) -> bool:
    """Try to download a single polyhaven model."""
    asset_dir = OUT_ROOT / f"poly_{slug}"
    asset_dir.mkdir(exist_ok=True)
    for tmpl in POLYHAVEN_URL_TEMPLATES:
        url = tmpl.format(slug=slug)
        ext = url.rsplit(".", 1)[-1]
        target = asset_dir / f"poly_{slug}.{ext}"
        if target.exists() and target.stat().st_size > 1024:
            print(f"[polyhaven] already cached: {slug}")
            manifest_records.append(record(slug, target, category, "polyhaven"))
            return True
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as resp, open(target, "wb") as fh:
                shutil.copyfileobj(resp, fh)
            if target.stat().st_size > 1024:
                print(f"[polyhaven] OK: {slug} ({target.stat().st_size//1024} KB)")
                manifest_records.append(record(slug, target, category, "polyhaven"))
                return True
        except Exception as e:
            print(f"[polyhaven] {slug} {ext} fail: {e}")
            continue
    return False


def fetch_objaverse(num: int = 8, manifest_records: list = None) -> int:
    """Download Objaverse subset using objaverse python package."""
    import objaverse
    uids = objaverse.load_uids()
    print(f"[objaverse] total {len(uids)} uids; sampling {num}")
    # sample diverse uids by hash spread
    picked = uids[::max(1, len(uids)//200)][:num]
    objects = objaverse.load_objects(uids=picked, download_processes=2)
    n_ok = 0
    for uid, glb_path in objects.items():
        if not glb_path or not Path(glb_path).exists():
            continue
        size_kb = Path(glb_path).stat().st_size // 1024
        if size_kb < 4:
            print(f"[objaverse] {uid} too small ({size_kb} KB), skip")
            continue
        slug = f"objav_{uid[:10]}"
        asset_dir = OUT_ROOT / slug
        asset_dir.mkdir(exist_ok=True)
        target = asset_dir / f"{slug}.glb"
        shutil.copy(glb_path, target)
        manifest_records.append(record(slug.split("_", 1)[1], target, "objaverse_curated", "objaverse"))
        print(f"[objaverse] OK: {uid} -> {target} ({size_kb} KB)")
        n_ok += 1
    return n_ok


def record(slug: str, path: Path, category: str, source: str) -> dict:
    return {
        "asset_id": f"{source[:5]}_{slug}",
        "mesh_path": str(path),
        "source": source,
        "category": category,
        "status": "ok",
        "seed": 42,
        "failure_reason": None,
        "metadata": {"original_filename": path.name},
    }


def main() -> None:
    manifest_records: list = []

    # Check existing set-A manifest, merge to keep all in one
    existing_manifest = OUT_ROOT / "PG_REAL_MESHES_MANIFEST.json"
    if existing_manifest.exists():
        try:
            existing_records = json.loads(existing_manifest.read_text())
            print(f"loaded {len(existing_records)} existing records (set A)")
            manifest_records.extend(existing_records)
        except Exception:
            pass

    print("=" * 60)
    print("fetching Polyhaven artist-built meshes...")
    poly_ok = 0
    for slug, cat in POLYHAVEN_PICKS:
        if fetch_polyhaven(slug, cat, manifest_records):
            poly_ok += 1
        time.sleep(0.5)
    print(f"polyhaven success: {poly_ok}/{len(POLYHAVEN_PICKS)}")

    print("=" * 60)
    print("fetching Objaverse curated subset...")
    try:
        obj_ok = fetch_objaverse(num=10, manifest_records=manifest_records)
        print(f"objaverse success: {obj_ok}")
    except Exception as e:
        print(f"objaverse failed: {e}")

    # Dedup by asset_id
    seen = set()
    deduped = []
    for r in manifest_records:
        if r["asset_id"] in seen:
            continue
        seen.add(r["asset_id"])
        deduped.append(r)

    out = OUT_ROOT / "PG_REAL_MESHES_MANIFEST_v2.json"
    out.write_text(json.dumps(deduped, indent=2))
    print("=" * 60)
    print(f"final manifest: {out}")
    print(f"total mesh records: {len(deduped)}")
    by_source = {}
    for r in deduped:
        by_source[r["source"]] = by_source.get(r["source"], 0) + 1
    for s, n in sorted(by_source.items()):
        print(f"  {s}: {n}")


if __name__ == "__main__":
    main()

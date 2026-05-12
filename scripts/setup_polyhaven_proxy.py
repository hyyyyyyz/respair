#!/usr/bin/env python
"""Download Poly Haven CC0 PBR models and texture bundles.

For each slug, download the gltf bundle (mesh + bin + textures) at 1k.
Idempotent: skips already-complete slugs. Saves to
``$OUT/raw/<slug>/`` matching the gltf relative paths.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import urllib.request
from pathlib import Path


SLUGS_DEFAULT = [
    "ceramic_vase_01", "wooden_bowl_01", "concrete_brick", "iron_chair_01",
    "marble_bust_01", "metal_lamp_01", "plastic_crate", "rocky_boulder_01",
    "rusted_barrel", "stone_buddha", "vintage_camera", "wooden_box_01",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="/data/dip_1_ws/datasets/polyhaven_proxy")
    p.add_argument("--res", default="1k", choices=["1k", "2k", "4k", "8k"])
    p.add_argument("--slugs", nargs="*", default=SLUGS_DEFAULT)
    p.add_argument("--timeout", type=int, default=120)
    return p.parse_args()


def _download(url: str, target: Path, *, timeout: int) -> bool:
    import time
    target.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) PG2026-pbr-atlas/1.0",
            "Accept": "*/*",
        },
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                with target.open("wb") as f:
                    shutil.copyfileobj(response, f)
            return True
        except Exception as exc:
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            print(f"    fail {url}: {exc}")
            return False
    return False


def _slug_files(out_root: Path, slug: str, res: str, timeout: int) -> dict:
    asset_dir = out_root / "raw" / slug
    asset_dir.mkdir(parents=True, exist_ok=True)
    files_json = asset_dir / "files.json"
    if not files_json.exists():
        files_url = f"https://api.polyhaven.com/files/{slug}"
        if not _download(files_url, files_json, timeout=timeout):
            return {"slug": slug, "status": "files_api_failed"}
    data = json.loads(files_json.read_text())
    gltf = data.get("gltf", {}).get(res, {}).get("gltf", {})
    main_url = gltf.get("url")
    if not main_url:
        return {"slug": slug, "status": "no_gltf_url"}
    main_path = asset_dir / Path(main_url).name
    files = [(main_url, main_path)]
    include = gltf.get("include", {}) or {}
    for rel, info in include.items():
        files.append((info["url"], asset_dir / rel))
    ok = 0
    for url, p in files:
        if p.exists() and p.stat().st_size > 0:
            ok += 1
            continue
        if _download(url, p, timeout=timeout):
            ok += 1
    status = "ok" if ok == len(files) else f"partial:{ok}/{len(files)}"
    (asset_dir / ".done").write_text(status, encoding="utf-8")
    return {"slug": slug, "status": status, "n_files": len(files), "n_ok": ok, "main": str(main_path), "gltf_size": main_path.stat().st_size if main_path.exists() else 0}


def main() -> None:
    args = parse_args()
    out_root = Path(args.out)
    log_path = out_root / "setup.log"
    out_root.mkdir(parents=True, exist_ok=True)
    summary: list[dict] = []
    with log_path.open("a", encoding="utf-8") as log:
        log.write(f"=== Poly Haven download (res={args.res}, n={len(args.slugs)}) ===\n")
        for slug in args.slugs:
            print(f"  {slug}")
            row = _slug_files(out_root, slug, args.res, args.timeout)
            log.write(json.dumps(row) + "\n")
            print(f"    status={row.get('status')} n_ok={row.get('n_ok','-')} main_size={row.get('gltf_size','-')}")
            summary.append(row)
    out_summary = out_root / "polyhaven_setup_summary.json"
    out_summary.write_text(json.dumps({"rows": summary}, indent=2))
    print(f"Wrote {out_summary}")


if __name__ == "__main__":
    main()

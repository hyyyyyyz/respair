#!/usr/bin/env python
"""Prepare B7 generated/noisy mesh cache."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pbr_atlas.data.generated_mesh_loader import (  # noqa: E402
    DEFAULT_B7_DATA_ROOT,
    default_asset_ids,
    prepare_generated_mesh_set,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare B7 generated/noisy meshes.")
    parser.add_argument("--asset", default="all", help="Asset id or 'all'.")
    parser.add_argument("--count", type=int, default=None, help="Limit the default procedural fallback set.")
    parser.add_argument("--data-root", default=str(DEFAULT_B7_DATA_ROOT))
    parser.add_argument("--manifest", default=None, help="Optional JSON manifest with local_path/url/hf_repo sources.")
    parser.add_argument("--no-fallback", action="store_true", help="Fail if manifest downloads are unavailable.")
    parser.add_argument("--force", action="store_true", help="Regenerate or redownload cached meshes.")
    parser.add_argument("--list", action="store_true", help="List default procedural B7 asset ids and exit.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.list:
        for asset_id in default_asset_ids():
            print(asset_id)
        return

    asset_ids = None if args.asset == "all" else [args.asset]
    records = prepare_generated_mesh_set(
        data_root=Path(args.data_root),
        asset_ids=asset_ids,
        count=args.count,
        manifest=args.manifest,
        offline_ok=not args.no_fallback,
        force=args.force,
    )
    for record in records:
        print(f"{record.asset_id}\t{record.status}\t{record.source}\t{record.mesh_path}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""Prepare B1 sample assets with offline-friendly primitive fallbacks."""

from __future__ import annotations

import argparse
from pathlib import Path

from pbr_atlas.data.asset_registry import DEFAULT_DATA_ROOT, prepare_all, prepare_asset


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare B1 sample assets.")
    parser.add_argument("--asset", default="all", choices=["all", "bunny", "spot", "objaverse", "objaverse_sample"])
    parser.add_argument("--data-root", default=str(DEFAULT_DATA_ROOT))
    parser.add_argument("--no-fallback", action="store_true", help="Fail instead of writing primitive fallback meshes.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data_root = Path(args.data_root)
    if args.asset == "all":
        paths = prepare_all(data_root, offline_ok=not args.no_fallback)
    else:
        paths = [prepare_asset(args.asset, data_root, offline_ok=not args.no_fallback)]
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()


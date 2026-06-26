#!/usr/bin/env python
"""Build a controlled Phase 40 current-data refresh manifest."""

from __future__ import annotations

import argparse

from dotenv import load_dotenv

from business_cycle.current.current_data_refresh import (
    build_current_data_refresh_manifest,
    summarize_current_data_refresh_manifest,
    write_current_data_refresh_manifest,
)


def main() -> int:
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--cache-dir")
    parser.add_argument("--snapshot-as-of")
    parser.add_argument("--no-live-fetch", action="store_true")
    parser.add_argument("--allow-fixture-fallback", action="store_true")
    args = parser.parse_args()

    manifest = build_current_data_refresh_manifest(
        snapshot_as_of=args.snapshot_as_of,
        no_live_fetch=args.no_live_fetch,
        allow_fixture_fallback=args.allow_fixture_fallback,
        cache_dir=args.cache_dir,
    )
    write = write_current_data_refresh_manifest(manifest, output=args.output)
    summary = summarize_current_data_refresh_manifest(manifest)
    for key, value in summary.items():
        print(f"{key}={_format(value)}")
    print(f"output={write['output']}")
    print("result=passed")
    return 0


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())

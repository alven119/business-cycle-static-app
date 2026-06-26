#!/usr/bin/env python
"""Show Phase 41 live current refresh environment probe."""

from __future__ import annotations

import argparse

from dotenv import load_dotenv

from business_cycle.current.current_live_refresh_probe import (
    probe_current_live_refresh_environment,
)


def main() -> int:
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    parser.add_argument("--cache-dir", default="data/raw/fred_current_cache")
    args = parser.parse_args()

    summary = probe_current_live_refresh_environment(
        output=args.output,
        cache_dir=args.cache_dir,
    )
    for key, value in summary.items():
        print(f"{key}={_format(value)}")
    if args.output:
        print(f"output={args.output}")
    print("result=passed")
    return 0


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python
"""Show Phase 41 current stale remediation diagnostics."""

from __future__ import annotations

import argparse

from business_cycle.current.current_stale_remediation import (
    summarize_current_stale_remediation,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh-manifest")
    args = parser.parse_args()

    summary = summarize_current_stale_remediation(
        refresh_manifest_path=args.refresh_manifest,
    )
    for key, value in summary.items():
        print(f"{key}={_format(value)}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())

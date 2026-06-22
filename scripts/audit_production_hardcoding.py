#!/usr/bin/env python
"""Audit production hard-coded scenario/date references."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.audits.production_hardcoding import (  # noqa: E402
    summarize_production_hardcoding,
)


def main() -> int:
    summary = summarize_production_hardcoding()
    for key, value in summary.items():
        if key == "findings":
            print(f"finding_count={len(value)}")
            continue
        print(f"{key}={_format(value)}")
    return 0


def _format(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())

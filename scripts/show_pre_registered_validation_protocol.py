#!/usr/bin/env python
"""Show QA3 pre-registered data-only validation protocol."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.audits.pre_registered_validation import (  # noqa: E402
    summarize_pre_registered_validation_protocol,
)


def main() -> int:
    summary = summarize_pre_registered_validation_protocol()
    for key, value in summary.items():
        print(f"{key}={_format(value)}")
    return 0


def _format(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())

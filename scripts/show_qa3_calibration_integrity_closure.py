#!/usr/bin/env python
"""Show QA3 calibration integrity closure status."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.audits.qa3_calibration_integrity_closure import (  # noqa: E402
    summarize_qa3_calibration_integrity_closure,
)


def main() -> int:
    summary = summarize_qa3_calibration_integrity_closure()
    for key, value in summary.items():
        if isinstance(value, dict):
            print(f"{key}_ready=true")
            continue
        print(f"{key}={_format(value)}")
    return 0


def _format(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())

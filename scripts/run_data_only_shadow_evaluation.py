#!/usr/bin/env python
"""Run QA3 data-only shadow diagnostics without writing outputs."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.audits.data_only_shadow_evaluation import (  # noqa: E402
    run_data_only_shadow_evaluation,
)


def main() -> int:
    summary = run_data_only_shadow_evaluation()
    for key, value in summary.items():
        if key == "rows":
            print(f"shadow_row_count={len(value)}")
            continue
        print(f"{key}={_format(value)}")
    return 0


def _format(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())

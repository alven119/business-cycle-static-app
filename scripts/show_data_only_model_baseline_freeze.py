#!/usr/bin/env python
"""Show QA3 data-only baseline freeze status."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from business_cycle.audits.data_only_model_freeze import (  # noqa: E402
    summarize_data_only_model_baseline_freeze,
)


def main() -> int:
    summary = summarize_data_only_model_baseline_freeze()
    for key, value in summary.items():
        if key in {"phase_spec_hashes", "transition_control_hashes"}:
            print(f"{key}_count={len(value)}")
            continue
        if key in {"missing_files", "hash_mismatches", "unfrozen_decision_files"}:
            print(f"{key}_count={len(value)}")
            continue
        print(f"{key}={_format(value)}")
    return 0


def _format(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())

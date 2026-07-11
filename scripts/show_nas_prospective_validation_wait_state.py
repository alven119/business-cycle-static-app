#!/usr/bin/env python
"""Show the current read-only prospective calendar gate."""

from __future__ import annotations

from business_cycle.validation.nas_prospective_validation_wait_state import (
    summarize_nas_prospective_validation_wait_state,
)


def main() -> int:
    summary = summarize_nas_prospective_validation_wait_state()
    for key, value in summary.items():
        if not isinstance(value, (dict, list)):
            print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

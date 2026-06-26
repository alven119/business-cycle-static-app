#!/usr/bin/env python
"""Show Phase 37 recession/recovery PIT gap matrix summary."""

from __future__ import annotations

from business_cycle.validation.recession_recovery_pit_gap_matrix import (
    summarize_recession_recovery_pit_gap_matrix,
)


def main() -> int:
    summary = summarize_recession_recovery_pit_gap_matrix()
    for key, value in summary.items():
        if key == "matrix_rows":
            continue
        print(f"{key}={value}")
    print(f"result={'passed' if summary['recession_recovery_pit_gap_matrix_ready'] else 'blocked'}")
    return 0 if summary["recession_recovery_pit_gap_matrix_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

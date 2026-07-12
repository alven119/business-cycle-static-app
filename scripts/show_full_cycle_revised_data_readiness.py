#!/usr/bin/env python
"""Show Phase 130 four-phase revised data readiness."""

from business_cycle.storage.full_cycle_revised_data_readiness import (
    summarize_full_cycle_revised_data_readiness,
)


def main() -> int:
    summary = summarize_full_cycle_revised_data_readiness()
    for key, value in summary.items():
        if key == "role_rows":
            continue
        rendered = str(value).lower() if isinstance(value, bool) else value
        print(f"{key}={rendered}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

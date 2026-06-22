#!/usr/bin/env python
"""Show QA1 temporal integrity closure state."""

from __future__ import annotations

from business_cycle.audits.qa1_temporal_integrity_closure import (
    summarize_qa1_temporal_integrity_closure,
)


def main() -> int:
    summary = summarize_qa1_temporal_integrity_closure()
    for key, value in summary.items():
        if key in {"qa2_prohibited_use_cases", "qa2_required_data_tiers", "unresolved_archive_series_ids"}:
            print(f"{key}={','.join(value)}")
        else:
            print(f"{key}={_format(value)}")
    return 0


def _format(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())

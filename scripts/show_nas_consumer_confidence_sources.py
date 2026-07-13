#!/usr/bin/env python
"""Show the Phase 136 consumer-confidence source contract and drills."""

from __future__ import annotations

from business_cycle.service.nas_consumer_confidence_sources import (
    build_consumer_confidence_failure_drills,
    summarize_consumer_confidence_source_contract,
)


def main() -> int:
    summary = summarize_consumer_confidence_source_contract()
    drills = build_consumer_confidence_failure_drills()
    for key, value in (summary | {"drill_pass_count": drills["drill_pass_count"]}).items():
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

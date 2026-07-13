#!/usr/bin/env python
"""Show Phase 136 consumer-confidence source closure."""

from __future__ import annotations

from business_cycle.audits.phase136_consumer_confidence_sources_closure import (
    summarize_phase136_consumer_confidence_sources_closure,
)


def main() -> int:
    summary = summarize_phase136_consumer_confidence_sources_closure()
    for key, value in summary.items():
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

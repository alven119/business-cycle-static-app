#!/usr/bin/env python
"""Show Phase 42 closure."""

from __future__ import annotations

from business_cycle.audits.phase42_current_freshness_and_evidence_profile_closure import (
    summarize_phase42_current_freshness_and_evidence_profile_closure,
)


def main() -> int:
    summary = summarize_phase42_current_freshness_and_evidence_profile_closure()
    for key, value in summary.items():
        if key in {"audit", "freeze"}:
            continue
        print(f"{key}={_format(value)}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())

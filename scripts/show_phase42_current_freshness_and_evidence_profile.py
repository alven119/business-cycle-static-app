#!/usr/bin/env python
"""Show Phase 42 current freshness and evidence-profile audit."""

from __future__ import annotations

from business_cycle.audits.phase42_current_freshness_and_evidence_profile import (
    summarize_phase42_current_freshness_and_evidence_profile,
)


def main() -> int:
    summary = summarize_phase42_current_freshness_and_evidence_profile()
    for key, value in summary.items():
        if key in {"freshness", "readiness", "snapshot", "dashboard", "browser_verification"}:
            continue
        print(f"{key}={_format(value)}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())

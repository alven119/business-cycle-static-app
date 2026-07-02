#!/usr/bin/env python
"""Show Phase61 major-group evidence profile readiness closure."""

from __future__ import annotations

from business_cycle.audits.phase61_major_group_evidence_profile_readiness_closure import (
    summarize_phase61_major_group_evidence_profile_readiness_closure,
)


def main() -> int:
    summary = summarize_phase61_major_group_evidence_profile_readiness_closure()
    for key, value in summary.items():
        if key.endswith("_summary") or key == "product_capability_progress":
            continue
        print(f"{key}={value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

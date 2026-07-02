#!/usr/bin/env python
"""Show Phase60 evidence freshness/release/value continuity closure."""

from __future__ import annotations

from business_cycle.audits.phase60_evidence_freshness_release_value_continuity_closure import (
    summarize_phase60_evidence_freshness_release_value_continuity_closure,
)


def main() -> int:
    summary = summarize_phase60_evidence_freshness_release_value_continuity_closure()
    for key, value in summary.items():
        if key.endswith("_summary") or key == "product_capability_progress":
            continue
        print(f"{key}={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

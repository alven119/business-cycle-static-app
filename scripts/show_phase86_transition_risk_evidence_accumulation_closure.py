#!/usr/bin/env python3
"""Show Phase86 transition risk evidence accumulation closure summary."""

from __future__ import annotations

from business_cycle.audits.phase86_transition_risk_evidence_accumulation_closure import (
    summarize_phase86_transition_risk_evidence_accumulation_closure,
)


def main() -> int:
    summary = summarize_phase86_transition_risk_evidence_accumulation_closure()
    for key, value in summary.items():
        if key == "product_capability_rows":
            continue
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Show Phase86 transition risk evidence accumulation summary."""

from __future__ import annotations

from business_cycle.render.transition_risk_evidence_accumulation import (
    summarize_transition_risk_evidence_accumulation,
)


def main() -> int:
    summary = summarize_transition_risk_evidence_accumulation()
    for key, value in summary.items():
        if key == "transition_risk_evidence_accumulation_artifact":
            continue
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

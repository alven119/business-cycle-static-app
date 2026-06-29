#!/usr/bin/env python
"""Show Phase48 boom transition evidence wiring closure summary."""

from __future__ import annotations

from business_cycle.audits.phase48_boom_transition_evidence_wiring_closure import (
    summarize_phase48_boom_transition_evidence_wiring_closure,
)


def main() -> int:
    summary = summarize_phase48_boom_transition_evidence_wiring_closure()
    for key, value in summary.items():
        print(f"{key}={_format(value)}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())

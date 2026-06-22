#!/usr/bin/env python
"""Audit formal phase decision gates for strict historical scoring."""

from __future__ import annotations

from business_cycle.audits.formal_phase_decision_eligibility import (
    summarize_formal_phase_decision_eligibility,
)


def main() -> int:
    summary = summarize_formal_phase_decision_eligibility()
    for key, value in summary.items():
        print(f"{key}={_format(value)}")
    return 0


def _format(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())

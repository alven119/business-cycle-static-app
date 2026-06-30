#!/usr/bin/env python
"""Show Phase51 closure."""

from __future__ import annotations

from business_cycle.audits.phase51_declared_start_and_gap_alternatives_closure import (
    summarize_phase51_declared_start_and_gap_alternatives_closure,
)


def main() -> int:
    summary = summarize_phase51_declared_start_and_gap_alternatives_closure()
    for key, value in summary.items():
        if key in {"declared_start_summary", "macro_gap_alternative_summary"}:
            continue
        print(f"{key}={_format(value)}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())

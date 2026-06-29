#!/usr/bin/env python
"""Show Phase47 phase-start research assistant summary."""

from __future__ import annotations

from business_cycle.cycle_state.phase_start_research_assistant import (
    summarize_phase_start_research_assistant,
)


def main() -> int:
    summary = summarize_phase_start_research_assistant()
    for key, value in summary.items():
        print(f"{key}={_format(value)}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())

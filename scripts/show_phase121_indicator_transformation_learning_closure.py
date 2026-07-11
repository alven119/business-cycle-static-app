#!/usr/bin/env python
"""Show Phase 121 indicator transformation and learning closure."""

from business_cycle.audits.phase121_indicator_transformation_learning_closure import (
    summarize_phase121_indicator_transformation_learning_closure,
)


def main() -> int:
    summary = summarize_phase121_indicator_transformation_learning_closure()
    for key, value in summary.items():
        rendered = str(value).lower() if isinstance(value, bool) else value
        print(f"{key}={rendered}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

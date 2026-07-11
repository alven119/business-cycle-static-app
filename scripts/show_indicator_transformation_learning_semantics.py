#!/usr/bin/env python
"""Show Phase 121 indicator transformation and learning audit."""

from business_cycle.audits.indicator_transformation_learning_semantics import (
    summarize_indicator_transformation_learning_semantics,
)


def main() -> int:
    summary = summarize_indicator_transformation_learning_semantics()
    for key, value in summary.items():
        if key == "rows":
            continue
        rendered = str(value).lower() if isinstance(value, bool) else value
        print(f"{key}={rendered}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

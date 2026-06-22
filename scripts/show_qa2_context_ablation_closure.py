#!/usr/bin/env python
"""Show QA2 context ablation closure status."""

from __future__ import annotations

from business_cycle.audits.qa2_context_ablation_closure import (
    summarize_qa2_context_ablation_closure,
)


def main() -> int:
    summary = summarize_qa2_context_ablation_closure()
    for key, value in summary.items():
        if key == "production_context_dependency_cases":
            print(f"{key}_count={len(value)}")
            continue
        print(f"{key}={_format(value)}")
    return 0


def _format(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())

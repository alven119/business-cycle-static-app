#!/usr/bin/env python3
"""Show Phase83-87 product capability completion sprint summary."""

from __future__ import annotations

from business_cycle.audits.product_capability_completion_sprint import (
    summarize_product_capability_completion_sprint,
)


def main() -> int:
    """Print key=value sprint readiness lines."""

    summary = summarize_product_capability_completion_sprint()
    for key, value in summary.items():
        if key in {"phase_table_rows", "target_capability_outcomes"}:
            continue
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

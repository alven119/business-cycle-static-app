#!/usr/bin/env python
"""Show Phase52 closure."""

from __future__ import annotations

from business_cycle.audits.phase52_official_macro_source_adapter_wiring_closure import (
    summarize_phase52_official_macro_source_adapter_wiring_closure,
)


def main() -> int:
    summary = summarize_phase52_official_macro_source_adapter_wiring_closure()
    for key, value in summary.items():
        if key in {
            "official_macro_source_wiring_summary",
            "product_capability_progress_summary",
            "product_capability_progress",
        }:
            continue
        print(f"{key}={_format(value)}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())

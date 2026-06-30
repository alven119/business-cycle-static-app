#!/usr/bin/env python
"""Show Phase52 official macro source adapter wiring."""

from __future__ import annotations

from business_cycle.current.official_macro_source_wiring import (
    summarize_official_macro_source_adapter_wiring,
)


def main() -> int:
    summary = summarize_official_macro_source_adapter_wiring()
    for key, value in summary.items():
        if key == "rows":
            continue
        print(f"{key}={_format(value)}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python
"""Show the Phase 40 current data refresh contract summary."""

from __future__ import annotations

from business_cycle.current.current_data_refresh_contract import (
    summarize_current_data_refresh_contract,
)


def main() -> int:
    summary = summarize_current_data_refresh_contract()
    for key, value in summary.items():
        if key == "contract":
            continue
        print(f"{key}={_format(value)}")
    return 0 if summary["current_data_refresh_contract_ready"] else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())

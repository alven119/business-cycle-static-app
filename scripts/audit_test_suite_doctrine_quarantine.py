#!/usr/bin/env python
"""Run the test-suite doctrine quarantine audit."""

from __future__ import annotations

from business_cycle.audits.test_suite_doctrine_quarantine import (
    summarize_test_suite_doctrine_quarantine,
)


def main() -> int:
    summary = summarize_test_suite_doctrine_quarantine()
    for key, value in summary.items():
        print(f"{key}={_format(value)}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python
"""Show Phase96 NAS app shell closure."""

from __future__ import annotations

from business_cycle.audits.phase96_nas_app_shell_closure import (
    summarize_phase96_nas_app_shell_closure,
)


def main() -> int:
    summary = summarize_phase96_nas_app_shell_closure()
    for key, value in summary.items():
        print(f"{key}={_format(value)}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python
"""Show Phase97 NAS ASGI adapter closure."""

from __future__ import annotations

from business_cycle.audits.phase97_nas_asgi_adapter_closure import (
    summarize_phase97_nas_asgi_adapter_closure,
)


def main() -> int:
    summary = summarize_phase97_nas_asgi_adapter_closure()
    for key, value in summary.items():
        print(f"{key}={_format(value)}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())

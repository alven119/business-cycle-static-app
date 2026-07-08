#!/usr/bin/env python
"""Show Phase97 NAS ASGI adapter readiness."""

from __future__ import annotations

from business_cycle.service.nas_asgi_adapter import summarize_nas_asgi_adapter


def main() -> int:
    summary = summarize_nas_asgi_adapter()
    for key, value in summary.items():
        if key == "nas_asgi_adapter":
            continue
        print(f"{key}={_format(value)}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python
"""Show Phase99 DS925+ deployment package assessment."""

from __future__ import annotations

from business_cycle.audits.nas_ds925_deployment_package_assessment import (
    summarize_nas_ds925_deployment_package_assessment,
)


def main() -> int:
    summary = summarize_nas_ds925_deployment_package_assessment()
    for key, value in summary.items():
        if key == "assessment":
            continue
        print(f"{key}={_format(value)}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())

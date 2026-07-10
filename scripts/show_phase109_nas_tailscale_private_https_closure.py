#!/usr/bin/env python
"""Show Phase109 Tailscale private HTTPS checkpoint closure."""

from business_cycle.audits.phase109_nas_tailscale_private_https_closure import (
    summarize_phase109_nas_tailscale_private_https_closure,
)


def _format(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


if __name__ == "__main__":
    summary = summarize_phase109_nas_tailscale_private_https_closure()
    for key, value in summary.items():
        print(f"{key}={_format(value)}")

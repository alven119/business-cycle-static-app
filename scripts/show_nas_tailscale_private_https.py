#!/usr/bin/env python
"""Show Phase109 private Tailscale HTTPS acceptance status."""

from business_cycle.service.nas_tailscale_private_https import (
    format_nas_tailscale_private_https_summary,
    summarize_nas_tailscale_private_https,
)


if __name__ == "__main__":
    print(format_nas_tailscale_private_https_summary(summarize_nas_tailscale_private_https()))

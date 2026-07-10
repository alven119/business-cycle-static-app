#!/usr/bin/env python
"""Show Phase 116 fixed-time and release-aware refresh contract."""

from business_cycle.service.nas_release_aware_refresh import (
    summarize_nas_release_aware_refresh_contract,
)


if __name__ == "__main__":
    for key, value in summarize_nas_release_aware_refresh_contract().items():
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")

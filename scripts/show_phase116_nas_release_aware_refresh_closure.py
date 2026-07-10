#!/usr/bin/env python
"""Show Phase 116 fixed-time and release-aware refresh closure."""

from business_cycle.audits.phase116_nas_release_aware_refresh_closure import (
    summarize_phase116_nas_release_aware_refresh_closure,
)


if __name__ == "__main__":
    for key, value in summarize_phase116_nas_release_aware_refresh_closure().items():
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")

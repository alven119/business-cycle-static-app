#!/usr/bin/env python
"""Show Phase 112 NAS scheduled revised refresh closure."""

from business_cycle.audits.phase112_nas_scheduled_revised_refresh_closure import (
    summarize_phase112_nas_scheduled_revised_refresh_closure,
)


if __name__ == "__main__":
    for key, value in summarize_phase112_nas_scheduled_revised_refresh_closure().items():
        rendered = str(value).lower() if isinstance(value, bool) else value
        print(f"{key}={rendered}")

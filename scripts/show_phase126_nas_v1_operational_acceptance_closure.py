#!/usr/bin/env python
"""Show Phase 126 private NAS v1.0 operational acceptance closure."""

from business_cycle.audits.phase126_nas_v1_operational_acceptance_closure import (
    summarize_phase126_nas_v1_operational_acceptance_closure,
)


if __name__ == "__main__":
    summary = summarize_phase126_nas_v1_operational_acceptance_closure()
    for key, value in summary.items():
        if key != "artifact":
            print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")

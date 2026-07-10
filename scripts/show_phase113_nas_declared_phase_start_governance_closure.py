#!/usr/bin/env python
"""Show Phase 113 private NAS declared-start governance closure."""

from business_cycle.audits.phase113_nas_declared_phase_start_governance_closure import (
    summarize_phase113_nas_declared_phase_start_governance_closure,
)


if __name__ == "__main__":
    for key, value in summarize_phase113_nas_declared_phase_start_governance_closure().items():
        rendered = str(value).lower() if isinstance(value, bool) else value
        print(f"{key}={rendered}")

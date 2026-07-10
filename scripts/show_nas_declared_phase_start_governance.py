#!/usr/bin/env python
"""Show Phase 113 private NAS declared-start governance readiness."""

from business_cycle.cycle_state.nas_declared_phase_start_registry import (
    summarize_nas_declared_phase_start_governance_contract,
)


if __name__ == "__main__":
    for key, value in summarize_nas_declared_phase_start_governance_contract().items():
        rendered = str(value).lower() if isinstance(value, bool) else value
        print(f"{key}={rendered}")

#!/usr/bin/env python
"""Show Phase 111 live Postgres dashboard closure."""

from business_cycle.audits.phase111_nas_live_postgres_dashboard_closure import (
    summarize_phase111_nas_live_postgres_dashboard_closure,
)


if __name__ == "__main__":
    for key, value in summarize_phase111_nas_live_postgres_dashboard_closure().items():
        rendered = str(value).lower() if isinstance(value, bool) else value
        print(f"{key}={rendered}")

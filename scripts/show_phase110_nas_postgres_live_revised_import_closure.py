#!/usr/bin/env python
"""Show Phase 110 NAS Postgres live revised import closure."""

from business_cycle.audits.phase110_nas_postgres_live_revised_import_closure import (
    summarize_phase110_nas_postgres_live_revised_import_closure,
)


if __name__ == "__main__":
    for key, value in summarize_phase110_nas_postgres_live_revised_import_closure().items():
        rendered = str(value).lower() if isinstance(value, bool) else value
        print(f"{key}={rendered}")

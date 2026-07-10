#!/usr/bin/env python
"""Show Phase 110 live revised-history import contract readiness."""

from business_cycle.storage.nas_postgres_live_revised_import import (
    summarize_nas_postgres_live_revised_import_contract,
)


if __name__ == "__main__":
    for key, value in summarize_nas_postgres_live_revised_import_contract().items():
        rendered = str(value).lower() if isinstance(value, bool) else value
        print(f"{key}={rendered}")

#!/usr/bin/env python
"""Show Phase 115 governed retry and backup/restore closure."""

from business_cycle.audits.phase115_nas_source_retry_restore_closure import (
    summarize_phase115_nas_source_retry_restore_closure,
)


if __name__ == "__main__":
    for key, value in summarize_phase115_nas_source_retry_restore_closure().items():
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")

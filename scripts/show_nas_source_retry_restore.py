"""Show Phase 115 source retry and backup/restore readiness."""

from business_cycle.service.nas_source_retry_restore import (
    summarize_nas_source_retry_restore_contract,
)


if __name__ == "__main__":
    for key, value in summarize_nas_source_retry_restore_contract().items():
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")

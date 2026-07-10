"""Show Phase 114 source-operations closure."""

from business_cycle.audits.phase114_nas_official_release_operations_closure import (
    summarize_phase114_nas_official_release_operations_closure,
)


if __name__ == "__main__":
    for key, value in summarize_phase114_nas_official_release_operations_closure().items():
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")

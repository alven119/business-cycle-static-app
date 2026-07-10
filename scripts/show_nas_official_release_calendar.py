"""Show Phase 114 official release-calendar contract readiness."""

from business_cycle.service.nas_official_release_calendar import (
    summarize_nas_official_release_calendar_contract,
)


if __name__ == "__main__":
    for key, value in summarize_nas_official_release_calendar_contract().items():
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")

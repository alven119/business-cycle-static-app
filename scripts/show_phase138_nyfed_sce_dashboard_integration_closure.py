#!/usr/bin/env python
"""Show Phase 138 NY Fed SCE dashboard integration closure."""

from business_cycle.audits.phase138_nyfed_sce_dashboard_integration_closure import (
    summarize_phase138_nyfed_sce_dashboard_integration_closure,
)


def main() -> int:
    summary = summarize_phase138_nyfed_sce_dashboard_integration_closure()
    for key, value in summary.items():
        rendered = str(value).lower() if isinstance(value, bool) else value
        print(f"{key}={rendered}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python
"""Show the private NAS source incident center without mutating it."""

from __future__ import annotations

from business_cycle.service.nas_source_incident_center import (
    build_source_incident_center,
    summarize_nas_source_incident_center_contract,
)


def main() -> int:
    contract = summarize_nas_source_incident_center_contract()
    center = build_source_incident_center()
    for key, value in contract.items():
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    for key in (
        "registry_status",
        "open_incident_count",
        "critical_open_incident_count",
        "affected_role_count",
        "affected_cycle_lane_count",
        "fallback_active_count",
        "recovery_receipt_count",
    ):
        print(f"{key}={center[key]}")
    return 0 if contract["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

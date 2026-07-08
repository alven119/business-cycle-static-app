#!/usr/bin/env python
"""Run Phase98 local NAS service lifecycle rehearsal."""

from __future__ import annotations

from business_cycle.service.nas_service_lifecycle import build_nas_service_lifecycle


def main() -> int:
    lifecycle = build_nas_service_lifecycle()
    for key in (
        "nas_service_lifecycle_ready",
        "lifecycle_rehearsal_ready",
        "startup_rehearsed",
        "readiness_probe_ready",
        "shutdown_rehearsed",
        "rollback_rehearsal_ready",
        "readiness_probe_pass_count",
        "service_health_status",
        "uvicorn_run_attempt_count",
        "network_bind_attempt_count",
        "live_server_start_attempt_count",
        "live_db_connection_attempt_count",
        "postgres_read_attempt_count",
        "postgres_write_attempt_count",
        "public_output_count",
    ):
        value = lifecycle[key]
        if isinstance(value, bool):
            value = str(value).lower()
        print(f"{key}={value}")
    return 0 if lifecycle["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

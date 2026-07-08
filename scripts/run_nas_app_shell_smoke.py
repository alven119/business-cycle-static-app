#!/usr/bin/env python
"""Run Phase96 in-process NAS app shell smoke."""

from __future__ import annotations

from business_cycle.service.nas_app_shell import build_nas_app_shell


def main() -> int:
    shell = build_nas_app_shell()
    for key in (
        "nas_app_shell_ready",
        "local_service_smoke_ready",
        "authenticated_smoke_pass_count",
        "unauthenticated_smoke_rejected_count",
        "service_health_status",
        "network_bind_attempt_count",
        "live_server_start_attempt_count",
        "live_db_connection_attempt_count",
        "postgres_write_attempt_count",
        "public_output_count",
    ):
        value = shell[key]
        if isinstance(value, bool):
            value = str(value).lower()
        print(f"{key}={value}")
    return 0 if shell["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

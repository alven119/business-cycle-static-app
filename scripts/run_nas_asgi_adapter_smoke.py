#!/usr/bin/env python
"""Run Phase97 in-process ASGI adapter smoke."""

from __future__ import annotations

from business_cycle.service.nas_asgi_adapter import build_nas_asgi_adapter


def main() -> int:
    adapter = build_nas_asgi_adapter()
    for key in (
        "nas_asgi_adapter_ready",
        "local_asgi_smoke_ready",
        "authenticated_asgi_smoke_pass_count",
        "unauthenticated_asgi_smoke_rejected_count",
        "unsupported_method_rejected_count",
        "unknown_route_rejected_count",
        "uvicorn_run_attempt_count",
        "network_bind_attempt_count",
        "live_server_start_attempt_count",
        "live_db_connection_attempt_count",
        "postgres_write_attempt_count",
        "public_output_count",
    ):
        value = adapter[key]
        if isinstance(value, bool):
            value = str(value).lower()
        print(f"{key}={value}")
    return 0 if adapter["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python
"""Run Phase100 Container Manager bundle dry-run."""

from __future__ import annotations

import argparse

from business_cycle.service.nas_container_manager_bundle import (
    build_nas_container_manager_bundle,
    write_nas_container_manager_bundle_dry_run,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir")
    args = parser.parse_args()

    bundle = build_nas_container_manager_bundle()
    for key in (
        "nas_container_manager_bundle_ready",
        "compose_yaml_valid",
        "compose_service_count",
        "host_port_publish_count",
        "secret_value_literal_count",
        "container_manager_import_attempt_count",
        "docker_compose_execution_count",
        "container_start_attempt_count",
        "live_db_connection_attempt_count",
        "postgres_write_attempt_count",
        "public_output_count",
    ):
        print(f"{key}={_format(bundle[key])}")
    if args.output_dir:
        output = write_nas_container_manager_bundle_dry_run(args.output_dir)
        for key in (
            "dry_run_output_path_count",
            "dry_run_output_under_tmp_only",
            "repo_output_written_count",
            "public_output_count",
        ):
            print(f"{key}={_format(output[key])}")
    return 0 if bundle["result"] == "passed" else 1


def _format(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())

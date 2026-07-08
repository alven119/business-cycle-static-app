#!/usr/bin/env python
"""Run Phase101 private local startup smoke report generation."""

from __future__ import annotations

import argparse

from business_cycle.service.nas_private_local_startup_smoke import (
    summarize_nas_private_local_startup_smoke,
    write_nas_private_local_startup_smoke_report,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=False)
    args = parser.parse_args()
    summary = summarize_nas_private_local_startup_smoke()
    for key in (
        "nas_private_local_startup_smoke_ready",
        "startup_plan_ready",
        "startup_command_preview_ready",
        "readiness_probe_pass_count",
        "startup_command_executed_count",
        "uvicorn_run_attempt_count",
        "network_bind_attempt_count",
        "live_server_start_attempt_count",
        "result",
    ):
        print(
            f"{key}="
            f"{str(summary[key]).lower() if isinstance(summary[key], bool) else summary[key]}",
        )
    if args.output_dir:
        written = write_nas_private_local_startup_smoke_report(args.output_dir)
        for key in (
            "startup_smoke_output_path_count",
            "startup_smoke_output_under_tmp_only",
            "repo_output_written_count",
            "public_output_count",
        ):
            print(
                f"{key}="
                f"{str(written[key]).lower() if isinstance(written[key], bool) else written[key]}",
            )
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

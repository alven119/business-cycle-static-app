#!/usr/bin/env python
"""Generate Phase102 guided DS925+ install/read-only smoke artifacts."""

from __future__ import annotations

import argparse

from business_cycle.service.nas_guided_ds925_install_smoke import (
    summarize_nas_guided_ds925_install_smoke,
    write_nas_guided_ds925_install_smoke_report,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=False)
    args = parser.parse_args()
    summary = summarize_nas_guided_ds925_install_smoke()
    for key in (
        "nas_guided_ds925_install_smoke_ready",
        "guided_install_runbook_ready",
        "nas_side_readonly_smoke_plan_ready",
        "readonly_smoke_command_executed_count",
        "actual_nas_connection_attempt_count",
        "container_manager_import_attempt_count",
        "container_start_attempt_count",
        "result",
    ):
        print(
            f"{key}="
            f"{str(summary[key]).lower() if isinstance(summary[key], bool) else summary[key]}",
        )
    if args.output_dir:
        written = write_nas_guided_ds925_install_smoke_report(args.output_dir)
        for key in (
            "guided_install_output_path_count",
            "guided_install_output_under_tmp_only",
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

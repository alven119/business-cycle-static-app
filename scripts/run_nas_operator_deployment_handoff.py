#!/usr/bin/env python
"""Write Phase105 NAS operator handoff artifacts under /tmp."""

from __future__ import annotations

import argparse

from business_cycle.service.nas_operator_deployment_handoff import (
    write_nas_operator_deployment_handoff_report,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    result = write_nas_operator_deployment_handoff_report(args.output_dir)
    for key, value in {
        "nas_operator_deployment_handoff_ready": result[
            "nas_operator_deployment_handoff_ready"
        ],
        "handoff_output_path_count": result["handoff_output_path_count"],
        "handoff_output_under_tmp_only": result["handoff_output_under_tmp_only"],
        "repo_output_written_count": result["repo_output_written_count"],
        "public_output_count": result["public_output_count"],
    }.items():
        rendered = str(value).lower() if isinstance(value, bool) else value
        print(f"{key}={rendered}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

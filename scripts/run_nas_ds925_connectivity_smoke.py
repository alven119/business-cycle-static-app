#!/usr/bin/env python
"""Generate Phase103 DS925+ connectivity smoke artifacts."""

from __future__ import annotations

import argparse

from business_cycle.service.nas_ds925_connectivity_smoke import (
    build_nas_ds925_connectivity_smoke,
    write_nas_ds925_connectivity_smoke_report,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=False)
    parser.add_argument("--execute-live", action="store_true")
    args = parser.parse_args()
    summary = build_nas_ds925_connectivity_smoke(execute_live=args.execute_live)
    for key in (
        "nas_ds925_connectivity_smoke_ready",
        "nas_private_ip",
        "nas_private_ip_private_lan",
        "probe_port_count",
        "live_probe_executed",
        "live_probe_attempt_count",
        "live_probe_reachable_count",
        "live_probe_unreachable_count",
        "dsm_login_attempt_count",
        "postgres_write_attempt_count",
        "result",
    ):
        print(
            f"{key}="
            f"{str(summary[key]).lower() if isinstance(summary[key], bool) else summary[key]}",
        )
    if args.output_dir:
        written = write_nas_ds925_connectivity_smoke_report(
            args.output_dir,
            execute_live=args.execute_live,
        )
        for key in (
            "connectivity_smoke_output_path_count",
            "connectivity_smoke_output_under_tmp_only",
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

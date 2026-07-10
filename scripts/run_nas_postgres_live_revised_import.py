#!/usr/bin/env python
"""Run the operator-gated NAS Postgres revised-history import."""

from __future__ import annotations

import argparse

from business_cycle.storage.nas_postgres_live_revised_import import (
    CONFIRMATION,
    summarize_nas_postgres_live_revised_import_contract,
)
from business_cycle.service.nas_revised_import_worker import main as worker_main


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--artifact-dir",
        default="/var/lib/business-cycle/source-artifacts/phase110",
    )
    parser.add_argument("--execute-live", action="store_true")
    parser.add_argument("--operator-confirmation")
    parser.add_argument("--no-resume", action="store_true")
    parser.add_argument("--show-confirmation-token", action="store_true")
    args = parser.parse_args()

    if not args.execute_live:
        summary = summarize_nas_postgres_live_revised_import_contract()
        for key, value in summary.items():
            print(f"{key}={_format(value)}")
        if args.show_confirmation_token:
            print(f"operator_confirmation_token={CONFIRMATION}")
        return 0 if summary["result"] == "passed" else 1

    worker_args = [
        "--artifact-dir",
        args.artifact_dir,
        "--execute-live",
        "--operator-confirmation",
        args.operator_confirmation or "",
    ]
    if args.no_resume:
        worker_args.append("--no-resume")
    return worker_main(worker_args)


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())

"""Container entrypoint for the operator-gated Phase 110 revised import."""

from __future__ import annotations

import argparse

from business_cycle.storage.nas_postgres_live_revised_import import (
    run_nas_postgres_live_revised_import,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--artifact-dir",
        default="/var/lib/business-cycle/source-artifacts/phase110",
    )
    parser.add_argument("--execute-live", action="store_true")
    parser.add_argument("--operator-confirmation", required=True)
    parser.add_argument("--no-resume", action="store_true")
    args = parser.parse_args(argv)
    report = run_nas_postgres_live_revised_import(
        execute_live=args.execute_live,
        operator_confirmation=args.operator_confirmation,
        artifact_dir=args.artifact_dir,
        resume=not args.no_resume,
    )
    for key in (
        "requested_series_count",
        "completed_series_count",
        "failed_series_count",
        "observation_revised_row_count_planned",
        "source_artifact_count",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "result",
    ):
        value = report[key]
        rendered = str(value).lower() if isinstance(value, bool) else value
        print(f"{key}={rendered}")
    return 0 if report["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

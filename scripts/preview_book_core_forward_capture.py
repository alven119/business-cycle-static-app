"""Preview QA11 forward-capture plan without API or registry writes."""

from __future__ import annotations

import argparse

from business_cycle.audits.forward_capture_dry_run import (
    preview_book_core_forward_capture,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--role-id")
    parser.add_argument("--major-group")
    parser.add_argument("--all-forward-ready", action="store_true")
    parser.add_argument("--as-of")
    parser.add_argument("--no-api", action="store_true", default=True)
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--cache-dir")
    parser.add_argument("--output")
    args = parser.parse_args()
    summary = preview_book_core_forward_capture(
        role_id=args.role_id,
        major_group=args.major_group,
        all_forward_ready=args.all_forward_ready,
        as_of=args.as_of,
        output=args.output,
    )
    for key in (
        "phase",
        "forward_capture_dry_run_ready",
        "requested_role_count",
        "forward_ready_role_count",
        "forward_blocked_role_count",
        "source_request_plan_count",
        "release_artifact_plan_count",
        "derived_capture_plan_count",
        "unresolved_contract_count",
        "registry_write_attempted",
        "prospective_result_inspected",
        "candidate_selection_enabled",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
from pathlib import Path

from business_cycle.audits.shadow_candidate_diagnostics import (
    run_shadow_candidate_diagnostics,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run QA7 shadow candidate diagnostics.")
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--data-mode", required=True, choices=("vintage_as_of", "revised"))
    parser.add_argument("--point-in-time-cache-dir", default=None)
    parser.add_argument("--output", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = run_shadow_candidate_diagnostics(
        as_of=args.as_of,
        data_mode=args.data_mode,
        output=Path(args.output) if args.output else None,
        point_in_time_cache_dir=args.point_in_time_cache_dir,
    )
    for key in (
        "phase",
        "model_id",
        "rule_registry_version",
        "candidate_selection_contract_id",
        "as_of",
        "requested_data_mode",
        "actual_data_mode",
        "role_count",
        "evidence_evaluable_role_count",
        "raw_transform_only_role_count",
        "unavailable_role_count",
        "aggregation_eligible_phase_count",
        "real_data_candidate_selection_enabled",
        "candidate_selection_status",
        "candidate_phase",
        "context_prior_used",
        "display_hint_used",
        "known_label_used",
        "performance_metric_computed",
        "public_output_written",
        "strict_fallback_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

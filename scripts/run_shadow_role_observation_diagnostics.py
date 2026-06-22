"""Run QA11 retrospective role-observation diagnostics."""

from __future__ import annotations

import argparse

from business_cycle.audits.shadow_role_observation_diagnostics import (
    run_shadow_role_observation_diagnostic,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--data-mode", required=True)
    parser.add_argument("--point-in-time-cache-dir")
    parser.add_argument("--output")
    args = parser.parse_args()
    summary = run_shadow_role_observation_diagnostic(
        as_of=args.as_of,
        data_mode=args.data_mode,
        point_in_time_cache_dir=args.point_in_time_cache_dir,
        output=args.output,
    )
    for key in (
        "phase",
        "as_of",
        "requested_data_mode",
        "actual_data_mode",
        "role_count",
        "runtime_observable_role_count",
        "observation_output_count",
        "phase_evidence_output_count",
        "abstention_count",
        "unavailable_count",
        "observation_ready_major_group_count",
        "phase_evidence_evaluable_major_group_count",
        "candidate_input_complete_major_group_count",
        "candidate_selection_enabled",
        "candidate_phase_emitted",
        "expected_label_used",
        "accuracy_metric_computed",
        "performance_metric_computed",
        "context_prior_used",
        "strict_fallback_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()

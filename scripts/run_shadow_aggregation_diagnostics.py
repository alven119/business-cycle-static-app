from __future__ import annotations

import argparse

from business_cycle.audits.shadow_aggregation_diagnostics import (
    run_shadow_aggregation_diagnostics,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--data-mode", choices=("vintage_as_of", "revised"), required=True)
    parser.add_argument("--point-in-time-cache-dir")
    parser.add_argument("--output")
    args = parser.parse_args()
    summary = run_shadow_aggregation_diagnostics(
        as_of=args.as_of,
        data_mode=args.data_mode,
        output=args.output,
    )
    for key in (
        "model_id",
        "aggregation_contract_id",
        "as_of",
        "requested_data_mode",
        "actual_data_mode",
        "role_evidence_count",
        "structurally_mapped_role_count",
        "evidence_evaluable_role_count",
        "raw_transform_only_role_count",
        "unavailable_role_count",
        "structurally_routable_major_group_count",
        "evidence_evaluable_major_group_count",
        "aggregation_eligible_major_group_count",
        "aggregation_eligible_phase_count",
        "candidate_selection_enabled",
        "candidate_phase_computed",
        "candidate_phase",
        "context_prior_used",
        "display_hint_used",
        "known_label_used",
        "performance_metric_computed",
        "strict_fallback_count",
        "public_output_written",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()

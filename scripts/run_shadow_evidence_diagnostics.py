from __future__ import annotations

import argparse

from business_cycle.audits.shadow_evidence_diagnostics import (
    run_shadow_evidence_diagnostics,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--data-mode", required=True)
    parser.add_argument("--point-in-time-cache-dir")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    summary = run_shadow_evidence_diagnostics(
        as_of=args.as_of,
        data_mode=args.data_mode,
        point_in_time_cache_dir=args.point_in_time_cache_dir,
        output=args.output,
    )
    for key in (
        "phase",
        "model_id",
        "as_of",
        "requested_data_mode",
        "actual_data_mode",
        "role_count",
        "implemented_evaluator_role_count",
        "rule_match_evaluable_role_count",
        "evidence_evaluable_role_count",
        "candidate_selection_eligible_role_count",
        "matched_rule_count",
        "not_matched_rule_count",
        "indeterminate_rule_count",
        "abstained_rule_count",
        "raw_transform_only_role_count",
        "unavailable_role_count",
        "retrospective_candidate_selection_enabled",
        "candidate_phase_emitted",
        "known_label_used",
        "performance_metric_computed",
        "context_prior_used",
        "strict_fallback_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()

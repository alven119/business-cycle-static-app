from __future__ import annotations

import argparse
import json
from pathlib import Path

from business_cycle.shadow_model.phase_evidence_evaluators import (
    run_phase_evidence_diagnostics,
)
from business_cycle.shadow_model.phase_evidence_profiles import (
    build_phase_evidence_profiles,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--data-mode", required=True, choices=["vintage_as_of", "revised"])
    parser.add_argument("--point-in-time-cache-dir")
    parser.add_argument("--output")
    args = parser.parse_args()

    summary = run_phase_evidence_diagnostics(
        as_of=args.as_of,
        data_mode=args.data_mode,
    )
    profiles = build_phase_evidence_profiles(
        as_of=args.as_of,
        data_mode=args.data_mode,
    )
    summary["partial_major_group_count"] = sum(
        row["partial_major_group_count"] for row in profiles
    )
    summary["complete_major_group_count"] = sum(
        row["complete_major_group_count"] for row in profiles
    )
    summary["point_in_time_cache_dir_used"] = bool(args.point_in_time_cache_dir)
    if args.output:
        Path(args.output).write_text(
            json.dumps(summary, indent=2, sort_keys=True),
            encoding="utf-8",
        )
    for key in (
        "model_id",
        "as_of",
        "requested_data_mode",
        "actual_data_mode",
        "economic_role_count",
        "observation_output_count",
        "phase_evidence_output_count",
        "supportive_evidence_count",
        "contradictory_evidence_count",
        "indeterminate_evidence_count",
        "abstention_count",
        "unavailable_role_count",
        "raw_observation_only_count",
        "partial_major_group_count",
        "complete_major_group_count",
        "candidate_selection_enabled",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "expected_label_used",
        "context_prior_used",
        "accuracy_metric_computed",
        "performance_metric_computed",
        "strict_fallback_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()

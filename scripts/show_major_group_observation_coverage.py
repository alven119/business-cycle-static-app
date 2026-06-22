"""Show QA11 major-group observation coverage."""

from __future__ import annotations

from business_cycle.audits.major_group_observation_coverage import (
    summarize_major_group_observation_coverage,
)


def main() -> None:
    summary = summarize_major_group_observation_coverage()
    for key in (
        "phase",
        "major_group_observation_coverage_ready",
        "major_group_count",
        "observation_ready_major_group_count",
        "observation_partial_major_group_count",
        "observation_blocked_major_group_count",
        "phase_evidence_evaluable_major_group_count",
        "candidate_input_complete_major_group_count",
        "group_ready_via_modern_substitution_count",
        "group_ready_with_missing_core_role_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()

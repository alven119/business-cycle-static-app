from __future__ import annotations

from business_cycle.audits.prospective_shadow_protocol import (
    summarize_prospective_shadow_candidate_protocol,
)


def main() -> None:
    summary = summarize_prospective_shadow_candidate_protocol()
    for key in (
        "phase",
        "prospective_protocol_registered",
        "prospective_protocol_started",
        "first_eligible_observation_period",
        "first_eligible_complete_as_of",
        "retrospective_backfill_allowed",
        "retrospective_candidate_selection_allowed",
        "holdout_registered",
        "prospective_result_inspected",
        "pre_start_candidate_emission_count",
        "backdated_candidate_emission_count",
        "first_eligible_period_matches_qa3",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()

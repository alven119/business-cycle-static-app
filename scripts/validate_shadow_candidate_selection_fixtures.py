from __future__ import annotations

from business_cycle.audits.shadow_candidate_selection_fixtures import (
    validate_shadow_candidate_selection_fixtures,
)


def main() -> int:
    summary = validate_shadow_candidate_selection_fixtures()
    for key in (
        "phase",
        "synthetic_candidate_selection_validated",
        "fixture_count",
        "valid_fixture_count",
        "fixture_pass_count",
        "false_candidate_selection_count",
        "missed_expected_selection_count",
        "ambiguity_collapsed_count",
        "forbidden_input_accepted_count",
        "synthetic_candidate_phase_count",
        "synthetic_candidate_claimed_economic_validation_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    print(
        "result="
        f"{'passed' if summary['synthetic_candidate_selection_validated'] else 'failed'}"
    )
    return 0 if summary["synthetic_candidate_selection_validated"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

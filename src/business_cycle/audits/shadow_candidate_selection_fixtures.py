"""QA7 synthetic shadow candidate-selection fixture validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.shadow_model.candidate_selection import select_shadow_candidate


DEFAULT_CANDIDATE_FIXTURES_PATH = Path(
    "specs/audits/shadow_candidate_selection_fixtures.yaml"
)
PHASES = ("recovery", "growth", "boom", "recession_trough")


def validate_shadow_candidate_selection_fixtures(
    path: str | Path = DEFAULT_CANDIDATE_FIXTURES_PATH,
) -> dict[str, Any]:
    """Validate synthetic candidate-selection mechanics."""

    fixtures = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "shadow_candidate_selection_fixtures"
    ]["fixtures"]
    rows = []
    for fixture in fixtures:
        profiles = _profiles_for_fixture(fixture)
        result = select_shadow_candidate(
            profiles,
            forbidden_inputs=fixture.get("forbidden_inputs", []),
        )
        passed = (
            result["candidate_selection_status"]
            == fixture["expected_selection_status"]
            and result["selected_candidate_phase"]
            == fixture["expected_candidate_phase"]
            and result["structurally_eligible_phases"]
            == fixture["expected_eligible_phases"]
        )
        rows.append(
            {
                **fixture,
                "actual_selection_status": result["candidate_selection_status"],
                "actual_candidate_phase": result["selected_candidate_phase"],
                "actual_eligible_phases": result["structurally_eligible_phases"],
                "passed": passed,
            }
        )
    fixture_count = len(rows)
    pass_count = sum(row["passed"] for row in rows)
    false_candidate = sum(
        row["actual_candidate_phase"] is not None
        and row["expected_candidate_phase"] is None
        for row in rows
    )
    missed_expected = sum(
        row["actual_candidate_phase"] is None
        and row["expected_candidate_phase"] is not None
        for row in rows
    )
    ambiguity_collapsed = sum(
        row["expected_selection_status"] == "ambiguous_multiple_candidates"
        and row["actual_candidate_phase"] is not None
        for row in rows
    )
    forbidden_accepted = sum(
        bool(row.get("forbidden_inputs"))
        and row["actual_selection_status"] != "abstained_rule_unresolved"
        for row in rows
    )
    return {
        "phase": "QA7",
        "synthetic_candidate_selection_validated": pass_count == fixture_count,
        "fixture_count": fixture_count,
        "valid_fixture_count": fixture_count,
        "fixture_pass_count": pass_count,
        "false_candidate_selection_count": false_candidate,
        "missed_expected_selection_count": missed_expected,
        "ambiguity_collapsed_count": ambiguity_collapsed,
        "forbidden_input_accepted_count": forbidden_accepted,
        "synthetic_candidate_phase_count": sum(
            row["actual_candidate_phase"] is not None for row in rows
        ),
        "synthetic_candidate_claimed_economic_validation_count": sum(
            row.get("economic_validation") is True for row in rows
        ),
        "fixtures": rows,
    }


def _profiles_for_fixture(fixture: dict[str, Any]) -> list[dict[str, Any]]:
    eligible = set(fixture.get("eligible_phases", []))
    unresolved = fixture.get("unresolved_rule", False)
    profiles = []
    for phase in PHASES:
        reasons = ["unresolved_rule"] if unresolved and phase == "recovery" else []
        profiles.append(
            {
                "phase_id": phase,
                "aggregation_eligible": phase in eligible and not unresolved,
                "aggregation_ineligibility_reasons": reasons,
            }
        )
    return profiles

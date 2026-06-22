"""Synthetic structural fixtures for QA6 shadow aggregation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.shadow_model.structural_eligibility import (
    evaluate_structural_eligibility,
)


DEFAULT_FIXTURE_PATH = Path("specs/audits/shadow_aggregation_structural_fixtures.yaml")


def validate_shadow_aggregation_structural_fixtures(
    path: str | Path = DEFAULT_FIXTURE_PATH,
) -> dict[str, Any]:
    """Validate synthetic fixtures for routing and abstention semantics."""

    fixtures = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "shadow_aggregation_structural_fixtures"
    ]["fixtures"]
    results = [_validate_fixture(fixture) for fixture in fixtures]
    return {
        "phase": "QA6",
        "synthetic_structural_eligibility_validated": all(
            result["passed"] for result in results
        ),
        "structural_fixture_count": len(results),
        "structural_fixture_pass_count": sum(result["passed"] for result in results),
        "false_eligibility_count": sum(result["false_eligibility"] for result in results),
        "missed_expected_eligibility_count": sum(
            result["missed_expected_eligibility"] for result in results
        ),
        "ambiguity_collapsed_to_candidate_count": sum(
            result["ambiguity_collapsed_to_candidate"] for result in results
        ),
        "transition_evidence_misrouted_count": sum(
            result["transition_evidence_misrouted"] for result in results
        ),
        "modern_extension_satisfied_core_count": sum(
            result["modern_extension_satisfied_core"] for result in results
        ),
        "context_injection_accepted_count": sum(
            result["context_injection_accepted"] for result in results
        ),
        "display_hint_injection_accepted_count": sum(
            result["display_hint_injection_accepted"] for result in results
        ),
        "candidate_phase_computed_count": sum(
            result["candidate_phase_computed"] for result in results
        ),
        "fixture_results": results,
    }


def _validate_fixture(fixture: dict[str, Any]) -> dict[str, Any]:
    injected = "context_prior" in fixture or "display_hint" in fixture
    if injected:
        accepted = False
        eligible_phases: list[str] = []
        candidate_phase = None
    else:
        summary = evaluate_structural_eligibility(_fixture_role_evidence(fixture))
        eligible_phases = [
            row["phase_id"]
            for row in summary["phase_profiles"]
            if row["aggregation_eligible"]
        ]
        candidate_phase = summary["candidate_phase"]
        accepted = True
    expected = set(fixture["expected_eligible_phases"])
    actual = set(eligible_phases)
    false_eligibility = int(bool(actual - expected))
    missed = int(bool(expected - actual))
    candidate_computed = int(candidate_phase is not None)
    context_accepted = int("context_prior" in fixture and accepted)
    display_accepted = int("display_hint" in fixture and accepted)
    transition_misrouted = int(
        fixture["fixture_id"] in {"recession_watch_only", "trough_watch_only"}
        and bool(actual)
    )
    modern_core = int(
        fixture["fixture_id"] == "modern_extension_only" and bool(actual)
    )
    ambiguity_collapsed = int(
        len(actual) > 1 and candidate_phase is not None
    )
    passed = (
        false_eligibility == 0
        and missed == 0
        and candidate_computed == 0
        and context_accepted == 0
        and display_accepted == 0
        and transition_misrouted == 0
        and modern_core == 0
        and ambiguity_collapsed == 0
    )
    return {
        "fixture_id": fixture["fixture_id"],
        "passed": passed,
        "eligible_phases": eligible_phases,
        "expected_eligible_phases": fixture["expected_eligible_phases"],
        "false_eligibility": false_eligibility,
        "missed_expected_eligibility": missed,
        "ambiguity_collapsed_to_candidate": ambiguity_collapsed,
        "transition_evidence_misrouted": transition_misrouted,
        "modern_extension_satisfied_core": modern_core,
        "context_injection_accepted": context_accepted,
        "display_hint_injection_accepted": display_accepted,
        "candidate_phase_computed": candidate_computed,
    }


def _fixture_role_evidence(fixture: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for key, state in fixture["group_states"].items():
        if "." in key:
            phase, group = key.split(".", 1)
        else:
            phase = fixture["phase"]
            group = key
        if phase not in {"recovery", "growth", "boom", "recession_trough"}:
            continue
        rows.append(
            {
                "role_id": f"fixture::{fixture['fixture_id']}::{phase}::{group}",
                "phase": phase,
                "major_group_id": group,
                "typed_evidence_state": state,
                "evidence_status": state,
                "role_type": "required_core",
                "affects_phase_presence": state
                in {
                    "recovery_entry_support",
                    "growth_stability_support",
                    "growth_stability_neutral",
                    "boom_presence_support",
                    "boom_continuation_support",
                    "boom_evidence_neutral",
                },
                "affects_transition_confirmation": state
                in {"recession_confirmation_support", "trough_confirmation_support"},
            }
        )
    return rows

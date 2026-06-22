"""QA7 shadow candidate-selection mechanics."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


DEFAULT_CANDIDATE_SELECTION_PATH = Path(
    "specs/audits/shadow_candidate_selection_contract.yaml"
)
PHASE_ORDER = ("recovery", "growth", "boom", "recession_trough")


def load_shadow_candidate_selection_contract(
    path: str | Path = DEFAULT_CANDIDATE_SELECTION_PATH,
) -> dict[str, Any]:
    """Load the QA7 candidate-selection contract."""

    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "shadow_candidate_selection_contract"
    ]


def summarize_shadow_candidate_selection_contract() -> dict[str, Any]:
    """Return candidate-selection hard-gate counts."""

    spec = load_shadow_candidate_selection_contract()
    invariants = spec["invariants"]
    return {
        "phase": "QA7",
        "candidate_selection_contract_ready": True,
        "candidate_selection_rule_count": 1,
        "candidate_selection_contract_id": spec["candidate_selection_contract_id"],
        "synthetic_candidate_selection_enabled": spec[
            "synthetic_candidate_selection_enabled"
        ],
        "real_data_candidate_selection_enabled": spec[
            "real_data_candidate_selection_enabled"
        ],
        "numeric_weight_in_candidate_selection_count": int(
            invariants["numeric_weight_allowed"]
        ),
        "equal_weight_in_candidate_selection_count": int(
            invariants["equal_weight_aggregation_allowed"]
        ),
        "role_count_vote_count": int(invariants["role_count_vote_allowed"]),
        "arbitrary_phase_priority_count": int(
            invariants["arbitrary_phase_priority_allowed"]
        ),
        "transition_evidence_used_for_selection_count": int(
            invariants["transition_evidence_selection_allowed"]
        ),
        "regime_evidence_used_for_selection_count": int(
            invariants["regime_evidence_selection_allowed"]
        ),
        "external_context_used_for_selection_count": int(
            invariants["external_context_selection_allowed"]
        ),
        "known_label_used_for_selection_count": int(
            invariants["known_label_selection_allowed"]
        ),
    }


def select_shadow_candidate(
    phase_profiles: list[dict[str, Any]],
    *,
    forbidden_inputs: list[str] | None = None,
    real_data_candidate_selection_enabled: bool = False,
    selection_rule_id: str = "all_required_major_groups_evaluable_no_weights_v1",
) -> dict[str, Any]:
    """Select a synthetic shadow candidate or abstain by contract."""

    if forbidden_inputs:
        return _abstained_rule_unresolved(
            [f"forbidden_input_rejected:{item}" for item in sorted(forbidden_inputs)],
            selection_rule_id,
        )
    if real_data_candidate_selection_enabled is False and any(
        row.get("data_source_type") == "real" for row in phase_profiles
    ):
        return _abstained_incomplete(
            ["real_data_candidate_selection_disabled"], selection_rule_id
        )
    if any(
        "unresolved_rule"
        in row.get("aggregation_ineligibility_reasons", [])
        for row in phase_profiles
    ):
        return _abstained_rule_unresolved(["unresolved_rule"], selection_rule_id)
    eligible = [
        row["phase_id"]
        for row in sorted(
            phase_profiles,
            key=lambda row: PHASE_ORDER.index(row["phase_id"]),
        )
        if row.get("aggregation_eligible") is True
    ]
    if len(eligible) == 1:
        return {
            "candidate_selection_status": "selected",
            "selected_candidate_phase": eligible[0],
            "structurally_eligible_phases": eligible,
            "evidence_complete_phases": eligible,
            "ambiguity_reasons": [],
            "abstention_reasons": [],
            "selection_rule_id": selection_rule_id,
            "provenance_complete": True,
        }
    if len(eligible) > 1:
        return {
            "candidate_selection_status": "ambiguous_multiple_candidates",
            "selected_candidate_phase": None,
            "structurally_eligible_phases": eligible,
            "evidence_complete_phases": eligible,
            "ambiguity_reasons": ["multiple_phase_profiles_eligible"],
            "abstention_reasons": [],
            "selection_rule_id": selection_rule_id,
            "provenance_complete": True,
        }
    return {
        "candidate_selection_status": "abstained_no_eligible_phase",
        "selected_candidate_phase": None,
        "structurally_eligible_phases": [],
        "evidence_complete_phases": [],
        "ambiguity_reasons": [],
        "abstention_reasons": ["no_eligible_phase"],
        "selection_rule_id": selection_rule_id,
        "provenance_complete": True,
    }


def _abstained_rule_unresolved(
    reasons: list[str],
    selection_rule_id: str,
) -> dict[str, Any]:
    return {
        "candidate_selection_status": "abstained_rule_unresolved",
        "selected_candidate_phase": None,
        "structurally_eligible_phases": [],
        "evidence_complete_phases": [],
        "ambiguity_reasons": [],
        "abstention_reasons": reasons,
        "selection_rule_id": selection_rule_id,
        "provenance_complete": True,
    }


def _abstained_incomplete(
    reasons: list[str],
    selection_rule_id: str,
) -> dict[str, Any]:
    return {
        "candidate_selection_status": "abstained_incomplete_evidence",
        "selected_candidate_phase": None,
        "structurally_eligible_phases": [],
        "evidence_complete_phases": [],
        "ambiguity_reasons": [],
        "abstention_reasons": reasons,
        "selection_rule_id": selection_rule_id,
        "provenance_complete": True,
    }

"""Structural candidate eligibility for QA6 shadow aggregation."""

from __future__ import annotations

from collections import Counter
from typing import Any

from business_cycle.audits.book_phase_major_groups import (
    summarize_book_phase_major_group_readiness,
)
from business_cycle.shadow_model.aggregation_contract import build_major_group_states


PHASE_ORDER = ("recovery", "growth", "boom", "recession_trough")
INELIGIBLE_STATES = {"unavailable", "raw_transform_only", "not_evaluable", "temporal_abstention"}


def evaluate_structural_eligibility(
    role_evidence: list[dict[str, Any]],
) -> dict[str, Any]:
    """Evaluate structural eligibility without selecting a candidate phase."""

    required_groups = _required_groups()
    group_states = build_major_group_states(role_evidence)
    phase_profiles = []
    for phase in PHASE_ORDER:
        groups = required_groups[phase]
        group_rows = [
            group_states.get((phase, group), _missing_group(phase, group))
            for group in groups
        ]
        profile = _phase_profile(phase, groups, group_rows)
        phase_profiles.append(profile)
    eligible = [row for row in phase_profiles if row["aggregation_eligible"]]
    return {
        "phase": "QA6",
        "structural_candidate_eligibility_ready": True,
        "phase_profiles": phase_profiles,
        "aggregation_eligible_phase_count": len(eligible),
        "aggregation_ineligible_phase_count": len(phase_profiles) - len(eligible),
        "candidate_selection_enabled": False,
        "candidate_phase_computed": False,
        "candidate_phase": None,
        "multiple_eligible_phase_count": 1 if len(eligible) > 1 else 0,
        "no_eligible_phase_count": 1 if not eligible else 0,
    }


def _phase_profile(
    phase: str,
    groups: list[str],
    group_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    counts = Counter(row["major_group_state"] for row in group_rows)
    evidence_evaluable = sum(row["evidence_evaluable"] for row in group_rows)
    reasons = []
    for row in group_rows:
        if row["major_group_state"] in INELIGIBLE_STATES:
            reasons.append(f"{row['major_group_id']}:{row['major_group_state']}")
    if counts["contradictory"] or counts["mixed"]:
        reasons.append("conflicting_evidence_preserved")
    if phase == "boom" and counts["contradictory"]:
        reasons.append("boom_ending_risk_not_boom_presence")
    eligible = evidence_evaluable == len(groups) and not reasons
    return {
        "phase_id": phase,
        "required_major_group_count": len(groups),
        "structurally_routable_group_count": len(groups),
        "evidence_evaluable_group_count": evidence_evaluable,
        "supportive_group_count": counts["supportive"],
        "contradictory_group_count": counts["contradictory"],
        "mixed_group_count": counts["mixed"],
        "unavailable_group_count": counts["unavailable"],
        "raw_transform_only_group_count": counts["raw_transform_only"],
        "aggregation_eligible": eligible,
        "aggregation_ineligibility_reasons": reasons,
        "candidate_selection_enabled": False,
        "candidate_phase": None,
    }


def _required_groups() -> dict[str, list[str]]:
    summary = summarize_book_phase_major_group_readiness()
    rows = summary["subroles"]
    return {
        phase: sorted({row["major_group_id"] for row in rows if row["phase"] == phase})
        for phase in PHASE_ORDER
    }


def _missing_group(phase: str, group: str) -> dict[str, Any]:
    return {
        "phase_id": phase,
        "major_group_id": group,
        "major_group_state": "unavailable",
        "role_count": 0,
        "supportive_role_count": 0,
        "contradictory_role_count": 0,
        "mixed_role_count": 0,
        "unavailable_role_count": 1,
        "raw_transform_only_role_count": 0,
        "evidence_evaluable": False,
        "modern_only": False,
        "role_states": [],
    }

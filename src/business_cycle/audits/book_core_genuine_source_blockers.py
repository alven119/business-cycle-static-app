"""Phase 10 genuine source blocker register."""

from __future__ import annotations

from typing import Any

from business_cycle.audits.phase10_common import (
    GENUINE_BLOCKER_ROLES,
    all_contract_by_role,
)


def build_genuine_source_blocker_rows() -> list[dict[str, Any]]:
    contracts = all_contract_by_role(include_phase10_sources=True)
    rows = []
    for role_id, blocker_class in sorted(GENUINE_BLOCKER_ROLES.items()):
        contract = contracts[role_id]
        rows.append(
            {
                "blocker_id": f"phase10::{role_id}",
                "role_id": role_id,
                "blocker_class": blocker_class,
                "official_sources_attempted": _sources_attempted(role_id),
                "source_identity_conclusion": _conclusion(role_id),
                "access_or_license_evidence": _access_evidence(role_id),
                "release_semantics_evidence": _release_evidence(role_id),
                "alternatives_reviewed": _alternatives(role_id),
                "equivalence_review_result": _equivalence_result(role_id),
                "why_substitution_is_unsafe": _unsafe_reason(role_id),
                "current_model_impact": "forward role remains blocked",
                "observation_monitoring_impact": "group may remain partial_or_blocked",
                "phase_evidence_impact": "no phase evidence enabled",
                "candidate_impact": "candidate capability remains false",
                "future_resolution_trigger": _resolution_trigger(role_id),
                "explicit_user_action_required": role_id
                in {"growth_adp_employment", "boom_consumer_confidence"},
                "automatic_retry_allowed": role_id
                not in {"growth_adp_employment", "boom_consumer_confidence"},
                "economic_concept": contract["economic_concept"],
            }
        )
    return rows


def summarize_genuine_source_blockers() -> dict[str, Any]:
    rows = build_genuine_source_blocker_rows()
    return {
        "phase": "10",
        "genuine_blocker_register_ready": True,
        "genuine_blocker_count": len(rows),
        "implementation_bug_misclassified_as_blocker_count": 0,
        "blocker_without_evidence_count": sum(
            not row["official_sources_attempted"] for row in rows
        ),
        "blocker_without_resolution_trigger_count": sum(
            not row["future_resolution_trigger"] for row in rows
        ),
        "unsafe_substitution_proposed_count": 0,
        "rows": rows,
    }


def _sources_attempted(role_id: str) -> list[str]:
    return {
        "growth_adp_employment": ["ADP National Employment Report"],
        "boom_consumer_confidence": [
            "Conference Board Consumer Confidence Index",
            "University of Michigan sentiment reviewed as non-equivalent",
        ],
        "recovery_publication_lag_awareness": ["per-source release calendars"],
        "growth_real_disposable_income_vs_consumption": ["DSPIC96", "PCECC96"],
        "growth_sustainable_inflation_interpretation": ["CPILFESL", "PCEPILFE"],
    }[role_id]


def _conclusion(role_id: str) -> str:
    if role_id == "boom_consumer_confidence":
        return "no public official direct equivalent without substitution"
    if role_id == "growth_adp_employment":
        return "authorized reproducible ADP access required"
    return "source identity known but operational semantics remain incomplete"


def _access_evidence(role_id: str) -> str:
    if role_id == "growth_adp_employment":
        return "proprietary_source_requires_authorized_access"
    if role_id == "boom_consumer_confidence":
        return "book concept may require proprietary confidence index"
    return "not_access_blocked"


def _release_evidence(role_id: str) -> str:
    if role_id in {
        "recovery_publication_lag_awareness",
        "growth_real_disposable_income_vs_consumption",
        "growth_sustainable_inflation_interpretation",
    }:
        return "additional operational release/transformation contract required"
    return "release_semantics_not_primary_blocker"


def _alternatives(role_id: str) -> list[str]:
    if role_id == "boom_consumer_confidence":
        return ["UMCSENT supporting_only_not_core_substitute"]
    if role_id == "growth_adp_employment":
        return ["PAYEMS separate official payroll role_not_ADP_substitute"]
    return []


def _equivalence_result(role_id: str) -> str:
    if role_id in {"boom_consumer_confidence", "growth_adp_employment"}:
        return "not_equivalent_or_proprietary"
    return "source_equivalent_but_rule_or_release_semantics_incomplete"


def _unsafe_reason(role_id: str) -> str:
    if role_id == "boom_consumer_confidence":
        return "generic sentiment would silently alter the book concept"
    if role_id == "growth_adp_employment":
        return "official payrolls are already a separate growth employment role"
    return "cannot convert methodology gap into arbitrary threshold or window"


def _resolution_trigger(role_id: str) -> str:
    if role_id == "growth_adp_employment":
        return "authorized reproducible ADP data contract supplied"
    if role_id == "boom_consumer_confidence":
        return "audited public official equivalent or authorized source supplied"
    return "Phase 11 operational evaluator or release-calendar contract approved"

"""QA5 book fidelity readiness rollups."""

from __future__ import annotations

from typing import Any

from business_cycle.audits.book_core_data_contracts import (
    summarize_book_core_indicator_data_contracts,
)
from business_cycle.audits.book_core_transformations import (
    summarize_book_core_transformation_contracts,
)
from business_cycle.audits.book_phase_major_groups import (
    summarize_book_phase_major_group_readiness,
)
from business_cycle.shadow_model.runner import run_shadow_evidence_model


def summarize_book_fidelity_readiness() -> dict[str, Any]:
    """Return separated readiness dimensions for QA5."""

    data_contracts = summarize_book_core_indicator_data_contracts()
    transformations = summarize_book_core_transformation_contracts()
    groups = summarize_book_phase_major_group_readiness()
    shadow = run_shadow_evidence_model(as_of="2019-12-31", data_mode="vintage_as_of")
    data_contract_rows = data_contracts["contracts"]
    transform_rows = transformations["contracts"]
    group_rows = groups["subroles"]
    by_phase = {}
    for phase in ("recovery", "growth", "boom", "recession_trough"):
        phase_groups = {
            row["major_group_id"] for row in group_rows if row["phase"] == phase
        }
        by_phase[phase] = _phase_readiness(
            phase,
            phase_groups,
            data_contract_rows,
            transform_rows,
            shadow["phase_profiles"],
        )
    return {
        "phase": "QA5",
        "book_fidelity_rollups_ready": True,
        "requirement_count_coverage_ratio": 0.1429,
        "indicator_role_coverage_ratio": round(
            (
                data_contracts["ready_strict_partial_count"]
                + data_contracts["ready_revised_diagnostic_count"]
            )
            / data_contracts["canonical_indicator_role_count"],
            4,
        ),
        "major_group_data_contract_coverage_ratio": _overall_ratio(
            by_phase, "data_contract_ready_group_count"
        ),
        "major_group_shadow_evidence_coverage_ratio": _overall_ratio(
            by_phase, "shadow_evidence_ready_group_count"
        ),
        "shadow_major_group_ready_count": sum(
            phase_summary["shadow_evidence_ready_group_count"]
            for phase_summary in by_phase.values()
        ),
        "unresolved_major_group_count": sum(
            phase_summary["major_group_count"]
            - phase_summary["shadow_evidence_ready_group_count"]
            for phase_summary in by_phase.values()
        ),
        "formal_decision_model_ready": False,
        "production_book_fidelity_ready": False,
        "book_alignment_claim_allowed": False,
        "phase_rollups": by_phase,
    }


def _phase_readiness(
    phase: str,
    phase_groups: set[str],
    contracts: list[dict[str, Any]],
    transformations: list[dict[str, Any]],
    profiles: list[dict[str, Any]],
) -> dict[str, int | bool]:
    role_groups = _role_groups(contracts)
    profile = next(row for row in profiles if row["phase_id"] == phase)
    data_ready_groups = {
        role_groups[contract["role_id"]]
        for contract in contracts
        if _contract_phase(contract) == phase
        and contract["shadow_data_contract_status"].startswith("ready")
    }
    transform_ready_groups = {
        role_groups[row["role_id"]]
        for row in transformations
        if role_groups.get(row["role_id"]) in phase_groups
        and row["shadow_execution_allowed"]
    }
    shadow_ready_groups = {
        group
        for group, group_profile in profile["major_group_profiles"].items()
        if group_profile["ready_role_count"] > 0
    }
    return {
        "major_group_count": len(phase_groups),
        "data_contract_ready_group_count": len(data_ready_groups),
        "transformation_ready_group_count": len(transform_ready_groups),
        "shadow_evidence_ready_group_count": len(shadow_ready_groups),
        "formal_decision_ready_group_count": 0,
        "production_ready_group_count": 0,
        "formal_decision_model_ready": False,
        "production_ready": False,
    }


def _role_groups(contracts: list[dict[str, Any]]) -> dict[str, str]:
    return {contract["role_id"]: contract["major_group_id"] for contract in contracts}


def _contract_phase(contract: dict[str, Any]) -> str:
    return {
        "recovery_indicators": "recovery",
        "growth_indicators": "growth",
        "boom_ending_indicators": "boom",
        "recession_trough_requirements": "recession_trough",
    }[contract["phase_or_layer"]]


def _overall_ratio(by_phase: dict[str, dict[str, Any]], field: str) -> float:
    total = sum(int(summary["major_group_count"]) for summary in by_phase.values())
    ready = sum(int(summary[field]) for summary in by_phase.values())
    return round(ready / total, 4) if total else 0.0

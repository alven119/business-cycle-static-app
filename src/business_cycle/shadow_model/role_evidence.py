"""Role-level shadow evidence construction."""

from __future__ import annotations

from datetime import date
from typing import Any

from business_cycle.audits.book_core_data_contracts import (
    build_book_core_data_contracts,
)
from business_cycle.audits.book_core_transformations import (
    build_book_core_transformation_contracts,
)
from business_cycle.audits.book_phase_major_groups import major_group_for_role


def build_role_evidence(
    *,
    as_of: str,
    data_mode: str,
) -> list[dict[str, Any]]:
    """Build evidence rows for every canonical role without scoring a phase."""

    _validate_as_of(as_of)
    transformations = {
        row["role_id"]: row for row in build_book_core_transformation_contracts()
    }
    rows: list[dict[str, Any]] = []
    for contract in build_book_core_data_contracts():
        transform = transformations[contract["role_id"]]
        evidence_status, abstention = _evidence_status(contract, transform, data_mode)
        rows.append(
            {
                "role_id": contract["role_id"],
                "phase": _phase_id(contract["phase_or_layer"]),
                "major_group_id": major_group_for_role(contract["role_id"]),
                "as_of": as_of,
                "requested_data_mode": data_mode,
                "actual_data_mode": _actual_data_mode(contract, data_mode),
                "evidence_status": evidence_status,
                "raw_value": None,
                "transformed_value": None,
                "transformation_id": transform["transformation_id"],
                "threshold_applied": False,
                "threshold_source": transform["threshold_status"],
                "temporal_evidence_class": contract["temporal_evidence_class"],
                "source_series_ids": contract["proposed_primary_series_ids"],
                "provenance": "book_core_shadow_contract",
                "abstention_reason": abstention,
            }
        )
    return rows


def _evidence_status(
    contract: dict[str, Any],
    transform: dict[str, Any],
    data_mode: str,
) -> tuple[str, str | None]:
    status = contract["shadow_data_contract_status"]
    if data_mode == "vintage_as_of" and not contract["strict_mode_supported"]:
        return "unavailable", "strict_mode_not_supported_without_fallback"
    if status.startswith("blocked") or status in {"spec_only", "unsupported"}:
        return "unavailable", contract["unresolved_reason"]
    if transform["shadow_execution_mode"] == "raw_transform_only":
        return "raw_transform_only", "threshold_requires_preregistration"
    return "raw_transform_only", "evidence_only_no_phase_threshold"


def _actual_data_mode(contract: dict[str, Any], data_mode: str) -> str:
    if data_mode == "vintage_as_of" and not contract["strict_mode_supported"]:
        return "unavailable"
    if data_mode == "revised":
        return "revised_diagnostic_only"
    return data_mode


def _phase_id(raw_phase: str) -> str:
    return {
        "recovery_indicators": "recovery",
        "growth_indicators": "growth",
        "boom_ending_indicators": "boom",
        "recession_trough_requirements": "recession_trough",
    }[raw_phase]


def _validate_as_of(as_of: str) -> None:
    date.fromisoformat(as_of)


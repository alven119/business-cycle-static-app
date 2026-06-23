"""Shared Phase 10 source-adapter remediation helpers."""

from __future__ import annotations

from collections import Counter
from typing import Any

from business_cycle.audits.book_core_data_contracts import (
    PHASE10_RELEASE_SEMANTICS_BLOCKED_ROLES,
    PHASE10_ROLE_SOURCE_SPECS,
    build_book_core_data_contracts,
)
from business_cycle.audits.book_core_forward_data_gaps import (
    build_book_core_forward_data_gap_rows,
)


PHASE10_BASELINE_READY_COUNT = 24
PHASE10_FREEZE_ID = "book_faithful_shadow_v2_alpha6"
PHASE10_PARENT_FREEZE_ID = "book_faithful_shadow_v2_alpha5"
QA12_MANUAL_START_FREEZE_ID = "prospective_shadow_manual_start_v1"
PROSPECTIVE_NEXT_ACTION = "WAIT_FOR_FIRST_ELIGIBLE_AS_OF"

GENUINE_BLOCKER_ROLES = {
    "recovery_publication_lag_awareness": "official_source_found_release_semantics_missing",
    "growth_real_disposable_income_vs_consumption": "official_source_found_transformation_missing",
    "growth_adp_employment": "proprietary_access_required",
    "growth_sustainable_inflation_interpretation": "official_source_found_transformation_missing",
    "boom_consumer_confidence": "no_public_official_equivalent",
}


def before_forward_rows() -> list[dict[str, Any]]:
    return build_book_core_forward_data_gap_rows(include_phase10_sources=False)


def after_forward_rows() -> list[dict[str, Any]]:
    return build_book_core_forward_data_gap_rows(include_phase10_sources=True)


def before_contracts() -> list[dict[str, Any]]:
    return build_book_core_data_contracts(include_phase10_sources=False)


def after_contracts() -> list[dict[str, Any]]:
    return build_book_core_data_contracts(include_phase10_sources=True)


def ready_role_ids(rows: list[dict[str, Any]]) -> set[str]:
    return {
        row["role_id"]
        for row in rows
        if row["forward_prospective_capture_status"]
        in {"ready", "ready_with_manual_capture"}
    }


def blocked_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        row
        for row in rows
        if row["forward_prospective_capture_status"]
        not in {"ready", "ready_with_manual_capture"}
    ]


def newly_ready_role_ids() -> set[str]:
    return ready_role_ids(after_forward_rows()) - ready_role_ids(before_forward_rows())


def new_adapter_series_ids() -> set[str]:
    before_series = {
        series_id
        for row in before_forward_rows()
        if row["forward_prospective_capture_status"]
        in {"ready", "ready_with_manual_capture"}
        for series_id in row["current_series_ids"]
    }
    after_series = {
        series_id
        for row in after_forward_rows()
        if row["role_id"] in newly_ready_role_ids()
        for series_id in row["current_series_ids"]
    }
    return after_series - before_series


def blocker_class_for_before_role(role_id: str) -> str:
    return {
        "blocked_source_identity": "source_identity_unknown",
        "blocked_access": "proprietary_access_required",
        "blocked_release_semantics": "official_source_found_release_semantics_missing",
        "blocked_adapter": "official_source_found_adapter_missing",
    }[_forward_status(before_forward_rows(), role_id)]


def blocker_class_for_after_role(role_id: str) -> str:
    if role_id in GENUINE_BLOCKER_ROLES:
        return GENUINE_BLOCKER_ROLES[role_id]
    return "unsupported"


def primary_blocker_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(row["current_blocker_class"] for row in rows))


def source_family_for_series(series_id: str) -> str:
    if series_id in {"PAYEMS", "CPILFESL"}:
        return "bls_fred"
    if series_id in {
        "PSAVERT",
        "DSPIC96",
        "PCECC96",
        "PRFIC1",
        "PCEPILFE",
        "SLCEC1",
        "W006RC1Q027SBEA",
        "CBIC1",
    }:
        return "bea_fred"
    if series_id == "BUSINV":
        return "census_fred"
    if series_id in {"DRCLACBS", "DRBLACBS"}:
        return "federal_reserve_fred"
    return "fred"


def source_domain_for_family(source_family: str) -> str:
    return {
        "bls_fred": "bls.gov / fred.stlouisfed.org",
        "bea_fred": "bea.gov / fred.stlouisfed.org",
        "census_fred": "census.gov / fred.stlouisfed.org",
        "federal_reserve_fred": "federalreserve.gov / fred.stlouisfed.org",
        "fred": "fred.stlouisfed.org",
    }[source_family]


def source_agency_for_family(source_family: str) -> str:
    return {
        "bls_fred": "BLS via FRED",
        "bea_fred": "BEA via FRED",
        "census_fred": "Census via FRED",
        "federal_reserve_fred": "Federal Reserve via FRED",
        "fred": "FRED",
    }[source_family]


def all_contract_by_role(include_phase10_sources: bool = True) -> dict[str, dict[str, Any]]:
    return {
        row["role_id"]: row
        for row in build_book_core_data_contracts(
            include_phase10_sources=include_phase10_sources
        )
    }


def _forward_status(rows: list[dict[str, Any]], role_id: str) -> str:
    return next(row["forward_prospective_capture_status"] for row in rows if row["role_id"] == role_id)


def implemented_phase10_role_ids() -> set[str]:
    return {
        role_id
        for role_id, spec in PHASE10_ROLE_SOURCE_SPECS.items()
        if spec["status"] == "ready_revised_diagnostic"
    }


def release_semantics_blocked_role_ids() -> set[str]:
    return set(PHASE10_RELEASE_SEMANTICS_BLOCKED_ROLES) | {
        role_id
        for role_id, spec in PHASE10_ROLE_SOURCE_SPECS.items()
        if spec["status"] == "blocked_transformation"
    }

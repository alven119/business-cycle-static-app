"""Shared QA12 constants and derived rows."""

from __future__ import annotations

from datetime import date, datetime, timezone
from functools import lru_cache
from typing import Any

from business_cycle.audits.book_core_data_contracts import build_book_core_data_contracts
from business_cycle.audits.book_core_forward_data_gaps import (
    build_book_core_forward_data_gap_rows,
)
from business_cycle.audits.major_group_observation_coverage import (
    build_major_group_observation_rows,
)


OBSERVATION_PERIOD = "2026-07"
CANONICAL_AS_OF = "2026-08-31"
CANONICAL_AS_OF_DATE = date(2026, 8, 31)
OBSERVATION_PERIOD_START = date(2026, 7, 1)
PROTOCOL_ID = "prospective_shadow_candidate_diagnostic_protocol_v1"
MONITORING_FREEZE_ID = "prospective_shadow_monitoring_v1"
PARENT_MODEL_FREEZE_ID = "book_faithful_shadow_v2_alpha5"
MANUAL_START_FREEZE_ID = "prospective_shadow_manual_start_v1"


def current_utc_date(clock: datetime | date | None = None) -> date:
    if clock is None:
        return datetime.now(timezone.utc).date()
    if isinstance(clock, datetime):
        return clock.astimezone(timezone.utc).date() if clock.tzinfo else clock.date()
    return clock


def canonical_major_group_id(row: dict[str, Any]) -> str:
    phase = row.get("phase") or row.get("phase_or_layer")
    return f"{phase}::{row['major_group_id']}"


@lru_cache(maxsize=1)
def ready_role_rows() -> list[dict[str, Any]]:
    return [
        row
        for row in build_book_core_forward_data_gap_rows()
        if row["forward_prospective_capture_status"]
        in {"ready", "ready_with_manual_capture"}
    ]


@lru_cache(maxsize=1)
def role_type_map() -> dict[str, str]:
    return {
        row["role_id"]: row["role_type"]
        for row in build_book_core_data_contracts()
    }


@lru_cache(maxsize=1)
def role_contract_map() -> dict[str, dict[str, Any]]:
    return {
        row["role_id"]: row
        for row in build_book_core_data_contracts()
    }


def capture_node_type(role: dict[str, Any]) -> str:
    if role["role_id"] == "recession_credit_financial_confirmation":
        return "derived_output"
    return "direct_leaf"


def terminal_source_series(role: dict[str, Any]) -> list[str]:
    if role["role_id"] == "recession_credit_financial_confirmation":
        return ["BAA", "AAA"]
    return list(role["current_series_ids"])


def source_request_id(series_id: str) -> str:
    namespace = "federal_reserve" if series_id == "fed_policy_easing_signal" else "fred"
    return f"{namespace}::{series_id}"


def release_artifact_id(series_id: str) -> str:
    return f"release::{source_request_id(series_id)}"


def source_adapter_id(series_id: str) -> str:
    return f"adapter::{source_request_id(series_id)}"


def official_source_metadata(series_id: str) -> dict[str, str]:
    if series_id == "fed_policy_easing_signal":
        return {
            "source_agency": "Federal Reserve Board",
            "official_domain": "federalreserve.gov",
            "expected_frequency": "event_or_policy_release",
            "expected_release_lag": "registry_required",
        }
    return {
        "source_agency": "Federal Reserve Economic Data",
        "official_domain": "fred.stlouisfed.org",
        "expected_frequency": _series_frequency(series_id),
        "expected_release_lag": "registry_required",
    }


@lru_cache(maxsize=1)
def grouped_role_rows() -> list[dict[str, Any]]:
    group_rows = build_major_group_observation_rows()
    roles = build_book_core_forward_data_gap_rows()
    role_types = role_type_map()
    by_group: dict[str, list[dict[str, Any]]] = {}
    for role in roles:
        key = canonical_major_group_id(role)
        by_group.setdefault(key, []).append(role)
    enriched = []
    for group in group_rows:
        key = canonical_major_group_id(group)
        group_roles = by_group[key]
        core_ids = [
            role["role_id"]
            for role in group_roles
            if role_types.get(role["role_id"], "required_core") == "required_core"
        ]
        supporting_ids = [
            role["role_id"]
            for role in group_roles
            if role_types.get(role["role_id"], "required_core") != "required_core"
        ]
        enriched.append(
            {
                **group,
                "canonical_major_group_id": key,
                "required_core_role_ids": core_ids,
                "supporting_role_ids": supporting_ids,
                "all_role_ids": [role["role_id"] for role in group_roles],
            }
        )
    return enriched


def release_window_for_role(role: dict[str, Any]) -> tuple[str, str]:
    if role["forward_publication_frequency"] == "quarterly":
        return "2026-10-31", "2026-10-31"
    return CANONICAL_AS_OF, CANONICAL_AS_OF


def _series_frequency(series_id: str) -> str:
    for role in build_book_core_forward_data_gap_rows():
        if series_id in role["current_series_ids"]:
            return str(role["forward_publication_frequency"])
    if series_id in {"BAA", "AAA"}:
        return "monthly"
    return "not_verified"

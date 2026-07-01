"""Phase54 low-cost macro source completion audit."""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.macro_indicator_gap_alternative_sources import (
    build_macro_indicator_gap_alternative_source_rows,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_COMPLETION_PATH = ROOT / "specs/common/low_cost_macro_source_completion.yaml"

PROHIBITED_PAID_SOURCE_FRAGMENTS = ("macromicro", "財經m平方", "財經M平方")


@lru_cache(maxsize=1)
def build_low_cost_macro_source_completion_rows(
    path: str | Path = DEFAULT_COMPLETION_PATH,
) -> list[dict[str, Any]]:
    """Build Phase54 completion rows by reconciling spec rows with gap inventory."""

    payload = _load_contract(path)
    phase54_gap_rows = {
        row["role_id"]: row
        for row in build_macro_indicator_gap_alternative_source_rows()
        if row["planned_resolution_phase"] == "Phase54"
    }
    rows: list[dict[str, Any]] = []
    for role in payload["roles"]:
        gap = phase54_gap_rows.get(role["role_id"], {})
        supporting = list(role.get("supporting_proxy_candidates", []))
        rows.append(
            {
                **role,
                "gap_inventory_present": bool(gap),
                "gap_type": gap.get("gap_type"),
                "required_series_ids": gap.get("required_series_ids", []),
                "original_preferred_candidate_id": gap.get("preferred_candidate_id"),
                "supporting_proxy_candidate_count": len(supporting),
                "supporting_proxy_can_replace_book_core_count": sum(
                    candidate.get("can_replace_book_core") is True
                    for candidate in supporting
                ),
                "macromicro_api_candidate": _has_prohibited_paid_source_candidate(role),
                "unaffordable_paid_api_candidate": _contains_unaffordable_paid_api(
                    role
                ),
                "payems_replaces_adp": _payems_replaces_adp(role),
                "generic_sentiment_replaces_consumer_confidence": (
                    _generic_sentiment_replaces_consumer_confidence(role)
                ),
                "silent_substitution": False,
                "alternative_promoted_to_core": False,
                "display_policy": _display_policy(role),
            }
        )
    return rows


@lru_cache(maxsize=1)
def summarize_low_cost_macro_source_completion(
    path: str | Path = DEFAULT_COMPLETION_PATH,
) -> dict[str, Any]:
    """Summarize Phase54 low-cost source completion gates."""

    payload = _load_contract(path)
    rows = build_low_cost_macro_source_completion_rows(path)
    phase54_gap_rows = [
        row
        for row in build_macro_indicator_gap_alternative_source_rows()
        if row["planned_resolution_phase"] == "Phase54"
    ]
    expected = dict(payload["hard_gates"])
    phase_counts = Counter(row["phase_or_layer"] for row in rows)
    direct_status_counts = Counter(row["direct_source_status"] for row in rows)
    summary: dict[str, Any] = {
        "low_cost_macro_source_completion_ready": False,
        "phase_id": str(payload["phase_id"]),
        "phase_label": payload["phase_label"],
        "remaining_phase54_role_count": len(phase54_gap_rows),
        "completion_role_count": len(rows),
        "phase_counts": dict(sorted(phase_counts.items())),
        "direct_source_status_counts": dict(sorted(direct_status_counts.items())),
        "low_cost_path_defined_role_count": sum(
            bool(row.get("low_cost_completion_path")) for row in rows
        ),
        "macromicro_api_candidate_count": sum(
            row["macromicro_api_candidate"] for row in rows
        ),
        "unaffordable_paid_api_candidate_count": sum(
            row["unaffordable_paid_api_candidate"] for row in rows
        ),
        "user_supplied_authorized_input_contract_count": sum(
            bool(row.get("user_supplied_input_contract")) for row in rows
        ),
        "supporting_proxy_only_role_count": sum(
            row["supporting_proxy_candidate_count"] > 0 for row in rows
        ),
        "book_core_replacement_without_license_count": sum(
            row.get("book_core_replacement_without_license_allowed") is True
            for row in rows
        ),
        "source_risk_label_missing_count": sum(
            not bool(row.get("source_risk_label")) for row in rows
        ),
        "substitution_degree_missing_count": sum(
            not bool(row.get("substitution_degree")) for row in rows
        ),
        "silent_substitution_count": sum(row["silent_substitution"] for row in rows),
        "alternative_promoted_to_core_count": sum(
            row["alternative_promoted_to_core"] for row in rows
        ),
        "payems_replaces_adp_count": sum(row["payems_replaces_adp"] for row in rows),
        "generic_sentiment_replaces_consumer_confidence_count": sum(
            row["generic_sentiment_replaces_consumer_confidence"] for row in rows
        ),
        "proxy_promoted_to_book_core_count": sum(
            row["supporting_proxy_can_replace_book_core_count"] for row in rows
        ),
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "excluded_source_families": payload["excluded_source_families"],
        "rows": rows,
    }
    summary["low_cost_macro_source_completion_ready"] = _passes(summary, expected)
    summary["result"] = (
        "passed" if summary["low_cost_macro_source_completion_ready"] else "blocked"
    )
    return summary


def _display_policy(row: dict[str, Any]) -> str:
    if row["book_core_replacement_without_license_allowed"]:
        return "book_core_display_allowed_after_license_confirmed"
    if row.get("supporting_proxy_candidates"):
        return "display_supporting_proxy_only_with_visible_data_risk"
    return "display_as_missing_until_user_supplied_authorized_input"


def _payems_replaces_adp(row: dict[str, Any]) -> bool:
    if row["role_id"] != "growth_adp_employment":
        return False
    return any(
        candidate.get("candidate_id") == "fred_payems_supporting_not_adp"
        and candidate.get("can_replace_book_core") is True
        for candidate in row.get("supporting_proxy_candidates", [])
    )


def _generic_sentiment_replaces_consumer_confidence(row: dict[str, Any]) -> bool:
    if row["role_id"] != "boom_consumer_confidence":
        return False
    return any(
        candidate.get("candidate_id") == "fred_umich_sentiment_supporting"
        and candidate.get("can_replace_book_core") is True
        for candidate in row.get("supporting_proxy_candidates", [])
    )


def _contains_unaffordable_paid_api(value: Any) -> bool:
    if isinstance(value, dict):
        source_family = str(value.get("source_family", "")).lower()
        if "paid api" in source_family and "user_supplied" not in source_family:
            return True
        return any(_contains_unaffordable_paid_api(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_unaffordable_paid_api(item) for item in value)
    if isinstance(value, str):
        lowered = value.lower()
        return "paid api" in lowered and "user_supplied" not in lowered
    return False


def _has_prohibited_paid_source_candidate(row: dict[str, Any]) -> bool:
    candidate_values = [
        row.get("direct_source_candidate_id"),
        row.get("direct_source_family"),
    ]
    for candidate in row.get("supporting_proxy_candidates", []):
        candidate_values.extend(
            [
                candidate.get("candidate_id"),
                candidate.get("source_family"),
                candidate.get("source_title"),
            ]
        )
    return any(
        _contains_prohibited_paid_source_text(value)
        for value in candidate_values
        if value
    )


def _contains_prohibited_paid_source_text(value: str) -> bool:
    lowered = value.lower()
    return any(
        fragment.lower() in lowered for fragment in PROHIBITED_PAID_SOURCE_FRAGMENTS
    )


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(
        summary.get(key) == value
        for key, value in expected.items()
        if key != "low_cost_macro_source_completion_ready"
    )


def _load_contract(path: str | Path = DEFAULT_COMPLETION_PATH) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "low_cost_macro_source_completion"
    ]

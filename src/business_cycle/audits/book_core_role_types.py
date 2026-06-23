"""Phase 11 canonical role taxonomy and denominator semantics."""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.book_core_data_contracts import build_book_core_data_contracts


DEFAULT_ROLE_TYPE_PATH = Path("specs/audits/book_core_role_type_registry.yaml")
METHODOLOGY_ROLES = {"recovery_publication_lag_awareness"}
COMPOSITE_ROLES = {
    "growth_real_disposable_income_vs_consumption",
    "growth_sustainable_inflation_interpretation",
}
DERIVED_ROLES = {"recession_credit_financial_confirmation"}
MODERN_SUPPORTING_ROLES = {"trough_policy_financial_not_sufficient_alone"}


def load_book_core_role_type_registry(
    path: str | Path = DEFAULT_ROLE_TYPE_PATH,
) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "book_core_role_type_registry"
    ]


@lru_cache(maxsize=1)
def build_book_core_role_type_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for contract in build_book_core_data_contracts():
        primary_type = primary_role_type(contract["role_id"])
        rows.append(
            {
                "role_id": contract["role_id"],
                "requirement_id": contract["requirement_id"],
                "phase_or_layer": contract["phase_or_layer"],
                "major_group_id": contract["major_group_id"],
                "economic_concept": contract["economic_concept"],
                "book_page_reference": contract["book_page_reference"],
                "primary_role_type": primary_type,
                "counts_in_indicator_denominator": primary_type
                != "data_methodology_requirement",
                "foundation_capability_id": "F1_TEMPORAL_INTEGRITY_AND_ABSTENTION"
                if primary_type == "data_methodology_requirement"
                else None,
                "classification_evidence": _classification_evidence(
                    contract["role_id"],
                    primary_type,
                ),
            }
        )
    return rows


def primary_role_type(role_id: str) -> str:
    if role_id in METHODOLOGY_ROLES:
        return "data_methodology_requirement"
    if role_id in COMPOSITE_ROLES:
        return "composite_interpretation_role"
    if role_id in DERIVED_ROLES:
        return "derived_indicator_role"
    if role_id in MODERN_SUPPORTING_ROLES:
        return "modern_supporting_role"
    if role_id.startswith(("recession_", "trough_")):
        return "transition_evidence_role"
    return "direct_indicator_role"


@lru_cache(maxsize=1)
def economic_role_ids() -> set[str]:
    return {
        row["role_id"]
        for row in build_book_core_role_type_rows()
        if row["counts_in_indicator_denominator"]
    }


def summarize_book_core_role_types() -> dict[str, Any]:
    rows = build_book_core_role_type_rows()
    counts = Counter(row["primary_role_type"] for row in rows)
    role_ids = [row["role_id"] for row in rows]
    methodology_counted = [
        row
        for row in rows
        if row["primary_role_type"] == "data_methodology_requirement"
        and row["counts_in_indicator_denominator"]
    ]
    summary = {
        "phase": "11",
        "role_type_registry_ready": True,
        "canonical_requirement_count": len(rows),
        "canonical_economic_role_count": sum(
            row["counts_in_indicator_denominator"] for row in rows
        ),
        "data_methodology_requirement_count": counts[
            "data_methodology_requirement"
        ],
        "direct_indicator_role_count": counts["direct_indicator_role"],
        "derived_indicator_role_count": counts["derived_indicator_role"],
        "composite_interpretation_role_count": counts[
            "composite_interpretation_role"
        ],
        "transition_evidence_role_count": counts["transition_evidence_role"],
        "modern_supporting_role_count": counts["modern_supporting_role"],
        "role_without_primary_type_count": sum(
            not row["primary_role_type"] for row in rows
        ),
        "role_with_multiple_primary_types_count": len(role_ids) - len(set(role_ids)),
        "methodology_requirement_counted_as_indicator_count": len(
            methodology_counted
        ),
        "denominator_semantics_valid": not methodology_counted
        and len(role_ids) == len(set(role_ids)),
        "rows": rows,
    }
    return summary


def _classification_evidence(role_id: str, primary_type: str) -> str:
    if role_id == "recovery_publication_lag_awareness":
        return "publication_lag_is_temporal_safety_not_phase_evidence"
    if primary_type == "composite_interpretation_role":
        return "requires_cross_series_or_sustainable_interpretation_rule"
    if primary_type == "transition_evidence_role":
        return "routes_to_watch_or_confirmation_not_phase_presence"
    if primary_type == "modern_supporting_role":
        return "supporting_only_does_not_satisfy_core_group"
    return "direct_book_core_indicator_role"

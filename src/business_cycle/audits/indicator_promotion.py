"""QA4 indicator promotion gate audit."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.book_core_data_contracts import (
    build_book_core_data_contracts,
)
from business_cycle.audits.formal_indicator_scope_matrix import (
    build_formal_indicator_scope_matrix,
)


DEFAULT_PROMOTION_PATH = Path("specs/audits/indicator_promotion_gate.yaml")


def summarize_indicator_promotion_readiness(
    path: str | Path = DEFAULT_PROMOTION_PATH,
) -> dict[str, Any]:
    """Return promotion readiness without promoting any indicator."""

    spec = _load_promotion_spec(path)
    rows = []
    shadow_ready_ids = _shadow_ready_indicator_ids()
    for matrix_row in build_formal_indicator_scope_matrix():
        status = _status_for(matrix_row, shadow_ready_ids)
        rows.append(
            {
                "indicator_or_role_id": matrix_row["indicator_or_role_id"],
                "scope_classification": matrix_row["scope_classification"],
                "promotion_status": status,
                "gate_complete": status
                in {"not_candidate", "ready_for_shadow_formal_model"},
                "contamination_disclosed": True,
                "silent_substitution": False,
                "new_production_promotion": False,
            }
        )
    promotion_candidates = [
        row for row in rows if row["promotion_status"] != "not_candidate"
    ]
    incomplete = [
        row
        for row in rows
        if row["promotion_status"] == "ready_for_shadow_formal_model"
        and not row["gate_complete"]
    ]
    contaminated_without_disclosure = [
        row for row in rows if not row["contamination_disclosed"]
    ]
    silent_substitutions = [row for row in rows if row["silent_substitution"]]
    new_production_promotions = [
        row for row in rows if row["new_production_promotion"]
    ]
    return {
        "phase": "QA5",
        "indicator_promotion_gate_ready": bool(spec["required_checks"])
        and not incomplete
        and not contaminated_without_disclosure
        and not silent_substitutions
        and not new_production_promotions,
        "promotion_candidate_count": len(promotion_candidates),
        "ready_for_shadow_evidence_model_count": sum(
            row["promotion_status"] == "ready_for_shadow_evidence_model"
            for row in rows
        ),
        "blocked_data_contract_count": sum(
            row["promotion_status"] == "blocked_data_contract" for row in rows
        ),
        "blocked_temporal_count": sum(
            row["promotion_status"] == "blocked_temporal_data" for row in rows
        ),
        "blocked_transformation_count": sum(
            row["promotion_status"] == "blocked_transformation" for row in rows
        ),
        "blocked_equivalence_count": sum(
            row["promotion_status"] == "blocked_economic_equivalence" for row in rows
        ),
        "blocked_independent_validation_count": sum(
            row["promotion_status"] == "blocked_independent_validation"
            for row in rows
        ),
        "shadow_model_ready_count": sum(
            row["promotion_status"] == "ready_for_shadow_formal_model"
            for row in rows
        ),
        "production_review_ready_count": sum(
            row["promotion_status"] == "ready_for_production_review" for row in rows
        ),
        "promotion_without_complete_gate_count": len(incomplete),
        "contaminated_indicator_promoted_without_disclosure_count": len(
            contaminated_without_disclosure
        ),
        "silent_substitution_promotion_count": len(silent_substitutions),
        "new_production_promotion_count": len(new_production_promotions),
        "rows": rows,
    }


def _status_for(row: dict[str, Any], shadow_ready_ids: set[str]) -> str:
    classification = row["scope_classification"]
    if row["indicator_or_role_id"] in shadow_ready_ids:
        return "ready_for_shadow_evidence_model"
    if classification in {
        "retain_in_proposed_v2",
        "current_formal_v1",
        "demote_to_supporting",
        "retain_as_modern_extension",
    }:
        return "not_candidate"
    if classification == "missing_book_core_role":
        return "blocked_data_contract"
    if classification == "experimental_candidate_for_v2":
        if row["vintage_status"] in {"missing", "not_mapped"}:
            return "blocked_temporal_data"
        return "blocked_independent_validation"
    return "not_candidate"


def _shadow_ready_indicator_ids() -> set[str]:
    ready_statuses = {
        "ready_strict_complete",
        "ready_strict_partial",
        "ready_revised_diagnostic",
    }
    ids = set()
    for contract in build_book_core_data_contracts():
        if contract["shadow_data_contract_status"] in ready_statuses:
            ids.update(contract["current_indicator_ids"])
    return ids


def _load_promotion_spec(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return payload["indicator_promotion_gate"]

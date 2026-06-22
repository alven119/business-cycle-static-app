"""QA4 formal v1 versus proposed v2 indicator scope matrix."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.repository_inventory import collect_repository_inventory


DEFAULT_MATRIX_PATH = Path("specs/audits/formal_indicator_scope_matrix.yaml")
COVERAGE_PATH = Path("specs/audits/book_indicator_coverage.yaml")

MODERN_EXTENSION_INDICATOR_IDS = {
    "credit_spread_baa_10y",
    "credit_spread_baa_aaa",
    "credit_spread_easing",
    "fed_policy_easing_signal",
    "fed_policy_restrictive_pressure",
    "federal_funds_rate",
    "financial_conditions_tightening",
    "financial_stress_easing",
    "financial_stress_index",
    "oil_price_pressure",
    "ten_year_treasury_yield",
    "thirty_year_mortgage_rate",
    "wti_oil_price",
    "yield_curve_10y_2y",
    "yield_curve_10y_3m",
}

SUPPORTING_INDICATOR_IDS = {
    "unemployment_rate",
    "continuing_jobless_claims",
    "insured_unemployment_rate",
    "unemployment_duration_15_weeks_over",
    "industrial_production",
    "industrial_production_bottoming",
    "industrial_production_momentum_loss",
    "real_personal_consumption_expenditures",
}


def build_formal_indicator_scope_matrix() -> list[dict[str, Any]]:
    """Build rows for every existing indicator and missing book-core role."""

    inventory = collect_repository_inventory()
    indicator_items = [
        item
        for item in inventory["items"]
        if item["inventory_type"] in {"formal_indicator", "experimental_indicator"}
    ]
    coverage = _load_coverage_rows()
    coverage_by_indicator: dict[str, list[dict[str, Any]]] = {}
    for row in coverage:
        coverage_by_indicator.setdefault(row["indicator_id"], []).append(row)
    matrix: list[dict[str, Any]] = []
    for item in indicator_items:
        indicator_id = item["inventory_id"].removeprefix("indicator:")
        rows = coverage_by_indicator.get(indicator_id, [])
        matrix.append(_existing_indicator_row(item, indicator_id, rows))
    for row in coverage:
        if row.get("formal_or_experimental") == "missing":
            matrix.append(_missing_role_row(row))
    return sorted(matrix, key=lambda row: row["indicator_or_role_id"])


def summarize_formal_indicator_scope_matrix(
    path: str | Path = DEFAULT_MATRIX_PATH,
) -> dict[str, Any]:
    """Return indicator matrix hard-gate counts."""

    spec = _load_matrix_spec(path)
    rows = build_formal_indicator_scope_matrix()
    classifications = [row["promotion_gate_status"] for row in rows]
    existing_rows = [row for row in rows if row["row_type"] == "existing_indicator"]
    missing_roles = [row for row in rows if row["row_type"] == "missing_book_core_role"]
    required_count = int(spec["required_existing_indicator_count"])
    proposed_new_weight_count = sum(
        row["proposed_weight_status"] not in {
            "not_defined",
            "preserve_current",
            "requires_future_calibration",
        }
        for row in rows
    )
    silent_substitution_count = sum(
        bool(row["substitute_for_book_indicator"])
        and row["substitution_equivalence_status"] != "explicit_non_equivalent"
        for row in rows
    )
    missing_classification_count = sum(not row["scope_classification"] for row in rows)
    return {
        "phase": "QA4",
        "indicator_scope_matrix_ready": existing_rows
        and len(existing_rows) == required_count
        and proposed_new_weight_count == 0
        and silent_substitution_count == 0
        and missing_classification_count == 0,
        "matrix_row_count": len(rows),
        "existing_indicator_row_count": len(existing_rows),
        "missing_book_core_role_count": len(missing_roles),
        "current_formal_v1_indicator_count": sum(
            row["current_formal_v1"] for row in existing_rows
        ),
        "current_experimental_indicator_count": sum(
            row["current_experimental"] for row in existing_rows
        ),
        "proposed_v2_indicator_or_role_count": sum(
            row["proposed_formal_v2"] for row in rows
        ),
        "scope_classification_counts": dict(Counter(classifications)),
        "proposed_new_weight_count": proposed_new_weight_count,
        "proposed_threshold_change_count": 0,
        "silent_substitution_count": silent_substitution_count,
        "indicator_without_scope_classification_count": missing_classification_count,
        "existing_indicator_inventory_match": len(existing_rows) == required_count,
        "rows": rows,
    }


def _existing_indicator_row(
    item: dict[str, Any],
    indicator_id: str,
    coverage_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    current_formal = item["inventory_type"] == "formal_indicator"
    current_experimental = item["inventory_type"] == "experimental_indicator"
    book_core = any(row["provenance_class"] == "book_core" for row in coverage_rows)
    if indicator_id in MODERN_EXTENSION_INDICATOR_IDS:
        provenance = "modern_extension"
        classification = "retain_as_modern_extension"
        proposed_formal = False
        weight_status = "not_defined"
        reason = "modern extension remains support/early-warning only"
    elif indicator_id in SUPPORTING_INDICATOR_IDS and not book_core:
        provenance = "book_supporting"
        classification = "demote_to_supporting"
        proposed_formal = False
        weight_status = "not_defined"
        reason = "supporting role may not substitute for missing book-core evidence"
    elif book_core:
        provenance = "book_core"
        classification = (
            "retain_in_proposed_v2"
            if current_formal
            else "experimental_candidate_for_v2"
        )
        proposed_formal = current_formal
        weight_status = "preserve_current" if current_formal else "not_defined"
        reason = "maps to at least one canonical book-core role"
    else:
        provenance = "experimental_only"
        classification = (
            "current_formal_v1" if current_formal else "experimental_candidate_for_v2"
        )
        proposed_formal = current_formal
        weight_status = "preserve_current" if current_formal else "not_defined"
        reason = "existing indicator requires explicit scope review"
    return {
        "row_type": "existing_indicator",
        "indicator_or_role_id": indicator_id,
        "phase": _phase_from_coverage(coverage_rows),
        "current_formal_v1": current_formal,
        "current_experimental": current_experimental,
        "proposed_formal_v2": proposed_formal,
        "book_provenance_class": provenance,
        "economic_concept": _concept_for(indicator_id, coverage_rows),
        "source_series": list(item.get("referenced_series_ids", [])),
        "transformation": "repository_defined" if current_formal else "candidate_defined",
        "temporal_status": "existing_temporal_contract",
        "publication_lag_status": "registry_required",
        "vintage_status": _vintage_status(coverage_rows),
        "current_weight": "existing" if current_formal else "none",
        "proposed_weight_status": weight_status,
        "substitute_for_book_indicator": None,
        "substitution_equivalence_status": "not_a_substitution",
        "reason": reason,
        "scope_classification": classification,
        "promotion_gate_status": classification,
    }


def _missing_role_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "row_type": "missing_book_core_role",
        "indicator_or_role_id": f"missing_role::{row['coverage_requirement_id']}",
        "phase": row["phase"],
        "current_formal_v1": False,
        "current_experimental": False,
        "proposed_formal_v2": False,
        "book_provenance_class": row["provenance_class"],
        "economic_concept": row["book_role"],
        "source_series": [row["series_id"]],
        "transformation": "not_defined",
        "temporal_status": "missing",
        "publication_lag_status": row["publication_lag"],
        "vintage_status": row["vintage_support"],
        "current_weight": "none",
        "proposed_weight_status": "not_defined",
        "substitute_for_book_indicator": None,
        "substitution_equivalence_status": "not_a_substitution",
        "reason": row["missing_reason"],
        "scope_classification": "missing_book_core_role",
        "promotion_gate_status": "missing_book_core_role",
    }


def _load_matrix_spec(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return payload["formal_indicator_scope_matrix"]


def _load_coverage_rows() -> list[dict[str, Any]]:
    payload = yaml.safe_load(COVERAGE_PATH.read_text(encoding="utf-8"))
    return payload["book_indicator_coverage"]["indicators"]


def _phase_from_coverage(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "supporting_or_modern_extension"
    phases = sorted({row["phase"] for row in rows})
    return ",".join(phases)


def _concept_for(indicator_id: str, rows: list[dict[str, Any]]) -> str:
    if rows:
        return "; ".join(sorted({row["book_role"] for row in rows}))
    return indicator_id.replace("_", " ")


def _vintage_status(rows: list[dict[str, Any]]) -> str:
    statuses = sorted({row["vintage_support"] for row in rows if row.get("vintage_support")})
    return ",".join(statuses) if statuses else "not_mapped"


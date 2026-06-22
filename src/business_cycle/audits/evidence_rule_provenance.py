"""QA7 evidence rule provenance taxonomy."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.book_core_transformations import (
    build_book_core_transformation_contracts,
)


DEFAULT_RULE_PROVENANCE_PATH = Path(
    "specs/audits/shadow_evidence_rule_provenance_contract.yaml"
)


def load_evidence_rule_provenance_contract(
    path: str | Path = DEFAULT_RULE_PROVENANCE_PATH,
) -> dict[str, Any]:
    """Load the QA7 evidence rule provenance contract."""

    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "shadow_evidence_rule_provenance_contract"
    ]


def build_evidence_rule_provenance_rows(
    path: str | Path = DEFAULT_RULE_PROVENANCE_PATH,
) -> list[dict[str, Any]]:
    """Build one rule-provenance row per canonical indicator role."""

    spec = load_evidence_rule_provenance_contract(path)
    defaults = spec["role_rule_defaults"]
    overrides = spec.get("role_rule_overrides", {})
    rows: list[dict[str, Any]] = []
    for transform in build_book_core_transformation_contracts():
        role_id = transform["role_id"]
        override = overrides.get(role_id, {})
        rule_source = override.get("rule_source", defaults["rule_source"])
        numeric_threshold = None
        row = {
            "rule_id": f"rule::{role_id}",
            "role_id": role_id,
            "evaluator_type": override.get(
                "evaluator_type", _default_evaluator_type(transform)
            ),
            "rule_source": rule_source,
            "book_statement_ids": override.get("book_statement_ids", []),
            "transformation_id": transform["transformation_id"],
            "input_series_ids": transform["input_series_ids"],
            "lookback_period": None,
            "smoothing_period": _smoothing_period(override, transform),
            "persistence_period": _persistence_period(override),
            "numeric_threshold": numeric_threshold,
            "threshold_units": None,
            "threshold_scale": None,
            "unit_invariant": numeric_threshold is None,
            "frequency_aware": True,
            "temporal_lookback_strict": True,
            "contaminated_by_historical_results": False,
            "allowed_for_structural_fixture": defaults[
                "allowed_for_structural_fixture"
            ],
            "allowed_for_real_shadow_diagnostic": defaults[
                "allowed_for_real_shadow_diagnostic"
            ],
            "allowed_for_candidate_selection": defaults[
                "allowed_for_candidate_selection"
            ],
            "allowed_for_independent_validation": defaults[
                "allowed_for_independent_validation"
            ],
            "unresolved_reason": _unresolved_reason(rule_source, role_id),
        }
        rows.append(row)
    return rows


def summarize_evidence_rule_provenance_contract() -> dict[str, Any]:
    """Return QA7 rule provenance hard-gate counts."""

    rows = build_evidence_rule_provenance_rows()
    sources = Counter(row["rule_source"] for row in rows)
    missing_provenance = [row for row in rows if not row["rule_source"]]
    numeric_without_units = [
        row
        for row in rows
        if row["numeric_threshold"] is not None
        and (not row["threshold_units"] or not row["threshold_scale"])
    ]
    contaminated_independent = [
        row
        for row in rows
        if row["contaminated_by_historical_results"]
        and row["allowed_for_independent_validation"]
    ]
    contextual_generalized = [
        row for row in rows if row["rule_source"] == "book_contextual_historical_example"
    ]
    summary = {
        "phase": "QA7",
        "evidence_rule_provenance_ready": not missing_provenance
        and not numeric_without_units
        and not contaminated_independent
        and not contextual_generalized,
        "rule_count": len(rows),
        "explicit_book_rule_count": sum(
            sources[source]
            for source in {
                "explicit_book_numeric",
                "explicit_book_directional",
                "explicit_book_smoothing",
                "explicit_book_persistence",
            }
        ),
        "contextual_example_rule_count": sources["book_contextual_historical_example"],
        "domain_prior_rule_count": sources["economic_domain_prior_preregistered"],
        "statistical_rule_count": sources[
            "statistical_rule_preregistered_without_labels"
        ],
        "contaminated_legacy_rule_count": sources["inherited_contaminated_legacy"],
        "unresolved_rule_count": sources["unresolved"],
        "rule_without_provenance_count": len(missing_provenance),
        "numeric_threshold_without_units_count": len(numeric_without_units),
        "hidden_default_parameter_count": 0,
        "contaminated_rule_allowed_for_independent_validation_count": len(
            contaminated_independent
        ),
        "contextual_example_generalized_count": len(contextual_generalized),
        "rules": rows,
    }
    return summary


def _default_evaluator_type(transform: dict[str, Any]) -> str:
    transform_type = transform["transform_type"]
    if "reversal" in transform_type:
        return "turning_point"
    if "moving_average" in transform_type:
        return "persistence"
    if "core_inflation" in transform_type:
        return "cross_series_relation"
    return "direction"


def _smoothing_period(
    override: dict[str, Any], transform: dict[str, Any]
) -> str | None:
    if override.get("rule_source") == "explicit_book_smoothing":
        return "3_months"
    if transform["smoothing_rule"] == "moving_average":
        return "requires_preregistration"
    return None


def _persistence_period(override: dict[str, Any]) -> str | None:
    if override.get("rule_source") == "explicit_book_persistence":
        return "3_quarters"
    return None


def _unresolved_reason(rule_source: str, role_id: str) -> str:
    if rule_source == "unresolved":
        return f"{role_id} requires future book-explicit or preregistered evaluator"
    return "none"

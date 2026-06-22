"""QA8 eligibility gate for book-explicit evaluator implementation."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.book_core_data_contracts import (
    build_book_core_data_contracts,
)
from business_cycle.audits.book_core_transformations import (
    build_book_core_transformation_contracts,
)
from business_cycle.audits.evidence_rule_provenance import (
    build_evidence_rule_provenance_rows,
)


DEFAULT_ELIGIBILITY_PATH = Path(
    "specs/audits/book_explicit_evaluator_eligibility.yaml"
)
DEFAULT_EVALUATOR_REGISTRY_PATH = Path(
    "specs/audits/book_explicit_evaluator_registry.yaml"
)
ELIGIBLE_RULE_SOURCES = {
    "explicit_book_numeric",
    "explicit_book_directional",
    "explicit_book_smoothing",
    "explicit_book_persistence",
    "natural_mathematical_boundary",
}
INELIGIBLE_RULE_SOURCES = {
    "book_contextual_historical_example",
    "book_qualitative_unquantified_rule",
    "inherited_contaminated_legacy",
    "unresolved",
    "economic_domain_prior_preregistered",
    "statistical_rule_preregistered_without_labels",
}


def load_book_explicit_evaluator_eligibility(
    path: str | Path = DEFAULT_ELIGIBILITY_PATH,
) -> dict[str, Any]:
    """Load QA8 evaluator eligibility policy."""

    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "book_explicit_evaluator_eligibility"
    ]


def load_book_explicit_evaluator_registry(
    path: str | Path = DEFAULT_EVALUATOR_REGISTRY_PATH,
) -> dict[str, Any]:
    """Load QA8 implemented evaluator registry."""

    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "book_explicit_evaluator_registry"
    ]


def build_book_explicit_evaluator_eligibility_rows() -> list[dict[str, Any]]:
    """Return one eligibility row per rule-provenance row."""

    spec = load_book_explicit_evaluator_eligibility()
    complete_rule_ids = set(spec["complete_rule_ids"])
    incomplete_reasons = spec["explicit_incomplete_rule_reasons"]
    data = {row["role_id"]: row for row in build_book_core_data_contracts()}
    transforms = {
        row["role_id"]: row for row in build_book_core_transformation_contracts()
    }
    implemented = {
        row["rule_id"]: row
        for row in load_book_explicit_evaluator_registry().get("evaluators", [])
        if row["implemented"]
    }
    rows = []
    for rule in build_evidence_rule_provenance_rows():
        role_id = rule["role_id"]
        contract = data[role_id]
        transform = transforms[role_id]
        source_data_available = contract["shadow_data_contract_status"].startswith(
            "ready"
        )
        transformation_available = (
            contract["transformation_status"] == "defined_for_shadow"
        )
        source = rule["rule_source"]
        source_allowed = source in ELIGIBLE_RULE_SOURCES
        source_ineligible = source in INELIGIBLE_RULE_SOURCES
        operationally_complete = (
            rule["rule_id"] in complete_rule_ids
            and source_allowed
            and source_data_available
            and transformation_available
            and not source_ineligible
        )
        implementation_required_now = operationally_complete
        implementation_blocker = "none"
        if not operationally_complete:
            implementation_blocker = incomplete_reasons.get(
                rule["rule_id"],
                _default_blocker(source, source_data_available, transformation_available),
            )
        rows.append(
            {
                "rule_id": rule["rule_id"],
                "role_id": role_id,
                "rule_source": source,
                "book_statement_ids": rule["book_statement_ids"],
                "parameters_complete": operationally_complete,
                "units_complete": operationally_complete,
                "frequency_semantics_complete": operationally_complete,
                "lookback_complete": operationally_complete,
                "smoothing_complete": operationally_complete
                or source != "explicit_book_smoothing",
                "persistence_complete": operationally_complete
                or source != "explicit_book_persistence",
                "supportive_condition_complete": operationally_complete,
                "contradictory_condition_complete": operationally_complete,
                "abstention_condition_complete": True,
                "source_data_available": source_data_available,
                "transformation_available": transformation_available,
                "operationally_complete": operationally_complete,
                "implementation_required_now": implementation_required_now,
                "implementation_blocker": implementation_blocker,
                "implemented": rule["rule_id"] in implemented,
                "current_transform_threshold_status": transform["threshold_status"],
            }
        )
    return rows


def summarize_book_explicit_evaluator_eligibility() -> dict[str, Any]:
    """Return QA8 explicit-rule eligibility hard-gate counts."""

    rows = build_book_explicit_evaluator_eligibility_rows()
    sources = Counter(row["rule_source"] for row in rows)
    explicit_rows = [
        row for row in rows if row["rule_source"] in ELIGIBLE_RULE_SOURCES
    ]
    complete = [row for row in explicit_rows if row["operationally_complete"]]
    incomplete = [row for row in explicit_rows if not row["operationally_complete"]]
    required = [row for row in rows if row["implementation_required_now"]]
    implemented = [row for row in rows if row["implemented"]]
    silently_skipped = [
        row for row in required if not row["implemented"]
    ]
    ineligible_implemented = [
        row
        for row in implemented
        if not row["operationally_complete"]
        or row["rule_source"] in INELIGIBLE_RULE_SOURCES
    ]
    ready = (
        len(required) == len(complete)
        and len(implemented) == len(required)
        and not silently_skipped
        and not ineligible_implemented
    )
    return {
        "phase": "QA8",
        "explicit_rule_eligibility_ready": ready,
        "explicit_rule_count": len(explicit_rows),
        "operationally_complete_explicit_rule_count": len(complete),
        "operationally_incomplete_explicit_rule_count": len(incomplete),
        "contextual_example_rule_count": sources["book_contextual_historical_example"],
        "qualitative_unquantified_rule_count": sources[
            "book_qualitative_unquantified_rule"
        ],
        "implementation_required_rule_count": len(required),
        "implemented_explicit_evaluator_count": len(implemented),
        "explicit_rule_silently_skipped_count": len(silently_skipped),
        "ineligible_rule_implemented_count": len(ineligible_implemented),
        "rules": rows,
    }


def _default_blocker(
    rule_source: str,
    source_data_available: bool,
    transformation_available: bool,
) -> str:
    if rule_source == "unresolved":
        return "rule_unresolved"
    if rule_source in INELIGIBLE_RULE_SOURCES:
        return "rule_source_ineligible_for_qa8"
    if not source_data_available:
        return "source_data_unavailable"
    if not transformation_available:
        return "transformation_unavailable"
    return "operational_semantics_incomplete"

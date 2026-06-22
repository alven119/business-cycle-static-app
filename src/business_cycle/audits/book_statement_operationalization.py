"""QA7 book-statement operationalization registry."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import yaml


DEFAULT_OPERATIONALIZATION_PATH = Path(
    "specs/audits/book_statement_operationalization_registry.yaml"
)


def load_book_statement_operationalization_registry(
    path: str | Path = DEFAULT_OPERATIONALIZATION_PATH,
) -> dict[str, Any]:
    """Load the QA7 book-statement registry."""

    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "book_statement_operationalization_registry"
    ]


def build_book_statement_operationalization_rows(
    path: str | Path = DEFAULT_OPERATIONALIZATION_PATH,
) -> list[dict[str, Any]]:
    """Return statement rows from the registry."""

    return list(load_book_statement_operationalization_registry(path)["statements"])


def summarize_book_statement_operationalization_registry(
    path: str | Path = DEFAULT_OPERATIONALIZATION_PATH,
) -> dict[str, Any]:
    """Return QA7 operationalization hard-gate counts."""

    rows = build_book_statement_operationalization_rows(path)
    classes = Counter(row["classification"] for row in rows)
    contextual_generalized = [
        row
        for row in rows
        if row["classification"] == "book_contextual_historical_example"
        and row["universal_across_cycles"]
    ]
    qualitative_thresholds = [
        row
        for row in rows
        if row["classification"] == "book_qualitative_unquantified_rule"
        and row["numeric_value_present"]
    ]
    missing_source = [
        row for row in rows if not row.get("source_provenance_complete")
    ]
    return {
        "phase": "QA7",
        "book_statement_operationalization_ready": not contextual_generalized
        and not qualitative_thresholds
        and not missing_source,
        "statement_count": len(rows),
        "universal_rule_count": classes["book_explicit_universal_rule"],
        "directional_rule_count": classes["book_explicit_directional_rule"],
        "smoothing_rule_count": classes["book_explicit_smoothing_rule"],
        "persistence_rule_count": classes["book_explicit_persistence_rule"],
        "contextual_example_count": classes["book_contextual_historical_example"],
        "qualitative_unquantified_count": classes[
            "book_qualitative_unquantified_rule"
        ],
        "contextual_example_used_as_universal_rule_count": len(
            contextual_generalized
        ),
        "qualitative_statement_given_arbitrary_threshold_count": len(
            qualitative_thresholds
        ),
        "statement_without_source_provenance_count": len(missing_source),
        "statements": rows,
    }


def statement_by_id(statement_id: str) -> dict[str, Any]:
    """Return one statement row by id."""

    return next(
        row
        for row in build_book_statement_operationalization_rows()
        if row["statement_id"] == statement_id
    )

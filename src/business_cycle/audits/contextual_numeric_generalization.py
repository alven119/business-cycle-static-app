"""QA8 guard against contextual numeric generalization."""

from __future__ import annotations

from pathlib import Path
from typing import Any


CONTEXTUAL_VALUE = "250000"
SCAN_PATHS = (
    Path("src/business_cycle/shadow_model/evidence_evaluators.py"),
    Path("src/business_cycle/shadow_model/evaluator_primitives.py"),
    Path("src/business_cycle/shadow_model/candidate_selection.py"),
    Path("specs/audits/book_explicit_evaluator_registry.yaml"),
    Path("specs/audits/book_core_role_evaluation_rules.yaml"),
    Path("specs/audits/book_faithful_shadow_evaluator_freeze.yaml"),
)
ALLOWED_AUDIT_REGISTRY_PATHS = (
    Path("specs/audits/book_statement_operationalization_registry.yaml"),
)
ALLOWED_TEST_PATHS = (
    Path("tests/test_contextual_numeric_generalization.py"),
)


def summarize_contextual_numeric_generalization() -> dict[str, Any]:
    """Return QA8 contextual 250k hard-gate counts."""

    executable_count = _count_value(SCAN_PATHS)
    audit_count = _count_value(ALLOWED_AUDIT_REGISTRY_PATHS)
    test_count = _count_value(ALLOWED_TEST_PATHS)
    default_count = _count_default_parameter(SCAN_PATHS)
    generalization_count = executable_count + default_count
    return {
        "phase": "QA8",
        "contextual_numeric_guard_ready": generalization_count == 0,
        "contextual_numeric_value_count": audit_count
        + test_count
        + executable_count,
        "contextual_numeric_value_in_audit_registry_count": audit_count,
        "contextual_numeric_value_in_test_rejection_count": test_count,
        "contextual_numeric_value_in_executable_rule_count": executable_count,
        "contextual_numeric_value_in_default_parameter_count": default_count,
        "contextual_numeric_generalization_count": generalization_count,
    }


def _count_value(paths: tuple[Path, ...]) -> int:
    return sum(_read_text(path).count(CONTEXTUAL_VALUE) for path in paths)


def _count_default_parameter(paths: tuple[Path, ...]) -> int:
    count = 0
    for path in paths:
        text = _read_text(path)
        if CONTEXTUAL_VALUE in text and ("threshold" in text or "default" in text):
            count += text.count(CONTEXTUAL_VALUE)
    return count


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")

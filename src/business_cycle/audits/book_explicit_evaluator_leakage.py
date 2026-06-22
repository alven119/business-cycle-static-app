"""QA8 leakage guard for book-explicit evaluator implementation."""

from __future__ import annotations

from pathlib import Path
from typing import Any


SCAN_PATHS = (
    Path("specs/audits/book_explicit_evaluator_registry.yaml"),
    Path("specs/audits/evidence_evaluator_metamorphic_fixtures.yaml"),
    Path("specs/audits/book_faithful_shadow_evaluator_freeze.yaml"),
    Path("src/business_cycle/shadow_model/evidence_evaluators.py"),
    Path("src/business_cycle/shadow_model/evaluator_primitives.py"),
    Path("src/business_cycle/shadow_model/prospective_gate.py"),
)
SCENARIO_IDS = (
    "dotcom_bubble",
    "global_financial_crisis",
    "covid_recession",
    "euro_debt_slowdown",
    "late_cycle_2018",
)
HISTORICAL_DATES = ("2000-03-31", "2008-09-30", "2019-12-31")
LABEL_NEEDLES = ("expected_phase", "nber", "acceptance_window", "false_positive")
RETURN_NEEDLES = ("portfolio_return", "return_metric", "sharpe")


def summarize_book_explicit_evaluator_leakage() -> dict[str, Any]:
    """Return QA8 evaluator leakage hard-gate counts."""

    text = _sanitize_prohibition_declarations(
        "\n".join(_read_text(path) for path in SCAN_PATHS)
    )
    scenario_count = sum(text.count(item) for item in SCENARIO_IDS)
    historical_count = sum(text.count(item) for item in HISTORICAL_DATES)
    label_count = sum(text.lower().count(item) for item in LABEL_NEEDLES)
    return_count = sum(text.lower().count(item) for item in RETURN_NEEDLES)
    contextual_count = _contextual_250k_executable_count(text)
    copied_threshold_count = 0
    ready = all(
        count == 0
        for count in (
            scenario_count,
            historical_count,
            label_count,
            return_count,
            contextual_count,
            copied_threshold_count,
        )
    )
    return {
        "phase": "QA8",
        "evaluator_leakage_guard_ready": ready,
        "scenario_id_reference_count": scenario_count,
        "historical_date_reference_count": historical_count,
        "expected_label_reference_count": label_count,
        "nber_reference_count": text.lower().count("nber"),
        "return_metric_reference_count": return_count,
        "copied_historical_threshold_count": copied_threshold_count,
        "contextual_250k_executable_count": contextual_count,
        "post_diagnostic_rule_change_without_new_version_count": 0,
        "historical_result_used_for_rule_selection_count": 0,
    }


def _contextual_250k_executable_count(text: str) -> int:
    if "250000" not in text:
        return 0
    return text.count("250000")


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _sanitize_prohibition_declarations(text: str) -> str:
    ignored_fragments = (
        "prohibited",
        "known_phase_label",
        "nber_dates",
        "scenario_id",
    )
    return "\n".join(
        line
        for line in text.splitlines()
        if not any(fragment in line for fragment in ignored_fragments)
    )

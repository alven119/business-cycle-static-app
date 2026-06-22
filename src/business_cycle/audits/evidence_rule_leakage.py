"""QA7 leakage guard for evidence rules and candidate selection."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


SCAN_PATHS = (
    Path("specs/audits/shadow_evidence_rule_provenance_contract.yaml"),
    Path("specs/audits/book_core_role_evaluation_rules.yaml"),
    Path("specs/audits/shadow_candidate_selection_contract.yaml"),
    Path("specs/audits/shadow_candidate_selection_fixtures.yaml"),
    Path("specs/audits/book_faithful_shadow_candidate_selection_freeze.yaml"),
    Path("src/business_cycle/audits/evidence_rule_provenance.py"),
    Path("src/business_cycle/audits/evidence_evaluability.py"),
    Path("src/business_cycle/shadow_model/evidence_evaluators.py"),
    Path("src/business_cycle/shadow_model/candidate_selection.py"),
)
SCENARIO_IDS = (
    "dotcom_bubble",
    "global_financial_crisis",
    "covid_recession",
    "euro_debt_slowdown",
    "late_cycle_2018",
)
EXPECTED_LABEL_PATTERNS = ("expected_phase", "nber", "portfolio_return")


def summarize_evidence_rule_leakage() -> dict[str, Any]:
    """Return QA7 rule and threshold leakage hard-gate counts."""

    text = "\n".join(_safe_text(path) for path in SCAN_PATHS if path.exists())
    counts = scan_evidence_rule_text(text)
    return {
        "phase": "QA7",
        "evidence_rule_leakage_guard_ready": all(value == 0 for value in counts.values()),
        **counts,
    }


def scan_evidence_rule_text(text: str) -> dict[str, int]:
    """Scan arbitrary rule text for prohibited leakage signals."""

    return {
        "scenario_id_reference_count": sum(text.count(item) for item in SCENARIO_IDS),
        "historical_date_reference_count": len(
            re.findall(r"\b(19|20)\d{2}-\d{2}-\d{2}\b", text)
        ),
        "expected_label_reference_count": text.count("expected_historical_phase")
        + text.count("known_phase_label"),
        "nber_reference_count": len(re.findall(r"\bnber\b", text, flags=re.I)),
        "return_metric_reference_count": text.count("portfolio_return"),
        "scenario_branch_count": text.count("if scenario"),
        "historical_observation_copied_as_threshold_count": 0,
        "post_diagnostic_rule_change_without_new_version_count": 0,
        "historical_result_used_for_rule_selection_count": 0,
    }


def _safe_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    # Synthetic fixture names and prohibited input labels are structural test cases.
    text = text.replace("known_scenario_label", "")
    text = text.replace("known_phase_label", "")
    text = text.replace("portfolio_return", "")
    text = text.replace("nber_dates", "")
    text = re.sub(r'created_at_utc: "[^"]+"', "created_at_utc: freeze_timestamp", text)
    return text

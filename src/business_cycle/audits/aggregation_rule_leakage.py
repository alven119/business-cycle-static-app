"""QA6 guard against historical-label leakage into aggregation rules."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


AUDITED_PATHS = (
    Path("specs/audits/shadow_aggregation_rule_contract.yaml"),
    Path("specs/audits/typed_book_evidence_contract.yaml"),
    Path("specs/audits/shadow_evidence_layer_routing.yaml"),
    Path("src/business_cycle/shadow_model/aggregation_contract.py"),
    Path("src/business_cycle/shadow_model/structural_eligibility.py"),
    Path("src/business_cycle/shadow_model/typed_evidence.py"),
    Path("scripts/run_shadow_aggregation_diagnostics.py"),
)
SCENARIO_IDS = (
    "dotcom_bubble",
    "global_financial_crisis",
    "covid_recession",
    "euro_debt_slowdown",
    "late_cycle_2018",
)


def summarize_aggregation_rule_leakage() -> dict[str, Any]:
    """Scan aggregation rules for scenario labels and tuning leakage."""

    texts = {path: _sanitized_text(path) for path in AUDITED_PATHS if path.exists()}
    combined = "\n".join(texts.values()).lower()
    scenario_refs = sum(combined.count(scenario) for scenario in SCENARIO_IDS)
    date_refs = len(re.findall(r"\b(?:19|20)\d{2}-\d{2}-\d{2}\b", combined))
    expected_refs = combined.count("expected_phase") + combined.count(
        "historical_outcome"
    )
    nber_refs = combined.count("nber")
    return_refs = combined.count("portfolio_return") + combined.count("total_return")
    branch_refs = combined.count("if scenario") + combined.count("scenario_id ==")
    historical_selection = combined.count("historical_label_rule_selection_allowed: true")
    return {
        "phase": "QA6",
        "aggregation_rule_leakage_guard_ready": scenario_refs == 0
        and date_refs == 0
        and expected_refs == 0
        and nber_refs == 0
        and return_refs == 0
        and branch_refs == 0
        and historical_selection == 0,
        "aggregation_rule_scenario_id_reference_count": scenario_refs,
        "aggregation_rule_historical_date_reference_count": date_refs,
        "aggregation_rule_expected_label_reference_count": expected_refs,
        "aggregation_rule_nber_reference_count": nber_refs,
        "aggregation_rule_return_metric_reference_count": return_refs,
        "aggregation_rule_scenario_branch_count": branch_refs,
        "historical_result_used_for_rule_selection_count": historical_selection,
        "audited_path_count": len(texts),
    }


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _sanitized_text(path: Path) -> str:
    text = _read(path)
    if path.name == "shadow_aggregation_rule_contract.yaml":
        for allowed_declaration in (
            "expected_historical_phase",
            "historical_outcome_labels",
            "nber_labels",
            "portfolio_returns",
        ):
            text = text.replace(allowed_declaration, "")
    return text

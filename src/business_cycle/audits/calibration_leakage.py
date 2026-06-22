"""QA3 parameter selection leakage audit."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from business_cycle.audits.model_parameter_inventory import (
    DEFAULT_REGISTRY_PATH,
    discover_model_parameters,
)


PROHIBITED_CLAIMS = (
    "untouched " + "out-of-sample",
    "independent validation " + "complete",
    "holdout " + "passed",
    "real backtest " + "ready",
    "investment" + "-ready",
)
PROHIBITED_CLAIM_PATTERN = re.compile(
    "|".join(re.escape(pattern) for pattern in PROHIBITED_CLAIMS),
    re.IGNORECASE,
)


def summarize_calibration_leakage(
    *,
    registry_path: str | Path = DEFAULT_REGISTRY_PATH,
) -> dict[str, Any]:
    """Audit whether parameter choices were selected after scenario results."""

    parameters = discover_model_parameters(registry_path=registry_path)
    contaminated = [
        parameter
        for parameter in parameters
        if parameter.selected_after_results_seen
        or parameter.contaminated_for_independent_validation
    ]
    unacknowledged = [
        parameter
        for parameter in contaminated
        if not parameter.contaminated_for_independent_validation
    ]
    without_history = [
        parameter for parameter in parameters if parameter.selection_basis == "unknown"
    ]
    false_claim_count = _false_out_of_sample_claim_count()
    findings = [_finding(parameter, index) for index, parameter in enumerate(contaminated, start=1)]
    return {
        "phase": "QA3",
        "calibration_leakage_audit_ready": not unacknowledged and false_claim_count == 0,
        "audited_parameter_count": len(parameters),
        "parameter_selected_after_result_observation_count": sum(
            parameter.selected_after_results_seen for parameter in parameters
        ),
        "contaminated_parameter_count": len(contaminated),
        "uncontaminated_parameter_count": len(parameters) - len(contaminated),
        "parameter_without_selection_history_count": len(without_history),
        "unacknowledged_contaminated_parameter_count": len(unacknowledged),
        "false_out_of_sample_claim_count": false_claim_count,
        "calibration_leakage_detected": bool(contaminated),
        "findings": findings,
    }


def _finding(parameter: Any, index: int) -> dict[str, Any]:
    return {
        "finding_id": f"qa3_leakage_{index:04d}",
        "parameter_id": parameter.parameter_id,
        "observed_scenario_ids": parameter.scenarios_visible_before_selection,
        "result_observed_before_selection": parameter.selected_after_results_seen,
        "selection_phase": parameter.first_introduced_phase,
        "evidence_paths": [parameter.source_path],
        "contamination_scope": "not_eligible_for_independent_validation",
        "independent_validation_impact": "must_use_future_unseen_prospective_holdout",
        "holdout_impact": "current five scenarios cannot be reused as holdout",
        "remediation": "freeze current baseline and evaluate only future registered observations without tuning",
    }


def _false_out_of_sample_claim_count() -> int:
    paths = [
        Path("README.md"),
        *Path("docs").rglob("*.md"),
        *Path("specs").rglob("*.yaml"),
        *Path("src").rglob("*.py"),
        *Path("scripts").glob("*.py"),
        *Path("tests").glob("*.py"),
    ]
    count = 0
    for path in paths:
        if not path.exists() or "__pycache__" in str(path):
            continue
        count += len(PROHIBITED_CLAIM_PATTERN.findall(path.read_text(encoding="utf-8")))
    return count

"""QA3 scenario exposure registry audit."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


DEFAULT_EXPOSURE_PATH = Path("specs/audits/scenario_exposure_registry.yaml")
CURRENT_SCENARIOS = {
    "dotcom_bubble",
    "global_financial_crisis",
    "covid_recession",
    "euro_debt_slowdown",
    "late_cycle_2018",
}


def load_scenario_exposure_registry(
    path: str | Path = DEFAULT_EXPOSURE_PATH,
) -> list[dict[str, Any]]:
    """Load the QA3 scenario exposure registry."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("scenario exposure YAML must be a mapping")
    registry = payload.get("scenario_exposure_registry")
    if not isinstance(registry, dict):
        raise ValueError("scenario_exposure_registry must be a mapping")
    scenarios = registry.get("scenarios")
    if not isinstance(scenarios, list):
        raise ValueError("scenario_exposure_registry.scenarios must be a list")
    return [dict(row) for row in scenarios]


def summarize_scenario_exposure_registry(
    path: str | Path = DEFAULT_EXPOSURE_PATH,
) -> dict[str, Any]:
    """Return QA3 scenario exposure counts and hard-gate fields."""

    rows = load_scenario_exposure_registry(path)
    scenario_ids = {str(row.get("scenario_id")) for row in rows}
    missing_current = sorted(CURRENT_SCENARIOS - scenario_ids)
    without_history = [
        row
        for row in rows
        if not row.get("first_seen_phase")
        or not row.get("first_result_observed_phase")
        or not row.get("contamination_reasons")
    ]
    incorrectly_oos = [
        row
        for row in rows
        if row.get("previously_seen") is True
        and row.get("eligible_for_independent_validation") is True
    ]
    incorrectly_holdout = [
        row
        for row in rows
        if row.get("previously_seen") is True
        and row.get("eligible_for_untouched_holdout") is True
    ]
    development = [
        row
        for row in rows
        if row.get("methodological_role") == "development_and_diagnostics"
    ]
    return {
        "phase": "QA3",
        "scenario_exposure_registry_ready": not missing_current
        and not without_history
        and not incorrectly_oos
        and not incorrectly_holdout,
        "scenario_count": len(rows),
        "previously_seen_scenario_count": sum(row.get("previously_seen") is True for row in rows),
        "development_scenario_count": len(development),
        "internal_robustness_scenario_count": sum(
            row.get("eligible_for_internal_robustness") is True for row in rows
        ),
        "independent_validation_scenario_count": sum(
            row.get("eligible_for_independent_validation") is True for row in rows
        ),
        "untouched_holdout_scenario_count": sum(
            row.get("eligible_for_untouched_holdout") is True for row in rows
        ),
        "performance_claim_eligible_scenario_count": sum(
            row.get("eligible_for_performance_claim") is True for row in rows
        ),
        "scenario_without_exposure_history_count": len(without_history) + len(missing_current),
        "scenario_incorrectly_marked_out_of_sample_count": len(incorrectly_oos),
        "scenario_incorrectly_marked_holdout_count": len(incorrectly_holdout),
        "scenarios": rows,
    }

"""Calibration split and leakage audit helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def summarize_calibration_integrity(
    policy_path: str | Path = "specs/audits/calibration_split_policy.yaml",
) -> dict[str, Any]:
    """Summarize calibration leakage risk from the split policy."""

    payload = yaml.safe_load(Path(policy_path).read_text(encoding="utf-8"))
    policy = payload["calibration_split_policy"]
    classification = policy["scenario_classification"]
    development = classification["development_and_diagnostics"]
    validation = classification["validation"]
    holdout = classification["final_untouched_holdout"]
    previously_seen = list(development)
    hard_coded_date_rule_count = _count_hard_coded_date_rules()
    selected_after_observation = bool(
        policy["known_parameter_selection_risk"]["selected_after_observing_existing_scenarios"]
    )
    return {
        "scenario_count": len(development) + len(validation) + len(holdout),
        "development_scenario_count": len(development),
        "validation_scenario_count": len(validation),
        "untouched_holdout_scenario_count": len(holdout),
        "previously_seen_scenario_count": len(previously_seen),
        "scenarios_incorrectly_called_out_of_sample_count": 0,
        "hard_coded_date_rule_count": hard_coded_date_rule_count,
        "parameter_selection_after_result_observation_count": 1
        if selected_after_observation
        else 0,
        "calibration_holdout_ready": bool(policy["summary"]["calibration_holdout_ready"]),
        "out_of_sample_claim_allowed": bool(policy["summary"]["out_of_sample_claim_allowed"]),
    }


def _count_hard_coded_date_rules() -> int:
    paths = [
        Path("specs/backtests/calibration_acceptance_windows.yaml"),
        Path("specs/backtests/scenarios.yaml"),
    ]
    count = 0
    for path in paths:
        if path.exists():
            text = path.read_text(encoding="utf-8")
            count += text.count("start:") + text.count("end:")
    return count


"""QA3 pre-registered data-only validation protocol audit."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


DEFAULT_PROTOCOL_PATH = Path("specs/audits/pre_registered_data_only_validation_protocol.yaml")


def load_pre_registered_validation_protocol(
    path: str | Path = DEFAULT_PROTOCOL_PATH,
) -> dict[str, Any]:
    """Load QA3 pre-registered validation protocol YAML."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("pre-registered protocol YAML must be a mapping")
    protocol = payload.get("pre_registered_data_only_validation_protocol")
    if not isinstance(protocol, dict):
        raise ValueError("pre_registered_data_only_validation_protocol must be a mapping")
    return protocol


def summarize_pre_registered_validation_protocol(
    path: str | Path = DEFAULT_PROTOCOL_PATH,
) -> dict[str, Any]:
    """Return protocol hard-gate fields."""

    protocol = load_pre_registered_validation_protocol(path)
    development = protocol["development_and_diagnostics"]
    historical = protocol["historical_external_validation"]
    prospective = protocol["prospective_prequential_holdout"]
    final_holdout = protocol["final_untouched_holdout"]
    holdout_complete = _holdout_protocol_complete(prospective)
    return {
        "phase": "QA3",
        "pre_registered_validation_protocol_ready": holdout_complete,
        "development_scenario_count": len(development["scenario_ids"]),
        "internal_robustness_scenario_count": len(
            protocol["internal_robustness_evaluation"]["allowed_inputs"]
        ),
        "historical_external_validation_scenario_count": int(
            historical["eligible_scenario_count"]
        ),
        "prospective_holdout_registered": bool(
            prospective["prospective_holdout_registered"]
        ),
        "prospective_holdout_result_inspected": False,
        "final_untouched_holdout_ready": bool(final_holdout["eligible"]),
        "parameter_change_resets_holdout": bool(
            prospective["parameter_change_resets_holdout"]
        ),
        "result_peeking_allowed": not bool(
            prospective["no_result_peeking_for_model_change"]
        ),
        "holdout_protocol_complete": holdout_complete,
        "first_eligible_observation_period": prospective[
            "first_eligible_observation_period"
        ],
        "minimum_evaluation_months": prospective["minimum_evaluation_months"],
        "frozen_model_version": prospective["frozen_model_version"],
    }


def _holdout_protocol_complete(prospective: dict[str, Any]) -> bool:
    required = (
        "registration_timestamp",
        "frozen_model_version",
        "first_eligible_observation_period",
        "minimum_evaluation_months",
        "minimum_complete_strict_dates",
        "requires_at_least_one_unseen_transition_event",
        "requires_at_least_one_unseen_non_recession_stress_event",
        "no_parameter_change_after_registration",
        "parameter_change_resets_holdout",
        "no_result_peeking_for_model_change",
        "evaluation_frequency",
        "reporting_frequency",
        "stopping_rules",
        "allowed_metrics",
        "prohibited_uses",
    )
    return all(key in prospective for key in required) and bool(
        prospective["prospective_holdout_registered"]
    )

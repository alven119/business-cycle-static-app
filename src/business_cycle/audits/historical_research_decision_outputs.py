"""Phase 25 research decision output registry audit."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.validation.historical_research_decision_outputs import (
    summarize_historical_research_decision_outputs,
)


DEFAULT_RESEARCH_DECISION_OUTPUT_REGISTRY_PATH = Path(
    "specs/audits/historical_research_decision_output_registry.yaml"
)


def load_historical_research_decision_output_registry(
    path: str | Path = DEFAULT_RESEARCH_DECISION_OUTPUT_REGISTRY_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("historical research decision output registry must map")
    registry = payload.get("historical_research_decision_output_registry")
    if not isinstance(registry, dict):
        raise ValueError("historical_research_decision_output_registry must map")
    return registry


def summarize_historical_research_decision_output_registry(
    path: str | Path = DEFAULT_RESEARCH_DECISION_OUTPUT_REGISTRY_PATH,
) -> dict[str, Any]:
    registry = load_historical_research_decision_output_registry(path)
    outputs = summarize_historical_research_decision_outputs()
    expected = registry["expected_counters"]
    storage = registry["storage_policy"]
    prohibited_runtime = registry["prohibited_runtime_usage"]
    ready = (
        registry["registry_status"]
        == "research_outputs_generated_no_predicted_labels_or_metrics"
        and outputs["research_decision_output_artifact_contract_ready"] is True
        and outputs["research_decision_output_runtime_ready"] is True
        and all(outputs[key] == value for key, value in expected.items())
        and storage["committed_artifacts_allowed"] is False
        and storage["tmp_artifacts_allowed"] is True
        and storage["data_backtests_write_allowed"] is False
        and storage["data_prospective_write_allowed"] is False
        and storage["public_output_allowed"] is False
        and prohibited_runtime["label_runtime_usage_allowed"] is False
        and prohibited_runtime["formal_decision_model_enabled"] is False
        and prohibited_runtime["candidate_model_enabled"] is False
    )
    return {
        "phase": "25",
        "registry_id": registry["registry_id"],
        "registry_version": registry["registry_version"],
        "research_decision_output_registry_ready": ready,
        "research_decision_output_artifact_contract_ready": outputs[
            "research_decision_output_artifact_contract_ready"
        ],
        "research_decision_output_runtime_ready": outputs[
            "research_decision_output_runtime_ready"
        ],
        **{key: outputs[key] for key in expected},
        "numeric_weight_added_count": outputs["numeric_weight_added_count"],
        "arbitrary_threshold_added_count": outputs[
            "arbitrary_threshold_added_count"
        ],
        "role_count_voting_added_count": outputs["role_count_voting_added_count"],
        "historical_tuning_leakage_count": outputs[
            "historical_tuning_leakage_count"
        ],
        "committed_artifacts_allowed": storage["committed_artifacts_allowed"],
        "data_backtests_write_allowed": storage["data_backtests_write_allowed"],
        "data_prospective_write_allowed": storage[
            "data_prospective_write_allowed"
        ],
        "public_output_allowed": storage["public_output_allowed"],
        "outputs": outputs,
        "registry": registry,
    }

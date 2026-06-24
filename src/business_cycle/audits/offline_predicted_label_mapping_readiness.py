"""Phase 26 offline predicted-label mapping readiness audit."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.validation.offline_predicted_label_mapping_contract import (
    summarize_offline_predicted_label_mapping_contract,
)


DEFAULT_OFFLINE_PREDICTED_LABEL_MAPPING_READINESS_PATH = Path(
    "specs/audits/offline_predicted_label_mapping_readiness.yaml"
)


def load_offline_predicted_label_mapping_readiness(
    path: str | Path = DEFAULT_OFFLINE_PREDICTED_LABEL_MAPPING_READINESS_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("offline predicted label mapping readiness must map")
    readiness = payload.get("offline_predicted_label_mapping_readiness")
    if not isinstance(readiness, dict):
        raise ValueError("offline_predicted_label_mapping_readiness must be a mapping")
    return readiness


def summarize_offline_predicted_label_mapping_readiness(
    path: str | Path = DEFAULT_OFFLINE_PREDICTED_LABEL_MAPPING_READINESS_PATH,
) -> dict[str, Any]:
    readiness = load_offline_predicted_label_mapping_readiness(path)
    contract = summarize_offline_predicted_label_mapping_contract()
    expected = readiness["expected_counters"]
    storage = readiness["storage_policy"]
    prohibited_runtime = readiness["prohibited_runtime_usage"]
    expected_without_self = {
        key: value
        for key, value in expected.items()
        if key != "predicted_label_mapping_readiness_ready"
    }
    ready = (
        readiness["readiness_status"] == "ready_no_predicted_label_emission"
        and contract["predicted_label_mapping_contract_ready"] is True
        and contract["research_decision_state_taxonomy_ready"] is True
        and contract["offline_predicted_label_taxonomy_ready"] is True
        and contract["mapping_rule_count"] > 0
        and all(contract[key] == value for key, value in expected_without_self.items())
        and storage["committed_predicted_label_artifacts_allowed"] is False
        and storage["tmp_predicted_label_artifacts_allowed"] is False
        and storage["data_backtests_write_allowed"] is False
        and storage["data_prospective_write_allowed"] is False
        and storage["public_output_allowed"] is False
        and prohibited_runtime["label_runtime_usage_allowed"] is False
        and prohibited_runtime["label_comparison_execution_allowed"] is False
        and prohibited_runtime["formal_decision_model_enabled"] is False
        and prohibited_runtime["candidate_model_enabled"] is False
        and prohibited_runtime["production_integration_allowed"] is False
    )
    return {
        "phase": "26",
        "readiness_id": readiness["readiness_id"],
        "readiness_version": readiness["readiness_version"],
        "predicted_label_mapping_contract_ready": contract[
            "predicted_label_mapping_contract_ready"
        ],
        "predicted_label_mapping_readiness_ready": ready,
        "research_decision_state_taxonomy_ready": contract[
            "research_decision_state_taxonomy_ready"
        ],
        "offline_predicted_label_taxonomy_ready": contract[
            "offline_predicted_label_taxonomy_ready"
        ],
        "mapping_rule_count": contract["mapping_rule_count"],
        **{key: contract[key] for key in expected_without_self},
        "numeric_weight_added_count": contract["numeric_weight_added_count"],
        "arbitrary_threshold_added_count": contract[
            "arbitrary_threshold_added_count"
        ],
        "role_count_voting_added_count": contract["role_count_voting_added_count"],
        "historical_tuning_leakage_count": contract[
            "historical_tuning_leakage_count"
        ],
        "committed_predicted_label_artifacts_allowed": storage[
            "committed_predicted_label_artifacts_allowed"
        ],
        "tmp_predicted_label_artifacts_allowed": storage[
            "tmp_predicted_label_artifacts_allowed"
        ],
        "data_backtests_write_allowed": storage["data_backtests_write_allowed"],
        "data_prospective_write_allowed": storage[
            "data_prospective_write_allowed"
        ],
        "public_output_allowed": storage["public_output_allowed"],
        "contract": contract,
        "readiness": readiness,
    }

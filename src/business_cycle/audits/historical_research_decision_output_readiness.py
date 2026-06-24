"""Phase 24 research decision output readiness audit."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.validation.historical_research_decision_output_contract import (
    summarize_historical_research_decision_output_contract,
)


DEFAULT_RESEARCH_DECISION_OUTPUT_READINESS_PATH = Path(
    "specs/audits/historical_research_decision_output_readiness.yaml"
)


def load_historical_research_decision_output_readiness(
    path: str | Path = DEFAULT_RESEARCH_DECISION_OUTPUT_READINESS_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("historical research decision output readiness must map")
    readiness = payload.get("historical_research_decision_output_readiness")
    if not isinstance(readiness, dict):
        raise ValueError(
            "historical_research_decision_output_readiness must be a mapping"
        )
    return readiness


def summarize_historical_research_decision_output_readiness(
    path: str | Path = DEFAULT_RESEARCH_DECISION_OUTPUT_READINESS_PATH,
) -> dict[str, Any]:
    readiness = load_historical_research_decision_output_readiness(path)
    contract = summarize_historical_research_decision_output_contract()
    expected = readiness["expected_counters"]
    storage = readiness["storage_policy"]
    prohibited_runtime = readiness["prohibited_runtime_usage"]
    expected_without_self = {
        key: value
        for key, value in expected.items()
        if key != "research_decision_output_readiness_ready"
    }
    ready = (
        readiness["readiness_status"] == "ready_no_output_emission"
        and contract["research_decision_output_contract_ready"] is True
        and contract["output_taxonomy_ready"] is True
        and all(contract[key] == value for key, value in expected_without_self.items())
        and storage["committed_decision_outputs_allowed"] is False
        and storage["tmp_preview_outputs_allowed"] is False
        and storage["data_backtests_write_allowed"] is False
        and storage["data_prospective_write_allowed"] is False
        and storage["public_output_allowed"] is False
        and prohibited_runtime["label_runtime_usage_allowed"] is False
        and prohibited_runtime["formal_decision_model_enabled"] is False
        and prohibited_runtime["candidate_model_enabled"] is False
    )
    return {
        "phase": "24",
        "readiness_id": readiness["readiness_id"],
        "readiness_version": readiness["readiness_version"],
        "research_decision_output_contract_ready": contract[
            "research_decision_output_contract_ready"
        ],
        "research_decision_output_readiness_ready": ready,
        "output_taxonomy_ready": contract["output_taxonomy_ready"],
        **{key: contract[key] for key in expected_without_self},
        "numeric_weight_added_count": contract["numeric_weight_added_count"],
        "arbitrary_threshold_added_count": contract[
            "arbitrary_threshold_added_count"
        ],
        "role_count_voting_added_count": contract["role_count_voting_added_count"],
        "historical_tuning_leakage_count": contract[
            "historical_tuning_leakage_count"
        ],
        "committed_decision_outputs_allowed": storage[
            "committed_decision_outputs_allowed"
        ],
        "data_backtests_write_allowed": storage["data_backtests_write_allowed"],
        "data_prospective_write_allowed": storage[
            "data_prospective_write_allowed"
        ],
        "public_output_allowed": storage["public_output_allowed"],
        "contract": contract,
        "readiness": readiness,
    }

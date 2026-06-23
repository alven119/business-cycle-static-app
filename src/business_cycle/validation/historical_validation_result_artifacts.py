"""Phase 19 future result artifact schema preregistration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


DEFAULT_RESULT_ARTIFACT_CONTRACT_PATH = Path(
    "specs/audits/historical_validation_result_artifact_contract.yaml"
)


def load_historical_validation_result_artifact_contract(
    path: str | Path = DEFAULT_RESULT_ARTIFACT_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("historical validation result artifact contract must map")
    contract = payload.get("historical_validation_result_artifact_contract")
    if not isinstance(contract, dict):
        raise ValueError(
            "historical_validation_result_artifact_contract must be a mapping"
        )
    return contract


def summarize_historical_validation_result_artifacts(
    path: str | Path = DEFAULT_RESULT_ARTIFACT_CONTRACT_PATH,
) -> dict[str, Any]:
    contract = load_historical_validation_result_artifact_contract(path)
    counters = contract["counters"]
    policy = contract["output_artifact_policy"]
    forbidden_output_field_count = _forbidden_output_field_count(
        contract["schema_fields"],
        contract["forbidden_outputs"],
    )
    ready = (
        contract["contract_status"] == "schema_preregistered_no_artifact_created"
        and policy["artifact_creation_allowed_this_phase"] is False
        and policy["data_backtests_write_allowed"] is False
        and policy["data_prospective_write_allowed"] is False
        and policy["public_output_allowed"] is False
        and policy["result_inspection_allowed"] is False
        and counters["historical_validation_result_count"] == 0
        and counters["forbidden_output_field_count"] == 0
        and counters["artifact_written_count"] == 0
        and counters["metric_field_enabled_count"] == 0
        and counters["candidate_or_current_phase_field_count"] == 0
        and forbidden_output_field_count == 0
    )
    return {
        "phase": "19",
        "contract_id": contract["contract_id"],
        "contract_version": contract["contract_version"],
        "result_artifact_contract_ready": ready,
        "historical_validation_result_count": counters[
            "historical_validation_result_count"
        ],
        "forbidden_output_field_count": forbidden_output_field_count,
        "artifact_written_count": counters["artifact_written_count"],
        "metric_field_enabled_count": counters["metric_field_enabled_count"],
        "candidate_or_current_phase_field_count": counters[
            "candidate_or_current_phase_field_count"
        ],
        "contract": contract,
    }


def _forbidden_output_field_count(
    payload: Any,
    forbidden_outputs: list[str],
) -> int:
    forbidden = set(forbidden_outputs)
    return len(forbidden.intersection(_all_keys(payload)))


def _all_keys(value: Any) -> set[str]:
    if isinstance(value, dict):
        keys = set(value)
        for item in value.values():
            keys.update(_all_keys(item))
        return keys
    if isinstance(value, list):
        keys: set[str] = set()
        for item in value:
            keys.update(_all_keys(item))
        return keys
    return set()

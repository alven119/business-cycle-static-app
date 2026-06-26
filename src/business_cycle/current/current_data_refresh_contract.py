"""Phase 40 controlled current data refresh contract."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml


DEFAULT_CONTRACT_PATH = Path("specs/common/current_data_refresh_contract.yaml")


@lru_cache(maxsize=1)
def load_current_data_refresh_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    contract = payload.get("current_data_refresh_contract")
    if not isinstance(contract, dict):
        raise ValueError("current_data_refresh_contract must be a mapping")
    return contract


def summarize_current_data_refresh_contract() -> dict[str, Any]:
    contract = load_current_data_refresh_contract()
    gates = contract["readiness_gates"]
    summary = {
        "phase": "40",
        "contract_id": contract["contract_id"],
        "contract_version": contract["contract_version"],
        "supported_provider_family_count": len(
            contract["supported_provider_families"]
        ),
        "required_environment_variable_count": len(
            contract["required_environment_variables"]
        ),
        "allowed_output_location_count": len(contract["allowed_output_locations"]),
        "forbidden_output_location_count": len(
            contract["forbidden_output_locations"]
        ),
        "current_data_refresh_contract_ready": _contract_ready(contract),
        "ci_requires_network": gates["ci_requires_network"],
        "ci_requires_fred_key": gates["ci_requires_fred_key"],
        "live_fetch_allowed_only_when_key_present": gates[
            "live_fetch_allowed_only_when_key_present"
        ],
        "raw_data_commit_forbidden": gates["raw_data_commit_forbidden"],
        "secret_redaction_required": gates["secret_redaction_required"],
        "revised_data_labeled_as_revised": gates[
            "revised_data_labeled_as_revised"
        ],
        "point_in_time_not_claimed_for_latest_revised": gates[
            "point_in_time_not_claimed_for_latest_revised"
        ],
        "contract": contract,
    }
    return summary


def _contract_ready(contract: dict[str, Any]) -> bool:
    gates = contract.get("readiness_gates", {})
    return (
        bool(contract.get("supported_provider_families"))
        and bool(contract.get("required_environment_variables"))
        and gates.get("current_data_refresh_contract_ready") is True
        and gates.get("ci_requires_network") is False
        and gates.get("ci_requires_fred_key") is False
        and gates.get("live_fetch_allowed_only_when_key_present") is True
        and gates.get("raw_data_commit_forbidden") is True
        and gates.get("secret_redaction_required") is True
        and gates.get("revised_data_labeled_as_revised") is True
        and gates.get("point_in_time_not_claimed_for_latest_revised") is True
    )

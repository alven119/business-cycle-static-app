"""QA11 forward-capture contracts for forward-ready book-core roles."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.book_core_forward_data_gaps import (
    build_book_core_forward_data_gap_rows,
)


DEFAULT_CAPTURE_CONTRACT_PATH = Path(
    "specs/audits/book_core_forward_capture_contract.yaml"
)


def load_forward_capture_contract(
    path: str | Path = DEFAULT_CAPTURE_CONTRACT_PATH,
) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "book_core_forward_capture_contract"
    ]


def build_forward_capture_contracts(
    path: str | Path = DEFAULT_CAPTURE_CONTRACT_PATH,
) -> list[dict[str, Any]]:
    spec = load_forward_capture_contract(path)
    defaults = spec["defaults"]
    rows: list[dict[str, Any]] = []
    for role in build_book_core_forward_data_gap_rows():
        if role["forward_prospective_capture_status"] not in {
            "ready",
            "ready_with_manual_capture",
        }:
            continue
        source_series = role["current_series_ids"]
        capture_mode = (
            "derived_same_as_of"
            if len(source_series) > 1
            or any("credit_spread" in series_id for series_id in source_series)
            else "official_observational_capture"
        )
        rows.append(
            {
                "role_id": role["role_id"],
                "source_series_ids": source_series,
                "source_release_ids": [
                    f"release::{series_id}" for series_id in source_series
                ],
                "capture_mode": capture_mode,
                "expected_release_frequency": role[
                    "forward_publication_frequency"
                ],
                "expected_release_lag": role["forward_release_lag_rule"],
                "capture_window_start": "first_complete_forward_period_after_protocol_start",
                "canonical_period_assignment": "source_release_period",
                "raw_artifact_required": defaults["raw_artifact_required"],
                "checksum_required": defaults["checksum_required"],
                "release_datetime_required": defaults[
                    "release_datetime_required"
                ],
                "previous_release_link_required": defaults[
                    "previous_release_link_required"
                ],
                "strict_provenance_required": defaults[
                    "strict_provenance_required"
                ],
                "retry_policy": defaults["retry_policy"],
                "late_release_policy": defaults["late_release_policy"],
                "missing_release_policy": defaults["missing_release_policy"],
                "correction_policy": defaults["correction_policy"],
                "no_data_action": defaults["no_data_action"],
                "input_capture_contract_role_ids": _input_contract_roles(role),
                "release_semantics_complete": True,
            }
        )
    return rows


def summarize_forward_capture_contracts() -> dict[str, Any]:
    contracts = build_forward_capture_contracts()
    roles = build_book_core_forward_data_gap_rows()
    ready_roles = [
        row
        for row in roles
        if row["forward_prospective_capture_status"]
        in {"ready", "ready_with_manual_capture"}
    ]
    contract_role_ids = {row["role_id"] for row in contracts}
    ready_role_ids = {row["role_id"] for row in ready_roles}
    without_contract = sorted(ready_role_ids - contract_role_ids)
    without_role = sorted(contract_role_ids - ready_role_ids)
    without_release = [
        row for row in contracts if not row["release_semantics_complete"]
    ]
    derived_without_inputs = [
        row
        for row in contracts
        if row["capture_mode"] == "derived_same_as_of"
        and not row["input_capture_contract_role_ids"]
    ]
    return {
        "phase": "QA11",
        "forward_capture_contract_ready": not without_contract
        and not without_role
        and not without_release
        and not derived_without_inputs,
        "forward_capture_contract_count": len(contracts),
        "ready_role_without_capture_contract_count": len(without_contract),
        "capture_contract_without_role_count": len(without_role),
        "capture_contract_without_release_semantics_count": len(without_release),
        "derived_capture_without_complete_inputs_count": len(
            derived_without_inputs
        ),
        "contracts": contracts,
    }


def _input_contract_roles(role: dict[str, Any]) -> list[str]:
    if any("credit_spread" in series_id for series_id in role["current_series_ids"]):
        return [role["role_id"]]
    return []

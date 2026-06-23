"""Phase 18 scenario input requirement audit."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.validation.historical_validation_manifest import (
    summarize_historical_validation_manifest,
)


DEFAULT_SCENARIO_INPUT_PATH = Path(
    "specs/audits/historical_validation_scenario_input_requirements.yaml"
)


def load_historical_validation_scenario_input_requirements(
    path: str | Path = DEFAULT_SCENARIO_INPUT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("historical validation scenario inputs must be a mapping")
    requirements = payload.get("historical_validation_scenario_input_requirements")
    if not isinstance(requirements, dict):
        raise ValueError(
            "historical_validation_scenario_input_requirements must be a mapping"
        )
    return requirements


def summarize_historical_validation_scenario_inputs(
    path: str | Path = DEFAULT_SCENARIO_INPUT_PATH,
) -> dict[str, Any]:
    requirements = load_historical_validation_scenario_input_requirements(path)
    manifest = summarize_historical_validation_manifest()
    rows = requirements["scenario_input_rows"]
    scenario_ids = {row["scenario_id"] for row in rows}
    manifest_ids = {
        row["scenario_id"]
        for row in manifest["scenario_manifest"]["scenario_rows"]
    }
    counters = requirements["counters"]
    scenario_with_complete_input_contract_count = sum(
        set(row["required_inputs"]) == set(row["available_inputs"])
        and not row["unavailable_inputs"]
        and set(row["required_vintages"]) == set(row["available_vintages"])
        and not row["missing_vintages"]
        and row["label_provenance_status"] == "complete"
        for row in rows
    )
    total_required_input_count = sum(len(row["required_inputs"]) for row in rows)
    total_available_input_count = sum(len(row["available_inputs"]) for row in rows)
    total_missing_input_count = sum(
        len(set(row["required_inputs"]).difference(row["available_inputs"]))
        for row in rows
    )
    total_unavailable_input_count = sum(
        len(row["unavailable_inputs"]) for row in rows
    )
    total_required_vintage_count = sum(len(row["required_vintages"]) for row in rows)
    total_available_vintage_count = sum(len(row["available_vintages"]) for row in rows)
    total_missing_vintage_count = sum(len(row["missing_vintages"]) for row in rows)
    ready = (
        requirements["requirements_status"]
        == "input_contracts_declared_no_model_execution"
        and manifest["historical_validation_scenario_manifest_ready"] is True
        and scenario_ids == manifest_ids
        and len(rows) == manifest["scenario_count"]
        and scenario_with_complete_input_contract_count == len(rows)
        and counters["scenario_with_complete_input_contract_count"] == len(rows)
        and counters["scenario_missing_input_contract_count"] == 0
        and counters["scenario_with_label_provenance_gap_count"] == 0
        and counters["forbidden_output_field_count"] == 0
        and counters["model_execution_count"] == 0
    )
    return {
        "phase": "18",
        "requirements_id": requirements["requirements_id"],
        "requirements_version": requirements["requirements_version"],
        "scenario_input_requirements_ready": ready,
        "scenario_count": len(rows),
        "scenario_id_mismatch_count": len(scenario_ids.symmetric_difference(manifest_ids)),
        "scenario_with_complete_input_contract_count": (
            scenario_with_complete_input_contract_count
        ),
        "scenario_missing_input_contract_count": counters[
            "scenario_missing_input_contract_count"
        ],
        "scenario_with_label_provenance_gap_count": counters[
            "scenario_with_label_provenance_gap_count"
        ],
        "total_required_input_count": total_required_input_count,
        "total_available_input_count": total_available_input_count,
        "total_missing_input_count": total_missing_input_count,
        "total_unavailable_input_count": total_unavailable_input_count,
        "total_required_vintage_count": total_required_vintage_count,
        "total_available_vintage_count": total_available_vintage_count,
        "total_missing_vintage_count": total_missing_vintage_count,
        "label_provenance_complete": (
            counters["scenario_with_label_provenance_gap_count"] == 0
        ),
        "forbidden_output_field_count": counters["forbidden_output_field_count"],
        "model_execution_count": counters["model_execution_count"],
        "requirements": requirements,
        "manifest": manifest,
    }

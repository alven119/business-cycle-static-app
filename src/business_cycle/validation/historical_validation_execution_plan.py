"""Phase 19 locked historical validation execution plan."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.validation.historical_validation_manifest import (
    summarize_historical_validation_manifest,
)


DEFAULT_EXECUTION_PLAN_PATH = Path(
    "specs/audits/historical_validation_execution_plan.yaml"
)


def load_historical_validation_execution_plan(
    path: str | Path = DEFAULT_EXECUTION_PLAN_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("historical validation execution plan must be a mapping")
    plan = payload.get("historical_validation_execution_plan")
    if not isinstance(plan, dict):
        raise ValueError("historical_validation_execution_plan must be a mapping")
    return plan


def summarize_historical_validation_execution_plan(
    path: str | Path = DEFAULT_EXECUTION_PLAN_PATH,
) -> dict[str, Any]:
    plan = load_historical_validation_execution_plan(path)
    manifest = summarize_historical_validation_manifest()
    rows = plan["scenario_plan_rows"]
    scenario_ids = {row["scenario_id"] for row in rows}
    manifest_ids = {
        row["scenario_id"]
        for row in manifest["scenario_manifest"]["scenario_rows"]
    }
    counters = plan["counters"]
    execution_allowed_plan_count = sum(
        row["execution_allowed_in_this_phase"] is True for row in rows
    )
    plan_without_required_input_artifacts_count = sum(
        not row["required_input_artifacts"] for row in rows
    )
    plan_without_required_label_artifacts_count = sum(
        not row["required_label_artifacts"] for row in rows
    )
    plan_without_required_freeze_ids_count = sum(
        not row["required_freeze_ids"] for row in rows
    )
    ready = (
        plan["plan_status"] == "locked_no_execution"
        and manifest["historical_validation_scenario_manifest_ready"] is True
        and scenario_ids == manifest_ids
        and len(rows) == manifest["scenario_count"]
        and counters["scenario_with_execution_plan_count"] == len(rows)
        and plan_without_required_input_artifacts_count == 0
        and plan_without_required_label_artifacts_count == 0
        and plan_without_required_freeze_ids_count == 0
        and execution_allowed_plan_count == 0
        and counters["execution_allowed_plan_count"] == 0
        and counters["model_execution_count"] == 0
        and counters["real_historical_validation_executed"] is False
        and counters["historical_validation_result_count"] == 0
        and plan["execution_allowed_in_this_phase"] is False
    )
    return {
        "phase": "19",
        "plan_id": plan["plan_id"],
        "plan_version": plan["plan_version"],
        "historical_validation_execution_plan_ready": ready,
        "scenario_count": len(rows),
        "scenario_id_mismatch_count": len(scenario_ids.symmetric_difference(manifest_ids)),
        "scenario_with_execution_plan_count": counters[
            "scenario_with_execution_plan_count"
        ],
        "plan_without_required_input_artifacts_count": (
            plan_without_required_input_artifacts_count
        ),
        "plan_without_required_label_artifacts_count": (
            plan_without_required_label_artifacts_count
        ),
        "plan_without_required_freeze_ids_count": (
            plan_without_required_freeze_ids_count
        ),
        "execution_allowed_in_this_phase": plan["execution_allowed_in_this_phase"],
        "execution_allowed_plan_count": execution_allowed_plan_count,
        "model_execution_count": counters["model_execution_count"],
        "real_historical_validation_executed": counters[
            "real_historical_validation_executed"
        ],
        "historical_validation_result_count": counters[
            "historical_validation_result_count"
        ],
        "plan": plan,
        "manifest": manifest,
    }

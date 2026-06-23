"""Phase 19 historical validation execution readiness gate."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.validation.economic_validation_protocol import (
    summarize_economic_validation_protocol,
)
from business_cycle.validation.historical_validation_execution_plan import (
    summarize_historical_validation_execution_plan,
)
from business_cycle.validation.historical_validation_input_readiness import (
    summarize_historical_validation_input_readiness,
)
from business_cycle.validation.historical_validation_manifest import (
    summarize_historical_validation_manifest,
)
from business_cycle.validation.historical_validation_result_artifacts import (
    summarize_historical_validation_result_artifacts,
)
from business_cycle.validation.validation_harness import (
    summarize_validation_harness_dry_run,
)
from business_cycle.validation.validation_label_policy import (
    summarize_validation_label_policy,
)


DEFAULT_CONTRACT_PATH = Path(
    "specs/common/historical_validation_execution_readiness_contract.yaml"
)
DECISION_RUNTIME_FREEZE_PATH = Path(
    "specs/audits/book_faithful_shadow_v2_alpha10_non_emitting_decision_runtime_freeze.yaml"
)
FREEZE_PATHS = {
    "book_faithful_shadow_v2_alpha10": DECISION_RUNTIME_FREEZE_PATH,
    "book_faithful_shadow_v2_alpha11": Path(
        "specs/audits/book_faithful_shadow_v2_alpha11_validation_protocol_freeze.yaml"
    ),
    "book_faithful_shadow_v2_alpha12": Path(
        "specs/audits/book_faithful_shadow_v2_alpha12_validation_harness_freeze.yaml"
    ),
    "book_faithful_shadow_v2_alpha13": Path(
        "specs/audits/book_faithful_shadow_v2_alpha13_historical_manifest_freeze.yaml"
    ),
    "book_faithful_shadow_v2_alpha14": Path(
        "specs/audits/book_faithful_shadow_v2_alpha14_historical_input_readiness_freeze.yaml"
    ),
}
REQUIRED_CONTRACT_FIELDS = {
    "contract_id",
    "contract_version",
    "required_prior_freezes",
    "required_manifest_artifacts",
    "required_label_policy_artifacts",
    "required_input_readiness_artifacts",
    "required_validation_protocol_artifacts",
    "required_harness_artifacts",
    "required_decision_runtime_artifacts",
    "scenario_execution_plan",
    "allowed_data_modes",
    "prohibited_data_modes",
    "result_artifact_schema",
    "output_directory_policy",
    "no_execution_policy_for_this_phase",
    "metric_computation_policy",
    "backtest_execution_policy",
    "holdout_policy",
    "prospective_policy",
    "production_isolation_policy",
    "readiness_gates",
    "disabled_runtime_guards",
}


def load_historical_validation_execution_readiness_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("historical validation execution readiness contract must map")
    contract = payload.get("historical_validation_execution_readiness_contract")
    if not isinstance(contract, dict):
        raise ValueError(
            "historical_validation_execution_readiness_contract must be a mapping"
        )
    return contract


def summarize_historical_validation_execution_readiness(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    contract = load_historical_validation_execution_readiness_contract(path)
    manifest = summarize_historical_validation_manifest()
    label_policy = summarize_validation_label_policy()
    input_readiness = summarize_historical_validation_input_readiness()
    protocol = summarize_economic_validation_protocol()
    harness = summarize_validation_harness_dry_run()
    plan = summarize_historical_validation_execution_plan()
    result_artifact = summarize_historical_validation_result_artifacts()
    missing_fields = sorted(REQUIRED_CONTRACT_FIELDS.difference(contract))
    output = contract["output_restrictions"]
    guards = contract["disabled_runtime_guards"]
    prospective = contract["prospective_policy"]
    production = contract["production_isolation_policy"]
    prior_freeze_dependency_complete = all(
        FREEZE_PATHS[freeze_id].exists()
        for freeze_id in contract["required_prior_freezes"]
    )
    decision_runtime_dependency_complete = (
        DECISION_RUNTIME_FREEZE_PATH.exists()
        and "book_faithful_shadow_v2_alpha10"
        in contract["required_decision_runtime_artifacts"]
    )
    validation_protocol_dependency_complete = (
        protocol["economic_validation_protocol_ready"] is True
    )
    validation_harness_dependency_complete = (
        harness["validation_harness_runtime_ready"] is True
    )
    input_readiness_dependency_complete = (
        input_readiness["input_readiness_registry_ready"] is True
    )
    label_policy_dependency_complete = (
        label_policy["validation_label_policy_ready"] is True
    )
    no_execution = (
        contract["no_execution_policy_for_this_phase"][
            "execution_allowed_in_this_phase"
        ]
        is False
        and output["execution_allowed_in_this_phase"] is False
        and output["model_execution_count"] == 0
        and output["real_historical_validation_executed"] is False
        and output["historical_validation_result_count"] == 0
        and output["historical_accuracy_metric_count"] == 0
        and output["economic_performance_metric_count"] == 0
        and output["metric_computation_enabled"] is False
        and output["backtest_execution_enabled"] is False
        and output["holdout_registered"] is False
        and output["candidate_selection_enabled"] is False
        and output["candidate_phase_emitted"] is False
        and output["current_phase_emitted"] is False
        and prospective["prospective_registry_record_count"] == 0
        and prospective["prospective_registry_write_attempt_count"] == 0
    )
    ready = (
        not missing_fields
        and prior_freeze_dependency_complete
        and decision_runtime_dependency_complete
        and manifest["historical_validation_scenario_manifest_ready"] is True
        and label_policy_dependency_complete
        and input_readiness_dependency_complete
        and validation_protocol_dependency_complete
        and validation_harness_dependency_complete
        and plan["historical_validation_execution_plan_ready"] is True
        and result_artifact["result_artifact_contract_ready"] is True
        and no_execution
        and all(value is False for value in guards.values())
        and production["production_behavior_change_count"] == 0
    )
    return {
        "phase": "19",
        "contract_id": contract["contract_id"],
        "contract_version": contract["contract_version"],
        "historical_validation_execution_readiness_contract_ready": (
            not missing_fields
            and contract["readiness_gates"][
                "historical_validation_execution_readiness_contract_ready"
            ]
            is True
        ),
        "historical_validation_execution_plan_ready": plan[
            "historical_validation_execution_plan_ready"
        ],
        "result_artifact_contract_ready": result_artifact[
            "result_artifact_contract_ready"
        ],
        "scenario_count": plan["scenario_count"],
        "scenario_with_execution_plan_count": plan[
            "scenario_with_execution_plan_count"
        ],
        "prior_freeze_dependency_complete": prior_freeze_dependency_complete,
        "decision_runtime_dependency_complete": decision_runtime_dependency_complete,
        "validation_protocol_dependency_complete": (
            validation_protocol_dependency_complete
        ),
        "validation_harness_dependency_complete": (
            validation_harness_dependency_complete
        ),
        "input_readiness_dependency_complete": input_readiness_dependency_complete,
        "label_policy_dependency_complete": label_policy_dependency_complete,
        "execution_allowed_in_this_phase": output["execution_allowed_in_this_phase"],
        "missing_required_field_count": len(missing_fields),
        "model_execution_count": output["model_execution_count"],
        "real_historical_validation_executed": output[
            "real_historical_validation_executed"
        ],
        "historical_validation_result_count": output[
            "historical_validation_result_count"
        ],
        "historical_accuracy_metric_count": output[
            "historical_accuracy_metric_count"
        ],
        "economic_performance_metric_count": output[
            "economic_performance_metric_count"
        ],
        "metric_computation_enabled": output["metric_computation_enabled"],
        "backtest_execution_enabled": output["backtest_execution_enabled"],
        "holdout_registered": output["holdout_registered"],
        "candidate_selection_enabled": output["candidate_selection_enabled"],
        "candidate_phase_emitted": output["candidate_phase_emitted"],
        "current_phase_emitted": output["current_phase_emitted"],
        "production_behavior_change_count": production[
            "production_behavior_change_count"
        ],
        "prospective_registry_record_count": prospective[
            "prospective_registry_record_count"
        ],
        "real_registry_write_attempt_count": prospective[
            "prospective_registry_write_attempt_count"
        ],
        "numeric_weight_added_count": int(guards["numeric_weight_added"]),
        "arbitrary_threshold_added_count": int(guards["arbitrary_threshold_added"]),
        "role_count_voting_added_count": int(guards["role_count_voting_added"]),
        "historical_tuning_leakage_count": int(guards["historical_tuning_used"]),
        "execution_readiness_gate_ready": ready,
        "contract": contract,
        "manifest": manifest,
        "label_policy": label_policy,
        "input_readiness": input_readiness,
        "protocol": protocol,
        "harness": harness,
        "plan": plan,
        "result_artifact": result_artifact,
    }

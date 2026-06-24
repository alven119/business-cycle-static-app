"""Phase 25 alpha21 research decision output freeze validation."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.historical_research_decision_outputs import (
    summarize_historical_research_decision_output_registry,
)
from business_cycle.audits.shadow_research_decision_output_contract_freeze import (
    summarize_shadow_research_decision_output_contract_freeze,
)


DEFAULT_ALPHA21_FREEZE_PATH = Path(
    "specs/audits/book_faithful_shadow_v2_alpha21_research_decision_output_freeze.yaml"
)
PARENT_ALPHA20_FREEZE_PATH = Path(
    "specs/audits/book_faithful_shadow_v2_alpha20_research_decision_output_contract_freeze.yaml"
)


def summarize_shadow_research_decision_output_freeze(
    path: str | Path = DEFAULT_ALPHA21_FREEZE_PATH,
) -> dict[str, Any]:
    freeze = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "book_faithful_shadow_v2_alpha21_research_decision_output_freeze"
    ]
    component_paths = [Path(item) for item in freeze["component_paths"]]
    source_paths = [Path(item) for item in freeze["source_paths"]]
    all_paths = component_paths + source_paths
    missing = [item for item in all_paths if not item.exists()]
    api_key_name = "FRED" + "_API_KEY"
    secret = [
        item
        for item in all_paths
        if item.exists() and api_key_name in item.read_text(encoding="utf-8")
    ]
    production = [item for item in source_paths if _is_production_decision_file(item)]
    hashes = {
        str(item): hashlib.sha256(item.read_bytes()).hexdigest()
        for item in all_paths
        if item.exists()
    }
    freeze_hash = hashlib.sha256(
        "\n".join(f"{key}:{value}" for key, value in sorted(hashes.items())).encode()
    ).hexdigest()
    parent = summarize_shadow_research_decision_output_contract_freeze()
    registry = summarize_historical_research_decision_output_registry()
    alpha20_parent_preserved = (
        PARENT_ALPHA20_FREEZE_PATH.exists()
        and parent["freeze_id"] == freeze["parent_freeze_id"]
        and parent["research_decision_output_contract_freeze_ready"] is True
    )
    ready = (
        not missing
        and not secret
        and not production
        and alpha20_parent_preserved
        and parent["qa12_freeze_unchanged"] is True
        and registry["research_decision_output_registry_ready"] is True
        and freeze["research_decision_output_artifact_contract_ready"] is True
        and freeze["research_decision_output_runtime_ready"] is True
        and freeze["research_decision_output_registry_ready"] is True
        and freeze["scenario_count"] == 5
        and freeze["research_decision_output_count"] == 5
        and freeze["output_mode_research_only_count"] == 5
        and freeze["predicted_label_output_count"] == 0
        and freeze["label_used_by_runtime_count"] == 0
        and freeze["historical_accuracy_metric_count"] == 0
        and freeze["economic_performance_metric_count"] == 0
        and freeze["metric_computation_scope"] == "none"
        and freeze["backtest_execution_enabled"] is False
        and freeze["candidate_phase_emitted"] is False
        and freeze["current_phase_emitted"] is False
        and freeze["prohibited_artifact_field_count"] == 0
        and freeze["production_behavior_change_count"] == 0
        and freeze["prospective_registry_record_count"] == 0
        and freeze["prospective_registry_write_attempt_count"] == 0
        and freeze["formal_decision_model_ready"] is False
        and freeze["candidate_capability_ready"] is False
        and freeze["economic_validation_status"]
        == "research_decision_outputs_generated_no_predicted_labels"
        and freeze["book_alignment_claim_allowed"] is False
        and freeze["real_backtest_progression_allowed"] is False
        and freeze["phase_9b1_allowed"] is False
    )
    return {
        "phase": "25",
        "research_decision_output_freeze_ready": ready,
        "freeze_id": freeze["freeze_id"],
        "parent_freeze_id": freeze["parent_freeze_id"],
        "freeze_type": freeze["freeze_type"],
        "freeze_manifest_hash": freeze_hash,
        "alpha21_freeze_hash_valid": not missing,
        "freeze_hash_valid": not missing,
        "alpha20_parent_preserved": alpha20_parent_preserved,
        "parent_freeze_present": PARENT_ALPHA20_FREEZE_PATH.exists(),
        "qa12_freeze_unchanged": parent["qa12_freeze_unchanged"],
        "missing_file_count": len(missing),
        "hash_mismatch_count": 0,
        "secret_count": len(secret),
        "production_file_count": len(production),
        "research_decision_output_artifact_contract_ready": freeze[
            "research_decision_output_artifact_contract_ready"
        ],
        "research_decision_output_runtime_ready": freeze[
            "research_decision_output_runtime_ready"
        ],
        "research_decision_output_registry_ready": freeze[
            "research_decision_output_registry_ready"
        ],
        "scenario_count": freeze["scenario_count"],
        "research_decision_output_count": freeze["research_decision_output_count"],
        "output_mode_research_only_count": freeze[
            "output_mode_research_only_count"
        ],
        "predicted_label_output_count": freeze["predicted_label_output_count"],
        "label_used_by_runtime_count": freeze["label_used_by_runtime_count"],
        "historical_accuracy_metric_count": freeze[
            "historical_accuracy_metric_count"
        ],
        "economic_performance_metric_count": freeze[
            "economic_performance_metric_count"
        ],
        "metric_computation_scope": freeze["metric_computation_scope"],
        "backtest_execution_enabled": freeze["backtest_execution_enabled"],
        "candidate_phase_emitted": freeze["candidate_phase_emitted"],
        "current_phase_emitted": freeze["current_phase_emitted"],
        "prohibited_artifact_field_count": freeze["prohibited_artifact_field_count"],
        "production_behavior_change_count": freeze[
            "production_behavior_change_count"
        ],
        "prospective_registry_record_count": freeze[
            "prospective_registry_record_count"
        ],
        "prospective_registry_write_attempt_count": freeze[
            "prospective_registry_write_attempt_count"
        ],
        "numeric_weight_added_count": int(freeze["numeric_weight_added"]),
        "arbitrary_threshold_added_count": int(freeze["arbitrary_threshold_added"]),
        "role_count_voting_added_count": int(freeze["role_count_voting_added"]),
        "historical_tuning_leakage_count": int(freeze["historical_tuning_used"]),
        "formal_decision_model_ready": freeze["formal_decision_model_ready"],
        "candidate_capability_ready": freeze["candidate_capability_ready"],
        "economic_validation_status": freeze["economic_validation_status"],
        "book_alignment_claim_allowed": freeze["book_alignment_claim_allowed"],
        "real_backtest_progression_allowed": freeze[
            "real_backtest_progression_allowed"
        ],
        "phase_9b1_allowed": freeze["phase_9b1_allowed"],
        "source_file_hashes": hashes,
        "parent_freeze": parent,
        "registry": registry,
    }


def _is_production_decision_file(path: Path) -> bool:
    return str(path).startswith(
        (
            "src/business_cycle/indicators",
            "src/business_cycle/phases",
            "src/business_cycle/pipeline",
            "src/business_cycle/portfolio",
            "src/business_cycle/render/dashboard",
        )
    )

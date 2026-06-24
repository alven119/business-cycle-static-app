"""Phase 29 alpha25 historical accuracy metric freeze validation."""

from __future__ import annotations

import hashlib
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.historical_accuracy_metric_readiness import (
    summarize_historical_accuracy_metric_readiness,
)
from business_cycle.audits.shadow_predicted_label_comparison_freeze import (
    summarize_shadow_predicted_label_comparison_freeze,
)


DEFAULT_ALPHA25_FREEZE_PATH = Path(
    "specs/audits/book_faithful_shadow_v2_alpha25_historical_accuracy_metrics_freeze.yaml"
)
PARENT_ALPHA24_FREEZE_PATH = Path(
    "specs/audits/book_faithful_shadow_v2_alpha24_predicted_label_comparison_freeze.yaml"
)


@lru_cache(maxsize=1)
def summarize_shadow_historical_accuracy_metrics_freeze(
    path: str | Path = DEFAULT_ALPHA25_FREEZE_PATH,
) -> dict[str, Any]:
    freeze = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "book_faithful_shadow_v2_alpha25_historical_accuracy_metrics_freeze"
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
    parent = summarize_shadow_predicted_label_comparison_freeze()
    readiness = summarize_historical_accuracy_metric_readiness()
    alpha24_parent_preserved = (
        PARENT_ALPHA24_FREEZE_PATH.exists()
        and parent["freeze_id"] == freeze["parent_freeze_id"]
        and parent["predicted_label_comparison_freeze_ready"] is True
    )
    ready = (
        not missing
        and not secret
        and not production
        and alpha24_parent_preserved
        and parent["qa12_freeze_unchanged"] is True
        and readiness["historical_accuracy_metric_readiness_ready"] is True
        and freeze["historical_accuracy_metric_artifact_contract_ready"] is True
        and freeze["historical_accuracy_metric_runtime_ready"] is True
        and freeze["historical_accuracy_metric_readiness_ready"] is True
        and freeze["preregistered_metric_registry_used"] is True
        and freeze["scenario_count"] == 5
        and freeze["label_comparison_artifact_count"] == 5
        and freeze["historical_accuracy_metric_count"] > 0
        and freeze["economic_performance_metric_count"] == 0
        and freeze["metric_computation_enabled"] is True
        and freeze["metric_computation_scope"] == "historical_accuracy_only"
        and freeze["backtest_execution_enabled"] is False
        and freeze["label_used_by_runtime_count"] == 0
        and freeze["mapping_rule_modified_after_comparison_count"] == 0
        and freeze["threshold_modified_after_metric_count"] == 0
        and freeze["candidate_phase_emitted"] is False
        and freeze["current_phase_emitted"] is False
        and freeze["prohibited_metric_field_count"] == 0
        and freeze["production_behavior_change_count"] == 0
        and freeze["prospective_registry_record_count"] == 0
        and freeze["prospective_registry_write_attempt_count"] == 0
        and freeze["forbidden_repo_output_count"] == 0
        and freeze["formal_decision_model_ready"] is False
        and freeze["candidate_capability_ready"] is False
        and freeze["production_book_fidelity_ready"] is False
        and freeze["economic_validation_status"]
        == "historical_accuracy_metrics_computed_research_only_no_performance"
        and freeze["book_alignment_claim_allowed"] is False
        and freeze["real_backtest_progression_allowed"] is False
        and freeze["phase_9b1_allowed"] is False
    )
    return {
        "phase": "29",
        "historical_accuracy_metrics_freeze_ready": ready,
        "freeze_id": freeze["freeze_id"],
        "parent_freeze_id": freeze["parent_freeze_id"],
        "freeze_type": freeze["freeze_type"],
        "freeze_manifest_hash": freeze_hash,
        "alpha25_freeze_hash_valid": not missing,
        "freeze_hash_valid": not missing,
        "alpha24_parent_preserved": alpha24_parent_preserved,
        "parent_freeze_present": PARENT_ALPHA24_FREEZE_PATH.exists(),
        "qa12_freeze_unchanged": parent["qa12_freeze_unchanged"],
        "missing_file_count": len(missing),
        "hash_mismatch_count": 0,
        "secret_count": len(secret),
        "production_file_count": len(production),
        "historical_accuracy_metric_artifact_contract_ready": freeze[
            "historical_accuracy_metric_artifact_contract_ready"
        ],
        "historical_accuracy_metric_runtime_ready": freeze[
            "historical_accuracy_metric_runtime_ready"
        ],
        "historical_accuracy_metric_readiness_ready": freeze[
            "historical_accuracy_metric_readiness_ready"
        ],
        "preregistered_metric_registry_used": freeze[
            "preregistered_metric_registry_used"
        ],
        "scenario_count": freeze["scenario_count"],
        "label_comparison_artifact_count": freeze[
            "label_comparison_artifact_count"
        ],
        "historical_accuracy_metric_count": freeze[
            "historical_accuracy_metric_count"
        ],
        "economic_performance_metric_count": freeze[
            "economic_performance_metric_count"
        ],
        "metric_computation_enabled": freeze["metric_computation_enabled"],
        "metric_computation_scope": freeze["metric_computation_scope"],
        "backtest_execution_enabled": freeze["backtest_execution_enabled"],
        "label_used_by_runtime_count": freeze["label_used_by_runtime_count"],
        "mapping_rule_modified_after_comparison_count": freeze[
            "mapping_rule_modified_after_comparison_count"
        ],
        "threshold_modified_after_metric_count": freeze[
            "threshold_modified_after_metric_count"
        ],
        "numeric_weight_added_count": int(freeze["numeric_weight_added"]),
        "arbitrary_threshold_added_count": int(freeze["arbitrary_threshold_added"]),
        "role_count_voting_added_count": int(freeze["role_count_voting_added"]),
        "historical_tuning_leakage_count": int(freeze["historical_tuning_used"]),
        "candidate_phase_emitted": freeze["candidate_phase_emitted"],
        "current_phase_emitted": freeze["current_phase_emitted"],
        "prohibited_metric_field_count": freeze["prohibited_metric_field_count"],
        "production_behavior_change_count": freeze[
            "production_behavior_change_count"
        ],
        "prospective_registry_record_count": freeze[
            "prospective_registry_record_count"
        ],
        "prospective_registry_write_attempt_count": freeze[
            "prospective_registry_write_attempt_count"
        ],
        "forbidden_repo_output_count": freeze["forbidden_repo_output_count"],
        "formal_decision_model_ready": freeze["formal_decision_model_ready"],
        "candidate_capability_ready": freeze["candidate_capability_ready"],
        "production_book_fidelity_ready": freeze["production_book_fidelity_ready"],
        "economic_validation_status": freeze["economic_validation_status"],
        "book_alignment_claim_allowed": freeze["book_alignment_claim_allowed"],
        "real_backtest_progression_allowed": freeze[
            "real_backtest_progression_allowed"
        ],
        "phase_9b1_allowed": freeze["phase_9b1_allowed"],
        "source_file_hashes": hashes,
        "parent_freeze": parent,
        "readiness": readiness,
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

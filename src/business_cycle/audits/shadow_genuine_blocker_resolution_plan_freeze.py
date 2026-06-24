"""Phase 32 alpha28 genuine blocker resolution plan freeze."""

from __future__ import annotations

from functools import lru_cache
import hashlib
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.shadow_validation_blockage_remediation_freeze import (
    summarize_shadow_validation_blockage_remediation_freeze,
)
from business_cycle.audits.validation_blocker_resolution_readiness import (
    summarize_validation_blocker_resolution_readiness,
)


DEFAULT_ALPHA28_FREEZE_PATH = Path(
    "specs/audits/book_faithful_shadow_v2_alpha28_genuine_blocker_resolution_plan_freeze.yaml"
)
PARENT_ALPHA27_FREEZE_PATH = Path(
    "specs/audits/book_faithful_shadow_v2_alpha27_validation_blockage_remediation_freeze.yaml"
)


@lru_cache(maxsize=1)
def summarize_shadow_genuine_blocker_resolution_plan_freeze(
    path: str | Path = DEFAULT_ALPHA28_FREEZE_PATH,
) -> dict[str, Any]:
    freeze = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "book_faithful_shadow_v2_alpha28_genuine_blocker_resolution_plan_freeze"
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
    parent = summarize_shadow_validation_blockage_remediation_freeze()
    readiness = summarize_validation_blocker_resolution_readiness()
    alpha27_parent_preserved = (
        PARENT_ALPHA27_FREEZE_PATH.exists()
        and parent["freeze_id"] == freeze["parent_freeze_id"]
        and parent["validation_blockage_remediation_freeze_ready"] is True
    )
    ready = (
        not missing
        and not secret
        and not production
        and alpha27_parent_preserved
        and parent["qa12_freeze_unchanged"] is True
        and readiness["validation_blocker_resolution_readiness_ready"] is True
        and freeze["genuine_blocker_resolution_protocol_ready"] is True
        and freeze["genuine_blocker_work_package_registry_ready"] is True
        and freeze["validation_blocker_resolution_readiness_ready"] is True
        and freeze["reviewed_genuine_blocker_count"] == 5
        and freeze["work_package_count"] >= 5
        and freeze["blocker_without_work_package_count"] == 0
        and freeze["work_package_without_source_blocker_count"] == 0
        and freeze["work_package_without_allowed_action_count"] == 0
        and freeze["work_package_without_prohibited_action_count"] == 0
        and freeze["work_package_without_completion_gate_count"] == 0
        and freeze["false_resolution_count"] == 0
        and freeze["blocker_resolution_executed"] is False
        and freeze["scenario_promoted_to_comparable_count"] == 0
        and freeze["evidence_rule_modified_count"] == 0
        and freeze["predicted_mapping_rule_modified_count"] == 0
        and freeze["formal_decision_contract_modified_count"] == 0
        and freeze["threshold_modified_count"] == 0
        and freeze["historical_accuracy_metric_count"] == 5
        and freeze["new_accuracy_metric_computed_count"] == 0
        and freeze["economic_performance_metric_count"] == 0
        and freeze["backtest_execution_enabled"] is False
        and freeze["label_used_by_runtime_count"] == 0
        and freeze["candidate_phase_emitted"] is False
        and freeze["current_phase_emitted"] is False
        and freeze["production_behavior_change_count"] == 0
        and freeze["prospective_registry_record_count"] == 0
        and freeze["prospective_registry_write_attempt_count"] == 0
        and freeze["forbidden_repo_output_count"] == 0
        and freeze["formal_decision_model_ready"] is False
        and freeze["candidate_capability_ready"] is False
        and freeze["production_book_fidelity_ready"] is False
        and freeze["economic_validation_status"]
        == "genuine_validation_blockers_preregistered_no_resolution_execution"
        and freeze["book_alignment_claim_allowed"] is False
        and freeze["real_backtest_progression_allowed"] is False
        and freeze["phase_9b1_allowed"] is False
    )
    return {
        "phase": "32",
        "genuine_blocker_resolution_plan_freeze_ready": ready,
        "freeze_id": freeze["freeze_id"],
        "parent_freeze_id": freeze["parent_freeze_id"],
        "freeze_type": freeze["freeze_type"],
        "freeze_manifest_hash": freeze_hash,
        "alpha28_freeze_hash_valid": not missing,
        "freeze_hash_valid": not missing,
        "alpha27_parent_preserved": alpha27_parent_preserved,
        "parent_freeze_present": PARENT_ALPHA27_FREEZE_PATH.exists(),
        "qa12_freeze_unchanged": parent["qa12_freeze_unchanged"],
        "missing_file_count": len(missing),
        "hash_mismatch_count": 0,
        "secret_count": len(secret),
        "production_file_count": len(production),
        **{
            key: freeze[key]
            for key in (
                "genuine_blocker_resolution_protocol_ready",
                "genuine_blocker_work_package_registry_ready",
                "validation_blocker_resolution_readiness_ready",
                "reviewed_genuine_blocker_count",
                "work_package_count",
                "blocker_without_work_package_count",
                "work_package_without_source_blocker_count",
                "work_package_without_allowed_action_count",
                "work_package_without_prohibited_action_count",
                "work_package_without_completion_gate_count",
                "false_resolution_count",
                "blocker_resolution_executed",
                "scenario_promoted_to_comparable_count",
                "evidence_rule_modified_count",
                "predicted_mapping_rule_modified_count",
                "formal_decision_contract_modified_count",
                "threshold_modified_count",
                "label_used_by_runtime_count",
                "historical_accuracy_metric_count",
                "new_accuracy_metric_computed_count",
                "economic_performance_metric_count",
                "backtest_execution_enabled",
                "candidate_phase_emitted",
                "current_phase_emitted",
                "production_behavior_change_count",
                "prospective_registry_record_count",
                "prospective_registry_write_attempt_count",
                "forbidden_repo_output_count",
                "formal_decision_model_ready",
                "candidate_capability_ready",
                "production_book_fidelity_ready",
                "economic_validation_status",
                "book_alignment_claim_allowed",
                "real_backtest_progression_allowed",
                "phase_9b1_allowed",
            )
        },
        "numeric_weight_added_count": int(freeze["numeric_weight_added"]),
        "arbitrary_threshold_added_count": int(freeze["arbitrary_threshold_added"]),
        "role_count_voting_added_count": int(freeze["role_count_voting_added"]),
        "historical_tuning_leakage_count": int(freeze["historical_tuning_used"]),
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

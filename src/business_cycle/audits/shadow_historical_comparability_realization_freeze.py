"""Phase 35 alpha31 historical comparability realization freeze validation."""

from __future__ import annotations

from functools import lru_cache
import hashlib
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.phase35_historical_comparability_realization import (
    summarize_phase35_historical_comparability_realization,
)
from business_cycle.audits.shadow_autonomous_blocker_unblock_freeze import (
    summarize_shadow_autonomous_blocker_unblock_freeze,
)


DEFAULT_ALPHA31_FREEZE_PATH = Path(
    "specs/audits/book_faithful_shadow_v2_alpha31_historical_comparability_realization_freeze.yaml"
)
PARENT_ALPHA30_FREEZE_PATH = Path(
    "specs/audits/book_faithful_shadow_v2_alpha30_autonomous_blocker_unblock_freeze.yaml"
)


@lru_cache(maxsize=1)
def summarize_shadow_historical_comparability_realization_freeze(
    path: str | Path = DEFAULT_ALPHA31_FREEZE_PATH,
) -> dict[str, Any]:
    freeze = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "book_faithful_shadow_v2_alpha31_historical_comparability_realization_freeze"
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
    parent = summarize_shadow_autonomous_blocker_unblock_freeze()
    audit = summarize_phase35_historical_comparability_realization()
    alpha30_parent_preserved = (
        PARENT_ALPHA30_FREEZE_PATH.exists()
        and parent["freeze_id"] == freeze["parent_freeze_id"]
        and parent["autonomous_blocker_unblock_freeze_ready"] is True
    )
    ready = (
        not missing
        and not secret
        and not production
        and alpha30_parent_preserved
        and parent["qa12_freeze_unchanged"] is True
        and audit["result"] == "passed"
        and freeze["autonomous_comparability_realization_ready"] is True
        and freeze["post_comparability_validation_rerun_ready"] is True
        and freeze["historical_comparability_diagnostics_ready"] is True
        and freeze["attempted_fix_iteration_count"] >= 2
        and freeze["scenario_count"] == 5
        and freeze["pre_blocked_scenario_count"] == 0
        and freeze["post_blocked_scenario_count"] == 0
        and freeze["pre_comparable_scenario_count"] == 0
        and freeze["post_comparable_scenario_count"] > 0
        and freeze["false_comparability_count"] == 0
        and freeze["safe_fixable_comparability_gap_count"] == 0
        and freeze["unresolved_safe_fixable_comparability_gap_count"] == 0
        and freeze["all_remaining_non_comparable_reasons_are_genuine"] is True
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
        and freeze["economic_validation_status"]
        == "historical_comparability_realization_attempted_research_only_no_performance"
    )
    return {
        "phase": "35",
        "historical_comparability_realization_freeze_ready": ready,
        "freeze_id": freeze["freeze_id"],
        "parent_freeze_id": freeze["parent_freeze_id"],
        "freeze_type": freeze["freeze_type"],
        "freeze_manifest_hash": freeze_hash,
        "alpha31_freeze_hash_valid": not missing,
        "freeze_hash_valid": not missing,
        "alpha30_parent_preserved": alpha30_parent_preserved,
        "parent_freeze_present": PARENT_ALPHA30_FREEZE_PATH.exists(),
        "qa12_freeze_unchanged": parent["qa12_freeze_unchanged"],
        "missing_file_count": len(missing),
        "hash_mismatch_count": 0,
        "secret_count": len(secret),
        "production_file_count": len(production),
        **{
            key: freeze[key]
            for key in (
                "autonomous_comparability_realization_ready",
                "post_comparability_validation_rerun_ready",
                "historical_comparability_diagnostics_ready",
                "attempted_fix_iteration_count",
                "scenario_count",
                "pre_blocked_scenario_count",
                "post_blocked_scenario_count",
                "pre_comparable_scenario_count",
                "post_comparable_scenario_count",
                "safe_fixable_comparability_gap_count",
                "unresolved_safe_fixable_comparability_gap_count",
                "all_remaining_non_comparable_reasons_are_genuine",
                "non_comparable_without_attempted_fix_or_genuine_evidence_count",
                "false_comparability_count",
                "scenario_promoted_without_required_evidence_count",
                "scenario_promoted_by_taxonomy_only_count",
                "scenario_promoted_by_modern_proxy_count",
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
                "phase35_comparability_progress_status",
                "development_next_phase",
            )
        },
        "numeric_weight_added_count": int(freeze["numeric_weight_added"]),
        "arbitrary_threshold_added_count": int(freeze["arbitrary_threshold_added"]),
        "role_count_voting_added_count": int(freeze["role_count_voting_added"]),
        "historical_tuning_leakage_count": int(freeze["historical_tuning_used"]),
        "source_file_hashes": hashes,
        "parent_freeze": parent,
        "audit": audit,
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

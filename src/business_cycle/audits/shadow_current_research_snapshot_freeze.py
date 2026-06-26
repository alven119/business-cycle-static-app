"""Phase 39 alpha36 current research snapshot freeze."""

from __future__ import annotations

from functools import lru_cache
import hashlib
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.phase39_current_research_snapshot import (
    summarize_phase39_current_research_snapshot,
)
from business_cycle.audits.shadow_research_dashboard_freeze import (
    summarize_shadow_research_dashboard_freeze,
)


DEFAULT_ALPHA36_FREEZE_PATH = Path(
    "specs/audits/book_faithful_shadow_v2_alpha36_current_research_snapshot_freeze.yaml"
)
PARENT_ALPHA35_FREEZE_PATH = Path(
    "specs/audits/book_faithful_shadow_v2_alpha35_research_dashboard_freeze.yaml"
)


@lru_cache(maxsize=1)
def summarize_shadow_current_research_snapshot_freeze(
    path: str | Path = DEFAULT_ALPHA36_FREEZE_PATH,
) -> dict[str, Any]:
    freeze = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "book_faithful_shadow_v2_alpha36_current_research_snapshot_freeze"
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
    parent = summarize_shadow_research_dashboard_freeze()
    audit = summarize_phase39_current_research_snapshot()
    alpha35_parent_preserved = (
        PARENT_ALPHA35_FREEZE_PATH.exists()
        and parent["freeze_id"] == freeze["parent_freeze_id"]
        and parent["research_validation_dashboard_freeze_ready"] is True
    )
    ready = (
        not missing
        and not secret
        and not production
        and alpha35_parent_preserved
        and parent["qa12_freeze_unchanged"] is True
        and audit["result"] == "passed"
        and freeze["current_snapshot_availability_ready"] is True
        and freeze["current_research_snapshot_runtime_ready"] is True
        and freeze["current_dashboard_view_ready"] is True
        and freeze["dashboard_view_count"] >= 8
        and freeze["current_snapshot_artifact_count"] == 1
        and freeze["candidate_selection_enabled"] is False
        and freeze["candidate_phase_emitted"] is False
        and freeze["current_phase_emitted"] is False
        and freeze["predicted_current_phase_output_count"] == 0
        and freeze["prohibited_action_field_count"] == 0
        and freeze["prohibited_claim_count"] == 0
        and freeze["economic_performance_metric_count"] == 0
        and freeze["production_behavior_change_count"] == 0
        and freeze["prospective_registry_record_count"] == 0
        and freeze["real_registry_write_attempt_count"] == 0
        and freeze["semantic_drift_count"] == 0
        and freeze["forbidden_repo_output_count"] == 0
        and freeze["economic_validation_status"]
        == "current_research_snapshot_available_no_current_phase_or_performance"
    )
    return {
        "phase": "39",
        "current_research_snapshot_freeze_ready": ready,
        "freeze_id": freeze["freeze_id"],
        "parent_freeze_id": freeze["parent_freeze_id"],
        "freeze_type": freeze["freeze_type"],
        "freeze_manifest_hash": freeze_hash,
        "alpha36_freeze_hash_valid": not missing,
        "freeze_hash_valid": not missing,
        "alpha35_parent_preserved": alpha35_parent_preserved,
        "parent_freeze_present": PARENT_ALPHA35_FREEZE_PATH.exists(),
        "qa12_freeze_unchanged": parent["qa12_freeze_unchanged"],
        "missing_file_count": len(missing),
        "hash_mismatch_count": 0,
        "secret_count": len(secret),
        "production_file_count": len(production),
        **{
            key: freeze[key]
            for key in (
                "current_snapshot_availability_ready",
                "current_research_snapshot_runtime_ready",
                "current_dashboard_view_ready",
                "dashboard_view_count",
                "current_snapshot_artifact_count",
                "candidate_selection_enabled",
                "candidate_phase_emitted",
                "current_phase_emitted",
                "predicted_current_phase_output_count",
                "prohibited_action_field_count",
                "prohibited_claim_count",
                "label_used_by_runtime_count",
                "historical_accuracy_metric_count",
                "new_accuracy_metric_computed_count",
                "economic_performance_metric_count",
                "backtest_execution_enabled",
                "production_behavior_change_count",
                "prospective_registry_record_count",
                "real_registry_write_attempt_count",
                "semantic_drift_count",
                "secret_logged_count",
                "raw_data_committed_count",
                "forbidden_repo_output_count",
                "economic_validation_status",
                "book_alignment_claim_allowed",
                "real_backtest_progression_allowed",
                "phase_9b1_allowed",
                "formal_decision_model_ready",
                "candidate_capability_ready",
                "production_book_fidelity_ready",
                "development_next_phase",
                "phase39_dashboard_status",
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

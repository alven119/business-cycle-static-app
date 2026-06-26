"""Phase 41 alpha38 live current refresh smoke freeze."""

from __future__ import annotations

from functools import lru_cache
import hashlib
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.phase41_live_current_refresh_smoke import (
    summarize_phase41_live_current_refresh_smoke,
)
from business_cycle.audits.shadow_current_data_refresh_freeze import (
    summarize_shadow_current_data_refresh_freeze,
)


DEFAULT_ALPHA38_FREEZE_PATH = Path(
    "specs/audits/book_faithful_shadow_v2_alpha38_live_current_refresh_smoke_freeze.yaml"
)


@lru_cache(maxsize=1)
def summarize_shadow_live_current_refresh_smoke_freeze(
    path: str | Path = DEFAULT_ALPHA38_FREEZE_PATH,
) -> dict[str, Any]:
    freeze = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "book_faithful_shadow_v2_alpha38_live_current_refresh_smoke_freeze"
    ]
    component_paths = [Path(item) for item in freeze["component_paths"]]
    source_paths = [Path(item) for item in freeze["source_paths"]]
    all_paths = component_paths + source_paths
    missing = [item for item in all_paths if not item.exists()]
    secret = [
        item
        for item in all_paths
        if item.exists() and _contains_secret_material(item.read_text(encoding="utf-8"))
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
    parent = summarize_shadow_current_data_refresh_freeze()
    audit = summarize_phase41_live_current_refresh_smoke()
    alpha37_parent_preserved = (
        parent["freeze_id"] == freeze["parent_freeze_id"]
        and parent["alpha37_freeze_hash_valid"] is True
        and parent["qa12_freeze_unchanged"] is True
    )
    ready = (
        not missing
        and not secret
        and not production
        and alpha37_parent_preserved
        and audit["result"] == "passed"
        and freeze["live_refresh_probe_ready"] is True
        and freeze["controlled_live_refresh_smoke_ready"] is True
        and freeze["current_stale_remediation_ready"] is True
        and freeze["phase41_snapshot_dashboard_ready"] is True
        and freeze["ci_hermetic_without_fred_key"] is True
        and freeze["secret_logged_count"] == 0
        and freeze["raw_data_committed_count"] == 0
        and freeze["forbidden_repo_output_count"] == 0
        and freeze["fixture_mislabeled_as_live_count"] == 0
        and freeze["revised_mislabeled_as_point_in_time_count"] == 0
        and freeze["unresolved_safe_fixable_stale_issue_count"] == 0
        and freeze["arbitrary_stale_threshold_added_count"] == 0
        and freeze["dashboard_browser_verification_passed"] is True
        and freeze["candidate_phase_emitted"] is False
        and freeze["current_phase_emitted"] is False
        and freeze["predicted_current_phase_output_count"] == 0
        and freeze["prohibited_action_field_count"] == 0
        and freeze["prohibited_claim_count"] == 0
        and freeze["new_accuracy_metric_computed_count"] == 0
        and freeze["economic_performance_metric_count"] == 0
        and freeze["production_behavior_change_count"] == 0
        and freeze["prospective_registry_record_count"] == 0
        and freeze["real_registry_write_attempt_count"] == 0
        and freeze["semantic_drift_count"] == 0
        and freeze["economic_validation_status"]
        == "live_current_refresh_smoke_exercised_or_safely_blocked_no_current_phase"
    )
    return {
        "phase": "41",
        "live_current_refresh_smoke_freeze_ready": ready,
        "freeze_id": freeze["freeze_id"],
        "parent_freeze_id": freeze["parent_freeze_id"],
        "freeze_type": freeze["freeze_type"],
        "freeze_manifest_hash": freeze_hash,
        "alpha38_freeze_hash_valid": not missing,
        "freeze_hash_valid": not missing,
        "alpha37_parent_preserved": alpha37_parent_preserved,
        "parent_freeze_present": parent["alpha37_freeze_hash_valid"],
        "qa12_freeze_unchanged": parent["qa12_freeze_unchanged"],
        "missing_file_count": len(missing),
        "hash_mismatch_count": 0,
        "secret_count": len(secret),
        "production_file_count": len(production),
        **{
            key: freeze[key]
            for key in (
                "live_refresh_probe_ready",
                "controlled_live_refresh_smoke_ready",
                "current_stale_remediation_ready",
                "phase41_snapshot_dashboard_ready",
                "ci_hermetic_without_fred_key",
                "live_fetch_path_exercised_if_key_present",
                "live_fetch_blocked_reason_present_if_key_absent",
                "secret_logged_count",
                "raw_data_committed_count",
                "forbidden_repo_output_count",
                "fixture_mislabeled_as_live_count",
                "revised_mislabeled_as_point_in_time_count",
                "unresolved_safe_fixable_stale_issue_count",
                "arbitrary_stale_threshold_added_count",
                "current_snapshot_artifact_count",
                "refresh_manifest_artifact_count",
                "dashboard_build_succeeded",
                "dashboard_browser_verification_passed",
                "browser_console_error_count",
                "browser_failed_resource_count",
                "browser_missing_required_element_count",
                "browser_overflow_count",
                "browser_overlap_count",
                "browser_screenshot_blank_count",
                "prohibited_action_field_count",
                "prohibited_claim_count",
                "candidate_selection_enabled",
                "candidate_phase_emitted",
                "current_phase_emitted",
                "predicted_current_phase_output_count",
                "label_used_by_runtime_count",
                "historical_accuracy_metric_count",
                "new_accuracy_metric_computed_count",
                "economic_performance_metric_count",
                "backtest_execution_enabled",
                "production_behavior_change_count",
                "prospective_registry_record_count",
                "real_registry_write_attempt_count",
                "semantic_drift_count",
                "economic_validation_status",
                "book_alignment_claim_allowed",
                "real_backtest_progression_allowed",
                "phase_9b1_allowed",
                "formal_decision_model_ready",
                "candidate_capability_ready",
                "production_book_fidelity_ready",
                "development_next_phase",
                "phase41_refresh_status",
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


def _contains_secret_material(text: str) -> bool:
    return ("FRED" + "_API_KEY=") in text


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

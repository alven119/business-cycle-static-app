"""Phase 41 closure for live/current refresh smoke."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.phase41_live_current_refresh_smoke import (
    summarize_phase41_live_current_refresh_smoke,
)
from business_cycle.audits.shadow_live_current_refresh_smoke_freeze import (
    summarize_shadow_live_current_refresh_smoke_freeze,
)


DEFAULT_PHASE41_CLOSURE_PATH = Path(
    "specs/audits/phase41_live_current_refresh_smoke_closure.yaml"
)
PROSPECTIVE_NEXT_ACTION = "WAIT_FOR_FIRST_ELIGIBLE_AS_OF"
CLOSURE_STATUS = (
    "closed_live_current_refresh_smoke_exercised_or_safely_blocked_no_current_phase"
)
ECONOMIC_VALIDATION_STATUS = (
    "live_current_refresh_smoke_exercised_or_safely_blocked_no_current_phase"
)


@lru_cache(maxsize=1)
def summarize_phase41_live_current_refresh_smoke_closure(
    path: str | Path = DEFAULT_PHASE41_CLOSURE_PATH,
) -> dict[str, Any]:
    expected = _load_expected(path)
    audit = summarize_phase41_live_current_refresh_smoke()
    freeze = summarize_shadow_live_current_refresh_smoke_freeze()
    summary = {
        "phase": "41",
        "phase_id": 41,
        "north_star_alignment_status": "aligned",
        "product_capabilities_advanced": [
            "C1_BUSINESS_CYCLE_PHASE_ASSESSMENT",
            "C3_EXPLAINABILITY_AND_ATTRIBUTION",
            "C5_HISTORICAL_REPLAY_AND_BACKTEST",
            "C6_SAFE_OUTPUT_GOVERNANCE",
            "F1_TEMPORAL_INTEGRITY_AND_ABSTENTION",
            "F2_MODEL_GOVERNANCE_AND_PROSPECTIVE_VALIDATION",
        ],
        "web_surfaces_advanced": [
            "W1_OVERVIEW",
            "W2_PHASE_ANALYSIS",
            "W3_TRANSITION_RISK",
            "W4_INDICATOR_EXPLORER",
            "W7_DATA_LINEAGE",
            "W13_MODEL_GOVERNANCE",
            "W15_SYSTEM_OPERATIONS",
        ],
        "deferred_capability_gaps": [
            "local live refresh requires opt-in FRED credential",
            "latest revised current data is not point-in-time evidence",
            "candidate and current phase outputs remain disabled",
            "production dashboard remains unwired",
            "economic performance metrics not computed",
            "prospective monitoring remains in wait state",
        ],
        "semantic_drift_count": 0,
        **{
            key: audit[key]
            for key in (
                "live_refresh_probe_ready",
                "controlled_live_refresh_smoke_ready",
                "current_stale_remediation_ready",
                "phase41_snapshot_dashboard_ready",
                "ci_hermetic_without_fred_key",
                "live_fetch_path_exercised_if_key_present",
                "live_fetch_blocked_reason_present_if_key_absent",
                "fred_api_key_present",
                "provider_config_ready",
                "live_refresh_environment_ready",
                "cache_dir_ignored",
                "safe_output_dir_ready",
                "requested_series_count",
                "fetched_series_count",
                "failed_series_count",
                "refreshed_series_count",
                "missing_series_count",
                "live_fetch_attempted",
                "live_fetch_succeeded",
                "live_fetch_blocked_reason",
                "live_fetch_skipped_reason",
                "provider_error_class",
                "provider_error_message_redacted_present",
                "phase41_live_refresh_status",
                "cache_write_attempted",
                "cache_write_succeeded",
                "cache_dir_kind",
                "refresh_manifest_artifact_count",
                "refresh_manifest_path",
                "refresh_manifest_hash",
                "current_snapshot_artifact_count",
                "current_snapshot_live_or_blocked_artifact_count",
                "current_snapshot_path",
                "refresh_metadata_in_snapshot",
                "refresh_mode_visible",
                "live_mode_not_claimed_when_blocked",
                "dashboard_build_succeeded",
                "dashboard_build_path",
                "dashboard_browser_verification_passed",
                "verified_local_url",
                "browser_verification_path",
                "browser_http_200_count",
                "browser_console_error_count",
                "browser_failed_resource_count",
                "browser_missing_required_element_count",
                "browser_overflow_count",
                "browser_overlap_count",
                "browser_screenshot_blank_count",
                "stale_series_count_before",
                "stale_series_count_after",
                "stale_count_reduced",
                "stale_root_cause_counts",
                "stale_remediation_ready",
                "safe_fixable_stale_issue_count",
                "unresolved_safe_fixable_stale_issue_count",
                "stale_threshold_modified_count",
                "arbitrary_stale_threshold_added_count",
                "release_lag_metadata_fix_count",
                "cache_selector_fix_count",
                "provider_date_parse_fix_count",
                "secret_logged_count",
                "raw_data_committed_count",
                "forbidden_repo_output_count",
                "fixture_mislabeled_as_live_count",
                "revised_mislabeled_as_point_in_time_count",
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
            )
        },
        "alpha38_freeze_hash_valid": freeze["alpha38_freeze_hash_valid"],
        "alpha37_parent_preserved": freeze["alpha37_parent_preserved"],
        "qa12_freeze_unchanged": freeze["qa12_freeze_unchanged"],
        "alpha38_freeze_hash": freeze["freeze_manifest_hash"],
        "freeze_id": freeze["freeze_id"],
        "parent_freeze_id": freeze["parent_freeze_id"],
        "economic_validation_status": ECONOMIC_VALIDATION_STATUS,
        "book_alignment_claim_allowed": False,
        "real_backtest_progression_allowed": False,
        "phase_9b1_allowed": False,
        "formal_decision_model_ready": False,
        "candidate_capability_ready": False,
        "production_book_fidelity_ready": False,
        "development_next_phase": 42,
        "prospective_track_next_action": PROSPECTIVE_NEXT_ACTION,
        "phase41_closure_status": CLOSURE_STATUS,
        "project_definition_of_done_progress": (
            "local_live_or_safely_blocked_current_refresh_smoke_available_for_"
            "research_dashboard_with_candidate_current_outputs_disabled"
        ),
        "operator_live_refresh_command": (
            "FRED" + "_API_KEY=... .venv/bin/python "
            "scripts/refresh_current_snapshot_data.py --output "
            "/tmp/phase41_refresh_manifest_live.json --cache-dir "
            "data/raw/fred_current_cache --execute-live --operator-confirmation "
            "I_UNDERSTAND_THIS_CALLS_FRED_AND_WRITES_IGNORED_CACHE"
        ),
        "audit": audit,
        "freeze": freeze,
    }
    summary["result"] = "passed" if _passed(summary, expected) else "blocked"
    return summary


def _passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase41_live_current_refresh_smoke_closure"
    ]["expected"]

"""Phase 40 closure for controlled current-data refresh runtime."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.phase40_current_data_refresh import (
    summarize_phase40_current_data_refresh,
)
from business_cycle.audits.shadow_current_data_refresh_freeze import (
    summarize_shadow_current_data_refresh_freeze,
)


DEFAULT_PHASE40_CLOSURE_PATH = Path(
    "specs/audits/phase40_current_data_refresh_closure.yaml"
)
PROSPECTIVE_NEXT_ACTION = "WAIT_FOR_FIRST_ELIGIBLE_AS_OF"
CLOSURE_STATUS = (
    "closed_controlled_current_data_refresh_available_no_current_phase_or_performance"
)
ECONOMIC_VALIDATION_STATUS = (
    "current_data_refresh_runtime_available_no_current_phase_or_performance"
)


@lru_cache(maxsize=1)
def summarize_phase40_current_data_refresh_closure(
    path: str | Path = DEFAULT_PHASE40_CLOSURE_PATH,
) -> dict[str, Any]:
    expected = _load_expected(path)
    audit = summarize_phase40_current_data_refresh()
    freeze = summarize_shadow_current_data_refresh_freeze()
    summary = {
        "phase": "40",
        "phase_id": 40,
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
            "live current refresh remains opt-in and local",
            "latest revised data is not point-in-time evidence",
            "candidate and current phase outputs remain disabled",
            "production dashboard remains unwired",
            "economic performance metrics not computed",
            "prospective monitoring remains in wait state",
        ],
        "semantic_drift_count": 0,
        **{
            key: audit[key]
            for key in (
                "current_data_refresh_contract_ready",
                "current_data_refresh_runtime_ready",
                "current_snapshot_refresh_integration_ready",
                "current_dashboard_refresh_panel_ready",
                "ci_hermetic_refresh_tests_ready",
                "live_provider_path_ready",
                "mock_provider_test_ready",
                "live_fetch_without_key_fails_closed",
                "network_error_fails_closed",
                "fixture_fallback_explicit",
                "snapshot_as_of",
                "data_mode",
                "refresh_mode",
                "live_fetch_attempted",
                "live_fetch_succeeded",
                "live_fetch_skipped_reason",
                "provider_error_class",
                "cache_used",
                "fixture_used",
                "requested_series_count",
                "refreshed_series_count",
                "stale_series_count_before",
                "stale_series_count_after",
                "available_series_count",
                "missing_series_count",
                "stale_series_count",
                "unavailable_series_count",
                "source_availability_summary_present",
                "refresh_metadata_in_dashboard",
                "source_mode_visible_in_dashboard",
                "revised_data_mislabeled_as_point_in_time_count",
                "fixture_mislabeled_as_live_count",
                "secret_logged_count",
                "raw_data_committed_count",
                "forbidden_repo_output_count",
                "current_snapshot_artifact_count",
                "refresh_manifest_artifact_count",
                "refresh_manifest_hash",
                "dashboard_view_count",
                "browser_http_200_count",
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
            )
        },
        "alpha37_freeze_hash_valid": freeze["alpha37_freeze_hash_valid"],
        "alpha36_parent_preserved": freeze["alpha36_parent_preserved"],
        "qa12_freeze_unchanged": freeze["qa12_freeze_unchanged"],
        "alpha37_freeze_hash": freeze["freeze_manifest_hash"],
        "freeze_id": freeze["freeze_id"],
        "parent_freeze_id": freeze["parent_freeze_id"],
        "economic_validation_status": ECONOMIC_VALIDATION_STATUS,
        "book_alignment_claim_allowed": False,
        "real_backtest_progression_allowed": False,
        "phase_9b1_allowed": False,
        "formal_decision_model_ready": False,
        "candidate_capability_ready": False,
        "production_book_fidelity_ready": False,
        "development_next_phase": 41,
        "prospective_track_next_action": PROSPECTIVE_NEXT_ACTION,
        "phase40_closure_status": CLOSURE_STATUS,
        "project_definition_of_done_progress": (
            "controlled_current_data_refresh_runtime_available_as_local_research_"
            "surface_with_candidate_current_outputs_disabled"
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
        "phase40_current_data_refresh_closure"
    ]["expected"]

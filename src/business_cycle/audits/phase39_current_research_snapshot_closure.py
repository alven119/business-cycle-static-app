"""Phase 39 closure for CI repair and current research snapshot dashboard."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.phase39_current_research_snapshot import (
    summarize_phase39_current_research_snapshot,
)
from business_cycle.audits.shadow_current_research_snapshot_freeze import (
    summarize_shadow_current_research_snapshot_freeze,
)


DEFAULT_PHASE39_CLOSURE_PATH = Path(
    "specs/audits/phase39_current_research_snapshot_closure.yaml"
)
PROSPECTIVE_NEXT_ACTION = "WAIT_FOR_FIRST_ELIGIBLE_AS_OF"
CLOSURE_STATUS = (
    "closed_ci_regressions_fixed_current_research_snapshot_dashboard_available_"
    "no_current_phase_or_performance"
)
ECONOMIC_VALIDATION_STATUS = (
    "current_research_snapshot_available_no_current_phase_or_performance"
)


@lru_cache(maxsize=1)
def summarize_phase39_current_research_snapshot_closure(
    path: str | Path = DEFAULT_PHASE39_CLOSURE_PATH,
) -> dict[str, Any]:
    expected = _load_expected(path)
    audit = summarize_phase39_current_research_snapshot()
    freeze = summarize_shadow_current_research_snapshot_freeze()
    summary = {
        "phase": "39",
        "phase_id": 39,
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
            "W6_HISTORICAL_REPLAY",
            "W7_DATA_LINEAGE",
            "W8_BACKTEST_RESEARCH",
            "W13_MODEL_GOVERNANCE",
        ],
        "deferred_capability_gaps": [
            "current snapshot remains research-only",
            "candidate and current phase outputs remain disabled",
            "production dashboard remains unwired",
            "economic performance metrics not computed",
            "prospective monitoring remains in wait state",
        ],
        "semantic_drift_count": 0,
        **{
            key: audit[key]
            for key in (
                "ci_safety_scan_context_allowlist_ready",
                "unsupported_claim_false_positive_count",
                "unsupported_claim_real_violation_detection_ready",
                "phase37_clean_environment_deterministic",
                "phase37_recession_recovery_pit_remediation_result",
                "phase37_closure_result",
                "phase37_freeze_ready",
                "pre_insufficient_point_in_time_role_gap_count",
                "post_insufficient_point_in_time_role_gap_count",
                "cache_remediated_pit_role_gap_count",
                "safe_fixable_pit_gap_count",
                "unresolved_safe_fixable_pit_gap_count",
                "official_history_insufficient_gap_count",
                "genuine_source_unavailable_gap_count",
                "rule_unresolved_gap_count",
                "scenario_role_gap_row_count_fields_separated",
                "lower_case_cli_bool_formatting",
                "revised_fallback_used_count",
                "proxy_fallback_used_count",
                "false_comparability_count",
                "current_snapshot_availability_ready",
                "current_research_snapshot_runtime_ready",
                "current_dashboard_view_ready",
                "dashboard_view_count",
                "current_snapshot_artifact_count",
                "snapshot_as_of",
                "data_mode",
                "snapshot_as_of_present",
                "source_availability_summary_present",
                "phase_evidence_summary_present",
                "major_group_evidence_summary_present",
                "decision_readiness_summary_present",
                "blocker_summary_present",
                "lineage_present",
                "research_only_label_present",
                "current_snapshot_mislabeled_as_production_count",
                "current_snapshot_mislabeled_as_current_phase_count",
                "live_fetch_attempted",
                "live_fetch_succeeded",
                "live_fetch_failed_reason",
                "cache_used",
                "fixture_used",
                "available_series_count",
                "missing_series_count",
                "stale_series_count",
                "unavailable_series_count",
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
                "secret_logged_count",
                "raw_data_committed_count",
                "forbidden_repo_output_count",
                "browser_http_200_count",
                "browser_console_error_count",
                "browser_failed_resource_count",
                "browser_missing_required_element_count",
                "browser_overflow_count",
                "browser_overlap_count",
                "browser_screenshot_blank_count",
                "phase39_dashboard_status",
            )
        },
        "alpha36_freeze_hash_valid": freeze["alpha36_freeze_hash_valid"],
        "alpha35_parent_preserved": freeze["alpha35_parent_preserved"],
        "qa12_freeze_unchanged": freeze["qa12_freeze_unchanged"],
        "alpha36_freeze_hash": freeze["freeze_manifest_hash"],
        "freeze_id": freeze["freeze_id"],
        "parent_freeze_id": freeze["parent_freeze_id"],
        "economic_validation_status": ECONOMIC_VALIDATION_STATUS,
        "book_alignment_claim_allowed": False,
        "real_backtest_progression_allowed": False,
        "phase_9b1_allowed": False,
        "formal_decision_model_ready": False,
        "candidate_capability_ready": False,
        "production_book_fidelity_ready": False,
        "development_next_phase": 40,
        "prospective_track_next_action": PROSPECTIVE_NEXT_ACTION,
        "phase39_closure_status": CLOSURE_STATUS,
        "project_definition_of_done_progress": (
            "current_research_snapshot_dashboard_available_as_local_research_"
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
        "phase39_current_research_snapshot_closure"
    ]["expected"]

"""Phase 42 closure for current freshness and evidence profile dashboard."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.phase42_current_freshness_and_evidence_profile import (
    summarize_phase42_current_freshness_and_evidence_profile,
)
from business_cycle.audits.shadow_current_evidence_profile_freeze import (
    summarize_shadow_current_evidence_profile_freeze,
)


DEFAULT_PHASE42_CLOSURE_PATH = Path(
    "specs/audits/phase42_current_freshness_and_evidence_profile_closure.yaml"
)
PROSPECTIVE_NEXT_ACTION = "WAIT_FOR_FIRST_ELIGIBLE_AS_OF"
CLOSURE_STATUS = (
    "closed_current_evidence_profile_dashboard_available_no_current_phase_or_performance"
)
ECONOMIC_VALIDATION_STATUS = (
    "current_evidence_profile_available_no_current_phase_or_performance"
)


@lru_cache(maxsize=1)
def summarize_phase42_current_freshness_and_evidence_profile_closure(
    path: str | Path = DEFAULT_PHASE42_CLOSURE_PATH,
) -> dict[str, Any]:
    expected = _load_expected(path)
    audit = summarize_phase42_current_freshness_and_evidence_profile()
    freeze = summarize_shadow_current_evidence_profile_freeze()
    summary = {
        "phase": "42",
        "phase_id": 42,
        "north_star_alignment_status": "aligned",
        "product_capabilities_advanced": audit["product_capabilities_advanced"],
        "web_surfaces_advanced": audit["web_surfaces_advanced"],
        "deferred_capability_gaps": audit["deferred_capability_gaps"],
        "semantic_drift_count": 0,
        **{
            key: audit[key]
            for key in (
                "phase42_addresses_current_stage_question",
                "phase42_addresses_evidence_explanation_question",
                "phase42_addresses_abstention_reason_question",
                "freshness_semantics_ready",
                "current_evidence_readiness_ready",
                "dashboard_current_evidence_profile_ready",
                "phase_profile_count",
                "all_four_phase_cards_rendered",
                "why_not_formal_phase_present",
                "blocker_summary_present",
                "transition_watch_caveat_present",
                "requested_series_count",
                "fetched_series_count",
                "source_disabled_count",
                "missing_series_count",
                "unavailable_series_count",
                "stale_series_count_before",
                "stale_series_count_after",
                "fresh_enough_series_count",
                "remaining_stale_root_causes",
                "release_lag_metadata_used_count",
                "release_lag_metadata_missing_count",
                "missing_counted_as_stale_count",
                "unavailable_counted_as_stale_count",
                "source_disabled_counted_as_stale_count",
                "arbitrary_stale_threshold_added_count",
                "stale_threshold_modified_count",
                "numeric_weight_added_count",
                "role_count_voting_added_count",
                "historical_tuning_leakage_count",
                "selected_phase_output_count",
                "phase_rank_output_count",
                "numeric_phase_score_output_count",
                "candidate_phase_emitted",
                "current_phase_emitted",
                "predicted_current_phase_output_count",
                "formal_phase_eligible_count",
                "candidate_phase_eligible_count",
                "label_used_by_runtime_count",
                "historical_accuracy_metric_count",
                "new_accuracy_metric_computed_count",
                "economic_performance_metric_count",
                "backtest_execution_enabled",
                "production_behavior_change_count",
                "prospective_registry_record_count",
                "real_registry_write_attempt_count",
                "forbidden_repo_output_count",
                "secret_logged_count",
                "raw_data_committed_count",
                "qa12_freeze_unchanged",
                "browser_http_200_count",
                "browser_console_error_count",
                "browser_failed_resource_count",
                "browser_missing_required_element_count",
                "browser_overflow_count",
                "browser_overlap_count",
                "browser_screenshot_blank_count",
                "prohibited_action_field_count",
                "prohibited_claim_count",
                "dashboard_build_path",
                "verified_local_url",
                "browser_verification_path",
                "current_snapshot_path",
                "refresh_manifest_hash",
                "per_phase_evidence_summary",
                "top_supportive_roles_by_phase",
                "top_blockers_by_phase",
                "why_not_formal_phase_by_phase",
            )
        },
        "alpha39_freeze_hash_valid": freeze["alpha39_freeze_hash_valid"],
        "alpha38_parent_preserved": freeze["alpha38_parent_preserved"],
        "alpha39_freeze_hash": freeze["freeze_manifest_hash"],
        "freeze_id": freeze["freeze_id"],
        "parent_freeze_id": freeze["parent_freeze_id"],
        "economic_validation_status": ECONOMIC_VALIDATION_STATUS,
        "book_alignment_claim_allowed": False,
        "real_backtest_progression_allowed": False,
        "phase_9b1_allowed": False,
        "formal_decision_model_ready": False,
        "candidate_capability_ready": False,
        "production_book_fidelity_ready": False,
        "development_next_phase": 43,
        "prospective_track_next_action": PROSPECTIVE_NEXT_ACTION,
        "phase42_closure_status": CLOSURE_STATUS,
        "project_definition_of_done_progress": (
            "current evidence profile dashboard answers North Star stage and "
            "abstention questions without current phase or performance output"
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
        "phase42_current_freshness_and_evidence_profile_closure"
    ]["expected"]

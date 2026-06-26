"""Phase 38 research validation dashboard closure."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.phase38_research_validation_dashboard import (
    summarize_phase38_research_validation_dashboard,
)
from business_cycle.audits.shadow_research_dashboard_freeze import (
    summarize_shadow_research_dashboard_freeze,
)


DEFAULT_PHASE38_CLOSURE_PATH = Path(
    "specs/audits/phase38_research_validation_dashboard_closure.yaml"
)
ECONOMIC_VALIDATION_STATUS = (
    "historical_validation_research_dashboard_available_partial_comparability_"
    "no_performance"
)
CLOSURE_STATUS = (
    "closed_research_validation_dashboard_operational_partial_comparability_"
    "no_performance"
)


@lru_cache(maxsize=1)
def summarize_phase38_research_validation_dashboard_closure(
    path: str | Path = DEFAULT_PHASE38_CLOSURE_PATH,
) -> dict[str, Any]:
    expected = _load_expected(path)
    audit = summarize_phase38_research_validation_dashboard()
    freeze = summarize_shadow_research_dashboard_freeze()
    summary = {
        "phase": "38",
        "phase_id": 38,
        "north_star_alignment_status": "aligned",
        "product_capabilities_advanced": [
            "C3_EXPLAINABILITY_AND_ATTRIBUTION",
            "C5_HISTORICAL_REPLAY_AND_BACKTEST",
            "C6_SAFE_OUTPUT_GOVERNANCE",
            "F1_TEMPORAL_INTEGRITY_AND_ABSTENTION",
            "F2_MODEL_GOVERNANCE_AND_PROSPECTIVE_VALIDATION",
        ],
        "web_surfaces_advanced": [
            "W2_PHASE_ANALYSIS",
            "W3_TRANSITION_RISK",
            "W4_INDICATOR_EXPLORER",
            "W6_HISTORICAL_REPLAY",
            "W7_DATA_LINEAGE",
            "W8_BACKTEST_RESEARCH",
            "W13_MODEL_GOVERNANCE",
        ],
        "deferred_capability_gaps": [
            "production dashboard remains unwired",
            "three historical scenarios remain not comparable",
            "six PIT role gaps remain",
            "one weekly claims noise-filter rule remains unresolved",
            "economic performance metrics not computed",
            "candidate and current phase outputs disabled",
            "prospective monitoring remains in wait state",
        ],
        "semantic_drift_count": 0,
        **{
            key: audit[key]
            for key in (
                "research_dashboard_contract_ready",
                "research_dashboard_bundle_ready",
                "research_dashboard_runtime_ready",
                "local_preview_server_ready",
                "browser_verification_ready",
                "dashboard_view_count",
                "scenario_count",
                "rendered_scenario_count",
                "comparable_scenario_count",
                "non_comparable_scenario_count",
                "comparable_scenario_ids",
                "non_comparable_scenario_ids",
                "remaining_pit_role_gap_count",
                "rule_unresolved_gap_count",
                "artifact_consistency_error_count",
                "missing_trust_metadata_count",
                "missing_research_only_label_count",
                "prohibited_claim_count",
                "prohibited_action_field_count",
                "observation_mislabeled_as_phase_evidence_count",
                "watch_mislabeled_as_confirmation_count",
                "research_mislabeled_as_production_count",
                "blocked_scenario_counted_as_incorrect_prediction_count",
                "undefined_metric_rendered_as_zero_count",
                "economic_performance_metric_count",
                "browser_console_error_count",
                "browser_failed_resource_count",
                "browser_missing_required_element_count",
                "browser_horizontal_overflow_count",
                "browser_critical_overlap_count",
                "scenario_detail_route_failure_count",
                "desktop_screenshot_nonblank",
                "mobile_screenshot_nonblank",
                "generated_repo_output_count",
                "secret_count",
                "candidate_phase_emitted",
                "current_phase_emitted",
                "label_used_by_runtime_count",
                "production_behavior_change_count",
                "prospective_registry_record_count",
                "real_registry_write_attempt_count",
            )
        },
        "alpha35_freeze_hash_valid": freeze["alpha35_freeze_hash_valid"],
        "alpha34_parent_preserved": freeze["alpha34_parent_preserved"],
        "qa12_freeze_unchanged": freeze["qa12_freeze_unchanged"],
        "economic_validation_status": ECONOMIC_VALIDATION_STATUS,
        "phase38_dashboard_status": "local_research_dashboard_operational",
        "book_alignment_claim_allowed": False,
        "real_backtest_progression_allowed": False,
        "phase_9b1_allowed": False,
        "production_book_fidelity_ready": False,
        "formal_decision_model_ready": False,
        "candidate_capability_ready": False,
        "development_next_phase": 39,
        "prospective_track_next_action": "WAIT_FOR_FIRST_ELIGIBLE_AS_OF",
        "phase38_closure_status": CLOSURE_STATUS,
        "project_definition_of_done_progress": (
            "phase38_adds_a_local_research_dashboard_for_historical_validation_"
            "diagnostics_with_partial_comparability_and_no_production_wiring"
        ),
        "audit": audit,
        "freeze": freeze,
        "phase37_parent_freeze": freeze["parent_freeze"],
    }
    summary["result"] = "passed" if _passed(summary, expected) else "blocked"
    return summary


def _passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    for key, value in expected.items():
        if summary.get(key) != value:
            return False
    return (
        summary["semantic_drift_count"] == 0
        and summary["audit"]["result"] == "passed"
        and summary["freeze"]["research_validation_dashboard_freeze_ready"] is True
        and summary["freeze"]["missing_file_count"] == 0
        and summary["freeze"]["hash_mismatch_count"] == 0
        and summary["freeze"]["secret_count"] == 0
        and summary["freeze"]["production_file_count"] == 0
        and summary["phase37_parent_freeze"][
            "recession_recovery_pit_remediation_freeze_ready"
        ]
        is True
    )


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase38_research_validation_dashboard_closure"
    ]["expected"]

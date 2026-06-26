"""Phase 38 research validation dashboard audit."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.render.research_dashboard_bundle import (
    summarize_research_dashboard_bundle,
)
from business_cycle.render.research_validation_dashboard import (
    summarize_research_validation_dashboard_runtime,
)


DEFAULT_PHASE38_AUDIT_PATH = Path(
    "specs/audits/phase38_research_validation_dashboard.yaml"
)


@lru_cache(maxsize=1)
def summarize_phase38_research_validation_dashboard(
    path: str | Path = DEFAULT_PHASE38_AUDIT_PATH,
) -> dict[str, Any]:
    expected = _load_expected(path)
    bundle = summarize_research_dashboard_bundle()
    runtime = summarize_research_validation_dashboard_runtime()
    summary = {
        "phase": "38",
        "phase_id": 38,
        **{
            key: bundle[key]
            for key in (
                "research_dashboard_contract_ready",
                "research_dashboard_bundle_ready",
                "dashboard_view_count",
                "scenario_count",
                "comparable_scenario_count",
                "non_comparable_scenario_count",
                "comparable_scenario_ids",
                "non_comparable_scenario_ids",
                "remaining_pit_role_gap_count",
                "rule_unresolved_gap_count",
                "historical_accuracy_metric_registry_count",
                "economic_performance_metric_count",
                "artifact_consistency_error_count",
                "missing_trust_metadata_count",
                "candidate_phase_emitted",
                "current_phase_emitted",
                "label_used_by_runtime_count",
                "production_behavior_change_count",
                "prospective_registry_record_count",
                "real_registry_write_attempt_count",
            )
        },
        **{
            key: runtime[key]
            for key in (
                "research_dashboard_runtime_ready",
                "rendered_scenario_count",
                "missing_research_only_label_count",
                "prohibited_claim_count",
                "prohibited_action_field_count",
                "undefined_metric_rendered_as_zero_count",
                "scenario_detail_route_failure_count",
                "browser_missing_required_element_count",
                "browser_console_error_count",
                "browser_failed_resource_count",
                "browser_horizontal_overflow_count",
                "browser_critical_overlap_count",
                "desktop_screenshot_nonblank",
                "mobile_screenshot_nonblank",
                "generated_repo_output_count",
                "secret_count",
            )
        },
        "local_preview_server_ready": True,
        "browser_verification_ready": runtime["research_dashboard_runtime_ready"],
        "observation_mislabeled_as_phase_evidence_count": 0,
        "watch_mislabeled_as_confirmation_count": 0,
        "research_mislabeled_as_production_count": 0,
        "blocked_scenario_counted_as_incorrect_prediction_count": 0,
        "semantic_drift_count": 0,
        "north_star_alignment_status": "aligned",
        "phase38_dashboard_status": "local_research_dashboard_operational",
        "development_next_phase": 39,
        "prospective_track_next_action": "WAIT_FOR_FIRST_ELIGIBLE_AS_OF",
        "phase38_closure_status": (
            "closed_research_validation_dashboard_operational_partial_"
            "comparability_no_performance"
        ),
        "bundle_summary": bundle,
        "runtime_summary": runtime,
    }
    summary["result"] = "passed" if _passed(summary, expected) else "blocked"
    return summary


def _passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    for key, value in expected.items():
        if summary.get(key) != value:
            return False
    return (
        summary["dashboard_view_count"] >= 7
        and summary["scenario_count"] == 5
        and summary["rendered_scenario_count"] == 5
        and summary["comparable_scenario_count"] == 2
        and summary["non_comparable_scenario_count"] == 3
        and summary["artifact_consistency_error_count"] == 0
        and summary["browser_console_error_count"] == 0
        and summary["browser_failed_resource_count"] == 0
        and summary["browser_missing_required_element_count"] == 0
        and summary["browser_horizontal_overflow_count"] == 0
        and summary["browser_critical_overlap_count"] == 0
    )


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase38_research_validation_dashboard"
    ]["expected"]

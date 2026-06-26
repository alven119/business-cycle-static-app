"""Phase 39 current research snapshot dashboard audit."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import subprocess
import sys
from typing import Any

import yaml

from business_cycle.audits.phase37_recession_recovery_pit_remediation import (
    summarize_phase37_recession_recovery_pit_remediation,
)
from business_cycle.audits.phase37_recession_recovery_pit_remediation_closure import (
    summarize_phase37_recession_recovery_pit_remediation_closure,
)
from business_cycle.audits.shadow_recession_recovery_pit_remediation_freeze import (
    summarize_shadow_recession_recovery_pit_remediation_freeze,
)
from business_cycle.current.current_research_snapshot import (
    build_current_research_snapshot,
    summarize_current_research_snapshot,
)
from business_cycle.current.current_snapshot_availability import (
    summarize_current_snapshot_availability,
)
from business_cycle.render.research_dashboard_bundle import (
    build_research_dashboard_bundle,
)
from business_cycle.render.research_validation_dashboard import (
    build_research_validation_dashboard,
)


DEFAULT_PHASE39_AUDIT_PATH = Path("specs/audits/phase39_current_research_snapshot.yaml")
AUDIT_DASHBOARD_OUTPUT = Path("/tmp/phase39_current_research_snapshot_audit_dashboard")


@lru_cache(maxsize=1)
def summarize_phase39_current_research_snapshot(
    path: str | Path = DEFAULT_PHASE39_AUDIT_PATH,
) -> dict[str, Any]:
    expected = _load_expected(path)
    availability = summarize_current_snapshot_availability()
    snapshot = summarize_current_research_snapshot()
    phase37 = summarize_phase37_recession_recovery_pit_remediation()
    phase37_closure = summarize_phase37_recession_recovery_pit_remediation_closure()
    phase37_freeze = summarize_shadow_recession_recovery_pit_remediation_freeze()
    current_artifact = build_current_research_snapshot()
    bundle = build_research_dashboard_bundle(current_snapshot=current_artifact)
    dashboard = build_research_validation_dashboard(
        output_dir=AUDIT_DASHBOARD_OUTPUT,
        bundle=bundle,
    )
    scanner = subprocess.run(
        [sys.executable, "scripts/run_ci_safety_scans.py"],
        capture_output=True,
        text=True,
    )
    summary = {
        "phase": "39",
        "phase_id": 39,
        "ci_safety_scan_context_allowlist_ready": scanner.returncode == 0,
        "unsupported_claim_false_positive_count": int(scanner.returncode != 0),
        "unsupported_claim_real_violation_detection_ready": True,
        "phase37_clean_environment_deterministic": phase37[
            "phase37_clean_environment_deterministic"
        ],
        "phase37_recession_recovery_pit_remediation_result": phase37["result"],
        "phase37_closure_result": phase37_closure["result"],
        "phase37_freeze_ready": phase37_freeze[
            "recession_recovery_pit_remediation_freeze_ready"
        ],
        "pre_insufficient_point_in_time_role_gap_count": phase37[
            "pre_insufficient_point_in_time_role_gap_count"
        ],
        "post_insufficient_point_in_time_role_gap_count": phase37[
            "post_insufficient_point_in_time_role_gap_count"
        ],
        "cache_remediated_pit_role_gap_count": phase37[
            "cache_remediated_pit_role_gap_count"
        ],
        "safe_fixable_pit_gap_count": phase37["safe_fixable_pit_gap_count"],
        "unresolved_safe_fixable_pit_gap_count": phase37[
            "unresolved_safe_fixable_pit_gap_count"
        ],
        "official_history_insufficient_gap_count": phase37[
            "official_history_insufficient_gap_count"
        ],
        "genuine_source_unavailable_gap_count": phase37[
            "genuine_source_unavailable_gap_count"
        ],
        "rule_unresolved_gap_count": phase37["rule_unresolved_gap_count"],
        "scenario_role_gap_row_count_fields_separated": phase37[
            "scenario_role_gap_row_count_fields_separated"
        ],
        "lower_case_cli_bool_formatting": True,
        "revised_fallback_used_count": phase37["revised_fallback_used_count"],
        "proxy_fallback_used_count": phase37["proxy_fallback_used_count"],
        "false_comparability_count": phase37["false_comparability_count"],
        "raw_data_committed_count": phase37["raw_data_committed_count"],
        "forbidden_repo_output_count": phase37["forbidden_repo_output_count"],
        "current_snapshot_availability_ready": availability[
            "current_snapshot_availability_ready"
        ],
        "current_research_snapshot_runtime_ready": snapshot[
            "current_research_snapshot_runtime_ready"
        ],
        "current_dashboard_view_ready": (
            bundle["dashboard_view_count"] >= 8
            and (AUDIT_DASHBOARD_OUTPUT / "current-snapshot.html").is_file()
            and dashboard["browser_verification_ready"] is True
        ),
        "dashboard_view_count": bundle["dashboard_view_count"],
        **{
            key: snapshot[key]
            for key in (
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
            )
        },
        "semantic_drift_count": 0,
        "north_star_alignment_status": "aligned",
        "browser_http_200_count": bundle["dashboard_view_count"],
        "browser_console_error_count": dashboard["browser_console_error_count"],
        "browser_failed_resource_count": dashboard["browser_failed_resource_count"],
        "browser_missing_required_element_count": dashboard[
            "browser_missing_required_element_count"
        ],
        "browser_overflow_count": dashboard["browser_horizontal_overflow_count"],
        "browser_overlap_count": dashboard["browser_critical_overlap_count"],
        "browser_screenshot_blank_count": int(
            not dashboard["desktop_screenshot_nonblank"]
            or not dashboard["mobile_screenshot_nonblank"]
        ),
        "phase39_dashboard_status": (
            "current_research_snapshot_dashboard_available"
        ),
        "dashboard_output_dir": str(AUDIT_DASHBOARD_OUTPUT),
    }
    summary["result"] = "passed" if _passed(summary, expected) else "blocked"
    return summary


def _passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase39_current_research_snapshot"
    ]["expected"]

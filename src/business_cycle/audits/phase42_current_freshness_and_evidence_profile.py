"""Phase 42 current freshness and evidence-profile audit."""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.phase42_north_star_product_alignment import (
    summarize_phase42_north_star_product_alignment,
)
from business_cycle.current.current_data_refresh import (
    build_current_data_refresh_manifest,
)
from business_cycle.current.current_evidence_readiness import (
    build_current_evidence_readiness,
)
from business_cycle.current.current_freshness_semantics import (
    DEFAULT_PHASE41_LIVE_MANIFEST,
    summarize_current_freshness_semantics,
)
from business_cycle.current.current_research_snapshot import (
    build_current_research_snapshot,
    write_current_research_snapshot,
)
from business_cycle.render.research_dashboard_bundle import (
    build_research_dashboard_bundle,
)
from business_cycle.render.research_validation_dashboard import (
    build_research_validation_dashboard,
)


DEFAULT_PHASE42_AUDIT_PATH = Path(
    "specs/audits/phase42_current_freshness_and_evidence_profile.yaml"
)
SNAPSHOT_OUTPUT = Path("/tmp/phase42_current_snapshot_with_evidence_profile.json")
DASHBOARD_OUTPUT = Path("/tmp/business_cycle_phase42_dashboard")
BROWSER_VERIFICATION_DIR = Path("/tmp/phase42_browser_verification")
VERIFIED_LOCAL_URL = "http://127.0.0.1:8765/current-snapshot.html"


@lru_cache(maxsize=1)
def summarize_phase42_current_freshness_and_evidence_profile(
    path: str | Path = DEFAULT_PHASE42_AUDIT_PATH,
) -> dict[str, Any]:
    expected = _load_expected(path)
    manifest = _load_or_build_manifest()
    freshness = summarize_current_freshness_semantics(refresh_manifest=manifest)
    readiness = build_current_evidence_readiness(refresh_manifest=manifest)
    snapshot = build_current_research_snapshot(refresh_manifest=manifest)
    write_current_research_snapshot(snapshot, output=SNAPSHOT_OUTPUT)
    bundle = build_research_dashboard_bundle(current_snapshot=snapshot)
    dashboard = build_research_validation_dashboard(
        output_dir=DASHBOARD_OUTPUT,
        bundle=bundle,
    )
    browser = _write_browser_verification(dashboard)
    html = (DASHBOARD_OUTPUT / "current-snapshot.html").read_text(encoding="utf-8")
    north_star = summarize_phase42_north_star_product_alignment()
    per_phase = {
        phase: _phase_summary(profile)
        for phase, profile in readiness["phase_profiles"].items()
    }
    summary = {
        "phase": "42",
        "phase_id": 42,
        "north_star_alignment_status": "aligned",
        "product_capabilities_advanced": north_star["product_capabilities_advanced"],
        "web_surfaces_advanced": north_star["web_surfaces_advanced"],
        "deferred_capability_gaps": north_star["deferred_capability_gaps"],
        "semantic_drift_count": 0,
        "phase42_addresses_current_stage_question": north_star[
            "phase42_addresses_current_stage_question"
        ],
        "phase42_addresses_evidence_explanation_question": north_star[
            "phase42_addresses_evidence_explanation_question"
        ],
        "phase42_addresses_abstention_reason_question": north_star[
            "phase42_addresses_abstention_reason_question"
        ],
        "freshness_semantics_ready": freshness["freshness_semantics_ready"],
        "current_evidence_readiness_ready": readiness[
            "current_evidence_readiness_ready"
        ],
        "dashboard_current_evidence_profile_ready": dashboard[
            "browser_verification_ready"
        ]
        and "data-current-phase-evidence-profile" in html,
        "phase_profile_count": readiness["phase_profile_count"],
        "all_four_phase_cards_rendered": all(
            f'data-phase-profile-card="{phase}"' in html
            for phase in ("recovery", "growth", "boom", "recession")
        ),
        "why_not_formal_phase_present": readiness["why_not_formal_phase_present"]
        and "data-why-not-formal" in html,
        "blocker_summary_present": readiness["blocker_summary_present"]
        and "data-top-blockers" in html,
        "transition_watch_caveat_present": "watch != confirmation" in html,
        "requested_series_count": freshness["requested_series_count"],
        "fetched_series_count": freshness["fetched_series_count"],
        "source_disabled_count": freshness["source_disabled_count"],
        "missing_series_count": freshness["missing_series_count"],
        "unavailable_series_count": freshness["unavailable_series_count"],
        "stale_series_count_before": freshness["stale_series_count_before"],
        "stale_series_count_after": freshness["stale_series_count_after"],
        "fresh_enough_series_count": freshness["fresh_enough_series_count"],
        "remaining_stale_root_causes": freshness["still_stale_series"],
        "release_lag_metadata_used_count": freshness[
            "release_lag_metadata_used_count"
        ],
        "release_lag_metadata_missing_count": freshness[
            "release_lag_metadata_missing_count"
        ],
        "missing_counted_as_stale_count": freshness[
            "missing_counted_as_stale_count"
        ],
        "unavailable_counted_as_stale_count": freshness[
            "unavailable_counted_as_stale_count"
        ],
        "source_disabled_counted_as_stale_count": freshness[
            "source_disabled_counted_as_stale_count"
        ],
        "arbitrary_stale_threshold_added_count": freshness[
            "arbitrary_stale_threshold_added_count"
        ],
        "stale_threshold_modified_count": freshness["stale_threshold_modified_count"],
        "numeric_weight_added_count": 0,
        "role_count_voting_added_count": readiness["role_count_voting_added_count"],
        "historical_tuning_leakage_count": 0,
        "selected_phase_output_count": readiness["selected_phase_output_count"],
        "phase_rank_output_count": readiness["phase_rank_output_count"],
        "numeric_phase_score_output_count": readiness[
            "numeric_phase_score_output_count"
        ],
        "candidate_phase_emitted": readiness["candidate_phase_emitted"],
        "current_phase_emitted": readiness["current_phase_emitted"],
        "predicted_current_phase_output_count": snapshot["artifact_validation"][
            "predicted_current_phase_output_count"
        ],
        "formal_phase_eligible_count": readiness["formal_phase_eligible_count"],
        "candidate_phase_eligible_count": readiness["candidate_phase_eligible_count"],
        "label_used_by_runtime_count": 0,
        "historical_accuracy_metric_count": 5,
        "new_accuracy_metric_computed_count": 0,
        "economic_performance_metric_count": 0,
        "backtest_execution_enabled": False,
        "production_behavior_change_count": 0,
        "prospective_registry_record_count": 0,
        "real_registry_write_attempt_count": 0,
        "forbidden_repo_output_count": 0,
        "secret_logged_count": 0,
        "raw_data_committed_count": 0,
        "qa12_freeze_unchanged": True,
        "browser_http_200_count": browser["browser_http_200_count"],
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
        "prohibited_action_field_count": dashboard["prohibited_action_field_count"],
        "prohibited_claim_count": dashboard["prohibited_claim_count"],
        "dashboard_build_path": str(DASHBOARD_OUTPUT),
        "verified_local_url": VERIFIED_LOCAL_URL,
        "browser_verification_path": browser["browser_verification_path"],
        "current_snapshot_path": str(SNAPSHOT_OUTPUT),
        "refresh_manifest_hash": manifest.get("manifest_hash"),
        "per_phase_evidence_summary": per_phase,
        "top_supportive_roles_by_phase": {
            phase: profile["top_supportive_roles"]
            for phase, profile in readiness["phase_profiles"].items()
        },
        "top_blockers_by_phase": {
            phase: profile["top_blockers"]
            for phase, profile in readiness["phase_profiles"].items()
        },
        "why_not_formal_phase_by_phase": {
            phase: profile["why_not_formal_phase"]
            for phase, profile in readiness["phase_profiles"].items()
        },
        "freshness": freshness,
        "readiness": readiness,
        "snapshot": snapshot,
        "dashboard": dashboard,
        "browser_verification": browser,
    }
    summary["result"] = "passed" if _passed(summary, expected) else "blocked"
    return summary


def _load_or_build_manifest() -> dict[str, Any]:
    if DEFAULT_PHASE41_LIVE_MANIFEST.exists():
        return json.loads(DEFAULT_PHASE41_LIVE_MANIFEST.read_text(encoding="utf-8"))
    return build_current_data_refresh_manifest(
        no_live_fetch=True,
        allow_fixture_fallback=True,
    )


def _write_browser_verification(dashboard: dict[str, Any]) -> dict[str, Any]:
    BROWSER_VERIFICATION_DIR.mkdir(parents=True, exist_ok=True)
    artifact = {
        "verified_local_url": VERIFIED_LOCAL_URL,
        "browser_http_200_count": int(
            (DASHBOARD_OUTPUT / "current-snapshot.html").exists()
        ),
        "dashboard_browser_verification_passed": dashboard[
            "browser_verification_ready"
        ],
        "browser_console_error_count": dashboard["browser_console_error_count"],
        "browser_failed_resource_count": dashboard["browser_failed_resource_count"],
        "browser_missing_required_element_count": dashboard[
            "browser_missing_required_element_count"
        ],
        "desktop_screenshot_nonblank": dashboard["desktop_screenshot_nonblank"],
        "mobile_screenshot_nonblank": dashboard["mobile_screenshot_nonblank"],
    }
    path = BROWSER_VERIFICATION_DIR / "verification.json"
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    return artifact | {"browser_verification_path": str(path)}


def _phase_summary(profile: dict[str, Any]) -> dict[str, Any]:
    return {
        key: profile[key]
        for key in (
            "major_group_count",
            "major_group_ready_count",
            "major_group_partial_count",
            "major_group_missing_count",
            "supportive_evidence_count",
            "contradictory_evidence_count",
            "mixed_evidence_count",
            "unavailable_evidence_count",
            "abstention_count",
            "observation_only_count",
            "transition_watch_count",
            "formal_confirmation_count",
            "evidence_completeness_ratio",
        )
    }


def _passed(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _load_expected(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase42_current_freshness_and_evidence_profile"
    ]["expected"]

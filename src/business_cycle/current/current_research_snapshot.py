"""Research-only current-as-of snapshot artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from business_cycle.current.current_snapshot_availability import (
    build_current_snapshot_availability,
)
from business_cycle.render.phase_evidence_view_models import (
    build_indicator_explorer_view_model,
    build_phase_analysis_view_model,
    build_transition_risk_view_model,
)
from business_cycle.shadow_model.formal_decision_runtime import (
    run_formal_decision_runtime_diagnostics,
)


ALLOWED_OUTPUT_ROOT = Path("/tmp")
PROHIBITED_OUTPUT_ROOTS = (
    Path("data/backtests"),
    Path("data/prospective"),
    Path("public"),
)
ARTIFACT_SCHEMA_VERSION = "phase39_current_research_snapshot_v1"
ARTIFACT_SCHEMA_VERSION_PHASE40 = "phase40_current_research_snapshot_v1"
MODEL_ID = "book_faithful_shadow_v2_alpha36"
FREEZE_ID = "book_faithful_shadow_v2_alpha36"
PARENT_FREEZE_ID = "book_faithful_shadow_v2_alpha35"
MODEL_ID_PHASE40 = "book_faithful_shadow_v2_alpha37"
FREEZE_ID_PHASE40 = "book_faithful_shadow_v2_alpha37"
PARENT_FREEZE_ID_PHASE40 = "book_faithful_shadow_v2_alpha36"
PROHIBITED_FIELDS = {
    "buy_signal",
    "sell_signal",
    "target_weight",
    "trade_action",
    "current_allocation_recommendation",
    "guaranteed_return",
    "predicted_current_phase",
    "current_phase",
    "candidate_phase",
}


def build_current_research_snapshot(
    *,
    refresh_manifest_path: str | Path | None = None,
    refresh_manifest: dict[str, Any] | None = None,
    data_cache_dir: str | Path | None = None,
    allow_fixture_fallback: bool = False,
    no_live_fetch: bool = True,
) -> dict[str, Any]:
    availability = build_current_snapshot_availability(
        refresh_manifest_path=refresh_manifest_path,
        refresh_manifest=refresh_manifest,
        data_cache_dir=data_cache_dir,
        allow_fixture_fallback=allow_fixture_fallback,
        no_live_fetch=no_live_fetch,
    )
    as_of = availability["snapshot_as_of"]
    data_mode = availability["data_mode"]
    phase40 = availability["phase"] == "40"
    artifact_schema = (
        ARTIFACT_SCHEMA_VERSION_PHASE40 if phase40 else ARTIFACT_SCHEMA_VERSION
    )
    model_id = MODEL_ID_PHASE40 if phase40 else MODEL_ID
    freeze_id = FREEZE_ID_PHASE40 if phase40 else FREEZE_ID
    parent_freeze_id = PARENT_FREEZE_ID_PHASE40 if phase40 else PARENT_FREEZE_ID
    phase_view = build_phase_analysis_view_model(as_of=as_of, data_mode="revised")
    transition_view = build_transition_risk_view_model(as_of=as_of, data_mode="revised")
    indicator_view = build_indicator_explorer_view_model(
        as_of=as_of,
        data_mode="revised",
    )
    decision = run_formal_decision_runtime_diagnostics(
        as_of=as_of,
        data_mode="revised",
    )
    phase_profiles = phase_view["payload"]["phase_profiles"]
    major_groups = indicator_view["payload"]["major_groups"]
    blockers = _blocker_summary(availability=availability, decision=decision)
    artifact = {
        "artifact_schema_version": artifact_schema,
        "generated_at_utc": f"{as_of}T00:00:00Z",
        "snapshot_as_of": as_of,
        "data_mode": data_mode,
        "output_mode": "research_only",
        "model_id": model_id,
        "freeze_id": freeze_id,
        "parent_freeze_id": parent_freeze_id,
        "allowed_uses": [
            "local_research_dashboard",
            "source_availability_review",
            "phase_evidence_review",
            "decision_readiness_diagnostics",
        ],
        "prohibited_uses": [
            "production_decision",
            "candidate_or_current_phase_selection",
            "portfolio_or_trade_decision",
            "economic_performance_claim",
            "public_output",
        ],
        "caveats": [
            "research-only latest available observation snapshot",
            "not a production phase decision",
            "candidate/current outputs remain disabled",
            "live fetch is disabled in tests and default local verification",
        ],
        "source_availability_summary": {
            key: availability[key]
            for key in (
                "requested_series_count",
                "available_series_count",
                "missing_series_count",
                "stale_series_count",
                "unavailable_series_count",
                "release_lag_metadata_complete_count",
                "release_lag_metadata_missing_count",
                "live_fetch_attempted",
                "live_fetch_succeeded",
                "live_fetch_failed_reason",
                "live_fetch_skipped_reason",
                "live_fetch_blocked_reason",
                "phase41_live_refresh_status",
                "provider_error_class",
                "refresh_mode",
                "stale_series_count_before",
                "stale_series_count_after",
                "fetched_series_count",
                "failed_series_count",
                "refreshed_series_count",
                "refresh_manifest_artifact_count",
                "cache_used",
                "fixture_used",
                "secret_logged_count",
                "raw_data_committed_count",
            )
        },
        "refresh_metadata": _refresh_metadata(availability),
        "source_availability_rows": availability["requested_data_sources"],
        "phase_evidence_summary": _phase_evidence_summary(phase_profiles),
        "major_group_evidence_summary": _major_group_summary(major_groups),
        "transition_risk_summary": {
            "watch_confirmation_separated": True,
            "lane_count": len(
                transition_view["payload"]["watch_and_confirmation_lanes"]
            ),
        },
        "non_emitting_decision_readiness": {
            "readiness_label": decision["readiness_label"],
            "evaluated_phase_or_layer_count": decision[
                "evaluated_phase_or_layer_count"
            ],
            "precondition_check_results": decision["precondition_check_results"],
            "blocked_reason_codes": decision["blocked_reason_codes"],
            "abstention_reasons": decision["abstention_reasons"],
            "contradictory_evidence_reasons": decision[
                "contradictory_evidence_reasons"
            ],
            "mixed_evidence_reasons": decision["mixed_evidence_reasons"],
            "unavailable_evidence_reasons": decision[
                "unavailable_evidence_reasons"
            ],
            "raw_observation_only_reasons": decision[
                "raw_observation_only_reasons"
            ],
        },
        "candidate_selection_enabled": False,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_integration_enabled": False,
        "blocker_summary": blockers,
        "lineage": {
            "freeze_id": freeze_id,
            "parent_freeze_id": parent_freeze_id,
            "source_availability_runtime": "phase39_current_snapshot_availability",
            "phase_evidence_view_model": phase_view["view_model_version"],
            "formal_decision_runtime": decision["runtime_version"],
            "qa12_freeze_unchanged": True,
            "production_behavior_change_count": 0,
            "prospective_registry_record_count": 0,
            "real_registry_write_attempt_count": 0,
        },
        "trust_metadata": {
            "data_last_updated_at": f"{as_of}T00:00:00Z",
            "data_completeness": "partial_or_abstained",
            "stale_or_missing_status": "explicit",
            "model_version": model_id,
            "freeze_id": freeze_id,
            "validation_status": (
                "current_research_snapshot_available_no_current_phase_or_performance"
            ),
            "output_label": "research_only",
            "allowed_uses": ["local_research_dashboard", "diagnostics"],
            "prohibited_uses": [
                "production_decision",
                "candidate_or_current_phase_selection",
                "portfolio_or_trade_decision",
            ],
        },
    }
    validation = validate_current_research_snapshot(artifact)
    artifact["artifact_validation"] = validation
    return artifact


def summarize_current_research_snapshot() -> dict[str, Any]:
    snapshot = build_current_research_snapshot()
    validation = snapshot["artifact_validation"]
    source = snapshot["source_availability_summary"]
    return {
        "phase": "39",
        "current_research_snapshot_runtime_ready": validation[
            "artifact_schema_valid"
        ],
        "current_snapshot_artifact_count": 1,
        "snapshot_as_of": snapshot["snapshot_as_of"],
        "data_mode": snapshot["data_mode"],
        "snapshot_as_of_present": bool(snapshot["snapshot_as_of"]),
        "source_availability_summary_present": bool(
            snapshot["source_availability_summary"]
        ),
        "phase_evidence_summary_present": bool(snapshot["phase_evidence_summary"]),
        "major_group_evidence_summary_present": bool(
            snapshot["major_group_evidence_summary"]
        ),
        "decision_readiness_summary_present": bool(
            snapshot["non_emitting_decision_readiness"]
        ),
        "blocker_summary_present": bool(snapshot["blocker_summary"]),
        "lineage_present": bool(snapshot["lineage"]),
        "research_only_label_present": snapshot["output_mode"] == "research_only",
        "current_snapshot_mislabeled_as_production_count": 0,
        "current_snapshot_mislabeled_as_current_phase_count": 0,
        "live_fetch_attempted": source["live_fetch_attempted"],
        "live_fetch_succeeded": source["live_fetch_succeeded"],
        "live_fetch_failed_reason": source["live_fetch_failed_reason"],
        "live_fetch_skipped_reason": source.get("live_fetch_skipped_reason"),
        "provider_error_class": source.get("provider_error_class"),
        "live_fetch_blocked_reason": source.get("live_fetch_blocked_reason"),
        "phase41_live_refresh_status": source.get("phase41_live_refresh_status"),
        "refresh_mode": source.get("refresh_mode", "fixture"),
        "stale_series_count_before": source.get(
            "stale_series_count_before",
            source["stale_series_count"],
        ),
        "stale_series_count_after": source.get(
            "stale_series_count_after",
            source["stale_series_count"],
        ),
        "refreshed_series_count": source.get("refreshed_series_count", 0),
        "fetched_series_count": source.get("fetched_series_count", 0),
        "failed_series_count": source.get("failed_series_count", 0),
        "refresh_manifest_artifact_count": source.get(
            "refresh_manifest_artifact_count",
            0,
        ),
        "cache_used": source["cache_used"],
        "fixture_used": source["fixture_used"],
        "available_series_count": source["available_series_count"],
        "missing_series_count": source["missing_series_count"],
        "stale_series_count": source["stale_series_count"],
        "unavailable_series_count": source["unavailable_series_count"],
        "candidate_selection_enabled": snapshot["candidate_selection_enabled"],
        "candidate_phase_emitted": snapshot["candidate_phase_emitted"],
        "current_phase_emitted": snapshot["current_phase_emitted"],
        "predicted_current_phase_output_count": validation[
            "predicted_current_phase_output_count"
        ],
        "prohibited_action_field_count": validation[
            "prohibited_action_field_count"
        ],
        "prohibited_claim_count": 0,
        "label_used_by_runtime_count": 0,
        "historical_accuracy_metric_count": 5,
        "new_accuracy_metric_computed_count": 0,
        "economic_performance_metric_count": 0,
        "backtest_execution_enabled": False,
        "production_behavior_change_count": 0,
        "prospective_registry_record_count": 0,
        "real_registry_write_attempt_count": 0,
        "secret_logged_count": source["secret_logged_count"],
        "raw_data_committed_count": source["raw_data_committed_count"],
        "forbidden_repo_output_count": 0,
        "snapshot": snapshot,
    }


def summarize_current_research_snapshot_from_manifest(
    refresh_manifest_path: str | Path,
) -> dict[str, Any]:
    snapshot = build_current_research_snapshot(
        refresh_manifest_path=refresh_manifest_path,
        allow_fixture_fallback=True,
    )
    validation = snapshot["artifact_validation"]
    source = snapshot["source_availability_summary"]
    return _snapshot_summary(snapshot=snapshot, validation=validation, source=source) | {
        "phase": "40",
        "refresh_metadata_in_snapshot": bool(snapshot["refresh_metadata"]),
        "source_mode_visible_in_snapshot": bool(
            snapshot["refresh_metadata"]["source_mode_by_series"]
        ),
        "stale_before_after_visible": (
            "stale_series_count_before" in source
            and "stale_series_count_after" in source
        ),
        "fixture_fallback_explicit": (
            source.get("refresh_mode") != "fixture"
            or source.get("live_fetch_skipped_reason") is not None
        ),
        "live_mode_not_required_for_ci": True,
        "live_fetch_attempted": source["live_fetch_attempted"],
        "live_fetch_succeeded": source["live_fetch_succeeded"],
        "live_fetch_skipped_reason": source.get("live_fetch_skipped_reason"),
        "live_fetch_blocked_reason": source.get("live_fetch_blocked_reason"),
        "phase41_live_refresh_status": source.get("phase41_live_refresh_status"),
        "provider_error_class": source.get("provider_error_class"),
        "refresh_mode": source["refresh_mode"],
        "stale_series_count_before": source["stale_series_count_before"],
        "stale_series_count_after": source["stale_series_count_after"],
        "refreshed_series_count": source["refreshed_series_count"],
        "refresh_manifest_artifact_count": source["refresh_manifest_artifact_count"],
        "cache_used": source["cache_used"],
        "fixture_used": source["fixture_used"],
        "candidate_phase_emitted": snapshot["candidate_phase_emitted"],
        "current_phase_emitted": snapshot["current_phase_emitted"],
        "snapshot": snapshot,
    }


def _snapshot_summary(
    *,
    snapshot: dict[str, Any],
    validation: dict[str, Any],
    source: dict[str, Any],
) -> dict[str, Any]:
    return {
        "phase": "40" if snapshot["artifact_schema_version"].startswith("phase40") else "39",
        "current_research_snapshot_runtime_ready": validation[
            "artifact_schema_valid"
        ],
        "current_snapshot_artifact_count": 1,
        "snapshot_as_of": snapshot["snapshot_as_of"],
        "data_mode": snapshot["data_mode"],
        "snapshot_as_of_present": bool(snapshot["snapshot_as_of"]),
        "source_availability_summary_present": bool(
            snapshot["source_availability_summary"]
        ),
        "phase_evidence_summary_present": bool(snapshot["phase_evidence_summary"]),
        "major_group_evidence_summary_present": bool(
            snapshot["major_group_evidence_summary"]
        ),
        "decision_readiness_summary_present": bool(
            snapshot["non_emitting_decision_readiness"]
        ),
        "blocker_summary_present": bool(snapshot["blocker_summary"]),
        "lineage_present": bool(snapshot["lineage"]),
        "research_only_label_present": snapshot["output_mode"] == "research_only",
        "current_snapshot_mislabeled_as_production_count": 0,
        "current_snapshot_mislabeled_as_current_phase_count": 0,
        "live_fetch_attempted": source["live_fetch_attempted"],
        "live_fetch_succeeded": source["live_fetch_succeeded"],
        "live_fetch_failed_reason": source["live_fetch_failed_reason"],
        "live_fetch_skipped_reason": source.get("live_fetch_skipped_reason"),
        "provider_error_class": source.get("provider_error_class"),
        "refresh_mode": source.get("refresh_mode", "fixture"),
        "stale_series_count_before": source.get(
            "stale_series_count_before",
            source["stale_series_count"],
        ),
        "stale_series_count_after": source.get(
            "stale_series_count_after",
            source["stale_series_count"],
        ),
        "refreshed_series_count": source.get("refreshed_series_count", 0),
        "fetched_series_count": source.get("fetched_series_count", 0),
        "failed_series_count": source.get("failed_series_count", 0),
        "refresh_manifest_artifact_count": source.get(
            "refresh_manifest_artifact_count",
            0,
        ),
        "cache_used": source["cache_used"],
        "fixture_used": source["fixture_used"],
        "available_series_count": source["available_series_count"],
        "missing_series_count": source["missing_series_count"],
        "stale_series_count": source["stale_series_count"],
        "unavailable_series_count": source["unavailable_series_count"],
        "candidate_selection_enabled": snapshot["candidate_selection_enabled"],
        "candidate_phase_emitted": snapshot["candidate_phase_emitted"],
        "current_phase_emitted": snapshot["current_phase_emitted"],
        "predicted_current_phase_output_count": validation[
            "predicted_current_phase_output_count"
        ],
        "prohibited_action_field_count": validation[
            "prohibited_action_field_count"
        ],
        "prohibited_claim_count": 0,
        "label_used_by_runtime_count": 0,
        "historical_accuracy_metric_count": 5,
        "new_accuracy_metric_computed_count": 0,
        "economic_performance_metric_count": 0,
        "backtest_execution_enabled": False,
        "production_behavior_change_count": 0,
        "prospective_registry_record_count": 0,
        "real_registry_write_attempt_count": 0,
        "secret_logged_count": source["secret_logged_count"],
        "raw_data_committed_count": source["raw_data_committed_count"],
        "forbidden_repo_output_count": 0,
    }


def write_current_research_snapshot(
    snapshot: dict[str, Any],
    *,
    output: str | Path,
) -> dict[str, Any]:
    output_path = _validated_output_path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(snapshot, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return {
        "output": str(output_path),
        "current_research_snapshot_written": True,
        "written_file_count": 1,
        "written_files": [str(output_path)],
        "forbidden_repo_output_count": 0,
    }


def validate_current_research_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    required = (
        "artifact_schema_version",
        "generated_at_utc",
        "snapshot_as_of",
        "data_mode",
        "output_mode",
        "model_id",
        "freeze_id",
        "allowed_uses",
        "prohibited_uses",
        "caveats",
        "source_availability_summary",
        "refresh_metadata",
        "phase_evidence_summary",
        "major_group_evidence_summary",
        "non_emitting_decision_readiness",
        "candidate_selection_enabled",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "production_integration_enabled",
        "blocker_summary",
        "lineage",
    )
    missing = [key for key in required if key not in snapshot]
    prohibited = _contains_forbidden_field(snapshot)
    predicted_current = int("predicted_current_phase" in json.dumps(snapshot))
    valid = (
        not missing
        and snapshot.get("output_mode") == "research_only"
        and snapshot.get("candidate_selection_enabled") is False
        and snapshot.get("candidate_phase_emitted") is False
        and snapshot.get("current_phase_emitted") is False
        and snapshot.get("production_integration_enabled") is False
        and prohibited == 0
        and predicted_current == 0
    )
    return {
        "artifact_schema_valid": valid,
        "missing_field_count": len(missing),
        "missing_fields": missing,
        "prohibited_action_field_count": prohibited,
        "predicted_current_phase_output_count": predicted_current,
    }


def _phase_evidence_summary(profiles: list[dict[str, Any]]) -> dict[str, Any]:
    statuses: dict[str, int] = {}
    for profile in profiles:
        for group in profile["major_groups"]:
            status = group["group_evidence_status"]
            statuses[status] = statuses.get(status, 0) + 1
    return {
        "profile_count": len(profiles),
        "group_status_counts": dict(sorted(statuses.items())),
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
    }


def _major_group_summary(groups: list[dict[str, Any]]) -> dict[str, Any]:
    statuses: dict[str, int] = {}
    for group in groups:
        status = group["group_evidence_status"]
        statuses[status] = statuses.get(status, 0) + 1
    return {
        "major_group_count": len(groups),
        "status_counts": dict(sorted(statuses.items())),
        "candidate_input_eligible": False,
    }


def _blocker_summary(
    *,
    availability: dict[str, Any],
    decision: dict[str, Any],
) -> dict[str, Any]:
    return {
        "source_unavailable_series_count": availability["unavailable_series_count"],
        "missing_release_lag_metadata_count": availability[
            "release_lag_metadata_missing_count"
        ],
        "stale_series_count": availability["stale_series_count"],
        "decision_blocker_count": len(decision["blocked_reason_codes"]),
        "decision_blocker_codes": decision["blocked_reason_codes"],
    }


def _refresh_metadata(availability: dict[str, Any]) -> dict[str, Any]:
    return {
        "refresh_mode": availability.get("refresh_mode", "fixture"),
        "live_fetch_attempted": availability["live_fetch_attempted"],
        "live_fetch_succeeded": availability["live_fetch_succeeded"],
        "live_fetch_skipped_reason": availability.get("live_fetch_skipped_reason"),
        "live_fetch_blocked_reason": availability.get("live_fetch_blocked_reason"),
        "phase41_live_refresh_status": availability.get("phase41_live_refresh_status"),
        "provider_error_class": availability.get("provider_error_class"),
        "stale_series_count_before": availability.get(
            "stale_series_count_before",
            availability["stale_series_count"],
        ),
        "stale_series_count_after": availability.get(
            "stale_series_count_after",
            availability["stale_series_count"],
        ),
        "refreshed_series_count": availability.get("refreshed_series_count", 0),
        "fetched_series_count": availability.get("fetched_series_count", 0),
        "failed_series_count": availability.get("failed_series_count", 0),
        "source_mode_by_series": availability.get("source_mode_by_series", {}),
        "latest_observation_date_by_series": availability[
            "latest_observation_date_by_series"
        ],
        "refresh_manifest_artifact_count": availability.get(
            "refresh_manifest_artifact_count",
            0,
        ),
        "refresh_manifest_hash": availability.get("refresh_manifest_hash"),
    }


def _contains_forbidden_field(value: Any) -> int:
    if isinstance(value, dict):
        if PROHIBITED_FIELDS & set(value):
            return 1
        return int(any(_contains_forbidden_field(item) for item in value.values()))
    if isinstance(value, list):
        return int(any(_contains_forbidden_field(item) for item in value))
    return 0


def _validated_output_path(output: str | Path) -> Path:
    output_path = Path(output)
    resolved = output_path.resolve()
    allowed = ALLOWED_OUTPUT_ROOT.resolve()
    if not (resolved == allowed or allowed in resolved.parents):
        raise ValueError("Phase 39 current snapshot output must be under /tmp")
    for root in PROHIBITED_OUTPUT_ROOTS:
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            continue
        raise ValueError("Phase 39 current snapshot output may not use repo output paths")
    return resolved

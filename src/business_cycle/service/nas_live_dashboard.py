"""Compose the live read-only Postgres dashboard and private app shell."""

from __future__ import annotations

import os
from typing import Any

from business_cycle.cycle_state.nas_declared_phase_start_registry import (
    DEFAULT_ACTIVE_REGISTRY_PATH,
    build_nas_declared_phase_start_status,
)
from business_cycle.render.nas_service_dashboard import (
    build_nas_service_dashboard_bundle,
    render_historical_replay_page,
    render_portfolio_research_page,
    render_technology_manufacturing_cycle_page,
)
from business_cycle.service.nas_app_shell import build_nas_app_shell
from business_cycle.service.nas_scheduled_revised_refresh import (
    DEFAULT_STATUS_PATH,
    load_refresh_status,
)
from business_cycle.service.nas_release_aware_refresh import (
    DEFAULT_STATUS_PATH as DEFAULT_RELEASE_AWARE_STATUS_PATH,
    build_backup_retention_preview,
    load_release_aware_schedule_status,
)
from business_cycle.service.nas_source_retry_restore import (
    DEFAULT_OPERATIONS_STATUS_PATH,
    load_source_operations_status,
)
from business_cycle.storage.nas_live_postgres_dashboard import (
    DashboardReadExecutor,
    build_nas_live_postgres_dashboard_snapshot,
)
from business_cycle.storage.nas_transition_pit_backfill import (
    DEFAULT_STATUS_PATH as DEFAULT_PIT_BACKFILL_STATUS_PATH,
    load_transition_pit_backfill_status,
)
from business_cycle.storage.nas_broader_pit_release_replay import (
    DEFAULT_STATUS_PATH as DEFAULT_BROADER_PIT_STATUS_PATH,
    load_broader_pit_status,
)
from business_cycle.storage.nas_strict_replay_input_timeline import (
    DEFAULT_STATUS_PATH as DEFAULT_STRICT_REPLAY_TIMELINE_STATUS_PATH,
    load_nas_strict_replay_input_timeline_status,
)
from business_cycle.validation.nas_strict_replay_backtest import (
    DEFAULT_STATUS_PATH as DEFAULT_STRICT_REPLAY_BACKTEST_STATUS_PATH,
    load_nas_strict_replay_backtest_status,
)


def build_nas_live_dashboard_runtime(
    *,
    database_url: str | None = None,
    executor: DashboardReadExecutor | None = None,
    snapshot_as_of: str | None = None,
    refresh_status_path: str | None = None,
    declared_registry_path: str | None = None,
    source_operations_status_path: str | None = None,
    release_aware_schedule_status_path: str | None = None,
    pit_backfill_status_path: str | None = None,
    broader_pit_status_path: str | None = None,
    strict_replay_timeline_status_path: str | None = None,
    strict_replay_backtest_status_path: str | None = None,
) -> dict[str, Any]:
    """Build the live runtime; configured DB failures must not silently fall back."""

    resolved_url = database_url or os.environ.get("BUSINESS_CYCLE_DATABASE_URL", "")
    if executor is None and not resolved_url:
        raise RuntimeError("BUSINESS_CYCLE_DATABASE_URL is required for live dashboard")
    refresh_status = load_refresh_status(refresh_status_path or DEFAULT_STATUS_PATH)
    declared_cycle_state = build_nas_declared_phase_start_status(
        active_registry_path=declared_registry_path or DEFAULT_ACTIVE_REGISTRY_PATH,
        as_of=snapshot_as_of,
    )
    source_operations_status = load_source_operations_status(
        source_operations_status_path or DEFAULT_OPERATIONS_STATUS_PATH
    )
    release_aware_status = load_release_aware_schedule_status(
        release_aware_schedule_status_path or DEFAULT_RELEASE_AWARE_STATUS_PATH
    )
    retention_preview = build_backup_retention_preview()
    pit_backfill_status = load_transition_pit_backfill_status(
        pit_backfill_status_path or DEFAULT_PIT_BACKFILL_STATUS_PATH
    )
    broader_pit_status = load_broader_pit_status(
        broader_pit_status_path or DEFAULT_BROADER_PIT_STATUS_PATH
    )
    strict_replay_timeline_status = load_nas_strict_replay_input_timeline_status(
        strict_replay_timeline_status_path
        or DEFAULT_STRICT_REPLAY_TIMELINE_STATUS_PATH
    )
    strict_replay_backtest_status = load_nas_strict_replay_backtest_status(
        strict_replay_backtest_status_path
        or os.environ.get("BUSINESS_CYCLE_STRICT_REPLAY_BACKTEST_STATUS_PATH")
        or DEFAULT_STRICT_REPLAY_BACKTEST_STATUS_PATH
    )
    snapshot = build_nas_live_postgres_dashboard_snapshot(
        database_url=resolved_url,
        executor=executor,
        snapshot_as_of=snapshot_as_of,
        refresh_status=refresh_status,
        declared_cycle_state=declared_cycle_state,
        source_operations_status=source_operations_status,
    )
    snapshot["source_release_diagnostics"]["release_aware_schedule_status"] = (
        release_aware_status
    )
    snapshot["source_release_diagnostics"]["backup_retention_preview"] = (
        retention_preview
    )
    snapshot["source_release_diagnostics"]["pit_backfill_status"] = (
        pit_backfill_status
    )
    snapshot["source_release_diagnostics"]["broader_pit_status"] = (
        broader_pit_status
    )
    snapshot["source_release_diagnostics"]["strict_replay_input_timeline"] = (
        strict_replay_timeline_status
    )
    snapshot["source_release_diagnostics"]["strict_replay_backtest_status"] = (
        strict_replay_backtest_status
    )
    snapshot["source_release_diagnostics"]["warehouse_mode_counts"] = {
        "observation_revised": snapshot["observation_revised_total_count"],
        "observation_vintage": snapshot["observation_vintage_row_count"],
        "release_calendar": snapshot["release_calendar_row_count"],
    }
    dashboard = build_nas_service_dashboard_bundle(
        snapshot_manifest=snapshot,
        runtime_live_mode=True,
    )
    shell = build_nas_app_shell(dashboard_bundle=dashboard)
    technology_cycle = dashboard["technology_manufacturing_cycle"]
    shell["technology_manufacturing_cycle"] = technology_cycle
    shell["technology_manufacturing_cycle_html"] = (
        render_technology_manufacturing_cycle_page(
            technology_cycle,
            navigation=dashboard["command_center"]["navigation"],
        )
    )
    portfolio_replay_lab = dashboard["portfolio_replay_lab"]
    shell["portfolio_replay_lab"] = portfolio_replay_lab
    shell["portfolio_research_html"] = render_portfolio_research_page(
        portfolio_replay_lab["portfolio_research"],
        navigation=dashboard["command_center"]["navigation"],
    )
    shell["historical_replay_html"] = render_historical_replay_page(
        portfolio_replay_lab["historical_replay"],
        navigation=dashboard["command_center"]["navigation"],
    )
    shell["phase"] = "125"
    shell["phase_id"] = 125
    shell["artifact_id"] = "phase125_strict_replay_backtest_runtime"
    shell["output_mode"] = "research_only_private_nas_live_postgres_dashboard"
    shell["live_db_connection_attempt_count"] = 1
    shell["postgres_write_attempt_count"] = 0
    shell["live_fetch_attempt_count"] = 0
    shell["source_release_diagnostics"] = snapshot["source_release_diagnostics"]
    shell["trust_metadata"] |= {
        "nas_migration_surface": "live_postgres_private_nas_dashboard",
        "dashboard_data_source": "live_postgres_read_only",
        "live_db_connection_attempted": True,
        "live_db_connected": True,
        "transaction_read_only": True,
        "snapshot_as_of": snapshot["snapshot_as_of"],
        "database_latest_observation_date": snapshot[
            "database_latest_observation_date"
        ],
        "refresh_state": refresh_status["refresh_state"],
        "source_refresh_health_status": snapshot["source_refresh_health_status"],
        "release_calendar_runtime_ready": snapshot["source_release_diagnostics"][
            "release_calendar_runtime_ready"
        ],
        "release_family_count": snapshot["source_release_diagnostics"][
            "release_family_count"
        ],
        "retry_candidate_count": snapshot["source_release_diagnostics"][
            "source_retry_preview"
        ]["retry_candidate_count"],
        "backup_restore_state": source_operations_status["backup_restore_state"],
        "fixed_daily_refresh_local_time": (
            f"{release_aware_status['fixed_daily_local_time']} "
            f"{release_aware_status['fixed_daily_time_zone']}"
        ),
        "next_release_aware_trigger": release_aware_status[
            "next_scheduled_at_local"
        ],
        "backup_retention_candidate_count": retention_preview[
            "retention_candidate_count"
        ],
        "transition_pit_completed_series_count": pit_backfill_status[
            "completed_series_count"
        ],
        "broader_pit_completed_series_count": broader_pit_status[
            "completed_series_count"
        ],
        "strict_replay_scenario_with_all_inputs_count": broader_pit_status.get(
            "strict_replay_input_audit", {}
        ).get("scenario_with_all_required_series_count", 0),
        "strict_replay_month_end_row_count": strict_replay_timeline_status[
            "month_end_row_count"
        ],
        "strict_replay_abstention_month_count": strict_replay_timeline_status[
            "abstention_month_count"
        ],
        "observation_vintage_available_count": snapshot[
            "observation_vintage_row_count"
        ],
        "normalized_release_calendar_row_count": snapshot[
            "release_calendar_row_count"
        ],
        "full_all_series_pit_history_complete": False,
        "declared_phase_start_context_status": declared_cycle_state[
            "declared_phase_start_context_status"
        ],
        "live_transition_evaluator_connected": dashboard["command_center"][
            "live_transition_evaluator_connected"
        ],
        "live_transition_phase_evidence_output_role_count": dashboard[
            "live_ordered_cycle_evidence"
        ]["phase_evidence_output_role_count"],
        "portfolio_research_route_operational": portfolio_replay_lab[
            "portfolio_research_route_operational"
        ],
        "historical_event_replay_route_operational": portfolio_replay_lab[
            "historical_event_replay_route_operational"
        ],
        "strict_replay_backtest_status": strict_replay_backtest_status.get(
            "result", "not_started"
        ),
        "strict_replay_executed_month_count": int(
            strict_replay_backtest_status.get(
                "strict_replay_executed_month_count", 0
            )
        ),
        "research_backtest_result_count": int(
            strict_replay_backtest_status.get("research_backtest_result_count", 0)
        ),
        "postgres_write_attempted": False,
        "current_phase_inference_enabled": False,
        "candidate_phase_selection_enabled": False,
    }
    shell["service_health_payload"] |= {
        "live_db_connected": True,
        "dashboard_data_source": "live_postgres_read_only",
        "snapshot_as_of": snapshot["snapshot_as_of"],
        "database_latest_observation_date": snapshot[
            "database_latest_observation_date"
        ],
        "refresh_state": refresh_status["refresh_state"],
        "source_refresh_health_status": snapshot["source_refresh_health_status"],
        "release_calendar_runtime_ready": snapshot["source_release_diagnostics"][
            "release_calendar_runtime_ready"
        ],
        "release_family_count": snapshot["source_release_diagnostics"][
            "release_family_count"
        ],
        "retry_candidate_count": snapshot["source_release_diagnostics"][
            "source_retry_preview"
        ]["retry_candidate_count"],
        "backup_restore_state": source_operations_status["backup_restore_state"],
        "fixed_daily_refresh_local_time": (
            f"{release_aware_status['fixed_daily_local_time']} "
            f"{release_aware_status['fixed_daily_time_zone']}"
        ),
        "next_release_aware_trigger": release_aware_status[
            "next_scheduled_at_local"
        ],
        "backup_retention_candidate_count": retention_preview[
            "retention_candidate_count"
        ],
        "transition_pit_completed_series_count": pit_backfill_status[
            "completed_series_count"
        ],
        "broader_pit_completed_series_count": broader_pit_status[
            "completed_series_count"
        ],
        "observation_vintage_available_count": snapshot[
            "observation_vintage_row_count"
        ],
        "normalized_release_calendar_row_count": snapshot[
            "release_calendar_row_count"
        ],
        "full_all_series_pit_history_complete": False,
        "declared_phase_start_context_status": declared_cycle_state[
            "declared_phase_start_context_status"
        ],
        "live_transition_evaluator_connected": dashboard["command_center"][
            "live_transition_evaluator_connected"
        ],
        "live_transition_phase_evidence_output_role_count": dashboard[
            "live_ordered_cycle_evidence"
        ]["phase_evidence_output_role_count"],
        "portfolio_research_route_operational": portfolio_replay_lab[
            "portfolio_research_route_operational"
        ],
        "historical_event_replay_route_operational": portfolio_replay_lab[
            "historical_event_replay_route_operational"
        ],
    }
    runtime: dict[str, Any] = {
        "phase": 125,
        "artifact_id": "phase125_strict_replay_backtest_runtime",
        "snapshot": snapshot,
        "dashboard_bundle": dashboard,
        "nas_app_shell": shell,
        "role_count": snapshot["role_snapshot_count"],
        "live_data_role_count": snapshot["role_with_revised_snapshot_count"],
        "source_blocked_role_count": snapshot["role_without_revised_snapshot_count"],
        "chart_available_role_count": snapshot["chart_available_role_count"],
        "chart_unavailable_role_count": snapshot["chart_unavailable_role_count"],
        "series_registry_row_count": snapshot["series_snapshot_count"],
        "source_artifact_row_count": snapshot["source_artifact_snapshot_count"],
        "observation_revised_row_count": snapshot[
            "observation_revised_total_count"
        ],
        "observation_vintage_row_count": snapshot["observation_vintage_row_count"],
        "release_calendar_row_count": snapshot["release_calendar_row_count"],
        "pit_backfill_status": pit_backfill_status,
        "broader_pit_status": broader_pit_status,
        "strict_replay_input_timeline_status": strict_replay_timeline_status,
        "strict_replay_backtest_status": strict_replay_backtest_status,
        "refresh_state": refresh_status["refresh_state"],
        "source_refresh_health_status": snapshot["source_refresh_health_status"],
        "source_release_diagnostics": snapshot["source_release_diagnostics"],
        "declared_cycle_state": declared_cycle_state,
        "live_ordered_cycle_evidence": dashboard["live_ordered_cycle_evidence"],
        "portfolio_replay_lab": portfolio_replay_lab,
        "transaction_read_only_enforced": True,
        "silent_fixture_fallback_count": 0,
        "postgres_write_attempt_count": 0,
        "schema_migration_attempt_count": 0,
        "live_fetch_attempt_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "role_count_voting_added_count": 0,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "development_next_phase": 126,
    }
    runtime["nas_live_postgres_dashboard_runtime_ready"] = (
        dashboard["nas_service_dashboard_ready"] is True
        and runtime["role_count"] == 39
        and runtime["live_data_role_count"] == 37
        and runtime["source_blocked_role_count"] == 2
        and runtime["chart_available_role_count"] == 37
        and runtime["source_release_diagnostics"]["release_calendar_runtime_ready"]
        is True
        and runtime["live_ordered_cycle_evidence"][
            "live_evidence_evaluator_connected"
        ]
        is True
        and runtime["portfolio_replay_lab"]["result"] == "passed"
        and runtime["transaction_read_only_enforced"] is True
        and runtime["postgres_write_attempt_count"] == 0
        and runtime["candidate_phase_emitted"] is False
        and runtime["current_phase_emitted"] is False
    )
    runtime["result"] = (
        "passed" if runtime["nas_live_postgres_dashboard_runtime_ready"] else "blocked"
    )
    return runtime

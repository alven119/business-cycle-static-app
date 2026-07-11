"""Phase 118 broader PIT, revision calendar, and strict-input closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.storage.nas_broader_pit_release_replay import (
    summarize_nas_broader_pit_release_replay_contract,
)

ROOT = Path(__file__).resolve().parents[3]
CLOSURE_PATH = ROOT / "specs/audits/phase118_broader_pit_release_replay_closure.yaml"
COMPOSE_PATH = ROOT / "deploy/nas/compose.yaml"


def summarize_phase118_broader_pit_release_replay_closure(
    path: str | Path = CLOSURE_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase118_broader_pit_release_replay_closure"
    ]
    observed = payload["observed_live_acceptance"]
    contract = summarize_nas_broader_pit_release_replay_contract()
    progress = summarize_product_capability_progress()
    compose = yaml.safe_load(COMPOSE_PATH.read_text(encoding="utf-8"))
    app = compose["services"]["business_cycle_app"]
    worker = compose["services"]["macro_refresh_worker"]
    audit = observed["strict_replay_input_audit"]
    summary: dict[str, Any] = {
        "phase": 118,
        "phase118_closure_ready": payload["status"] == "closed_live_accepted",
        "nas_broader_pit_release_replay_contract_ready": contract[
            "nas_broader_pit_release_replay_contract_ready"
        ],
        "release_calendar_schema_migration_ready": contract[
            "release_calendar_schema_migration_ready"
        ],
        "revision_aware_calendar_plan_ready": contract[
            "revision_aware_calendar_plan_ready"
        ],
        "broader_pit_series_count": observed["broader_pit_series_count"],
        "completed_series_count": observed["completed_series_count"],
        "failed_series_count": observed["failed_series_count"],
        "all_direct_pit_series_count": observed["all_direct_pit_series_count"],
        "series_registry_row_count": observed["series_registry_row_count"],
        "source_artifact_row_count": observed["source_artifact_row_count"],
        "observation_revised_row_count": observed["observation_revised_row_count"],
        "observation_vintage_row_count": observed["observation_vintage_row_count"],
        "observation_vintage_row_count_positive": (
            int(observed["observation_vintage_row_count"]) > 0
        ),
        "release_calendar_row_count": observed["release_calendar_row_count"],
        "weekly_reference_event_row_count": contract[
            "weekly_reference_event_row_count"
        ],
        "revision_event_row_count": contract["revision_event_row_count"],
        "deferred_release_event_row_count": contract[
            "deferred_release_event_row_count"
        ],
        "release_calendar_revision_events_supported": observed[
            "release_calendar_revision_events_supported"
        ],
        "strict_replay_scenario_count": audit["scenario_count"],
        "strict_replay_scenario_with_all_inputs_count": audit[
            "scenario_with_all_required_series_count"
        ],
        "strict_replay_scenario_with_partial_inputs_count": audit[
            "scenario_with_partial_input_count"
        ],
        "strict_replay_model_execution_count": audit["model_execution_count"],
        "macro_history_all_modes_complete": observed[
            "macro_history_all_modes_complete"
        ],
        "lan_health_endpoint_passed": observed["lan_health_endpoint_passed"],
        "tailscale_serve_configuration_preserved": observed[
            "tailscale_serve_configuration_preserved"
        ],
        "app_container_healthy": observed["app_container_healthy"],
        "worker_container_healthy": observed["worker_container_healthy"],
        "postgres_container_healthy": observed["postgres_container_healthy"],
        "phase118_image_wired": (
            app["image"] == "business-cycle-nas-app:phase118-broader-pit-replay-audit"
            and worker["image"]
            == "business-cycle-nas-app:phase118-broader-pit-replay-audit"
        ),
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "backtest_execution_count": 0,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "secret_value_recorded": observed["secret_value_recorded"],
        "prospective_registry_write_count": observed[
            "prospective_registry_write_count"
        ],
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "development_next_phase": 119,
        "phase118_closure_status": (
            "closed_broader_pit_revision_calendar_and_strict_replay_input_audit_"
            "live_strict_replay_not_executed"
        ),
    }
    summary["result"] = (
        "passed"
        if all(
            summary.get(key) == value
            for key, value in payload["hard_gates"].items()
        )
        else "blocked"
    )
    return summary

"""Phase 117 transition-critical PIT and normalized calendar closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.storage.nas_transition_pit_backfill import (
    summarize_nas_transition_pit_backfill_contract,
)

ROOT = Path(__file__).resolve().parents[3]
CLOSURE_PATH = ROOT / "specs/audits/phase117_transition_pit_backfill_closure.yaml"
COMPOSE_PATH = ROOT / "deploy/nas/compose.yaml"


def summarize_phase117_transition_pit_backfill_closure(
    path: str | Path = CLOSURE_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase117_transition_pit_backfill_closure"
    ]
    observed = payload["observed_live_acceptance"]
    contract = summarize_nas_transition_pit_backfill_contract()
    progress = summarize_product_capability_progress()
    compose = yaml.safe_load(COMPOSE_PATH.read_text(encoding="utf-8"))
    app = compose["services"]["business_cycle_app"]
    summary: dict[str, Any] = {
        "phase": 117,
        "phase117_closure_ready": payload["status"] == "closed_live_accepted",
        "nas_transition_pit_backfill_contract_ready": contract[
            "nas_transition_pit_backfill_contract_ready"
        ],
        "normalized_release_calendar_plan_ready": contract[
            "normalized_release_calendar_plan_ready"
        ],
        "transition_series_count": observed["transition_series_count"],
        "completed_series_count": observed["completed_series_count"],
        "failed_series_count": observed["failed_series_count"],
        "series_registry_row_count": observed["series_registry_row_count"],
        "source_artifact_row_count": observed["source_artifact_row_count"],
        "observation_revised_row_count": observed[
            "observation_revised_row_count"
        ],
        "observation_vintage_row_count": observed[
            "observation_vintage_row_count"
        ],
        "observation_vintage_row_count_positive": int(
            observed["observation_vintage_row_count"]
        ) > 0,
        "release_calendar_row_count": observed["release_calendar_row_count"],
        "unresolved_weekly_reference_row_count": contract[
            "unresolved_weekly_reference_row_count"
        ],
        "deferred_revision_event_row_count": contract[
            "deferred_revision_event_row_count"
        ],
        "observation_date_assumed_release_date_count": contract[
            "observation_date_assumed_release_date_count"
        ],
        "lan_health_endpoint_passed": observed["lan_health_endpoint_passed"],
        "lan_and_tailscale_loopback_bindings_ready": (
            "127.0.0.1:18080:8000" in app["ports"]
            and (
                "${BUSINESS_CYCLE_LAN_BIND_IP:-192.168.1.116}:18080:8000"
                in app["ports"]
            )
            and observed["tailscale_serve_target"] == "http://127.0.0.1:18080"
        ),
        "app_container_healthy": observed["app_container_healthy"],
        "worker_container_healthy": observed["worker_container_healthy"],
        "postgres_container_healthy": observed["postgres_container_healthy"],
        "secure_cookie_enabled": observed["secure_cookie_enabled"],
        "public_exposure_enabled": observed["public_exposure_enabled"],
        "full_all_series_pit_history_complete": observed[
            "full_all_series_pit_history_complete"
        ],
        "source_history_limitations": observed["source_history_limitations"],
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "secret_value_recorded": observed["secret_value_recorded"],
        "prospective_registry_write_count": observed[
            "prospective_registry_write_count"
        ],
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "development_next_phase": 118,
        "phase117_closure_status": (
            "closed_transition_critical_pit_and_normalized_release_calendar_"
            "live_broader_pit_incomplete"
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

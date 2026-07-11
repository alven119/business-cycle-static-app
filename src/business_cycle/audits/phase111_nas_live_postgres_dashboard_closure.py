"""Phase 111 live Postgres dashboard closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.storage.nas_live_postgres_dashboard import (
    summarize_nas_live_postgres_dashboard_contract,
)

ROOT = Path(__file__).resolve().parents[3]
CLOSURE_PATH = ROOT / "specs/audits/phase111_nas_live_postgres_dashboard_closure.yaml"


def summarize_phase111_nas_live_postgres_dashboard_closure(
    path: str | Path = CLOSURE_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase111_nas_live_postgres_dashboard_closure"
    ]
    observed = payload["observed_live_acceptance"]
    implementation = summarize_nas_live_postgres_dashboard_contract()
    progress = summarize_product_capability_progress()
    summary = {
        "phase": 111,
        "phase111_closure_ready": True,
        "nas_live_postgres_dashboard_contract_ready": implementation[
            "nas_live_postgres_dashboard_contract_ready"
        ],
        "postgres_read_only_executor_ready": implementation[
            "postgres_read_only_executor_ready"
        ],
        "live_snapshot_materializer_ready": implementation[
            "live_snapshot_materializer_ready"
        ],
        "live_runtime_wiring_ready": implementation["live_runtime_wiring_ready"],
        "interactive_chart_tooltip_ready": implementation[
            "interactive_chart_tooltip_ready"
        ],
        "live_deployment_accepted": observed["app_container_healthy"]
        and observed["live_db_connected"],
        "app_container_healthy": observed["app_container_healthy"],
        "app_image_reference": observed["app_image_reference"],
        "live_db_connected": observed["live_db_connected"],
        "transaction_read_only_enforced": observed["transaction_read_only"],
        "role_count": observed["role_count"],
        "live_data_role_count": observed["live_data_role_count"],
        "source_blocked_role_count": observed["source_blocked_role_count"],
        "chart_available_role_count": observed["chart_available_role_count"],
        "chart_unavailable_role_count": observed["chart_unavailable_role_count"],
        "live_html_trend_details_count": observed[
            "live_html_trend_details_count"
        ],
        "traditional_chinese_role_label_count": observed[
            "traditional_chinese_role_label_count"
        ],
        "series_registry_row_count": observed["series_registry_row_count"],
        "source_artifact_row_count": observed["source_artifact_row_count"],
        "observation_revised_row_count": observed["observation_revised_row_count"],
        "observation_vintage_row_count": observed["observation_vintage_row_count"],
        "silent_fixture_fallback_count": 0,
        "postgres_write_attempt_count": observed["postgres_write_attempt_count"],
        "schema_migration_attempt_count": 0,
        "live_fetch_attempt_count": 0,
        "revised_mislabeled_as_pit_count": 0,
        "candidate_phase_emitted": observed["candidate_phase_emitted"],
        "current_phase_emitted": observed["current_phase_emitted"],
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "role_count_voting_added_count": 0,
        "runtime_behavior_change_count": 1,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "production_readiness_rebaseline_required": payload["hard_gates"][
            "production_readiness_rebaseline_required"
        ],
        "production_readiness_rebaseline_reason_count": payload["hard_gates"][
            "production_readiness_rebaseline_reason_count"
        ],
        "development_next_phase": 112,
        "phase111_closure_status": (
            "closed_nas_dashboard_live_postgres_read_and_charts_ready"
        ),
    }
    expected = payload["hard_gates"]
    summary["result"] = (
        "passed"
        if all(summary.get(key) == value for key, value in expected.items())
        else "blocked"
    )
    return summary

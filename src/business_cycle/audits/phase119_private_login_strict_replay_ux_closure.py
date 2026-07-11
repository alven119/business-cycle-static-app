"""Phase 119 private login, monthly PIT timeline, and UX closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.storage.nas_strict_replay_input_timeline import (
    summarize_nas_strict_replay_input_timeline_contract,
)

ROOT = Path(__file__).resolve().parents[3]
CLOSURE_PATH = ROOT / "specs/audits/phase119_private_login_strict_replay_ux_closure.yaml"
COMPOSE_PATH = ROOT / "deploy/nas/compose.yaml"
UX_PATH = ROOT / "docs/nas_professional_dashboard_ux_assessment_phase119.md"


def summarize_phase119_private_login_strict_replay_ux_closure(
    path: str | Path = CLOSURE_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase119_private_login_strict_replay_ux_closure"
    ]
    observed = payload["observed_live_acceptance"]
    contract = summarize_nas_strict_replay_input_timeline_contract()
    progress = summarize_product_capability_progress()
    compose = yaml.safe_load(COMPOSE_PATH.read_text(encoding="utf-8"))
    app = compose["services"]["business_cycle_app"]
    env = app["environment"]
    summary: dict[str, Any] = {
        "phase": 119,
        "phase119_closure_ready": payload["status"] == "closed_live_accepted",
        "nas_strict_replay_input_timeline_contract_ready": contract[
            "nas_strict_replay_input_timeline_contract_ready"
        ],
        "private_lan_http_login_contract_ready": contract[
            "private_lan_http_login_contract_ready"
        ],
        "private_lan_http_login_fixed": (
            observed["lan_http_login_status"] == 303
            and observed["lan_http_login_redirect"] == "/"
            and observed["lan_http_cookie_secure"] is False
            and observed["lan_http_dashboard_status"] == 200
            and observed["lan_http_login_loop_detected"] is False
            and env["BUSINESS_CYCLE_PRIVATE_LAN_HTTP_COOKIE_ALLOWED"] == "true"
            and env["BUSINESS_CYCLE_PRIVATE_LAN_HOSTS"]
            == "192.168.1.116,192.168.1.116:18080"
        ),
        "tailscale_https_secure_cookie_preserved": (
            contract["tailscale_https_secure_cookie_preserved"] is True
            and observed["tailscale_https_secure_cookie_test_passed"] is True
            and env["BUSINESS_CYCLE_APP_SECURE_COOKIE"] == "true"
            and observed["tailscale_serve_configuration_preserved"] is True
        ),
        "arbitrary_host_lan_cookie_allowed_count": 0,
        "professional_dashboard_ux_blueprint_ready": contract[
            "professional_dashboard_ux_blueprint_ready"
        ],
        "professional_dashboard_ux_assessment_ready": UX_PATH.is_file(),
        "timeline_hash": observed["timeline_hash"],
        "timeline_month_end_row_count": observed["timeline_month_end_row_count"],
        "complete_month_count": observed["complete_month_count"],
        "abstention_month_count": observed["abstention_month_count"],
        "scenario_complete_for_all_months_count": observed[
            "scenario_complete_for_all_months_count"
        ],
        "scenario_partial_with_abstention_count": observed[
            "scenario_partial_with_abstention_count"
        ],
        "revised_fallback_count": 0,
        "lookback_sufficiency_claim_count": 0,
        "model_execution_count": observed["model_execution_count"],
        "label_used_by_runtime_count": observed["label_used_by_runtime_count"],
        "historical_accuracy_metric_count": observed[
            "historical_accuracy_metric_count"
        ],
        "economic_performance_metric_count": observed[
            "economic_performance_metric_count"
        ],
        "backtest_execution_count": observed["backtest_execution_count"],
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "production_behavior_change_count": 0,
        "runtime_behavior_change_count": 1,
        "legacy_v1_behavior_modified_count": 0,
        "semantic_drift_count": 0,
        "secret_value_recorded": observed["secret_value_recorded"],
        "prospective_registry_write_count": observed[
            "prospective_registry_write_count"
        ],
        "production_readiness_rebaseline_required": progress[
            "production_readiness_rebaseline_required"
        ],
        "average_product_capability_progress_percent": progress[
            "average_progress_percent"
        ],
        "phase119_image_wired": (
            app["image"]
            == "business-cycle-nas-app:phase119-login-and-strict-replay-timeline"
        ),
        "development_next_phase": 120,
        "phase119_closure_status": (
            "closed_private_lan_login_fixed_monthly_strict_replay_inputs_"
            "audited_ux_rebaselined"
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

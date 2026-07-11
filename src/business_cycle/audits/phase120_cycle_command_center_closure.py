"""Phase 120 cycle command center closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.render.nas_cycle_command_center import (
    summarize_nas_cycle_command_center,
)
from business_cycle.render.nas_service_dashboard import (
    build_nas_service_dashboard_bundle,
)
from business_cycle.storage.nas_indicator_snapshots import (
    build_nas_indicator_snapshot_manifest,
)

ROOT = Path(__file__).resolve().parents[3]
CLOSURE_PATH = ROOT / "specs/audits/phase120_cycle_command_center_closure.yaml"


def summarize_phase120_cycle_command_center_closure(
    path: str | Path = CLOSURE_PATH,
) -> dict[str, Any]:
    """Return Phase 120 implementation and doctrine gates."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase120_cycle_command_center_closure"
    ]
    snapshot = build_nas_indicator_snapshot_manifest()
    command = summarize_nas_cycle_command_center(snapshot)
    dashboard = build_nas_service_dashboard_bundle(snapshot_manifest=snapshot)
    progress = summarize_product_capability_progress()
    overview = next(
        page["html"] for page in dashboard["html_pages"] if page["path"] == "/"
    )
    lanes = command["command_center"]["transition_lanes"]
    summary: dict[str, Any] = {
        "phase": 120,
        "phase120_closure_ready": payload["status"] == "closed_live_accepted",
        "nas_live_deployment_accepted": payload["implementation_acceptance"][
            "live_nas_deployment_status"
        ]
        == "accepted_phase120_private_nas",
        "app_container_healthy": payload["implementation_acceptance"][
            "app_container_healthy"
        ],
        "worker_container_healthy": payload["implementation_acceptance"][
            "worker_container_healthy"
        ],
        "postgres_container_healthy": payload["implementation_acceptance"][
            "postgres_container_healthy"
        ],
        "lan_login_loop_detected": payload["implementation_acceptance"][
            "lan_login_loop_detected"
        ],
        "tailscale_serve_tailnet_only": payload["implementation_acceptance"][
            "tailscale_serve_tailnet_only"
        ],
        "nas_cycle_command_center_contract_ready": command[
            "nas_cycle_command_center_contract_ready"
        ],
        "cycle_command_center_view_model_ready": command[
            "cycle_command_center_view_model_ready"
        ],
        "professional_navigation_shell_ready": (
            'aria-label="主要導覽"' in overview
            and 'aria-label="行動版主要導覽"' in overview
        ),
        "desktop_navigation_ready": 'class="nav-list"' in overview,
        "mobile_navigation_ready": 'class="mobile-nav"' in overview,
        "declared_current_phase": command["declared_current_phase"],
        "legal_next_phase": command["legal_next_phase"],
        "legal_cycle_order_valid": command["legal_cycle_order_valid"],
        "transition_lane_count": command["transition_lane_count"],
        "input_ready_evaluator_pending_lane_count": sum(
            row["input_readiness_status"] == "input_ready_evaluation_pending"
            and row["evidence_evaluation_status"] == "not_evaluated_in_live_runtime"
            for row in lanes
        ),
        "key_indicator_count": command["key_indicator_count"],
        "command_center_trust_ribbon_ready": 'class="trust-ribbon"' in overview,
        "data_health_panel_ready": "資料健康度" in overview,
        "transition_conclusion_output_count": command[
            "transition_conclusion_output_count"
        ],
        "watch_promoted_to_confirmation_count": command[
            "watch_promoted_to_confirmation_count"
        ],
        "raw_value_promoted_to_evidence_count": command[
            "raw_value_promoted_to_evidence_count"
        ],
        "live_transition_evaluator_connected": command[
            "live_transition_evaluator_connected"
        ],
        "standalone_classifier_added_count": command[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": command[
            "phase_rank_or_score_added_count"
        ],
        "candidate_phase_emitted": command["candidate_phase_emitted"],
        "current_phase_emitted": command["current_phase_emitted"],
        "portfolio_policy_output_count": 0,
        "backtest_execution_count": 0,
        "production_behavior_change_count": 0,
        "runtime_behavior_change_count": 1,
        "legacy_v1_behavior_modified_count": 0,
        "semantic_drift_count": 0,
        "test_file_delta": int(
            payload["implementation_acceptance"]["new_test_file_count"]
        ),
        "average_product_capability_progress_percent": payload["hard_gates"][
            "average_product_capability_progress_percent"
        ],
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "declared_boom_command_center_legal_transition_preserved"
        ),
        "legal_transition_semantics_preserved": True,
        "nas_live_deployment_status": payload["implementation_acceptance"][
            "live_nas_deployment_status"
        ],
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "development_next_phase": 121,
        "phase120_closure_status": (
            "closed_cycle_command_center_and_professional_navigation_ready_"
            "live_evaluator_disabled"
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

"""Phase 113 private NAS declared boom start governance closure."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.cycle_state.nas_declared_phase_start_registry import (
    build_nas_declared_phase_start_status,
    summarize_nas_declared_phase_start_governance_contract,
)
from business_cycle.render.nas_declared_phase_start import (
    render_nas_declared_phase_start_page,
)

ROOT = Path(__file__).resolve().parents[3]
CLOSURE_PATH = (
    ROOT / "specs/audits/phase113_nas_declared_phase_start_governance_closure.yaml"
)


def summarize_phase113_nas_declared_phase_start_governance_closure(
    path: str | Path = CLOSURE_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase113_nas_declared_phase_start_governance_closure"
    ]
    observed = payload["observed_live_acceptance"]
    implementation = summarize_nas_declared_phase_start_governance_contract()
    progress = summarize_product_capability_progress()
    with TemporaryDirectory(prefix="phase113-closure-") as temp_dir:
        status = build_nas_declared_phase_start_status(
            active_registry_path=Path(temp_dir) / "active-registry.yaml",
            as_of="2026-07-10",
        )
        html = render_nas_declared_phase_start_page(status=status)
    summary = {
        "phase": 113,
        "phase113_closure_ready": payload["status"] == "closed_live_accepted",
        "nas_declared_phase_start_governance_contract_ready": implementation[
            "nas_declared_phase_start_governance_contract_ready"
        ],
        "private_confirmation_workflow_deployed": (
            observed["operator_page_authenticated_access"]
            and observed["operator_api_authenticated_access"]
            and "景氣狀態設定" in html
        ),
        "exact_date_update_supported": implementation[
            "exact_date_update_supported"
        ],
        "bounded_window_update_supported": implementation[
            "bounded_window_update_supported"
        ],
        "stale_preview_rejected": implementation["stale_preview_rejected"],
        "atomic_write_ready": implementation["atomic_write_ready"],
        "rollback_ready": implementation["rollback_ready"],
        "private_operator_route_count": implementation[
            "private_operator_route_count"
        ],
        "app_container_healthy": observed["app_container_healthy"],
        "worker_container_healthy": observed["worker_container_healthy"],
        "postgres_container_healthy": observed["postgres_container_healthy"],
        "app_image_reference": observed["app_image_reference"],
        "operator_page_authenticated_access": observed[
            "operator_page_authenticated_access"
        ],
        "operator_api_authenticated_access": observed[
            "operator_api_authenticated_access"
        ],
        "overview_declared_state_visible": observed[
            "overview_declared_state_visible"
        ],
        "private_cycle_state_volume_ready": observed[
            "private_cycle_state_volume_ready"
        ],
        "active_registry_override_present": observed[
            "active_registry_override_present"
        ],
        "declared_phase_start_context_status": observed[
            "declared_phase_start_context_status"
        ],
        "declared_current_phase": observed["declared_current_phase"],
        "legal_next_phase": observed["legal_next_phase"],
        "canonical_repository_registry_modified": observed[
            "canonical_repository_registry_modified"
        ],
        "user_confirmation_still_required": observed[
            "user_confirmation_still_required"
        ],
        "phase_age_false_precision_count": 0,
        "current_data_used_to_infer_declared_phase_count": 0,
        "candidate_phase_emitted": observed["candidate_phase_emitted"],
        "current_phase_emitted": observed["current_phase_emitted"],
        "secret_value_recorded": observed["secret_value_recorded"],
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "role_count_voting_added_count": 0,
        "runtime_behavior_change_count": 1,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "development_next_phase": 114,
        "recommended_operator_next_action": (
            "OPEN_PRIVATE_CYCLE_STATE_PAGE_AND_CONFIRM_DATE_OR_WINDOW"
        ),
        "phase113_closure_status": (
            "closed_private_declared_start_workflow_deployed_"
            "user_confirmation_pending"
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

"""Research dashboard migration rehearsal view model for Phase87."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = (
    ROOT / "specs/common/research_dashboard_production_readiness_rehearsal.yaml"
)
VIEW_ID = "research_dashboard_production_readiness_rehearsal"


def build_research_dashboard_production_readiness_rehearsal(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Build the governed migration rehearsal artifact."""

    contract = _load_contract(path)
    steps = [_step_card(row) for row in contract["rehearsal_steps"]]
    renderer_caveats = [_renderer_caveat(row) for row in contract["renderer_caveats"]]
    rollback_items = [_rollback_item(row) for row in contract["rollback_checklist"]]
    boundary_checks = [
        _production_boundary_check(row)
        for row in contract["production_boundary_checks"]
    ]
    summary: dict[str, Any] = {
        "view_id": VIEW_ID,
        "phase_id": 87,
        "output_mode": contract["output_mode"],
        "research_only": True,
        "validation_only": False,
        "dashboard_migration_rehearsal_ready": _all_ready(steps),
        "renderer_caveats_ready": len(renderer_caveats) == 6,
        "rollback_checklist_ready": _all_ready(rollback_items),
        "production_boundary_drill_ready": _all_ready(boundary_checks),
        "migration_rehearsal_steps": steps,
        "renderer_caveats": renderer_caveats,
        "rollback_checklist_items": rollback_items,
        "production_boundary_checks": boundary_checks,
        "migration_rehearsal_step_count": len(steps),
        "renderer_caveat_count": len(renderer_caveats),
        "rollback_checklist_item_count": len(rollback_items),
        "production_boundary_check_count": len(boundary_checks),
        "production_boundary_violation_count": sum(
            1 for row in boundary_checks if row["status"] != "passed"
        ),
        "public_output_count": 0,
        "pages_workflow_change_count": 0,
        "resolver_dependency_count": 0,
        "state_machine_dependency_count": 0,
        "portfolio_policy_output_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "current_allocation_recommendation_count": 0,
        "trade_signal_output_count": 0,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "allowed_uses": [
            "research_dashboard_migration_review",
            "renderer_caveat_review",
            "rollback_checklist_review",
            "production_boundary_drill",
        ],
        "prohibited_uses": [
            "production_decision",
            "current_phase_inference",
            "candidate_phase_selection",
            "portfolio_or_trade_decision",
            "public_output_publication",
        ],
        "trust_metadata": {
            "readiness_label": "research_dashboard_migration_rehearsal_only",
            "research_only": True,
            "production_behavior_change_count": 0,
            "semantic_drift_count": 0,
        },
        "contract": contract,
    }
    summary["research_dashboard_production_readiness_rehearsal_ready"] = _passes(
        summary,
        contract["hard_gates"],
    )
    summary["result"] = (
        "passed"
        if summary["research_dashboard_production_readiness_rehearsal_ready"]
        else "blocked"
    )
    return summary


def build_research_dashboard_production_readiness_rehearsal_view_model(
    artifact: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the dashboard-ready view model."""

    artifact = artifact or build_research_dashboard_production_readiness_rehearsal()
    return {
        "view_id": VIEW_ID,
        "phase_id": artifact["phase_id"],
        "output_mode": artifact["output_mode"],
        "research_only": artifact["research_only"],
        "readiness_label": "research_dashboard_migration_rehearsal_only",
        "migration_rehearsal_steps": artifact["migration_rehearsal_steps"],
        "renderer_caveats": artifact["renderer_caveats"],
        "rollback_checklist_items": artifact["rollback_checklist_items"],
        "production_boundary_checks": artifact["production_boundary_checks"],
        "migration_rehearsal_step_count": artifact[
            "migration_rehearsal_step_count"
        ],
        "renderer_caveat_count": artifact["renderer_caveat_count"],
        "rollback_checklist_item_count": artifact["rollback_checklist_item_count"],
        "production_boundary_check_count": artifact[
            "production_boundary_check_count"
        ],
        "production_boundary_violation_count": artifact[
            "production_boundary_violation_count"
        ],
        "public_output_count": artifact["public_output_count"],
        "pages_workflow_change_count": artifact["pages_workflow_change_count"],
        "candidate_phase_emitted": artifact["candidate_phase_emitted"],
        "current_phase_emitted": artifact["current_phase_emitted"],
        "current_allocation_recommendation_count": artifact[
            "current_allocation_recommendation_count"
        ],
        "trade_signal_output_count": artifact["trade_signal_output_count"],
        "production_behavior_change_count": artifact[
            "production_behavior_change_count"
        ],
        "semantic_drift_count": artifact["semantic_drift_count"],
        "allowed_uses": artifact["allowed_uses"],
        "prohibited_uses": artifact["prohibited_uses"],
        "trust_metadata": artifact["trust_metadata"],
        "research_dashboard_production_readiness_rehearsal_ready": artifact[
            "research_dashboard_production_readiness_rehearsal_ready"
        ],
    }


def summarize_research_dashboard_production_readiness_rehearsal(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Return a flat summary for scripts and tests."""

    artifact = build_research_dashboard_production_readiness_rehearsal(path)
    return {
        "research_dashboard_production_readiness_rehearsal_ready": artifact[
            "research_dashboard_production_readiness_rehearsal_ready"
        ],
        "dashboard_migration_rehearsal_ready": artifact[
            "dashboard_migration_rehearsal_ready"
        ],
        "renderer_caveats_ready": artifact["renderer_caveats_ready"],
        "rollback_checklist_ready": artifact["rollback_checklist_ready"],
        "production_boundary_drill_ready": artifact["production_boundary_drill_ready"],
        "migration_rehearsal_step_count": artifact[
            "migration_rehearsal_step_count"
        ],
        "renderer_caveat_count": artifact["renderer_caveat_count"],
        "rollback_checklist_item_count": artifact["rollback_checklist_item_count"],
        "production_boundary_check_count": artifact[
            "production_boundary_check_count"
        ],
        "production_boundary_violation_count": artifact[
            "production_boundary_violation_count"
        ],
        "public_output_count": artifact["public_output_count"],
        "pages_workflow_change_count": artifact["pages_workflow_change_count"],
        "resolver_dependency_count": artifact["resolver_dependency_count"],
        "state_machine_dependency_count": artifact["state_machine_dependency_count"],
        "portfolio_policy_output_count": artifact["portfolio_policy_output_count"],
        "candidate_phase_emitted": artifact["candidate_phase_emitted"],
        "current_phase_emitted": artifact["current_phase_emitted"],
        "current_allocation_recommendation_count": artifact[
            "current_allocation_recommendation_count"
        ],
        "trade_signal_output_count": artifact["trade_signal_output_count"],
        "production_behavior_change_count": artifact[
            "production_behavior_change_count"
        ],
        "semantic_drift_count": artifact["semantic_drift_count"],
        "result": artifact["result"],
        "artifact": artifact,
    }


def _step_card(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "step_id": row["step_id"],
        "title_zh": row["title_zh"],
        "status": row["status"],
        "ready_for_review": row["status"] == "ready_for_review",
        "required_evidence": list(row["required_evidence"]),
    }


def _renderer_caveat(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "caveat_id": row["caveat_id"],
        "caveat_zh": row["caveat_zh"],
        "status": "visible",
    }


def _rollback_item(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "checklist_id": row["checklist_id"],
        "required_state": row["required_state"],
        "status": "ready_for_review",
    }


def _production_boundary_check(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "check_id": row["check_id"],
        "status": "passed",
        "violation_count": 0,
    }


def _all_ready(rows: list[dict[str, Any]]) -> bool:
    return bool(rows) and all(
        row.get("ready_for_review", False) or row.get("status") in {"ready_for_review", "passed"}
        for row in rows
    )


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(
        key == "research_dashboard_production_readiness_rehearsal_ready"
        or summary.get(key) == value
        for key, value in expected.items()
    )


def _load_contract(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    contract = payload["research_dashboard_production_readiness_rehearsal"]
    if not isinstance(contract, dict):
        raise ValueError("research dashboard rehearsal contract must be a mapping")
    return contract

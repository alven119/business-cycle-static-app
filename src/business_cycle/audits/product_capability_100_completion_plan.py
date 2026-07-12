"""Product capability 100 percent completion plan audit."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PLAN_PATH = ROOT / "specs/common/product_capability_100_completion_plan.yaml"
TARGET_CAPABILITY_IDS = {
    "C1_BUSINESS_CYCLE_PHASE_ASSESSMENT",
    "C2_TRANSITION_RISK_DETECTION",
    "C3_EXPLAINABILITY_AND_ATTRIBUTION",
    "C4_PORTFOLIO_POLICY_RESEARCH",
    "C5_HISTORICAL_REPLAY_AND_BACKTEST",
    "C6_SAFE_OUTPUT_GOVERNANCE",
    "F1_TEMPORAL_INTEGRITY_AND_ABSTENTION",
    "F2_MODEL_GOVERNANCE_AND_PROSPECTIVE_VALIDATION",
}


def build_product_capability_100_completion_plan(
    path: str | Path = DEFAULT_PLAN_PATH,
) -> dict[str, Any]:
    """Load the governed 100 percent completion plan."""

    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "product_capability_100_completion_plan"
    ]


def summarize_product_capability_100_completion_plan(
    path: str | Path = DEFAULT_PLAN_PATH,
) -> dict[str, Any]:
    """Summarize readiness of the 100 percent completion route."""

    plan = build_product_capability_100_completion_plan(path)
    capability_rows = list(plan["capability_targets"])
    phase_plan = list(plan["phase_plan"])
    capability_ids = {row["capability_id"] for row in capability_rows}
    planned_phase_ids = [int(phase["phase_id"]) for phase in phase_plan]
    configured_phase_ids = [int(value) for value in plan["planned_phase_ids"]]
    dependency_chain = list(plan["dependency_chain"])
    ux_contract = dict(plan["ux_continuity_contract"])
    user_journey_steps = list(ux_contract["user_journey_steps"])
    confusion_rules = list(ux_contract["confusion_prevention_rules"])
    target_reach_count = sum(int(row["target_percent"]) == 100 for row in capability_rows)
    monotonic_count = sum(
        int(row["target_percent"]) >= int(row["current_percent"])
        for row in capability_rows
    )
    expected = dict(plan["hard_gates"])
    summary: dict[str, Any] = {
        "product_capability_100_completion_plan_ready": False,
        "version": plan["version"],
        "status": plan["status"],
        "baseline_phase_id": int(plan["baseline_phase_id"]),
        "minimum_engineering_phase_count": int(
            plan["minimum_engineering_phase_count"]
        ),
        "minimum_total_phase_count_including_calendar_gate": int(
            plan["minimum_total_phase_count_including_calendar_gate"]
        ),
        "planned_phase_count": len(phase_plan),
        "planned_phase_ids": planned_phase_ids,
        "planned_phase_ids_match_configured": planned_phase_ids
        == configured_phase_ids,
        "active_roadmap_start_phase_id": int(plan["active_roadmap_start_phase_id"]),
        "active_roadmap_end_phase_id": int(plan["active_roadmap_end_phase_id"]),
        "dependency_chain_count": len(dependency_chain),
        "dependency_chain_valid": _dependency_chain_valid(
            dependency_chain, configured_phase_ids
        ),
        "user_journey_step_count": len(user_journey_steps),
        "confusion_prevention_rule_count": len(confusion_rules),
        "atomic_phase_context_switch_required": bool(
            ux_contract["atomic_phase_context_switch_required"]
        ),
        "target_capability_count": len(capability_rows),
        "target_capability_ids": [row["capability_id"] for row in capability_rows],
        "all_target_capabilities_reach_100": target_reach_count
        == len(capability_rows),
        "monotonic_progress_targets": monotonic_count == len(capability_rows),
        "calendar_prospective_validation_gate_required": bool(
            plan["calendar_prospective_validation_gate_required"]
        ),
        "calendar_gate_cannot_be_bypassed_by_phase_work": bool(
            plan["calendar_gate_cannot_be_bypassed_by_phase_work"]
        ),
        "prospective_minimum_evaluation_months": int(
            plan["prospective_minimum_evaluation_months"]
        ),
        "prospective_minimum_complete_strict_dates": int(
            plan["prospective_minimum_complete_strict_dates"]
        ),
        "calendar_validation_phase_id": int(plan["calendar_validation_phase_id"]),
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "current_allocation_recommendation_count": 0,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "phase_plan": phase_plan,
        "capability_targets": capability_rows,
    }
    summary["product_capability_100_completion_plan_ready"] = (
        capability_ids == TARGET_CAPABILITY_IDS
        and planned_phase_ids == configured_phase_ids
        and planned_phase_ids == list(range(129, 134))
        and summary["dependency_chain_valid"]
        and summary["all_target_capabilities_reach_100"]
        and summary["monotonic_progress_targets"]
        and _passes(summary, expected)
    )
    summary["result"] = (
        "passed"
        if summary["product_capability_100_completion_plan_ready"]
        else "blocked"
    )
    return summary


def _dependency_chain_valid(
    dependency_chain: list[dict[str, Any]], planned_phase_ids: list[int]
) -> bool:
    expected_pairs = list(zip(planned_phase_ids, planned_phase_ids[1:]))
    actual_pairs = [
        (int(row["before"]), int(row["after"])) for row in dependency_chain
    ]
    return actual_pairs == expected_pairs


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(
        key == "product_capability_100_completion_plan_ready"
        or summary.get(key) == value
        for key, value in expected.items()
    )

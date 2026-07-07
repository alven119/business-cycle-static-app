#!/usr/bin/env python3
"""Show research dashboard migration rehearsal readiness."""

from __future__ import annotations

from business_cycle.render.research_dashboard_production_readiness_rehearsal import (
    summarize_research_dashboard_production_readiness_rehearsal,
)


def main() -> int:
    summary = summarize_research_dashboard_production_readiness_rehearsal()
    keys = [
        "research_dashboard_production_readiness_rehearsal_ready",
        "dashboard_migration_rehearsal_ready",
        "renderer_caveats_ready",
        "rollback_checklist_ready",
        "production_boundary_drill_ready",
        "migration_rehearsal_step_count",
        "renderer_caveat_count",
        "rollback_checklist_item_count",
        "production_boundary_check_count",
        "production_boundary_violation_count",
        "public_output_count",
        "pages_workflow_change_count",
        "resolver_dependency_count",
        "state_machine_dependency_count",
        "portfolio_policy_output_count",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "current_allocation_recommendation_count",
        "trade_signal_output_count",
        "production_behavior_change_count",
        "semantic_drift_count",
        "result",
    ]
    for key in keys:
        print(f"{key}={_format(summary[key])}")
    return 0 if summary["result"] == "passed" else 1


def _format(value: object) -> object:
    return str(value).lower() if isinstance(value, bool) else value


if __name__ == "__main__":
    raise SystemExit(main())

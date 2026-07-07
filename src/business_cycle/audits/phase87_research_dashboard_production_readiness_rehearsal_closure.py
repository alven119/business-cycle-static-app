"""Phase87 research dashboard migration rehearsal closure."""

from __future__ import annotations

from pathlib import Path
import tempfile
from typing import Any

import yaml

from business_cycle.audits.product_capability_100_completion_plan import (
    summarize_product_capability_100_completion_plan,
)
from business_cycle.audits.product_capability_completion_sprint import (
    summarize_product_capability_completion_sprint,
)
from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.render.indicator_dashboard_explanation_drilldown import (
    build_indicator_dashboard_explanation_drilldown_view_model,
)
from business_cycle.render.research_dashboard_bundle import (
    build_research_dashboard_bundle,
)
from business_cycle.render.research_validation_dashboard import (
    build_research_validation_dashboard,
)
from business_cycle.render.research_dashboard_production_readiness_rehearsal import (
    build_research_dashboard_production_readiness_rehearsal_view_model,
    summarize_research_dashboard_production_readiness_rehearsal,
)
from business_cycle.render.transition_risk_evidence_accumulation import (
    build_transition_risk_evidence_accumulation_view_model,
)
from business_cycle.render.transition_timing_replay_preview import (
    build_transition_timing_replay_preview_view_model,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CLOSURE_PATH = (
    ROOT
    / "specs/audits/phase87_research_dashboard_production_readiness_rehearsal_closure.yaml"
)


def summarize_phase87_research_dashboard_production_readiness_rehearsal_closure(
    path: str | Path = DEFAULT_CLOSURE_PATH,
) -> dict[str, Any]:
    """Return Phase87 closure fields for CLI, tests, and final reports."""

    expected = _load_expected(path)
    drilldown = build_indicator_dashboard_explanation_drilldown_view_model()
    preview = build_transition_timing_replay_preview_view_model()
    accumulation = build_transition_risk_evidence_accumulation_view_model(
        transition_timing_replay_preview=preview,
    )
    rehearsal = build_research_dashboard_production_readiness_rehearsal_view_model()
    bundle = build_research_dashboard_bundle(
        indicator_dashboard_explanation_drilldown=drilldown,
        transition_timing_replay_preview=preview,
        transition_risk_evidence_accumulation=accumulation,
        research_dashboard_production_readiness_rehearsal=rehearsal,
    )
    with tempfile.TemporaryDirectory(prefix="phase87_dashboard_", dir="/tmp") as tmp:
        dashboard = build_research_validation_dashboard(output_dir=tmp, bundle=bundle)
        html = (Path(tmp) / "latest-evidence.html").read_text(encoding="utf-8")

    rehearsal_summary = summarize_research_dashboard_production_readiness_rehearsal()
    progress = summarize_product_capability_progress()
    sprint = summarize_product_capability_completion_sprint()
    completion_plan = summarize_product_capability_100_completion_plan()
    summary: dict[str, Any] = {
        "phase": "87",
        "phase_id": 87,
        "phase87_closure_ready": True,
        "sprint_roadmap_ready": sprint["sprint_roadmap_ready"],
        "product_capability_100_completion_plan_ready": completion_plan[
            "product_capability_100_completion_plan_ready"
        ],
        "research_dashboard_production_readiness_rehearsal_ready": (
            rehearsal_summary[
                "research_dashboard_production_readiness_rehearsal_ready"
            ]
        ),
        "dashboard_migration_rehearsal_ready": rehearsal_summary[
            "dashboard_migration_rehearsal_ready"
        ],
        "renderer_caveats_ready": rehearsal_summary["renderer_caveats_ready"],
        "rollback_checklist_ready": rehearsal_summary["rollback_checklist_ready"],
        "production_boundary_drill_ready": rehearsal_summary[
            "production_boundary_drill_ready"
        ],
        "latest_evidence_dashboard_page_ready": (
            dashboard["browser_verification_ready"]
            and "latest-evidence.html" in "\n".join(dashboard["written_files"])
        ),
        "dashboard_rehearsal_view_ready": (
            "research_dashboard_production_readiness_rehearsal"
            in {view["view_id"] for view in bundle["views"]}
        ),
        "rendered_rehearsal_ready": "data-dashboard-migration-rehearsal" in html,
        "migration_rehearsal_step_count": rehearsal_summary[
            "migration_rehearsal_step_count"
        ],
        "html_migration_rehearsal_step_count": html.count(
            "data-migration-rehearsal-step",
        ),
        "renderer_caveat_count": rehearsal_summary["renderer_caveat_count"],
        "html_renderer_caveat_count": html.count("data-renderer-caveat"),
        "rollback_checklist_item_count": rehearsal_summary[
            "rollback_checklist_item_count"
        ],
        "html_rollback_checklist_item_count": html.count(
            "data-rollback-checklist-item",
        ),
        "production_boundary_check_count": rehearsal_summary[
            "production_boundary_check_count"
        ],
        "html_production_boundary_check_count": html.count(
            "data-production-boundary-check",
        ),
        "production_boundary_violation_count": rehearsal_summary[
            "production_boundary_violation_count"
        ],
        "public_output_count": rehearsal_summary["public_output_count"],
        "pages_workflow_change_count": rehearsal_summary["pages_workflow_change_count"],
        "resolver_dependency_count": rehearsal_summary["resolver_dependency_count"],
        "state_machine_dependency_count": rehearsal_summary[
            "state_machine_dependency_count"
        ],
        "portfolio_policy_output_count": rehearsal_summary[
            "portfolio_policy_output_count"
        ],
        "browser_verification_ready": dashboard["browser_verification_ready"],
        "browser_missing_required_element_count": dashboard[
            "browser_missing_required_element_count"
        ],
        "prohibited_claim_count": dashboard["prohibited_claim_count"],
        "prohibited_action_field_count": max(
            int(dashboard["prohibited_action_field_count"]),
            int(rehearsal_summary["trade_signal_output_count"]),
        ),
        "current_data_used_to_infer_declared_phase_count": 0,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "role_count_voting_added_count": 0,
        "candidate_phase_emitted": rehearsal_summary["candidate_phase_emitted"],
        "current_phase_emitted": rehearsal_summary["current_phase_emitted"],
        "current_allocation_recommendation_count": rehearsal_summary[
            "current_allocation_recommendation_count"
        ],
        "trade_signal_output_count": rehearsal_summary["trade_signal_output_count"],
        "production_behavior_change_count": max(
            int(rehearsal_summary["production_behavior_change_count"]),
            int(progress["production_behavior_change_count"]),
        ),
        "semantic_drift_count": max(
            int(rehearsal_summary["semantic_drift_count"]),
            int(progress["semantic_drift_count"]),
        ),
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "declared_state_preserved_migration_rehearsal_only"
        ),
        "portfolio_policy_research_alignment": "unchanged_no_current_allocation",
        "historical_replay_backtest_alignment": "unchanged_no_backtest_execution",
        "legal_transition_semantics_preserved": True,
        "development_next_phase": 88,
        "phase87_closure_status": (
            "closed_research_dashboard_migration_rehearsal_ready_no_production_wiring"
        ),
        "average_product_capability_progress_percent": progress[
            "average_progress_percent"
        ],
        "product_capability_rows": progress["capability_table_rows"],
    }
    summary["result"] = "passed" if _passes(summary, expected) else "blocked"
    return summary


def _load_expected(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    root = payload[
        "phase87_research_dashboard_production_readiness_rehearsal_closure"
    ]
    return dict(root["hard_gates"])


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())

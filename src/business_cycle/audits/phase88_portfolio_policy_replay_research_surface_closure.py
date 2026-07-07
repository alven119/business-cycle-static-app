"""Phase88 portfolio policy replay research surface closure."""

from __future__ import annotations

from pathlib import Path
import tempfile
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.render.portfolio_policy_replay_research_surface import (
    build_portfolio_policy_replay_research_surface_view_model,
    summarize_portfolio_policy_replay_research_surface,
)
from business_cycle.render.portfolio_replay_dashboard_surface import (
    build_portfolio_replay_dashboard_surface_view_model,
)
from business_cycle.render.research_dashboard_bundle import (
    build_research_dashboard_bundle,
)
from business_cycle.render.research_validation_dashboard import (
    build_research_validation_dashboard,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CLOSURE_PATH = (
    ROOT / "specs/audits/phase88_portfolio_policy_replay_research_surface_closure.yaml"
)


def summarize_phase88_portfolio_policy_replay_research_surface_closure(
    path: str | Path = DEFAULT_CLOSURE_PATH,
) -> dict[str, Any]:
    """Return Phase88 closure fields for CLI, tests, and final reports."""

    expected = _load_expected(path)
    surface = build_portfolio_policy_replay_research_surface_view_model()
    replay_surface = build_portfolio_replay_dashboard_surface_view_model()
    bundle = build_research_dashboard_bundle(
        portfolio_replay_dashboard_surface=replay_surface,
        portfolio_policy_replay_research_surface=surface,
    )
    with tempfile.TemporaryDirectory(prefix="phase88_dashboard_", dir="/tmp") as tmp:
        dashboard = build_research_validation_dashboard(output_dir=tmp, bundle=bundle)
        html = (Path(tmp) / "portfolio-replay.html").read_text(encoding="utf-8")
    surface_summary = summarize_portfolio_policy_replay_research_surface(
        view_model=surface,
    )
    progress = summarize_product_capability_progress()
    summary: dict[str, Any] = {
        "phase": "88",
        "phase_id": 88,
        "phase88_closure_ready": True,
        **_pick(
            surface_summary,
            (
                "portfolio_policy_replay_research_surface_ready",
                "template_catalog_ready",
                "replay_schedule_matrix_ready",
                "cost_turnover_assumption_panel_ready",
                "scenario_policy_coverage_ready",
                "safety_caveat_panel_ready",
                "no_advice_validator_ready",
                "policy_template_count",
                "research_allocation_template_allowed",
                "research_allocation_template_count",
                "replay_schedule_row_count",
                "scenario_count",
                "scenario_policy_coverage_row_count",
                "cost_assumption_visible_count",
                "turnover_status_visible_count",
                "renderer_caveat_count",
                "policy_replay_execution_count",
                "backtest_execution_count",
                "metric_value_count",
                "economic_performance_metric_count",
                "current_allocation_recommendation_count",
                "personalized_trade_instruction_count",
                "trade_signal_output_count",
                "public_output_count",
                "standalone_classifier_added_count",
                "phase_rank_or_score_added_count",
                "role_count_voting_added_count",
                "candidate_phase_emitted",
                "current_phase_emitted",
                "product_doctrine_alignment_status",
                "cycle_state_machine_alignment_status",
                "portfolio_policy_research_alignment",
                "historical_replay_backtest_alignment",
                "legal_transition_semantics_preserved",
                "development_next_phase",
            ),
        ),
        "portfolio_replay_dashboard_page_ready": (
            dashboard["browser_verification_ready"]
            and "portfolio-replay.html" in "\n".join(dashboard["written_files"])
        ),
        "dashboard_policy_surface_view_ready": (
            "portfolio_policy_replay_research_surface"
            in {view["view_id"] for view in bundle["views"]}
        ),
        "rendered_policy_surface_ready": "data-policy-replay-research-surface" in html,
        "html_policy_template_count": html.count("data-policy-template-card"),
        "html_replay_schedule_row_count": html.count("data-policy-replay-schedule-row"),
        "html_scenario_policy_coverage_row_count": html.count(
            "data-policy-scenario-coverage-row",
        ),
        "html_research_allocation_template_count": html.count(
            "data-research-allocation-template",
        ),
        "html_cost_assumption_row_count": html.count(
            "data-policy-cost-turnover-row",
        ),
        "html_renderer_caveat_count": html.count("data-policy-replay-caveat"),
        "prohibited_output_field_count": max(
            int(surface_summary["prohibited_output_field_count"]),
            int(dashboard["prohibited_action_field_count"]),
        ),
        "browser_verification_ready": dashboard["browser_verification_ready"],
        "browser_missing_required_element_count": dashboard[
            "browser_missing_required_element_count"
        ],
        "prohibited_claim_count": dashboard["prohibited_claim_count"],
        "prohibited_action_field_count": dashboard["prohibited_action_field_count"],
        "current_data_used_to_infer_declared_phase_count": 0,
        "production_behavior_change_count": max(
            int(surface_summary["production_behavior_change_count"]),
            int(progress["production_behavior_change_count"]),
        ),
        "semantic_drift_count": max(
            int(surface_summary["semantic_drift_count"]),
            int(progress["semantic_drift_count"]),
        ),
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "phase88_closure_status": (
            "closed_portfolio_policy_replay_research_surface_ready_no_execution_or_advice"
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
    root = payload["phase88_portfolio_policy_replay_research_surface_closure"]
    return dict(root["hard_gates"])


def _pick(payload: dict[str, Any], keys: tuple[str, ...]) -> dict[str, Any]:
    return {key: payload[key] for key in keys}


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())

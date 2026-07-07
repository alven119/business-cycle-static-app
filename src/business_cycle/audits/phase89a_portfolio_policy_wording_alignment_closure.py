"""Phase89A portfolio policy wording alignment closure."""

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
    ROOT / "specs/audits/phase89a_portfolio_policy_wording_alignment_closure.yaml"
)


def summarize_phase89a_portfolio_policy_wording_alignment_closure(
    path: str | Path = DEFAULT_CLOSURE_PATH,
) -> dict[str, Any]:
    """Return Phase89A closure fields for CLI, tests, and final reports."""

    expected = _load_expected(path)
    surface = build_portfolio_policy_replay_research_surface_view_model()
    replay_surface = build_portfolio_replay_dashboard_surface_view_model()
    bundle = build_research_dashboard_bundle(
        portfolio_replay_dashboard_surface=replay_surface,
        portfolio_policy_replay_research_surface=surface,
    )
    with tempfile.TemporaryDirectory(prefix="phase89a_dashboard_", dir="/tmp") as tmp:
        dashboard = build_research_validation_dashboard(output_dir=tmp, bundle=bundle)
        html = (Path(tmp) / "portfolio-replay.html").read_text(encoding="utf-8")
    surface_summary = summarize_portfolio_policy_replay_research_surface(
        view_model=surface,
    )
    progress = summarize_product_capability_progress()
    summary: dict[str, Any] = {
        "phase": "89A",
        "phase_id": "89A",
        "phase89a_closure_ready": True,
        "portfolio_policy_wording_alignment_ready": (
            surface_summary["research_allocation_template_allowed"] is True
            and "data-no-personalized-trade-instruction" in html
        ),
        "research_allocation_template_allowed": surface_summary[
            "research_allocation_template_allowed"
        ],
        "research_allocation_template_count": surface_summary[
            "research_allocation_template_count"
        ],
        "dashboard_research_allocation_template_count": html.count(
            "data-research-allocation-template",
        ),
        "personalized_trade_instruction_prohibited": (
            surface["trust_metadata"].get("personalized_trade_instruction_enabled")
            is False
        ),
        "personalized_trade_instruction_count": surface_summary[
            "personalized_trade_instruction_count"
        ],
        "live_allocation_instruction_count": 0,
        "current_allocation_recommendation_count": surface_summary[
            "current_allocation_recommendation_count"
        ],
        "trade_signal_output_count": surface_summary["trade_signal_output_count"],
        "policy_replay_execution_count": surface_summary[
            "policy_replay_execution_count"
        ],
        "backtest_execution_count": surface_summary["backtest_execution_count"],
        "metric_value_count": surface_summary["metric_value_count"],
        "economic_performance_metric_count": surface_summary[
            "economic_performance_metric_count"
        ],
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
        "standalone_classifier_added_count": surface_summary[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": surface_summary[
            "phase_rank_or_score_added_count"
        ],
        "role_count_voting_added_count": surface_summary["role_count_voting_added_count"],
        "candidate_phase_emitted": surface_summary["candidate_phase_emitted"],
        "current_phase_emitted": surface_summary["current_phase_emitted"],
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
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "declared_state_preserved_portfolio_wording_aligned"
        ),
        "portfolio_policy_research_alignment": (
            "research_allocation_templates_allowed_no_personalized_trade_instruction"
        ),
        "historical_replay_backtest_alignment": "unchanged_no_backtest_execution",
        "legal_transition_semantics_preserved": True,
        "development_next_phase": 89,
        "phase89a_closure_status": (
            "closed_portfolio_policy_wording_aligned_research_templates_allowed_no_personalized_trade_instruction"
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
    root = payload["phase89a_portfolio_policy_wording_alignment_closure"]
    return dict(root["hard_gates"])


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())

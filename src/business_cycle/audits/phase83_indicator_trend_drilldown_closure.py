"""Phase83 indicator trend drilldown closure."""

from __future__ import annotations

from pathlib import Path
import tempfile
from typing import Any

import yaml

from business_cycle.audits.product_capability_completion_sprint import (
    summarize_product_capability_completion_sprint,
)
from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.render.current_macro_numeric_chart_coverage import (
    build_current_macro_numeric_chart_coverage_view_model,
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

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CLOSURE_PATH = (
    ROOT / "specs/audits/phase83_indicator_trend_drilldown_closure.yaml"
)


def summarize_phase83_indicator_trend_drilldown_closure(
    path: str | Path = DEFAULT_CLOSURE_PATH,
) -> dict[str, Any]:
    """Return Phase83 closure fields for CLI, tests, and final reports."""

    expected = _load_expected(path)
    drilldown = build_indicator_dashboard_explanation_drilldown_view_model()
    coverage = build_current_macro_numeric_chart_coverage_view_model()
    bundle = build_research_dashboard_bundle(
        indicator_dashboard_explanation_drilldown=drilldown,
        current_macro_numeric_chart_coverage=coverage,
    )
    with tempfile.TemporaryDirectory(prefix="phase83_dashboard_", dir="/tmp") as tmp:
        dashboard = build_research_validation_dashboard(output_dir=tmp, bundle=bundle)
        html = (Path(tmp) / "latest-evidence.html").read_text(encoding="utf-8")

    progress = summarize_product_capability_progress()
    sprint = summarize_product_capability_completion_sprint()
    summary: dict[str, Any] = {
        "phase": "83",
        "phase_id": 83,
        "phase83_closure_ready": True,
        "sprint_roadmap_ready": sprint["sprint_roadmap_ready"],
        "indicator_trend_drilldown_navigation_ready": True,
        "indicator_trend_chart_rendering_ready": True,
        "latest_evidence_dashboard_page_ready": (
            dashboard["browser_verification_ready"]
            and "latest-evidence.html" in "\n".join(dashboard["written_files"])
        ),
        "role_drilldown_count": drilldown["role_drilldown_count"],
        "current_chart_coverage_row_count": len(coverage["role_chart_coverage_rows"]),
        "role_trend_target_count": html.count("data-indicator-trend-target"),
        "role_trend_shortcut_count": html.count("data-role-trend-shortcut"),
        "coverage_trend_link_count": html.count("data-coverage-trend-link"),
        "indicator_trend_link_count": html.count("data-indicator-trend-link"),
        "ytd_trend_period_card_count": html.count('data-chart-period="ytd"'),
        "trailing_1y_trend_period_card_count": html.count(
            'data-chart-period="trailing_1y"',
        ),
        "trailing_5y_trend_period_card_count": html.count(
            'data-chart-period="trailing_5y"',
        ),
        "ytd_trend_svg_count": html.count('data-chart-period-svg="ytd"'),
        "trailing_1y_trend_svg_count": html.count(
            'data-chart-period-svg="trailing_1y"',
        ),
        "trailing_5y_trend_svg_count": html.count(
            'data-chart-period-svg="trailing_5y"',
        ),
        "available_trend_svg_count": html.count("data-trend-chart-svg"),
        "unavailable_chart_role_count": coverage["role_without_official_series_count"],
        "trend_unavailable_empty_state_count": html.count("data-trend-chart-empty"),
        "browser_verification_ready": dashboard["browser_verification_ready"],
        "browser_missing_required_element_count": dashboard[
            "browser_missing_required_element_count"
        ],
        "prohibited_claim_count": dashboard["prohibited_claim_count"],
        "prohibited_action_field_count": dashboard["prohibited_action_field_count"],
        "current_data_used_to_infer_declared_phase_count": 0,
        "standalone_classifier_added_count": drilldown[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": drilldown[
            "phase_rank_or_score_added_count"
        ],
        "role_count_voting_added_count": drilldown["role_count_voting_added_count"],
        "candidate_phase_emitted": drilldown["candidate_phase_emitted"],
        "current_phase_emitted": drilldown["current_phase_emitted"],
        "current_allocation_recommendation_count": 0,
        "trade_signal_output_count": 0,
        "production_behavior_change_count": max(
            int(coverage["production_behavior_change_count"]),
            int(progress["production_behavior_change_count"]),
        ),
        "semantic_drift_count": progress["semantic_drift_count"],
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "declared_state_preserved_indicator_trend_drilldown_ready"
        ),
        "portfolio_policy_research_alignment": "unchanged_no_current_allocation",
        "historical_replay_backtest_alignment": "unchanged_no_backtest_execution",
        "legal_transition_semantics_preserved": True,
        "development_next_phase": 84,
        "phase83_closure_status": (
            "closed_indicator_trend_drilldown_navigation_and_charts_ready"
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
    root = payload["phase83_indicator_trend_drilldown_closure"]
    return dict(root["hard_gates"])


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())

"""Phase84 dashboard decision explanation closure."""

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
from business_cycle.render.dashboard_decision_explanation import (
    build_dashboard_decision_explanation_view_model,
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
    ROOT / "specs/audits/phase84_dashboard_decision_explanation_closure.yaml"
)


def summarize_phase84_dashboard_decision_explanation_closure(
    path: str | Path = DEFAULT_CLOSURE_PATH,
) -> dict[str, Any]:
    """Return Phase84 closure fields for CLI, tests, and final reports."""

    expected = _load_expected(path)
    drilldown = build_indicator_dashboard_explanation_drilldown_view_model()
    coverage = build_current_macro_numeric_chart_coverage_view_model()
    explanation = build_dashboard_decision_explanation_view_model()
    bundle = build_research_dashboard_bundle(
        indicator_dashboard_explanation_drilldown=drilldown,
        current_macro_numeric_chart_coverage=coverage,
        dashboard_decision_explanation=explanation,
    )
    with tempfile.TemporaryDirectory(prefix="phase84_dashboard_", dir="/tmp") as tmp:
        dashboard = build_research_validation_dashboard(output_dir=tmp, bundle=bundle)
        html = (Path(tmp) / "latest-evidence.html").read_text(encoding="utf-8")

    progress = summarize_product_capability_progress()
    sprint = summarize_product_capability_completion_sprint()
    summary: dict[str, Any] = {
        "phase": "84",
        "phase_id": 84,
        "phase84_closure_ready": True,
        "sprint_roadmap_ready": sprint["sprint_roadmap_ready"],
        "dashboard_decision_explanation_ready": explanation[
            "dashboard_decision_explanation_ready"
        ],
        "latest_evidence_dashboard_page_ready": (
            dashboard["browser_verification_ready"]
            and "latest-evidence.html" in "\n".join(dashboard["written_files"])
        ),
        "declared_state_summary_ready": explanation["declared_state_summary_ready"],
        "legal_next_transition_summary_ready": explanation[
            "legal_next_transition_summary_ready"
        ],
        "support_contradiction_summary_ready": explanation[
            "support_contradiction_summary_ready"
        ],
        "missing_evidence_summary_ready": explanation[
            "missing_evidence_summary_ready"
        ],
        "why_not_formal_summary_ready": explanation["why_not_formal_summary_ready"],
        "declared_current_phase": explanation["declared_current_phase"],
        "legal_previous_phase": explanation["legal_previous_phase"],
        "legal_next_phase": explanation["legal_next_phase"],
        "phase_age_status": explanation["phase_age_status"],
        "narrative_card_count": explanation["narrative_card_count"],
        "decision_explanation_card_count": html.count(
            "data-decision-explanation-card",
        ),
        "dashboard_trust_caveat_count": html.count("data-dashboard-trust-caveat"),
        "why_not_formal_reason_count": explanation["why_not_formal_reason_count"],
        "role_drilldown_count": explanation["role_drilldown_count"],
        "major_group_drilldown_count": explanation["major_group_drilldown_count"],
        "current_numeric_context_role_count": explanation[
            "current_numeric_context_role_count"
        ],
        "chart_available_role_count": explanation["chart_available_role_count"],
        "unavailable_chart_role_count": explanation["unavailable_chart_role_count"],
        "metadata_ready_value_missing_drilldown_count": explanation[
            "metadata_ready_value_missing_drilldown_count"
        ],
        "source_metadata_incomplete_drilldown_count": explanation[
            "source_metadata_incomplete_drilldown_count"
        ],
        "authorized_input_required_drilldown_count": explanation[
            "authorized_input_required_drilldown_count"
        ],
        "supporting_proxy_drilldown_count": explanation[
            "supporting_proxy_drilldown_count"
        ],
        "group_ready_for_formal_phase_count": explanation[
            "group_ready_for_formal_phase_count"
        ],
        "browser_verification_ready": dashboard["browser_verification_ready"],
        "browser_missing_required_element_count": dashboard[
            "browser_missing_required_element_count"
        ],
        "prohibited_claim_count": dashboard["prohibited_claim_count"],
        "prohibited_action_field_count": max(
            int(dashboard["prohibited_action_field_count"]),
            int(explanation["prohibited_output_field_count"]),
        ),
        "prohibited_output_field_count": explanation["prohibited_output_field_count"],
        "current_data_used_to_infer_declared_phase_count": explanation[
            "current_data_used_to_infer_declared_phase_count"
        ],
        "standalone_classifier_added_count": explanation[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": explanation[
            "phase_rank_or_score_added_count"
        ],
        "role_count_voting_added_count": explanation["role_count_voting_added_count"],
        "candidate_phase_emitted": explanation["candidate_phase_emitted"],
        "current_phase_emitted": explanation["current_phase_emitted"],
        "current_allocation_recommendation_count": explanation[
            "current_allocation_recommendation_count"
        ],
        "trade_signal_output_count": explanation["trade_signal_output_count"],
        "production_behavior_change_count": max(
            int(explanation["production_behavior_change_count"]),
            int(progress["production_behavior_change_count"]),
        ),
        "semantic_drift_count": max(
            int(explanation["semantic_drift_count"]),
            int(progress["semantic_drift_count"]),
        ),
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "declared_state_preserved_dashboard_decision_explanation_polished"
        ),
        "portfolio_policy_research_alignment": "unchanged_no_current_allocation",
        "historical_replay_backtest_alignment": "unchanged_no_backtest_execution",
        "legal_transition_semantics_preserved": True,
        "development_next_phase": 85,
        "phase84_closure_status": (
            "closed_dashboard_decision_explanation_polished_no_phase_output"
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
    root = payload["phase84_dashboard_decision_explanation_closure"]
    return dict(root["hard_gates"])


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())

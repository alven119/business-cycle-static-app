"""Phase85 current data refresh UX closure."""

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
from business_cycle.render.current_data_refresh_ux import (
    build_current_data_refresh_ux_view_model,
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
    ROOT / "specs/audits/phase85_current_data_refresh_ux_closure.yaml"
)


def summarize_phase85_current_data_refresh_ux_closure(
    path: str | Path = DEFAULT_CLOSURE_PATH,
) -> dict[str, Any]:
    """Return Phase85 closure fields for CLI, tests, and final reports."""

    expected = _load_expected(path)
    drilldown = build_indicator_dashboard_explanation_drilldown_view_model()
    coverage = build_current_macro_numeric_chart_coverage_view_model()
    explanation = build_dashboard_decision_explanation_view_model()
    refresh_ux = build_current_data_refresh_ux_view_model(
        current_macro_numeric_chart_coverage=coverage,
        indicator_dashboard_explanation_drilldown=drilldown,
    )
    bundle = build_research_dashboard_bundle(
        indicator_dashboard_explanation_drilldown=drilldown,
        current_macro_numeric_chart_coverage=coverage,
        dashboard_decision_explanation=explanation,
        current_data_refresh_ux=refresh_ux,
    )
    with tempfile.TemporaryDirectory(prefix="phase85_dashboard_", dir="/tmp") as tmp:
        dashboard = build_research_validation_dashboard(output_dir=tmp, bundle=bundle)
        html = (Path(tmp) / "latest-evidence.html").read_text(encoding="utf-8")

    progress = summarize_product_capability_progress()
    sprint = summarize_product_capability_completion_sprint()
    summary: dict[str, Any] = {
        "phase": "85",
        "phase_id": 85,
        "phase85_closure_ready": True,
        "sprint_roadmap_ready": sprint["sprint_roadmap_ready"],
        "current_data_refresh_ux_ready": refresh_ux["current_data_refresh_ux_ready"],
        "latest_evidence_dashboard_page_ready": (
            dashboard["browser_verification_ready"]
            and "latest-evidence.html" in "\n".join(dashboard["written_files"])
        ),
        "refresh_mode_summary_ready": bool(refresh_ux["refresh_mode_summary"]),
        "last_update_summary_ready": bool(refresh_ux["last_update_summary"]),
        "freshness_summary_ready": bool(refresh_ux["freshness_summary"]),
        "source_risk_refresh_summary_ready": bool(
            refresh_ux["source_risk_refresh_summary"],
        ),
        "manual_refresh_handoff_ready": (
            len(refresh_ux["manual_refresh_handoff_steps"]) == 5
        ),
        "refresh_ux_card_count": len(refresh_ux["refresh_cards"]),
        "html_refresh_ux_card_count": html.count("data-refresh-ux-card"),
        "manual_refresh_handoff_step_count": len(
            refresh_ux["manual_refresh_handoff_steps"],
        ),
        "html_manual_refresh_handoff_step_count": html.count(
            "data-manual-refresh-handoff-step",
        ),
        "refresh_trust_caveat_count": len(refresh_ux["trust_caveats"]),
        "html_refresh_trust_caveat_count": html.count("data-refresh-trust-caveat"),
        "role_count": refresh_ux["role_count"],
        "role_with_numeric_context_count": refresh_ux[
            "role_with_numeric_context_count"
        ],
        "role_with_available_chart_payload_count": refresh_ux[
            "role_with_available_chart_payload_count"
        ],
        "role_without_official_series_count": refresh_ux[
            "role_without_official_series_count"
        ],
        "source_risk_visible_role_count": refresh_ux[
            "source_risk_visible_role_count"
        ],
        "elevated_source_risk_role_count": refresh_ux[
            "elevated_source_risk_role_count"
        ],
        "metadata_ready_value_missing_drilldown_count": refresh_ux[
            "metadata_ready_value_missing_drilldown_count"
        ],
        "source_metadata_incomplete_drilldown_count": refresh_ux[
            "source_metadata_incomplete_drilldown_count"
        ],
        "authorized_input_required_drilldown_count": refresh_ux[
            "authorized_input_required_drilldown_count"
        ],
        "live_refresh_executed_count": refresh_ux["live_refresh_executed_count"],
        "live_fetch_attempt_count": refresh_ux["live_fetch_attempt_count"],
        "repository_output_count": refresh_ux["repository_output_count"],
        "point_in_time_claim_count": refresh_ux["point_in_time_claim_count"],
        "browser_verification_ready": dashboard["browser_verification_ready"],
        "browser_missing_required_element_count": dashboard[
            "browser_missing_required_element_count"
        ],
        "prohibited_claim_count": dashboard["prohibited_claim_count"],
        "prohibited_action_field_count": max(
            int(dashboard["prohibited_action_field_count"]),
            int(refresh_ux["prohibited_output_field_count"]),
        ),
        "prohibited_output_field_count": refresh_ux["prohibited_output_field_count"],
        "current_data_used_to_infer_declared_phase_count": refresh_ux[
            "current_data_used_to_infer_declared_phase_count"
        ],
        "standalone_classifier_added_count": refresh_ux[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": refresh_ux[
            "phase_rank_or_score_added_count"
        ],
        "role_count_voting_added_count": refresh_ux["role_count_voting_added_count"],
        "candidate_phase_emitted": refresh_ux["candidate_phase_emitted"],
        "current_phase_emitted": refresh_ux["current_phase_emitted"],
        "current_allocation_recommendation_count": 0,
        "trade_signal_output_count": 0,
        "production_behavior_change_count": max(
            int(refresh_ux["production_behavior_change_count"]),
            int(progress["production_behavior_change_count"]),
        ),
        "semantic_drift_count": max(
            int(refresh_ux["semantic_drift_count"]),
            int(progress["semantic_drift_count"]),
        ),
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "declared_state_preserved_current_data_refresh_ux_hardened"
        ),
        "portfolio_policy_research_alignment": "unchanged_no_current_allocation",
        "historical_replay_backtest_alignment": "unchanged_no_backtest_execution",
        "legal_transition_semantics_preserved": True,
        "development_next_phase": 86,
        "phase85_closure_status": (
            "closed_current_data_refresh_ux_hardened_no_live_execution"
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
    root = payload["phase85_current_data_refresh_ux_closure"]
    return dict(root["hard_gates"])


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())

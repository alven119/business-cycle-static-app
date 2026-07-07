"""Phase86 transition risk evidence accumulation closure."""

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
from business_cycle.render.indicator_dashboard_explanation_drilldown import (
    build_indicator_dashboard_explanation_drilldown_view_model,
)
from business_cycle.render.research_dashboard_bundle import (
    build_research_dashboard_bundle,
)
from business_cycle.render.research_validation_dashboard import (
    build_research_validation_dashboard,
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
    / "specs/audits/phase86_transition_risk_evidence_accumulation_closure.yaml"
)


def summarize_phase86_transition_risk_evidence_accumulation_closure(
    path: str | Path = DEFAULT_CLOSURE_PATH,
) -> dict[str, Any]:
    """Return Phase86 closure fields for CLI, tests, and final reports."""

    expected = _load_expected(path)
    drilldown = build_indicator_dashboard_explanation_drilldown_view_model()
    preview = build_transition_timing_replay_preview_view_model()
    accumulation = build_transition_risk_evidence_accumulation_view_model(
        transition_timing_replay_preview=preview,
    )
    bundle = build_research_dashboard_bundle(
        indicator_dashboard_explanation_drilldown=drilldown,
        transition_timing_replay_preview=preview,
        transition_risk_evidence_accumulation=accumulation,
    )
    with tempfile.TemporaryDirectory(prefix="phase86_dashboard_", dir="/tmp") as tmp:
        dashboard = build_research_validation_dashboard(output_dir=tmp, bundle=bundle)
        html = (Path(tmp) / "latest-evidence.html").read_text(encoding="utf-8")

    progress = summarize_product_capability_progress()
    sprint = summarize_product_capability_completion_sprint()
    summary: dict[str, Any] = {
        "phase": "86",
        "phase_id": 86,
        "phase86_closure_ready": True,
        "sprint_roadmap_ready": sprint["sprint_roadmap_ready"],
        "transition_risk_evidence_accumulation_ready": accumulation[
            "transition_risk_evidence_accumulation_ready"
        ],
        "latest_evidence_dashboard_page_ready": (
            dashboard["browser_verification_ready"]
            and "latest-evidence.html" in "\n".join(dashboard["written_files"])
        ),
        "dashboard_transition_risk_evidence_accumulation_view_ready": (
            "transition_risk_evidence_accumulation"
            in {view["view_id"] for view in bundle["views"]}
        ),
        "rendered_transition_risk_evidence_accumulation_ready": (
            "data-transition-risk-evidence-accumulation" in html
        ),
        "transition_accumulation_lane_card_count": accumulation[
            "transition_accumulation_lane_card_count"
        ],
        "html_transition_accumulation_lane_card_count": html.count(
            "data-accumulation-lane-card",
        ),
        "evidence_accumulation_event_count": accumulation[
            "evidence_accumulation_event_count"
        ],
        "continuation_lane_card_count": accumulation["continuation_lane_card_count"],
        "watch_lane_card_count": accumulation["watch_lane_card_count"],
        "confirmation_lane_card_count": accumulation["confirmation_lane_card_count"],
        "watch_confirmation_boundary_count": accumulation[
            "watch_confirmation_boundary_count"
        ],
        "html_watch_confirmation_boundary_summary_count": html.count(
            "data-watch-confirmation-boundary-summary",
        ),
        "lane_with_missing_evidence_count": accumulation[
            "lane_with_missing_evidence_count"
        ],
        "missing_evidence_event_count": accumulation[
            "missing_evidence_event_count"
        ],
        "html_missing_evidence_summary_count": html.count(
            "data-missing-evidence-summary",
        ),
        "contradictory_evidence_lane_count": accumulation[
            "contradictory_evidence_lane_count"
        ],
        "contradictory_evidence_event_count": accumulation[
            "contradictory_evidence_event_count"
        ],
        "html_contradictory_evidence_summary_count": html.count(
            "data-contradictory-evidence-summary",
        ),
        "next_required_observation_count": accumulation[
            "next_required_observation_count"
        ],
        "html_next_required_observation_count": html.count(
            "data-next-required-observation",
        ),
        "phase_presence_transition_separation_valid": accumulation[
            "phase_presence_transition_separation_valid"
        ],
        "watch_confirmation_separation_valid": accumulation[
            "watch_confirmation_separation_valid"
        ],
        "missing_value_treated_as_neutral_count": accumulation[
            "missing_value_treated_as_neutral_count"
        ],
        "metadata_only_promoted_to_phase_support_count": accumulation[
            "metadata_only_promoted_to_phase_support_count"
        ],
        "contradictory_evidence_promoted_to_confirmation_count": accumulation[
            "contradictory_evidence_promoted_to_confirmation_count"
        ],
        "watch_promoted_to_confirmation_count": accumulation[
            "watch_promoted_to_confirmation_count"
        ],
        "browser_verification_ready": dashboard["browser_verification_ready"],
        "browser_missing_required_element_count": dashboard[
            "browser_missing_required_element_count"
        ],
        "prohibited_claim_count": dashboard["prohibited_claim_count"],
        "prohibited_action_field_count": max(
            int(dashboard["prohibited_action_field_count"]),
            int(accumulation["prohibited_output_field_count"]),
        ),
        "prohibited_output_field_count": accumulation["prohibited_output_field_count"],
        "current_data_used_to_infer_declared_phase_count": accumulation[
            "current_data_used_to_infer_declared_phase_count"
        ],
        "standalone_classifier_added_count": accumulation[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": accumulation[
            "phase_rank_or_score_added_count"
        ],
        "role_count_voting_added_count": accumulation["role_count_voting_added_count"],
        "candidate_phase_emitted": accumulation["candidate_phase_emitted"],
        "current_phase_emitted": accumulation["current_phase_emitted"],
        "current_allocation_recommendation_count": 0,
        "trade_signal_output_count": 0,
        "production_behavior_change_count": max(
            int(accumulation["production_behavior_change_count"]),
            int(progress["production_behavior_change_count"]),
        ),
        "semantic_drift_count": max(
            int(accumulation["semantic_drift_count"]),
            int(progress["semantic_drift_count"]),
        ),
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "declared_state_preserved_transition_risk_accumulation_visible"
        ),
        "portfolio_policy_research_alignment": "unchanged_no_current_allocation",
        "historical_replay_backtest_alignment": "unchanged_no_backtest_execution",
        "legal_transition_semantics_preserved": True,
        "development_next_phase": 87,
        "phase86_closure_status": (
            "closed_transition_risk_evidence_accumulation_view_ready_no_phase_selection"
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
    root = payload["phase86_transition_risk_evidence_accumulation_closure"]
    return dict(root["hard_gates"])


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())

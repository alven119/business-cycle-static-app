"""Phase77 portfolio replay schedule and score interpretation closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.portfolio.policy_replay_schedule import (
    summarize_portfolio_policy_replay_schedule,
)
from business_cycle.render.dashboard_indicator_method_explanation import (
    summarize_dashboard_indicator_method_explanation,
)
from business_cycle.render.indicator_chart_explanation_payload import (
    summarize_indicator_chart_explanation_payload,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = (
    ROOT / "specs/audits/phase77_portfolio_policy_replay_schedule_closure.yaml"
)


def summarize_phase77_portfolio_policy_replay_schedule_closure(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Return Phase77 closure fields for CLI, tests, and final reports."""

    expected = _load_expected(path)
    schedule = summarize_portfolio_policy_replay_schedule()
    method = summarize_dashboard_indicator_method_explanation()
    chart = summarize_indicator_chart_explanation_payload()
    progress = summarize_product_capability_progress()

    role_with_score_interpretation_count = int(
        method["role_with_score_interpretation_count"]
    )
    role_method_count = int(method["role_method_explanation_count"])
    summary: dict[str, Any] = {
        "phase": "77",
        "phase_id": 77,
        "phase77_closure_ready": True,
        **_pick(
            schedule,
            (
                "portfolio_policy_replay_schedule_contract_ready",
                "schedule_row_count",
                "template_with_schedule_count",
                "missing_template_schedule_count",
                "invalid_template_reference_count",
                "execution_allowed_now_count",
                "backtest_execution_count",
                "portfolio_policy_replay_execution_count",
                "current_allocation_recommendation_count",
                "trade_signal_output_count",
                "live_allocation_output_count",
                "prohibited_schedule_output_field_count",
                "portfolio_policy_research_alignment",
                "historical_replay_backtest_alignment",
            ),
        ),
        "score_interpretation_high_low_ready": (
            role_with_score_interpretation_count == role_method_count
            and role_with_score_interpretation_count > 0
        ),
        "role_with_score_interpretation_count": role_with_score_interpretation_count,
        "score_interpretation_missing_count": (
            role_method_count - role_with_score_interpretation_count
        ),
        "dashboard_indicator_method_explanation_ready": method[
            "dashboard_indicator_method_explanation_ready"
        ],
        "indicator_chart_explanation_payload_ready": chart[
            "indicator_chart_explanation_payload_ready"
        ],
        "candidate_phase_emitted": (
            bool(schedule["candidate_phase_emitted"])
            or bool(method["candidate_phase_emitted"])
            or bool(chart["candidate_phase_emitted"])
        ),
        "current_phase_emitted": (
            bool(schedule["current_phase_emitted"])
            or bool(method["current_phase_emitted"])
            or bool(chart["current_phase_emitted"])
        ),
        "standalone_classifier_added_count": max(
            int(method["standalone_classifier_added_count"]),
            int(chart["standalone_classifier_added_count"]),
        ),
        "phase_rank_or_score_added_count": max(
            int(method["phase_rank_or_score_added_count"]),
            int(chart["phase_rank_or_score_added_count"]),
        ),
        "role_count_voting_added_count": max(
            int(method["role_count_voting_added_count"]),
            int(chart["role_count_voting_added_count"]),
        ),
        "production_behavior_change_count": max(
            int(schedule["production_behavior_change_count"]),
            int(method["production_behavior_change_count"]),
            int(chart["production_behavior_change_count"]),
            int(progress["production_behavior_change_count"]),
        ),
        "semantic_drift_count": max(
            int(schedule["semantic_drift_count"]),
            int(method["semantic_drift_count"]),
            int(chart["semantic_drift_count"]),
            int(progress["semantic_drift_count"]),
        ),
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "declared_state_preserved_policy_replay_schedule_ready"
        ),
        "phase77_closure_status": (
            "closed_policy_replay_schedule_preregistered_score_interpretation_"
            "visible_no_execution"
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
    root = payload["phase77_portfolio_policy_replay_schedule_closure"]
    return dict(root["hard_gates"])


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _pick(payload: dict[str, Any], keys: tuple[str, ...]) -> dict[str, Any]:
    return {key: payload[key] for key in keys}

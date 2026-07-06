"""Phase78 cash-flow-aware backtest kernel closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.portfolio.cash_flow_backtest_kernel_contract import (
    summarize_cash_flow_backtest_kernel_contract,
)
from business_cycle.portfolio.policy_replay_schedule import (
    summarize_portfolio_policy_replay_schedule,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = (
    ROOT / "specs/audits/phase78_cash_flow_backtest_kernel_closure.yaml"
)


def summarize_phase78_cash_flow_backtest_kernel_closure(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Return Phase78 closure fields for CLI, tests, and final reports."""

    expected = _load_expected(path)
    kernel = summarize_cash_flow_backtest_kernel_contract()
    schedule = summarize_portfolio_policy_replay_schedule()
    progress = summarize_product_capability_progress()

    summary: dict[str, Any] = {
        "phase": "78",
        "phase_id": 78,
        "phase78_closure_ready": True,
        **_pick(
            kernel,
            (
                "cash_flow_aware_backtest_kernel_contract_ready",
                "kernel_component_count",
                "required_kernel_component_count",
                "structural_fixture_count",
                "structural_fixture_validation_pass_count",
                "execution_allowed_now_count",
                "metric_computation_enabled",
                "backtest_execution_count",
                "generated_output_under_tmp_only",
                "current_allocation_recommendation_count",
                "trade_signal_output_count",
                "live_allocation_output_count",
                "prohibited_kernel_output_field_count",
                "investment_advice_wording_count",
                "portfolio_policy_research_alignment",
                "historical_replay_backtest_alignment",
            ),
        ),
        "portfolio_policy_replay_schedule_contract_ready": schedule[
            "portfolio_policy_replay_schedule_contract_ready"
        ],
        "candidate_phase_emitted": bool(kernel["candidate_phase_emitted"])
        or bool(schedule["candidate_phase_emitted"]),
        "current_phase_emitted": bool(kernel["current_phase_emitted"])
        or bool(schedule["current_phase_emitted"]),
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "role_count_voting_added_count": 0,
        "production_behavior_change_count": max(
            int(kernel["production_behavior_change_count"]),
            int(schedule["production_behavior_change_count"]),
            int(progress["production_behavior_change_count"]),
        ),
        "semantic_drift_count": max(
            int(kernel["semantic_drift_count"]),
            int(schedule["semantic_drift_count"]),
            int(progress["semantic_drift_count"]),
        ),
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "declared_state_preserved_cash_flow_backtest_kernel_contract_ready"
        ),
        "phase78_closure_status": (
            "closed_cash_flow_backtest_kernel_contract_ready_no_execution_or_metrics"
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
    root = payload["phase78_cash_flow_backtest_kernel_closure"]
    return dict(root["hard_gates"])


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _pick(payload: dict[str, Any], keys: tuple[str, ...]) -> dict[str, Any]:
    return {key: payload[key] for key in keys}

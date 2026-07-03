"""Portfolio policy research baseline contract helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_BASELINE_PATH = (
    ROOT / "specs/portfolio/portfolio_policy_research_baseline_contract.yaml"
)

REQUIRED_TEMPLATE_IDS = {
    "passive_all_stock_baseline",
    "stock_cash_initial",
    "stock_cash_advanced",
    "stock_long_treasury_initial",
    "stock_long_treasury_advanced",
    "boom_70_50_30_template",
    "recession_defense_research_template",
    "recovery_re_risk_research_template",
}


class PortfolioPolicyResearchBaselineError(ValueError):
    """Raised when the portfolio policy research baseline is invalid."""


def build_portfolio_policy_research_baseline(
    path: str | Path = DEFAULT_BASELINE_PATH,
) -> dict[str, Any]:
    """Load the portfolio policy research baseline contract."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise PortfolioPolicyResearchBaselineError("baseline YAML must be a mapping")
    baseline = payload.get("portfolio_policy_research_baseline_contract")
    if not isinstance(baseline, dict):
        raise PortfolioPolicyResearchBaselineError(
            "portfolio_policy_research_baseline_contract must be a mapping"
        )
    return baseline


def summarize_portfolio_policy_research_baseline(
    path: str | Path = DEFAULT_BASELINE_PATH,
) -> dict[str, Any]:
    """Summarize baseline readiness for Phase 75 gates."""

    baseline = build_portfolio_policy_research_baseline(path)
    templates = list(baseline.get("required_policy_templates", ()))
    template_ids = {str(row.get("template_id")) for row in templates}
    research_only_count = sum(row.get("research_only") is True for row in templates)
    backtest_only_count = sum(row.get("backtest_only") is True for row in templates)
    current_allocation_count = sum(
        row.get("current_allocation_recommendation_allowed") is not False
        for row in templates
    )
    trade_signal_count = sum(
        row.get("trade_signal_allowed") is not False for row in templates
    )
    output_policy = baseline.get("output_policy") or {}
    prohibited_outputs = set(output_policy.get("prohibited_outputs") or ())
    disabled_guards = baseline.get("disabled_runtime_guards") or {}
    expected = dict(baseline.get("hard_gates") or {})
    summary = {
        "portfolio_policy_research_baseline_contract_ready": (
            template_ids == REQUIRED_TEMPLATE_IDS
            and research_only_count == len(REQUIRED_TEMPLATE_IDS)
            and backtest_only_count == len(REQUIRED_TEMPLATE_IDS)
            and current_allocation_count == 0
            and trade_signal_count == 0
            and {"buy_signal", "sell_signal", "trade_action"}.issubset(
                prohibited_outputs
            )
            and disabled_guards.get("backtest_execution_enabled") is False
            and disabled_guards.get("portfolio_policy_replay_execution_enabled")
            is False
        ),
        "version": baseline["version"],
        "status": baseline["status"],
        "phase_id": int(baseline["phase_id"]),
        "contract_id": baseline["contract_id"],
        "required_policy_template_count": len(templates),
        "required_policy_template_ids": sorted(template_ids),
        "research_only_template_count": research_only_count,
        "backtest_only_template_count": backtest_only_count,
        "book_or_doctrine_template_count": len(templates),
        "current_allocation_recommendation_count": current_allocation_count,
        "trade_signal_output_count": trade_signal_count,
        "live_allocation_output_count": int(
            "live_allocation" not in prohibited_outputs
        ),
        "backtest_execution_count": int(
            disabled_guards.get("backtest_execution_enabled") is not False
        ),
        "portfolio_policy_replay_execution_count": int(
            disabled_guards.get("portfolio_policy_replay_execution_enabled")
            is not False
        ),
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "portfolio_policy_research_alignment": (
            "research_templates_preregistered_no_current_allocation"
        ),
        "historical_replay_backtest_alignment": (
            "future_replay_backtest_inputs_preregistered_no_execution"
        ),
        "allowed_inputs": list(baseline.get("allowed_inputs") or ()),
        "prohibited_inputs": list(baseline.get("prohibited_inputs") or ()),
        "templates": templates,
    }
    summary["result"] = "passed" if _passes(summary, expected) else "blocked"
    return summary


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())

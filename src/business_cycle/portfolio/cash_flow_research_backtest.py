"""Cash-flow-aware research backtest kernel for Phase 125."""

from __future__ import annotations

from datetime import date
from math import sqrt
from statistics import pstdev
from typing import Any


class CashFlowResearchBacktestError(ValueError):
    """Raised when a Phase 125 research backtest input is unsafe."""


def run_cash_flow_research_backtest(
    *,
    scenario_id: str,
    policy_template_id: str,
    parameter_id: str,
    periods: list[str],
    asset_returns: dict[str, dict[str, float]],
    equity_parameter: float,
    defensive_asset: str,
    initial_value: float,
    annual_contribution: float,
    transaction_cost_bps: float,
) -> dict[str, Any]:
    """Run a constant-parameter sensitivity path with unitized NAV."""

    _validate_inputs(
        periods=periods,
        asset_returns=asset_returns,
        equity_parameter=equity_parameter,
        defensive_asset=defensive_asset,
        initial_value=initial_value,
        annual_contribution=annual_contribution,
        transaction_cost_bps=transaction_cost_bps,
    )
    defensive_parameter = 1.0 - equity_parameter
    target = {"equity": equity_parameter, defensive_asset: defensive_parameter}
    nav = 100.0
    units = initial_value / nav
    holdings = {
        "equity": initial_value * equity_parameter,
        defensive_asset: initial_value * defensive_parameter,
    }
    total_contributions = 0.0
    total_cost = 0.0
    total_turnover = 0.0
    nav_path = [nav]
    account_value_path = [initial_value]
    monthly_returns: list[float] = []
    contribution_cashflows: list[tuple[date, float]] = []
    rows: list[dict[str, Any]] = []

    for index, period in enumerate(periods):
        period_date = date.fromisoformat(period)
        beginning_nav = nav
        account_value = sum(holdings.values())
        contribution = annual_contribution if period_date.month == 1 else 0.0
        if contribution:
            units += contribution / nav
            total_contributions += contribution
            contribution_cashflows.append(
                (period_date.replace(day=1), -contribution)
            )
            for asset, parameter in target.items():
                holdings[asset] += contribution * parameter
            account_value += contribution

        rebalance = index == 0 or period_date.month == 1
        turnover = 0.0
        cost = 0.0
        if rebalance:
            current = {
                asset: value / account_value for asset, value in holdings.items()
            }
            turnover = sum(
                abs(target[asset] - current.get(asset, 0.0)) for asset in target
            ) / 2.0
            cost = account_value * turnover * transaction_cost_bps / 10_000.0
            account_value -= cost
            holdings = {
                asset: account_value * parameter for asset, parameter in target.items()
            }
            total_turnover += turnover
            total_cost += cost

        period_returns = asset_returns[period]
        holdings = {
            asset: value * (1.0 + float(period_returns[asset]))
            for asset, value in holdings.items()
        }
        account_value = sum(holdings.values())
        nav = account_value / units
        monthly_return = nav / beginning_nav - 1.0
        nav_path.append(nav)
        account_value_path.append(account_value)
        monthly_returns.append(monthly_return)
        rows.append(
            {
                "as_of": period,
                "external_contribution": contribution,
                "rebalance_applied": rebalance,
                "turnover": turnover,
                "transaction_cost": cost,
                "unitized_nav": nav,
                "account_value": account_value,
                "cashflow_neutral_return": monthly_return,
            }
        )

    period_count = len(periods)
    twr = nav_path[-1] / nav_path[0] - 1.0
    annualized_twr = (1.0 + twr) ** (12.0 / period_count) - 1.0
    dated_cashflows = [
        (date.fromisoformat(periods[0]).replace(day=1), -initial_value)
    ]
    dated_cashflows.extend(contribution_cashflows)
    dated_cashflows.append((date.fromisoformat(periods[-1]), account_value_path[-1]))
    metrics = {
        "terminal_wealth": account_value_path[-1],
        "total_contributions": total_contributions,
        "net_investment_gain": (
            account_value_path[-1] - initial_value - total_contributions
        ),
        "time_weighted_return": twr,
        "annualized_time_weighted_return": annualized_twr,
        "money_weighted_return_xirr": _xirr(dated_cashflows),
        "annualized_volatility": (
            pstdev(monthly_returns) * sqrt(12.0)
            if len(monthly_returns) > 1
            else 0.0
        ),
        "max_drawdown_on_unitized_nav": _max_drawdown(nav_path),
        "turnover": total_turnover,
        "transaction_cost_total": total_cost,
    }
    return {
        "result_id": f"phase125::{scenario_id}::{parameter_id}",
        "scenario_id": scenario_id,
        "policy_template_id": policy_template_id,
        "parameter_id": parameter_id,
        "result_scope": "constant_parameter_sensitivity_only",
        "data_mode": "strict_pit_macro_with_realized_market_returns",
        "research_only": True,
        "backtest_only": True,
        "equity_parameter_percent": round(equity_parameter * 100),
        "defensive_asset": defensive_asset,
        "defensive_parameter_percent": round(defensive_parameter * 100),
        "period_count": period_count,
        "metrics": metrics,
        "monthly_rows": rows,
        "dynamic_transition_policy_executed": False,
        "current_allocation_recommendation_allowed": False,
        "trade_signal_allowed": False,
        "caveats_zh": [
            "此為固定參數 sensitivity backtest，不是動態換倉策略結果。",
            "backtest-only，不是目前配置建議。",
            "回測結果不代表未來績效，不構成投資建議。",
        ],
    }


def _validate_inputs(
    *,
    periods: list[str],
    asset_returns: dict[str, dict[str, float]],
    equity_parameter: float,
    defensive_asset: str,
    initial_value: float,
    annual_contribution: float,
    transaction_cost_bps: float,
) -> None:
    if not periods or periods != sorted(periods) or len(set(periods)) != len(periods):
        raise CashFlowResearchBacktestError("periods must be unique and sorted")
    if defensive_asset not in {"cash", "long_treasury_proxy"}:
        raise CashFlowResearchBacktestError("unsupported defensive asset")
    if not 0.0 <= equity_parameter <= 1.0:
        raise CashFlowResearchBacktestError("equity parameter must be within [0, 1]")
    if initial_value <= 0 or annual_contribution < 0 or transaction_cost_bps < 0:
        raise CashFlowResearchBacktestError("cash and cost inputs must be non-negative")
    for period in periods:
        date.fromisoformat(period)
        row = asset_returns.get(period)
        if row is None or "equity" not in row or defensive_asset not in row:
            raise CashFlowResearchBacktestError(
                f"missing required asset return for {period}"
            )
        if any(float(value) <= -1.0 for value in row.values()):
            raise CashFlowResearchBacktestError("asset return must be greater than -100%")


def _max_drawdown(values: list[float]) -> float:
    peak = values[0]
    drawdown = 0.0
    for value in values:
        peak = max(peak, value)
        drawdown = min(drawdown, value / peak - 1.0)
    return drawdown


def _xirr(cashflows: list[tuple[date, float]]) -> float | None:
    if not any(value < 0 for _, value in cashflows) or not any(
        value > 0 for _, value in cashflows
    ):
        return None
    origin = min(day for day, _ in cashflows)

    def npv(rate: float) -> float:
        return sum(
            value / ((1.0 + rate) ** ((day - origin).days / 365.0))
            for day, value in cashflows
        )

    low, high = -0.9999, 10.0
    low_value, high_value = npv(low), npv(high)
    if low_value * high_value > 0:
        return None
    for _ in range(200):
        mid = (low + high) / 2.0
        mid_value = npv(mid)
        if abs(mid_value) < 1e-10:
            return mid
        if low_value * mid_value <= 0:
            high = mid
        else:
            low, low_value = mid, mid_value
    return (low + high) / 2.0

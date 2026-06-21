"""Cash-flow-aware backtest methodology helpers."""

from __future__ import annotations

from dataclasses import dataclass
from math import prod


class CashflowMethodologyError(ValueError):
    """Raised when a cash-flow methodology guard is violated."""


@dataclass(frozen=True)
class CashflowAwareMetrics:
    """Cash-flow-aware deterministic metrics."""

    terminal_wealth: float
    total_contributions: float
    net_investment_gain: float
    time_weighted_return: float
    unitized_nav_path: list[float]
    max_drawdown_on_unitized_nav: float


def guard_simple_return_usage(external_cashflows_present: bool) -> None:
    """Block ending/beginning return misuse when external cash flows exist."""

    if external_cashflows_present:
        raise CashflowMethodologyError(
            "ending_value / beginning_value - 1 is prohibited when external cash flows exist"
        )


def calculate_cashflow_aware_metrics(
    *,
    initial_value: float,
    period_returns: list[float],
    external_cashflows: list[float],
) -> CashflowAwareMetrics:
    """Calculate TWR and unitized NAV for deterministic fixtures.

    Cash flows are modeled at each period end after the period return.
    Positive cash flows are contributions.
    """

    if len(period_returns) != len(external_cashflows):
        raise CashflowMethodologyError("period_returns and external_cashflows length mismatch")
    account_value = float(initial_value)
    nav = 100.0
    unit_count = account_value / nav
    nav_path = [nav]
    total_contributions = sum(flow for flow in external_cashflows if flow > 0.0)

    for period_return, cashflow in zip(period_returns, external_cashflows, strict=True):
        nav *= 1.0 + float(period_return)
        account_value = unit_count * nav
        if cashflow:
            unit_count += float(cashflow) / nav
            account_value += float(cashflow)
        nav_path.append(nav)

    time_weighted_return = prod(1.0 + float(value) for value in period_returns) - 1.0
    net_gain = account_value - initial_value - total_contributions
    return CashflowAwareMetrics(
        terminal_wealth=account_value,
        total_contributions=total_contributions,
        net_investment_gain=net_gain,
        time_weighted_return=time_weighted_return,
        unitized_nav_path=nav_path,
        max_drawdown_on_unitized_nav=_max_drawdown(nav_path),
    )


def _max_drawdown(values: list[float]) -> float:
    peak = values[0]
    max_drawdown = 0.0
    for value in values:
        peak = max(peak, value)
        max_drawdown = min(max_drawdown, value / peak - 1.0)
    return max_drawdown


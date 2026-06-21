from __future__ import annotations

import pytest

from business_cycle.audits import (
    CashflowMethodologyError,
    calculate_cashflow_aware_metrics,
    guard_simple_return_usage,
)


def test_external_cashflow_blocks_simple_ending_beginning_return() -> None:
    with pytest.raises(CashflowMethodologyError):
        guard_simple_return_usage(external_cashflows_present=True)


def test_zero_return_contribution_is_not_treated_as_gain() -> None:
    metrics = calculate_cashflow_aware_metrics(
        initial_value=100.0,
        period_returns=[0.0, 0.0],
        external_cashflows=[0.0, 100.0],
    )

    assert metrics.terminal_wealth == 200.0
    assert metrics.total_contributions == 100.0
    assert metrics.net_investment_gain == 0.0
    assert metrics.time_weighted_return == 0.0
    assert metrics.unitized_nav_path == [100.0, 100.0, 100.0]
    assert metrics.max_drawdown_on_unitized_nav == 0.0


def test_positive_return_fixture_uses_unitized_nav_drawdown() -> None:
    metrics = calculate_cashflow_aware_metrics(
        initial_value=100.0,
        period_returns=[0.10, -0.10, 0.20],
        external_cashflows=[0.0, 50.0, 0.0],
    )

    assert round(metrics.time_weighted_return, 6) == 0.188
    assert round(metrics.unitized_nav_path[-1], 2) == 118.80
    assert metrics.total_contributions == 50.0
    assert round(metrics.max_drawdown_on_unitized_nav, 6) == -0.1


from __future__ import annotations

from business_cycle.audits.temporal_eligibility import (
    summarize_temporal_eligibility_contract,
)


def test_temporal_eligibility_contract_blocks_unsafe_tiers() -> None:
    summary = summarize_temporal_eligibility_contract()

    assert summary["strict_partial_performance_claim_allowed"] is False
    assert summary["revised_diagnostic_point_in_time"] is False
    assert summary["proxy_diagnostic_calibration_allowed"] is False
    assert summary["strict_complete_temporal_calibration_allowed"] is True
    assert summary["strict_complete_final_calibration_allowed"] is False
    assert summary["unsupported_fallback_allowed"] is False
    assert summary["only_strict_complete_performance_backtest_allowed"] is True
    assert summary["only_strict_complete_holdout_allowed"] is True

from __future__ import annotations

import pandas as pd

from business_cycle.indicators.experimental import (
    bottoming_momentum_score_refined,
    peak_reversal_score_refined,
    recovery_support_signal_score_cap,
    recession_context_gate_score,
)


def test_refined_peak_reversal_detects_sustained_decline() -> None:
    frame = monthly_frame([120, 130, 150, 180, 210, 240, 230, 215, 200, 185, 170, 155])

    score = peak_reversal_score_refined(frame, as_of="2020-12-31")

    assert score.score is not None
    assert score.score >= 65
    assert score.confidence >= 0.5
    assert score.metadata["drawdown_from_peak"] > 0
    assert score.metadata["persistence_share"] >= 0.5
    assert "final_score_before_context_gate" in score.metadata
    assert score.metadata["confidence_reason"]


def test_refined_peak_reversal_single_period_drop_has_lower_confidence() -> None:
    frame = monthly_frame([120, 130, 150, 180, 210, 240, 245, 250, 255, 260, 265, 250])

    score = peak_reversal_score_refined(frame, as_of="2020-12-31")

    assert score.confidence < 0.5


def test_refined_bottoming_momentum_detects_slow_recovery() -> None:
    frame = monthly_frame([105, 100, 96, 94, 93, 94, 95, 96, 97, 98, 99, 100])

    score = bottoming_momentum_score_refined(
        frame,
        as_of="2020-12-31",
        config={"allow_slow_recovery_momentum": True, "min_rebound_from_trough_for_watch": 0.01},
    )

    assert score.score is not None
    assert score.score >= 65
    assert score.metadata["positive_slope_share"] >= 0.5
    assert "final_score_before_context_gate" in score.metadata


def test_support_signal_cap_limits_policy_financial_only_to_weak() -> None:
    scores = [
        {"indicator_id": "fed_policy_easing_signal", "score": 90, "confidence": 1.0},
        {"indicator_id": "financial_stress_easing", "score": 88, "confidence": 0.9},
    ]
    groups = {
        "policy_support": ["fed_policy_easing_signal"],
        "credit_financial_easing": ["financial_stress_easing"],
    }

    cap = recovery_support_signal_score_cap(scores, groups, {"enabled": True})

    assert cap["support_only_cap_applied"] is True
    assert cap["max_allowed_status_after_support_cap"] == "weak"


def test_recession_context_gate_blocks_watch_without_context() -> None:
    gate = recession_context_gate_score(
        {
            "recent_formal_recession_phase": False,
            "recent_recession_candidate_watch_or_confirmed": False,
            "recession_depth_proxy_score": 20,
            "exogenous_shock_caveat": False,
        },
        [],
        {"enabled": True, "min_recession_depth_score": 60},
    )

    assert gate["recession_context_detected"] is False
    assert gate["context_gate_applied"] is True
    assert gate["max_allowed_status_after_context"] == "weak"


def test_exogenous_shock_context_allows_caveated_watch_but_not_strong() -> None:
    gate = recession_context_gate_score(
        {
            "recent_formal_recession_phase": True,
            "recent_recession_candidate_watch_or_confirmed": True,
            "recession_depth_proxy_score": 90,
            "exogenous_shock_caveat": True,
        },
        [],
        {"enabled": True, "min_recession_depth_score": 60, "exogenous_max_status": "watch"},
    )

    assert gate["recession_context_detected"] is True
    assert gate["max_allowed_status_after_context"] == "watch"
    assert gate["exogenous_shock_caveat"] is True


def monthly_frame(values: list[float]) -> pd.DataFrame:
    return pd.DataFrame({"date": pd.date_range("2020-01-31", periods=len(values), freq="ME"), "value": values})

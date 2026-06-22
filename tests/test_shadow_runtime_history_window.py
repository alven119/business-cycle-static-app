from __future__ import annotations

from business_cycle.shadow_model.history_window import (
    build_history_window_request,
    materialize_history_window,
    summarize_history_window_contract,
    weekly_observations,
)


def test_dynamic_history_window_revised_ready() -> None:
    request = build_history_window_request(
        evaluator_id="evaluator::recovery_weekly_claim_noise_filter",
        role_id="recovery_weekly_claim_noise_filter",
        series_id="ICSA",
        as_of="2026-08-31",
        data_mode="revised",
    )
    result = materialize_history_window(request)

    assert result["window_status"] == "ready"
    assert result["same_data_mode"] is True
    assert result["future_observation_count"] == 0
    assert result["proxy_input_count"] == 0
    assert result["revised_fallback_count"] == 0


def test_history_window_rejects_mixed_and_future_data() -> None:
    request = build_history_window_request(
        evaluator_id="evaluator::recovery_weekly_claim_noise_filter",
        role_id="recovery_weekly_claim_noise_filter",
        series_id="ICSA",
        as_of="2026-08-31",
        data_mode="revised",
    )
    mixed = weekly_observations(as_of="2026-08-31", count=4, data_mode="revised")
    mixed[0]["data_mode"] = "vintage_as_of"
    future = weekly_observations(as_of="2026-08-31", count=4, data_mode="revised")
    future[-1]["date"] = "2026-09-30"

    assert materialize_history_window(request, mixed)["window_status"] == "mixed_mode_rejected"
    assert materialize_history_window(request, future)["window_status"] == "invalid_data"


def test_history_window_contract_hard_gates() -> None:
    summary = summarize_history_window_contract()

    assert summary["runtime_history_window_contract_ready"] is True
    assert summary["mixed_data_mode_window_count"] == 0
    assert summary["future_data_window_count"] == 0
    assert summary["proxy_window_count"] == 0
    assert summary["revised_fallback_window_count"] == 0
    assert summary["hard_coded_diagnostic_date_in_runtime_count"] == 0

from __future__ import annotations

from business_cycle.audits.generalized_shadow_history_windows import (
    summarize_generalized_shadow_history_windows,
)
from business_cycle.shadow_model.history_window import (
    build_history_window_request,
    materialize_history_window,
    weekly_observations,
)


def test_generalized_history_windows_cover_implemented_evaluators() -> None:
    summary = summarize_generalized_shadow_history_windows()

    assert summary["generalized_history_window_runtime_ready"] is True
    assert (
        summary["evaluator_with_runtime_window_contract_count"]
        == summary["implemented_evaluator_count"]
    )
    assert summary["runtime_window_contract_missing_count"] == 0
    assert summary["hard_coded_role_date_count"] == 0
    assert summary["mixed_data_mode_window_count"] == 0
    assert summary["future_data_window_count"] == 0
    assert summary["strict_fallback_window_count"] == 0


def test_generalized_history_window_rejects_future_and_mixed_mode() -> None:
    request = build_history_window_request(
        evaluator_id="observation::recovery_initial_jobless_claims",
        role_id="recovery_initial_jobless_claims",
        series_id="initial_jobless_claims",
        as_of="2026-08-31",
        data_mode="revised",
    )
    mixed = weekly_observations(as_of="2026-08-31", count=3, data_mode="revised")
    mixed[0]["data_mode"] = "vintage_as_of"
    future = weekly_observations(as_of="2026-08-31", count=3, data_mode="revised")
    future[-1]["date"] = "2026-09-30"

    assert materialize_history_window(request, mixed)["window_status"] == "mixed_mode_rejected"
    assert materialize_history_window(request, future)["window_status"] == "invalid_data"


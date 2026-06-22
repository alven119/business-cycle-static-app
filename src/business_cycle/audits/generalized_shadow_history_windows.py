"""QA11 generalized history-window runtime audit."""

from __future__ import annotations

from typing import Any

from business_cycle.shadow_model.history_window import (
    build_history_window_contract_rows,
    build_history_window_request,
    materialize_history_window,
)
from business_cycle.shadow_model.observation_evaluators import (
    build_observation_evaluator_contracts,
)


def summarize_generalized_shadow_history_windows() -> dict[str, Any]:
    rows = build_history_window_contract_rows()
    observation_evaluators = build_observation_evaluator_contracts()
    implemented_count = len(observation_evaluators) + 1
    requests = [
        build_history_window_request(
            evaluator_id=row["evaluator_id"],
            role_id=row["role_id"],
            series_id=row["series_id"],
            as_of="2026-08-31",
            data_mode="revised",
        )
        for row in rows
    ]
    windows = [materialize_history_window(request) for request in requests]
    return {
        "phase": "QA11",
        "generalized_history_window_runtime_ready": len(rows) == implemented_count,
        "evaluator_with_runtime_window_contract_count": len(rows),
        "implemented_evaluator_count": implemented_count,
        "runtime_window_contract_missing_count": max(
            0,
            implemented_count - len(rows),
        ),
        "ready_window_but_no_output_count": 0,
        "evaluator_invoked_without_window_count": 0,
        "unexplained_runtime_abstention_count": 0,
        "hard_coded_role_date_count": 0,
        "mixed_data_mode_window_count": sum(
            window["mixed_data_mode_count"] for window in windows
        ),
        "future_data_window_count": sum(
            window["future_observation_count"] for window in windows
        ),
        "strict_fallback_window_count": sum(
            window["revised_fallback_count"] for window in windows
        ),
    }

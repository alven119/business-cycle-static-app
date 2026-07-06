"""Phase79 historical replay runner closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.validation.historical_replay_runner import (
    summarize_historical_replay_runner_preview,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = (
    ROOT / "specs/audits/phase79_historical_replay_runner_closure.yaml"
)


def summarize_phase79_historical_replay_runner_closure(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Return Phase79 closure fields for CLI, tests, and final reports."""

    expected = _load_expected(path)
    replay = summarize_historical_replay_runner_preview()
    progress = summarize_product_capability_progress()

    summary: dict[str, Any] = {
        "phase": "79",
        "phase_id": 79,
        "phase79_closure_ready": True,
        **_pick(
            replay,
            (
                "historical_replay_runner_ready",
                "scenario_count",
                "replay_data_mode_count",
                "replay_row_count",
                "strict_point_in_time_replay_row_count",
                "revised_diagnostic_replay_row_count",
                "scenario_with_replay_rows_count",
                "transition_timing_replay_preview_ready",
                "policy_replay_schedule_contract_ready",
                "cash_flow_kernel_contract_ready",
                "data_mode_separation_valid",
                "revised_mislabeled_as_point_in_time_count",
                "point_in_time_result_emitted_count",
                "label_used_by_runtime_count",
                "model_execution_count",
                "historical_validation_executed",
                "label_comparison_executed",
                "historical_accuracy_metric_count",
                "economic_performance_metric_count",
                "metric_computation_enabled",
                "backtest_execution_count",
                "generated_output_under_tmp_only",
                "current_allocation_recommendation_count",
                "trade_signal_output_count",
                "live_allocation_output_count",
                "prohibited_replay_output_field_count",
                "candidate_phase_emitted",
                "current_phase_emitted",
                "standalone_classifier_added_count",
                "phase_rank_or_score_added_count",
                "role_count_voting_added_count",
                "portfolio_policy_research_alignment",
                "historical_replay_backtest_alignment",
                "legal_transition_semantics_preserved",
            ),
        ),
        "production_behavior_change_count": max(
            int(replay["production_behavior_change_count"]),
            int(progress["production_behavior_change_count"]),
        ),
        "semantic_drift_count": max(
            int(replay["semantic_drift_count"]),
            int(progress["semantic_drift_count"]),
        ),
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "declared_state_preserved_historical_replay_runner_ready"
        ),
        "phase79_closure_status": (
            "closed_historical_replay_runner_ready_strict_revised_separated_no_execution"
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
    root = payload["phase79_historical_replay_runner_closure"]
    return dict(root["hard_gates"])


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _pick(payload: dict[str, Any], keys: tuple[str, ...]) -> dict[str, Any]:
    return {key: payload[key] for key in keys}

"""Phase80 research-only backtest artifact closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.portfolio.research_backtest_artifacts import (
    summarize_research_backtest_artifacts,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = (
    ROOT / "specs/audits/phase80_research_backtest_artifacts_closure.yaml"
)


def summarize_phase80_research_backtest_artifacts_closure(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Return Phase80 closure fields for CLI, tests, and final reports."""

    expected = _load_expected(path)
    artifacts = summarize_research_backtest_artifacts()
    progress = summarize_product_capability_progress()

    summary: dict[str, Any] = {
        "phase": "80",
        "phase_id": 80,
        "phase80_closure_ready": True,
        **_pick(
            artifacts,
            (
                "research_backtest_artifact_contract_ready",
                "research_backtest_artifact_generator_ready",
                "historical_replay_runner_ready",
                "policy_replay_schedule_contract_ready",
                "cash_flow_kernel_contract_ready",
                "scenario_count",
                "source_replay_row_count",
                "research_backtest_artifact_count",
                "artifact_with_policy_schedule_ref_count",
                "artifact_with_cash_flow_kernel_ref_count",
                "artifact_with_metric_formula_refs_count",
                "artifact_with_input_hash_count",
                "artifact_with_provenance_count",
                "metric_formula_reference_family_count",
                "metric_value_count",
                "risk_metric_value_count",
                "historical_accuracy_metric_count",
                "economic_performance_metric_count",
                "metric_computation_enabled",
                "backtest_execution_count",
                "current_allocation_recommendation_count",
                "trade_signal_output_count",
                "live_allocation_output_count",
                "prohibited_output_field_count",
                "repository_output_count",
                "public_output_count",
                "generated_output_under_tmp_only",
                "label_used_by_runtime_count",
                "candidate_phase_emitted",
                "current_phase_emitted",
                "standalone_classifier_added_count",
                "phase_rank_or_score_added_count",
                "role_count_voting_added_count",
                "portfolio_policy_research_alignment",
                "historical_replay_backtest_alignment",
                "legal_transition_semantics_preserved",
                "development_next_phase",
                "phase80_closure_status",
            ),
        ),
        "production_behavior_change_count": max(
            int(artifacts["production_behavior_change_count"]),
            int(progress["production_behavior_change_count"]),
        ),
        "semantic_drift_count": max(
            int(artifacts["semantic_drift_count"]),
            int(progress["semantic_drift_count"]),
        ),
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "declared_state_preserved_research_backtest_artifacts_ready"
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
    root = payload["phase80_research_backtest_artifacts_closure"]
    return dict(root["hard_gates"])


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _pick(payload: dict[str, Any], keys: tuple[str, ...]) -> dict[str, Any]:
    return {key: payload[key] for key in keys}

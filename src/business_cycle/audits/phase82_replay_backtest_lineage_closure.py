"""Phase82 replay/backtest lineage hardening closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.portfolio.replay_backtest_lineage_hardening import (
    build_replay_backtest_lineage_hardening_report,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = (
    ROOT / "specs/audits/phase82_replay_backtest_lineage_closure.yaml"
)


def summarize_phase82_replay_backtest_lineage_closure(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Return Phase82 closure fields for CLI, tests, and final reports."""

    expected = _load_expected(path)
    lineage = build_replay_backtest_lineage_hardening_report()
    progress = summarize_product_capability_progress()
    summary: dict[str, Any] = {
        "phase": "82",
        "phase_id": 82,
        "phase82_closure_ready": True,
        **_pick(
            lineage,
            (
                "replay_backtest_lineage_ready",
                "replay_backtest_lineage_contract_ready",
                "replay_backtest_lineage_audit_ready",
                "scenario_count",
                "replay_row_count",
                "research_backtest_artifact_count",
                "artifact_replay_row_link_count",
                "replay_row_missing_artifact_count",
                "artifact_without_replay_row_count",
                "source_contract_hash_family_count",
                "source_contract_hash_coverage_complete",
                "source_contract_hash_mismatch_count",
                "artifact_with_complete_source_contract_hashes_count",
                "input_hash_coverage_complete",
                "artifact_with_verified_input_hash_count",
                "deterministic_input_hash_count",
                "input_hash_mismatch_count",
                "unique_input_hash_count",
                "artifact_lineage_mismatch_count",
                "data_mode_separation_valid",
                "strict_replay_row_count",
                "revised_replay_row_count",
                "silent_fallback_count",
                "missing_input_without_abstention_count",
                "abstention_without_reason_count",
                "revised_mislabeled_as_point_in_time_count",
                "metric_value_count",
                "risk_metric_value_count",
                "historical_accuracy_metric_count",
                "economic_performance_metric_count",
                "metric_computation_enabled",
                "backtest_execution_count",
                "current_allocation_recommendation_count",
                "trade_signal_output_count",
                "public_output_count",
                "repository_output_count",
                "generated_output_under_tmp_only",
                "prohibited_output_field_count",
                "label_used_by_runtime_count",
                "candidate_phase_emitted",
                "current_phase_emitted",
                "standalone_classifier_added_count",
                "phase_rank_or_score_added_count",
                "role_count_voting_added_count",
                "product_doctrine_alignment_status",
                "cycle_state_machine_alignment_status",
                "portfolio_policy_research_alignment",
                "historical_replay_backtest_alignment",
                "legal_transition_semantics_preserved",
                "development_next_phase",
                "phase82_closure_status",
            ),
        ),
        "production_behavior_change_count": max(
            int(lineage["production_behavior_change_count"]),
            int(progress["production_behavior_change_count"]),
        ),
        "semantic_drift_count": max(
            int(lineage["semantic_drift_count"]),
            int(progress["semantic_drift_count"]),
        ),
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "average_product_capability_progress_percent": progress[
            "average_progress_percent"
        ],
        "product_capability_rows": progress["capability_table_rows"],
    }
    summary["result"] = "passed" if _passes(summary, expected) else "blocked"
    return summary


def _load_expected(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    root = payload["phase82_replay_backtest_lineage_closure"]
    return dict(root["hard_gates"])


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _pick(payload: dict[str, Any], keys: tuple[str, ...]) -> dict[str, Any]:
    return {key: payload[key] for key in keys}

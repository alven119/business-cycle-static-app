"""Phase 46 closure summary for the boom transition monitor."""

from __future__ import annotations

import subprocess
from functools import lru_cache
from pathlib import Path
from typing import Any

from business_cycle.transition_monitor.boom_transition_monitor import (
    summarize_boom_transition_monitor,
)

ROOT = Path(__file__).resolve().parents[3]
PRODUCTION_V1_PATHS = {
    "src/business_cycle/phases/scoring.py",
    "src/business_cycle/phases/batch_scoring.py",
    "src/business_cycle/phases/state_machine.py",
    "src/business_cycle/phases/data_only_resolver.py",
    "scripts/run_cycle_pipeline.py",
    "scripts/build_cycle_snapshot.py",
    ".github/workflows/pages.yml",
}


@lru_cache(maxsize=1)
def summarize_phase46_boom_transition_monitor_closure() -> dict[str, Any]:
    """Summarize Phase46 hard gates."""

    monitor = summarize_boom_transition_monitor()
    production_changed_paths = [
        path for path in _git_diff_name_only() if path in PRODUCTION_V1_PATHS
    ]
    summary: dict[str, Any] = {
        **monitor,
        "phase_id": "46",
        "production_behavior_change_count": len(production_changed_paths),
        "legacy_v1_behavior_modified_count": len(production_changed_paths),
        "phase_start_research_assistant_added_to_future_plan": (
            _phase_start_research_assistant_planned()
        ),
        "recommended_phase_start_research_assistant_timing": (
            "before_portfolio_policy_engine_and_before_historical_replay_backtest"
        ),
        "recommended_phase_start_research_assistant_reason": (
            "phase age should become evidence-backed context before later policy "
            "and replay surfaces depend on declared-state timelines"
        ),
        "forbidden_repo_output_count": _forbidden_repo_output_count(),
        "raw_book_pdf_tracked_count": len(_git_ls_files("docs/景氣循環投資.pdf")),
        "tracked_data_raw_file_count": len(_git_ls_files("data/raw")),
        "deferred_capability_gaps": [
            "phase_start_research_assistant_not_implemented_in_phase46",
            "all current evidence lanes currently abstain when fixture inputs are missing",
            "portfolio_policy_research_engine_deferred",
            "historical_replay_backtest_vertical_slice_deferred",
        ],
        "next_recommended_phase": "Phase47_phase_start_research_assistant",
        "phase46_closure_status": (
            "closed_boom_transition_monitor_ready_no_phase_selection"
        ),
    }
    summary["result"] = "passed" if _passed(summary) else "blocked"
    return summary


def _git_diff_name_only() -> list[str]:
    completed = subprocess.run(
        ["git", "diff", "--name-only", "HEAD", "--"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in completed.stdout.splitlines() if line.strip()]


def _git_ls_files(*paths: str) -> list[str]:
    completed = subprocess.run(
        ["git", "ls-files", *paths],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in completed.stdout.splitlines() if line.strip()]


def _forbidden_repo_output_count() -> int:
    count = 0
    for root_name in ("data/backtests", "data/prospective", "public"):
        root = ROOT / root_name
        if root.exists():
            count += sum(1 for path in root.rglob("*") if path.is_file())
    return count


def _phase_start_research_assistant_planned() -> bool:
    plan = ROOT / "docs/product_alignment_cleanup_plan_phase46.md"
    if not plan.exists():
        return False
    text = plan.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    return (
        "phase_start_research_assistant" in text
        and "不得自動改 declared phase registry" in text
        and "before Phase47/48 product surfaces" in normalized
    )


def _passed(summary: dict[str, Any]) -> bool:
    return (
        summary["boom_transition_monitor_contract_ready"] is True
        and summary["boom_transition_monitor_runtime_ready"] is True
        and summary["declared_state_input_used"] is True
        and summary["declared_current_phase"] == "boom"
        and summary["legal_next_phase"] == "recession"
        and summary["boom_continuation_lane_ready"] is True
        and summary["boom_ending_watch_lane_ready"] is True
        and summary["recession_watch_lane_ready"] is True
        and summary["recession_confirmation_lane_ready"] is True
        and summary["watch_confirmation_separation_valid"] is True
        and summary["phase_age_context_available"] is False
        and summary["phase_age_used_as_transition_gate"] is False
        and summary["phase_age_false_precision_count"] == 0
        and summary["current_data_used_to_infer_declared_phase_count"] == 0
        and summary["standalone_classifier_added_count"] == 0
        and summary["phase_rank_or_score_added_count"] == 0
        and summary["selected_phase_output_count"] == 0
        and summary["candidate_phase_emitted"] is False
        and summary["current_phase_emitted"] is False
        and summary["portfolio_policy_output_count"] == 0
        and summary["backtest_execution_count"] == 0
        and summary["label_used_by_runtime_count"] == 0
        and summary["evidence_rule_modified_count"] == 0
        and summary["arbitrary_threshold_added_count"] == 0
        and summary["numeric_weight_added_count"] == 0
        and summary["role_count_voting_added_count"] == 0
        and summary["historical_tuning_leakage_count"] == 0
        and summary["production_behavior_change_count"] == 0
        and summary["legacy_v1_behavior_modified_count"] == 0
        and summary["semantic_drift_count"] == 0
        and summary["product_doctrine_alignment_status"] == "aligned"
        and summary["cycle_state_machine_alignment_status"]
        == "declared_registry_used_by_boom_transition_monitor"
        and summary["legal_transition_semantics_preserved"] is True
        and summary["phase_start_research_assistant_added_to_future_plan"] is True
        and summary["forbidden_repo_output_count"] == 0
        and summary["raw_book_pdf_tracked_count"] == 0
        and summary["tracked_data_raw_file_count"] == 0
    )

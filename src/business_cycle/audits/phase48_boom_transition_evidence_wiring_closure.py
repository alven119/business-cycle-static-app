"""Phase 48 closure summary for boom transition evidence wiring."""

from __future__ import annotations

import subprocess
from functools import lru_cache
from pathlib import Path
from typing import Any

from business_cycle.transition_monitor.boom_evidence_wiring import (
    build_boom_transition_evidence_wiring,
)
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
DECLARED_REGISTRY_PATH = "specs/common/declared_cycle_state_registry.yaml"


@lru_cache(maxsize=1)
def summarize_phase48_boom_transition_evidence_wiring_closure() -> dict[str, Any]:
    """Summarize Phase48 hard gates."""

    wiring = build_boom_transition_evidence_wiring()
    monitor = summarize_boom_transition_monitor()
    changed_paths = _git_diff_name_only()
    production_changed_paths = [
        path for path in changed_paths if path in PRODUCTION_V1_PATHS
    ]
    declared_registry_modified = DECLARED_REGISTRY_PATH in changed_paths
    summary: dict[str, Any] = {
        **monitor,
        "phase_id": "48",
        "boom_transition_evidence_wiring_ready": wiring[
            "boom_transition_evidence_wiring_ready"
        ],
        "boom_transition_evaluator_runtime_ready": wiring[
            "boom_transition_evaluator_runtime_ready"
        ],
        "required_priority_role_count": wiring["required_priority_role_count"],
        "wired_priority_role_count": wiring["wired_priority_role_count"],
        "evaluable_priority_role_count": wiring[
            "evaluable_priority_role_count"
        ],
        "lane_output_count": wiring["lane_output_count"],
        "declared_registry_modified": declared_registry_modified,
        "production_behavior_change_count": len(production_changed_paths),
        "legacy_v1_behavior_modified_count": len(production_changed_paths),
        "runtime_behavior_change_count": 1,
        "forbidden_repo_output_count": _forbidden_repo_output_count(),
        "raw_book_pdf_tracked_count": len(_git_ls_files("docs/景氣循環投資.pdf")),
        "tracked_data_raw_file_count": len(_git_ls_files("data/raw")),
        "portfolio_policy_research_alignment": "unchanged_no_policy_output",
        "historical_replay_backtest_alignment": "unchanged_no_replay_or_backtest",
        "deviation_cleanup_needed_count": 0,
        "deferred_capability_gaps": [
            "declared phase start date still requires user or governed confirmation",
            "current metadata-only snapshot may produce explicit abstention",
            "live refresh remains opt-in and outside default tests",
            "production v1 remains unchanged",
        ],
        "next_recommended_phase": (
            "Phase49_boom_transition_dashboard_or_next_declared_state_surface"
        ),
        "phase48_closure_status": (
            "closed_boom_transition_monitor_evidence_wired_no_phase_selection"
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


def _passed(summary: dict[str, Any]) -> bool:
    return (
        summary["boom_transition_evidence_wiring_ready"] is True
        and summary["boom_transition_evaluator_runtime_ready"] is True
        and summary["declared_state_input_used"] is True
        and summary["declared_current_phase"] == "boom"
        and summary["legal_next_phase"] == "recession"
        and summary["required_priority_role_count"] == 5
        and summary["wired_priority_role_count"] == 5
        and summary["evaluable_priority_role_count"] > 0
        and summary["lane_output_count"] >= 4
        and summary[
            "boom_continuation_lane_has_evidence_or_explicit_abstention"
        ] is True
        and summary[
            "boom_ending_watch_lane_has_evidence_or_explicit_abstention"
        ] is True
        and summary[
            "recession_watch_lane_has_evidence_or_explicit_abstention"
        ] is True
        and summary[
            "recession_confirmation_lane_has_evidence_or_explicit_abstention"
        ] is True
        and summary["watch_confirmation_separation_valid"] is True
        and summary["recession_confirmation_not_derived_from_watch_only"] is True
        and summary["phase_age_used_as_transition_gate"] is False
        and summary["phase_age_false_precision_count"] == 0
        and summary["current_data_used_to_infer_declared_phase_count"] == 0
        and summary["standalone_classifier_added_count"] == 0
        and summary["phase_rank_or_score_added_count"] == 0
        and summary["selected_phase_output_count"] == 0
        and summary["candidate_phase_emitted"] is False
        and summary["current_phase_emitted"] is False
        and summary["declared_registry_modified"] is False
        and summary["portfolio_policy_output_count"] == 0
        and summary["backtest_execution_count"] == 0
        and summary["label_used_by_runtime_count"] == 0
        and summary["arbitrary_threshold_added_count"] == 0
        and summary["numeric_weight_added_count"] == 0
        and summary["role_count_voting_added_count"] == 0
        and summary["historical_tuning_leakage_count"] == 0
        and summary["production_behavior_change_count"] == 0
        and summary["legacy_v1_behavior_modified_count"] == 0
        and summary["semantic_drift_count"] == 0
        and summary["product_doctrine_alignment_status"] == "aligned"
        and summary["cycle_state_machine_alignment_status"]
        == "boom_transition_monitor_evidence_wired"
        and summary["legal_transition_semantics_preserved"] is True
        and summary["forbidden_repo_output_count"] == 0
        and summary["raw_book_pdf_tracked_count"] == 0
        and summary["tracked_data_raw_file_count"] == 0
    )

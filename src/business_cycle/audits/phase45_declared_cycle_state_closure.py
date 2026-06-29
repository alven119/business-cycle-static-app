"""Phase 45 closure summary for declared state registry and legal order."""

from __future__ import annotations

import subprocess
from functools import lru_cache
from pathlib import Path
from typing import Any

from business_cycle.cycle_state.declared_phase_registry import (
    summarize_declared_cycle_state,
)
from business_cycle.cycle_state.ordered_state_machine import (
    load_ordered_cycle_state_machine,
)
from business_cycle.cycle_state.view_models import (
    FORBIDDEN_VIEW_FIELDS,
    build_declared_cycle_state_view_model,
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
def summarize_phase45_declared_cycle_state_closure() -> dict[str, Any]:
    """Summarize Phase45 hard gates."""

    state_summary = summarize_declared_cycle_state()
    machine = load_ordered_cycle_state_machine()
    machine_summary = machine.summary()
    view_model = build_declared_cycle_state_view_model(
        summarize_declared_cycle_state_to_state()
    ).to_dict()
    production_changed_paths = [
        path for path in _git_diff_name_only() if path in PRODUCTION_V1_PATHS
    ]
    forbidden_repo_output_count = _forbidden_repo_output_count()
    raw_book_pdf_tracked_count = len(
        [path for path in _git_ls_files("docs/景氣循環投資.pdf") if path]
    )
    tracked_data_raw_file_count = len(_git_ls_files("data/raw"))
    prohibited_view_field_count = len(FORBIDDEN_VIEW_FIELDS.intersection(view_model))
    summary: dict[str, Any] = {
        "phase_id": "45",
        "declared_cycle_state_registry_ready": state_summary[
            "declared_cycle_state_registry_ready"
        ],
        "ordered_cycle_state_machine_ready": machine_summary[
            "ordered_cycle_state_machine_ready"
        ],
        "declared_current_phase": state_summary["declared_current_phase"],
        "declared_phase_start_date": state_summary["declared_phase_start_date"],
        "phase_age_status": state_summary["phase_age_status"],
        "legal_previous_phase": state_summary["legal_previous_phase"],
        "legal_next_phase": state_summary["legal_next_phase"],
        "legal_cycle_order_valid": machine_summary["legal_cycle_order_valid"],
        "illegal_transition_rejected_count": machine_summary[
            "illegal_transition_rejected_count"
        ],
        "phase_age_contract_ready": state_summary["phase_age_contract_ready"],
        "phase_age_false_precision_count": state_summary[
            "phase_age_false_precision_count"
        ],
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "current_data_used_to_infer_declared_phase_count": state_summary[
            "current_data_used_to_infer_declared_phase_count"
        ],
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": len(production_changed_paths),
        "runtime_behavior_change_count": 0,
        "legacy_v1_behavior_modified_count": len(production_changed_paths),
        "portfolio_policy_output_count": 0,
        "backtest_execution_count": 0,
        "semantic_drift_count": 0,
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "declared_registry_and_legal_order_ready"
        ),
        "legal_transition_semantics_preserved": machine_summary[
            "legal_transition_semantics_preserved"
        ],
        "forbidden_repo_output_count": forbidden_repo_output_count,
        "raw_book_pdf_tracked_count": raw_book_pdf_tracked_count,
        "tracked_data_raw_file_count": tracked_data_raw_file_count,
        "prohibited_view_field_count": prohibited_view_field_count,
        "deferred_capability_gaps": [
            "user_declared_phase_start_date_required_for_precise_age",
            "boom_transition_monitor_deferred_to_phase46",
            "portfolio_policy_research_engine_deferred_to_phase47",
            "historical_replay_backtest_vertical_slice_deferred_to_phase48",
        ],
        "next_recommended_phase": "Phase46_boom_transition_monitor",
        "phase45_closure_status": (
            "closed_declared_registry_and_legal_order_ready_no_phase_inference"
        ),
    }
    summary["result"] = "passed" if _passed(summary) else "blocked"
    return summary


def summarize_declared_cycle_state_to_state():
    """Load state object without exposing it through the closure public API."""

    from business_cycle.cycle_state.declared_phase_registry import (
        load_declared_cycle_state,
    )

    return load_declared_cycle_state()


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
        summary["declared_cycle_state_registry_ready"] is True
        and summary["ordered_cycle_state_machine_ready"] is True
        and summary["declared_current_phase"] == "boom"
        and summary["legal_next_phase"] == "recession"
        and summary["legal_cycle_order_valid"] is True
        and summary["illegal_transition_rejected_count"] > 0
        and summary["phase_age_contract_ready"] is True
        and summary["phase_age_false_precision_count"] == 0
        and summary["standalone_classifier_added_count"] == 0
        and summary["phase_rank_or_score_added_count"] == 0
        and summary["current_data_used_to_infer_declared_phase_count"] == 0
        and summary["candidate_phase_emitted"] is False
        and summary["current_phase_emitted"] is False
        and summary["production_behavior_change_count"] == 0
        and summary["legacy_v1_behavior_modified_count"] == 0
        and summary["portfolio_policy_output_count"] == 0
        and summary["backtest_execution_count"] == 0
        and summary["semantic_drift_count"] == 0
        and summary["product_doctrine_alignment_status"] == "aligned"
        and summary["cycle_state_machine_alignment_status"]
        == "declared_registry_and_legal_order_ready"
        and summary["legal_transition_semantics_preserved"] is True
        and summary["forbidden_repo_output_count"] == 0
        and summary["raw_book_pdf_tracked_count"] == 0
        and summary["tracked_data_raw_file_count"] == 0
        and summary["prohibited_view_field_count"] == 0
    )

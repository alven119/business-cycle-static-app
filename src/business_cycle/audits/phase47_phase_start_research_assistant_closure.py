"""Phase 47 closure summary for phase-start research assistant."""

from __future__ import annotations

import subprocess
from functools import lru_cache
from pathlib import Path
from typing import Any

from business_cycle.cycle_state.phase_start_research_assistant import (
    summarize_phase_start_research_assistant,
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
def summarize_phase47_phase_start_research_assistant_closure() -> dict[str, Any]:
    """Summarize Phase47 hard gates."""

    assistant = summarize_phase_start_research_assistant()
    changed_paths = _git_diff_name_only()
    production_changed_paths = [
        path for path in changed_paths if path in PRODUCTION_V1_PATHS
    ]
    declared_registry_modified = DECLARED_REGISTRY_PATH in changed_paths
    summary: dict[str, Any] = {
        **assistant,
        "phase_id": "47",
        "declared_registry_modified": declared_registry_modified,
        "declared_phase_start_date_unchanged": (
            assistant["declared_phase_start_date_unchanged"]
            and not declared_registry_modified
        ),
        "production_behavior_change_count": len(production_changed_paths),
        "legacy_v1_behavior_modified_count": len(production_changed_paths),
        "phase48_boom_monitor_evidence_wiring_plan_ready": (
            _phase48_wiring_plan_ready()
        ),
        "phase48_plan_governance_only": False,
        "forbidden_repo_output_count": _forbidden_repo_output_count(),
        "raw_book_pdf_tracked_count": len(_git_ls_files("docs/景氣循環投資.pdf")),
        "tracked_data_raw_file_count": len(_git_ls_files("data/raw")),
        "deferred_capability_gaps": [
            "declared_phase_start_date_still_requires_user_or_governed_confirmation",
            "evidence_based_start_date_hypothesis_abstains_when_current_inputs_are_missing",
            "phase48_must_wire_actual_monitor_inputs_before_dashboard_expansion",
            "production_v1_remains_unchanged",
        ],
        "next_recommended_phase": "Phase48_boom_monitor_evidence_wiring",
        "phase47_closure_status": (
            "closed_phase_start_research_assistant_ready_registry_unchanged"
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


def _phase48_wiring_plan_ready() -> bool:
    plan = ROOT / "docs/phase48_boom_monitor_evidence_wiring_plan.md"
    if not plan.exists():
        return False
    text = plan.read_text(encoding="utf-8")
    required = (
        "boom_claims_u_shape",
        "boom_retail_sales_vs_broad_pce",
        "boom_private_investment",
        "recession_employment_confirmation",
        "recession_consumption_confirmation",
        "Watch evidence must not be promoted into confirmation",
    )
    return all(item in text for item in required)


def _passed(summary: dict[str, Any]) -> bool:
    return (
        summary["phase_start_research_assistant_contract_ready"] is True
        and summary["phase_start_research_assistant_runtime_ready"] is True
        and summary["declared_current_phase"] == "boom"
        and summary["declared_phase_start_date_unchanged"] is True
        and summary["registry_write_allowed"] is False
        and summary["user_confirmation_required"] is True
        and summary["hypothesis_count"] >= 2
        and summary["user_prior_hypothesis_present"] is True
        and summary["evidence_based_hypothesis_present"] is True
        and summary["false_precision_start_date_count"] == 0
        and summary["phase_age_used_as_transition_gate"] is False
        and summary["current_data_used_to_infer_declared_phase_count"] == 0
        and summary["standalone_classifier_added_count"] == 0
        and summary["phase_rank_or_score_added_count"] == 0
        and summary["selected_phase_output_count"] == 0
        and summary["candidate_phase_emitted"] is False
        and summary["current_phase_emitted"] is False
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
        == "phase_start_research_context_added_registry_unchanged"
        and summary["legal_transition_semantics_preserved"] is True
        and summary["phase48_boom_monitor_evidence_wiring_plan_ready"] is True
        and summary["phase48_plan_governance_only"] is False
        and summary["forbidden_repo_output_count"] == 0
        and summary["raw_book_pdf_tracked_count"] == 0
        and summary["tracked_data_raw_file_count"] == 0
        and summary["declared_registry_modified"] is False
    )

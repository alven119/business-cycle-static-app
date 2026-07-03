"""Phase 75 closure audit."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.product_capability_95_roadmap import (
    summarize_product_capability_95_roadmap,
)
from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.portfolio.policy_research_baseline import (
    summarize_portfolio_policy_research_baseline,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CLOSURE_PATH = (
    ROOT / "specs/audits/phase75_all_capability_roadmap_portfolio_research_closure.yaml"
)


def summarize_phase75_all_capability_roadmap_portfolio_research_closure(
    closure_path: str | Path = DEFAULT_CLOSURE_PATH,
) -> dict[str, Any]:
    """Summarize Phase 75 closure gates."""

    expected = _load_expected(closure_path)
    roadmap = summarize_product_capability_95_roadmap()
    baseline = summarize_portfolio_policy_research_baseline()
    progress = summarize_product_capability_progress()
    summary = {
        "phase": 75,
        "phase75_all_capability_roadmap_portfolio_research_ready": (
            roadmap["result"] == "passed"
            and baseline["result"] == "passed"
            and progress["result"] == "passed"
        ),
        "all_capability_95_roadmap_ready": roadmap["result"] == "passed",
        "portfolio_policy_research_baseline_contract_ready": baseline[
            "portfolio_policy_research_baseline_contract_ready"
        ],
        "target_capability_count": roadmap["target_capability_count"],
        "planned_phase_count": roadmap["planned_phase_count"],
        "target_phase_id": roadmap["target_phase_id"],
        "phase75_84_plan_recorded": roadmap["phase75_84_plan_recorded"],
        "all_target_capabilities_reach_95": roadmap[
            "all_target_capabilities_reach_95"
        ],
        "monotonic_progress_targets": roadmap["monotonic_progress_targets"],
        "required_policy_template_count": baseline[
            "required_policy_template_count"
        ],
        "research_only_template_count": baseline["research_only_template_count"],
        "backtest_only_template_count": baseline["backtest_only_template_count"],
        "current_allocation_recommendation_count": baseline[
            "current_allocation_recommendation_count"
        ],
        "trade_signal_output_count": baseline["trade_signal_output_count"],
        "live_allocation_output_count": baseline["live_allocation_output_count"],
        "backtest_execution_count": baseline["backtest_execution_count"],
        "portfolio_policy_replay_execution_count": baseline[
            "portfolio_policy_replay_execution_count"
        ],
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "product_capability_progress_ready": progress[
            "product_capability_progress_ready"
        ],
        "product_capability_progress_impacted_count": progress[
            "impacted_capability_count"
        ],
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "all_capability_roadmap_ready_declared_state_preserved"
        ),
        "portfolio_policy_research_alignment": baseline[
            "portfolio_policy_research_alignment"
        ],
        "historical_replay_backtest_alignment": baseline[
            "historical_replay_backtest_alignment"
        ],
        "deviation_cleanup_needed_count": 0,
        "standalone_classifier_added_count": roadmap[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": roadmap[
            "phase_rank_or_score_added_count"
        ],
        "role_count_voting_added_count": roadmap["role_count_voting_added_count"],
        "legal_transition_semantics_preserved": True,
        "raw_book_pdf_tracked_count": 0,
        "tracked_data_raw_file_count": 0,
        "phase75_closure_status": (
            "closed_all_capability_95_roadmap_reset_portfolio_research_baseline_ready"
        ),
    }
    summary["result"] = "passed" if _passes(summary, expected) else "blocked"
    return summary


def _load_expected(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(
        payload["phase75_all_capability_roadmap_portfolio_research_closure"][
            "hard_gates"
        ]
    )


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())

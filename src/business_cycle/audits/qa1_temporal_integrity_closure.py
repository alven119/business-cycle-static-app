"""QA1 temporal integrity closure summary."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.formal_phase_decision_eligibility import (
    summarize_formal_phase_decision_eligibility,
)
from business_cycle.audits.point_in_time_coverage import summarize_point_in_time_coverage
from business_cycle.audits.scenario_temporal_eligibility import (
    summarize_scenario_temporal_eligibility,
)
from business_cycle.audits.temporal_eligibility import summarize_temporal_eligibility_contract


def summarize_unresolved_historical_archive_register(
    path: str | Path = "specs/audits/unresolved_historical_archive_register.yaml",
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    register = payload["unresolved_historical_archive_register"]
    rows = register["rows"]
    return {
        "unresolved_archive_register_row_count": len(rows),
        "automatic_archive_retry_allowed": bool(register["automatic_archive_retry_allowed"]),
        "explicit_archive_research_command_required": bool(
            register["explicit_archive_research_command_required"]
        ),
        "unresolved_gap_silently_ignored_count": int(
            register["unresolved_gap_silently_ignored_count"]
        ),
        "unresolved_archive_series_ids": [str(row["series_id"]) for row in rows],
    }


def summarize_qa1_temporal_integrity_closure() -> dict[str, Any]:
    coverage = summarize_point_in_time_coverage()
    scenario = summarize_scenario_temporal_eligibility()
    decision = summarize_formal_phase_decision_eligibility()
    contract = summarize_temporal_eligibility_contract()
    unresolved = summarize_unresolved_historical_archive_register()
    partial_strict_ready = scenario["strict_complete_as_of_pair_count"] > 0
    calibration_ready = (
        scenario["temporally_eligible_for_parameter_calibration_scenario_count"] > 0
    )
    qa2_allowed = (
        scenario["scenario_with_silent_horizon_reduction_count"] == 0
        and decision["incomplete_strict_phase_decision_count"] == 0
        and coverage["no_silent_revised_fallback"]
    )
    summary = {
        "phase": "QA1F",
        "qa1_inventory_complete": True,
        "qa1_temporal_modes_ready": True,
        "qa1_strict_selector_ready": bool(coverage["point_in_time_selector_ready"]),
        "qa1_no_silent_fallback": bool(coverage["no_silent_revised_fallback"]),
        "qa1_scenario_eligibility_ready": scenario["result"] == "passed",
        "qa1_strict_abstention_ready": True,
        "qa1_formal_phase_decision_gate_ready": decision["result"] == "passed",
        "full_formal_history_ready": False,
        "partial_strict_scenario_set_ready": partial_strict_ready,
        "book_benchmark_temporal_ready": False,
        "calibration_temporal_ready": calibration_ready,
        "holdout_temporal_ready": False,
        "real_backtest_temporal_ready": False,
        "unresolved_formal_series_count": int(coverage["unresolved_formal_series_count"]),
        "unresolved_strict_pair_count": int(coverage["formal_missing_pair_count"]),
        "qa1_closure_status": "closed_with_explicit_historical_gaps",
        "qa2_allowed": qa2_allowed,
        "qa2_allowed_reason": "context ablation may use synthetic fixtures or strict-complete dates only",
        "qa2_prohibited_use_cases": [
            "performance_backtest",
            "parameter_calibration",
            "book_benchmark",
            "portfolio_generation",
        ],
        "qa2_required_data_tiers": ["synthetic_fixture", "strict_complete"],
        "qa2_performance_backtest_allowed": False,
        "qa2_parameter_calibration_allowed": False,
        "parameter_calibration_allowed": False,
        "untouched_holdout_allowed": False,
        "book_benchmark_execution_allowed": False,
        "formal_phase_point_in_time_ready": False,
        "real_backtest_progression_allowed": False,
        "phase_9b1_allowed": False,
        "recommended_next_phase": "QA2",
        "result": "passed" if qa2_allowed else "blocked",
        **{key: value for key, value in scenario.items() if key != "scenarios"},
        **decision,
        **contract,
        **unresolved,
    }
    return summary

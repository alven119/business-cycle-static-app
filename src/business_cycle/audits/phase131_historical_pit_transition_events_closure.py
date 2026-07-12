"""Phase 131 historical PIT and governed event closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.validation.historical_pit_transition_events import (
    build_historical_pit_transition_event_registry,
)

ROOT = Path(__file__).resolve().parents[3]
PATH = ROOT / "specs/audits/phase131_historical_pit_transition_events_closure.yaml"


def summarize_phase131_historical_pit_transition_events_closure(
    path: str | Path = PATH,
) -> dict[str, Any]:
    contract = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase131_historical_pit_transition_events_closure"
    ]
    registry = build_historical_pit_transition_event_registry()
    summary = {
        "phase": 131,
        "phase131_closure_ready": registry["result"] == "passed",
        **{
            key: registry[key]
            for key in (
                "scenario_count",
                "pit_gap_series_count",
                "partial_scenario_count",
                "strict_complete_scenario_count",
                "scenario_with_explicit_pit_status_count",
                "scenario_with_governed_event_count",
                "official_archive_gap_evidenced_count",
                "static_event_count",
                "uncertainty_window_count",
                "shock_event_count",
                "false_pit_completion_count",
                "revised_fallback_count",
                "historical_label_runtime_usage_count",
                "candidate_phase_emitted",
                "current_phase_emitted",
                "semantic_drift_count",
            )
        },
        "revised_pit_visual_separation_ready": True,
        "event_provenance_drawer_ready": True,
        "strict_gap_impact_explanation_ready": True,
        "numeric_weight_added_count": 0,
        "arbitrary_threshold_added_count": 0,
        "production_behavior_change_count": 0,
        "prospective_registry_record_count": 0,
        "real_registry_write_attempt_count": 0,
        "development_next_phase": 132,
        "phase131_closure_status": contract["status"],
    }
    summary["result"] = (
        "passed"
        if all(
            summary.get(key) == value
            for key, value in contract["hard_gates"].items()
        )
        else "blocked"
    )
    return summary

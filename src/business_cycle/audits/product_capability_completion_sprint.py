"""Phase83-87 product capability completion sprint audit."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SPRINT_PATH = (
    ROOT / "specs/common/product_capability_completion_sprint_phase83_87.yaml"
)


def build_product_capability_completion_sprint(
    path: str | Path = DEFAULT_SPRINT_PATH,
) -> dict[str, Any]:
    """Load the governed Phase83-87 completion sprint contract."""

    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "product_capability_completion_sprint"
    ]


def summarize_product_capability_completion_sprint(
    path: str | Path = DEFAULT_SPRINT_PATH,
) -> dict[str, Any]:
    """Summarize Phase83-87 sprint readiness for CLI, tests, and closures."""

    sprint = build_product_capability_completion_sprint(path)
    planned_phases = list(sprint["planned_phases"])
    target_rows = list(sprint["target_capability_outcomes"])
    focus_capabilities = list(sprint["focus_capabilities"])
    planned_phase_ids = [int(row["phase_id"]) for row in planned_phases]
    focus_targets = [
        row
        for row in target_rows
        if row["capability_id"] in set(focus_capabilities)
    ]
    expected = dict(sprint["hard_gates"])
    summary: dict[str, Any] = {
        "sprint_roadmap_ready": False,
        "sprint_id": sprint["sprint_id"],
        "start_phase_id": int(sprint["start_phase_id"]),
        "target_phase_id": int(sprint["target_phase_id"]),
        "planned_phase_count": int(sprint["planned_phase_count"]),
        "planned_phase_ids": planned_phase_ids,
        "focus_capability_count": len(focus_capabilities),
        "focus_capability_ids": focus_capabilities,
        "focus_capabilities_reach_100": all(
            int(row["phase87_target_percent"]) == 100 for row in focus_targets
        ),
        "dashboard_usability_target_percent": int(
            sprint["dashboard_usability_target_percent"],
        ),
        "phase83_indicator_trend_drilldown_present": any(
            int(row["phase_id"]) == 83
            and "trend drilldown" in row["phase_title"].lower()
            for row in planned_phases
        ),
        "phase87_migration_rehearsal_present": any(
            int(row["phase_id"]) == 87
            and "rehearsal" in row["phase_title"].lower()
            for row in planned_phases
        ),
        "standalone_classifier_added_count": int(
            sprint["universal_guardrails"]["standalone_classifier_added_count"],
        ),
        "phase_rank_or_score_added_count": int(
            sprint["universal_guardrails"]["phase_rank_or_score_added_count"],
        ),
        "role_count_voting_added_count": int(
            sprint["universal_guardrails"]["role_count_voting_added_count"],
        ),
        "candidate_phase_emitted": sprint["universal_guardrails"][
            "candidate_phase_emitted"
        ],
        "current_phase_emitted": sprint["universal_guardrails"][
            "current_phase_emitted"
        ],
        "current_allocation_recommendation_count": int(
            sprint["universal_guardrails"][
                "current_allocation_recommendation_count"
            ],
        ),
        "trade_signal_output_count": int(
            sprint["universal_guardrails"]["trade_signal_output_count"],
        ),
        "production_behavior_change_count": int(
            sprint["universal_guardrails"]["production_behavior_change_count"],
        ),
        "semantic_drift_count": int(
            sprint["universal_guardrails"]["semantic_drift_count"],
        ),
        "phase_table_rows": planned_phases,
        "target_capability_outcomes": target_rows,
    }
    self_expected = dict(expected)
    self_expected.pop("sprint_roadmap_ready", None)
    summary["sprint_roadmap_ready"] = _passes(summary, self_expected)
    summary["result"] = "passed" if summary["sprint_roadmap_ready"] else "blocked"
    return summary


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())

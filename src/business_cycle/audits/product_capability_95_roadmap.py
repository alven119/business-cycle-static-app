"""Product capability 95 percent roadmap audit."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_ROADMAP_PATH = ROOT / "specs/common/product_capability_95_roadmap.yaml"
TARGET_CAPABILITY_IDS = {
    "C1_BUSINESS_CYCLE_PHASE_ASSESSMENT",
    "C2_TRANSITION_RISK_DETECTION",
    "C3_EXPLAINABILITY_AND_ATTRIBUTION",
}

PROHIBITED_FRAGMENTS = {
    "standalone current phase classifier",
    "phase winner",
    "phase rank",
    "role-count vote",
    "buy_signal",
    "sell_signal",
    "trade_action",
    "target_weight",
}


def build_product_capability_95_roadmap(
    path: str | Path = DEFAULT_ROADMAP_PATH,
) -> dict[str, Any]:
    """Load the governed 95 percent roadmap."""

    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "product_capability_95_roadmap"
    ]


def summarize_product_capability_95_roadmap(
    path: str | Path = DEFAULT_ROADMAP_PATH,
) -> dict[str, Any]:
    """Summarize roadmap readiness and hard gates."""

    roadmap = build_product_capability_95_roadmap(path)
    target_rows = list(roadmap["target_capabilities"])
    planned_phases = list(roadmap["planned_phases"])
    target_ids = {row["capability_id"] for row in target_rows}
    max_phase_count = int(roadmap["max_phase_count"])
    planned_phase_count = int(roadmap["planned_phase_count"])
    target_phase_id = int(roadmap["target_phase_id"])
    post_target_enablers = list(roadmap.get("post_target_enablers", ()))
    target_reach_count = sum(int(row["target_percent"]) >= 95 for row in target_rows)
    monotonic_targets = _monotonic_target_count(target_rows)
    prohibited_claim_count = _prohibited_claim_count(roadmap)
    expected = dict(roadmap["hard_gates"])
    summary = {
        "roadmap_ready": target_ids == TARGET_CAPABILITY_IDS
        and planned_phase_count == len(planned_phases)
        and planned_phase_count <= max_phase_count
        and target_reach_count == len(target_rows)
        and monotonic_targets == len(target_rows)
        and prohibited_claim_count == 0,
        "version": roadmap["version"],
        "status": roadmap["status"],
        "baseline_phase_id": roadmap["baseline_phase_id"],
        "baseline_phase_label": roadmap["baseline_phase_label"],
        "max_phase_count": max_phase_count,
        "planned_phase_count_max": max_phase_count,
        "planned_phase_count": planned_phase_count,
        "target_phase_id": target_phase_id,
        "target_capability_count": len(target_rows),
        "target_capability_ids": [row["capability_id"] for row in target_rows],
        "all_target_capabilities_reach_95": target_reach_count == len(target_rows),
        "monotonic_progress_targets": monotonic_targets == len(target_rows),
        "planned_phase_ids": [int(row["phase_id"]) for row in planned_phases],
        "post_target_enabler_count": len(post_target_enablers),
        "post_target_enabler_phase_ids": [
            int(row["phase_id"]) for row in post_target_enablers
        ],
        "phase65_test_suite_reduction_enabler_present": any(
            int(row["phase_id"]) == 65
            and row.get("capability_percent_effect") == "no_percent_change_enabler"
            for row in post_target_enablers
        ),
        "phase66_archive_shard_enabler_present": any(
            int(row["phase_id"]) == 66
            and row.get("capability_percent_effect") == "no_percent_change_enabler"
            for row in post_target_enablers
        ),
        "phase67_transition_timing_enabler_present": any(
            int(row["phase_id"]) == 67
            and row.get("capability_percent_effect") == "product_surface_increment"
            for row in post_target_enablers
        ),
        "phase68_test_index_and_numeric_overlay_enabler_present": any(
            int(row["phase_id"]) == 68
            and row.get("capability_percent_effect") == "product_surface_increment"
            for row in post_target_enablers
        ),
        "phase69_start_confirmation_enabler_present": any(
            int(row["phase_id"]) == 69
            and row.get("capability_percent_effect") == "product_surface_increment"
            for row in post_target_enablers
        ),
        "phase70_registry_preview_enabler_present": any(
            int(row["phase_id"]) == 70
            and row.get("capability_percent_effect") == "product_surface_increment"
            for row in post_target_enablers
        ),
        "phase71_registry_update_gate_enabler_present": any(
            int(row["phase_id"]) == 71
            and row.get("capability_percent_effect") == "product_surface_increment"
            for row in post_target_enablers
        ),
        "phase72_current_macro_numeric_chart_enabler_present": any(
            int(row["phase_id"]) == 72
            and row.get("capability_percent_effect") == "product_surface_increment"
            for row in post_target_enablers
        ),
        "phase73_dashboard_method_explanation_enabler_present": any(
            int(row["phase_id"]) == 73
            and row.get("capability_percent_effect") == "product_surface_increment"
            for row in post_target_enablers
        ),
        "phase74_80_plan_recorded": {
            int(row["phase_id"]) for row in post_target_enablers
        }.issuperset(set(range(74, 81))),
        "final_targets": {
            row["capability_id"]: int(row["target_percent"]) for row in target_rows
        },
        "phase_table_rows": [_phase_table_row(row, target_rows) for row in planned_phases],
        "standalone_classifier_added_count": int(
            roadmap["universal_guardrails"]["standalone_classifier_added_count"]
        ),
        "phase_rank_or_score_added_count": int(
            roadmap["universal_guardrails"]["phase_rank_or_score_added_count"]
        ),
        "semantic_drift_count": 0,
        "prohibited_claim_count": prohibited_claim_count,
        "target_capabilities": target_rows,
        "planned_phases": planned_phases,
        "post_target_enablers": post_target_enablers,
    }
    summary["result"] = "passed" if _passes(summary, expected) else "blocked"
    return summary


def _phase_table_row(
    phase: dict[str, Any], target_rows: list[dict[str, Any]]
) -> dict[str, Any]:
    phase_id = str(phase["phase_id"])
    targets = {
        row["capability_id"]: int(row["phase_targets"][phase_id])
        for row in target_rows
    }
    return {
        "phase_id": int(phase["phase_id"]),
        "phase_title": phase["phase_title"],
        "objective": phase["objective_zh"],
        "capability_targets": targets,
    }


def _monotonic_target_count(target_rows: list[dict[str, Any]]) -> int:
    count = 0
    for row in target_rows:
        previous = int(row["baseline_percent"])
        monotonic = True
        for _, value in sorted(
            row["phase_targets"].items(), key=lambda item: int(item[0])
        ):
            current = int(value)
            if current < previous:
                monotonic = False
                break
            previous = current
        if monotonic and previous == int(row["target_percent"]):
            count += 1
    return count


def _prohibited_claim_count(value: Any) -> int:
    if isinstance(value, dict):
        return sum(_prohibited_claim_count(item) for item in value.values())
    if isinstance(value, list):
        return sum(_prohibited_claim_count(item) for item in value)
    if isinstance(value, str):
        lowered = value.lower()
        return int(any(fragment in lowered for fragment in PROHIBITED_FRAGMENTS))
    return 0


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())

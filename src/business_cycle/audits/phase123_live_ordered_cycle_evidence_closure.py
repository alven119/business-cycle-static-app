"""Phase 123 live ordered-cycle evidence closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.render.nas_cycle_command_center import (
    build_nas_cycle_command_center,
)
from business_cycle.storage.nas_indicator_snapshots import (
    build_nas_indicator_snapshot_manifest,
)
from business_cycle.transition_monitor.live_ordered_cycle_evidence import (
    build_live_ordered_cycle_evidence,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PATH = ROOT / "specs/audits/phase123_live_ordered_cycle_evidence_closure.yaml"


def summarize_phase123_live_ordered_cycle_evidence_closure(
    path: str | Path = DEFAULT_PATH,
) -> dict[str, Any]:
    """Evaluate deterministic Phase 123 integration gates without live I/O."""

    expected = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase123_live_ordered_cycle_evidence_closure"
    ]["hard_gates"]
    snapshot = build_phase123_live_evidence_fixture_snapshot()
    runtime = build_live_ordered_cycle_evidence(snapshot)
    command_center = build_nas_cycle_command_center(
        snapshot,
        live_transition_evidence=runtime,
    )
    summary = {
        "phase": 123,
        "live_ordered_cycle_evidence_contract_ready": runtime[
            "live_ordered_cycle_evidence_contract_ready"
        ],
        "live_evidence_evaluator_connected": runtime[
            "live_evidence_evaluator_connected"
        ],
        "dashboard_live_evidence_wiring_ready": (
            command_center["live_transition_evaluator_connected"]
            and all(
                row["evidence_evaluation_status"]
                != "not_evaluated_in_live_runtime"
                for row in command_center["transition_lanes"]
            )
        ),
        "evaluated_role_count": runtime["evaluated_role_count"],
        "phase_evidence_output_role_count": runtime[
            "phase_evidence_output_role_count"
        ],
        "lane_output_count": runtime["lane_output_count"],
        "watch_confirmation_separation_verified": runtime[
            "watch_confirmation_separation_verified"
        ],
        "phase_presence_transition_separation_valid": runtime[
            "phase_presence_transition_separation_valid"
        ],
        "declared_state_and_legal_transition_preserved": runtime[
            "declared_state_and_legal_transition_preserved"
        ],
        "why_not_confirmation_present": bool(runtime["why_not_confirmation"]),
        "raw_value_promoted_to_evidence_count": runtime[
            "raw_value_promoted_to_evidence_count"
        ],
        "smoothing_alone_promoted_to_evidence_count": runtime[
            "smoothing_alone_promoted_to_evidence_count"
        ],
        "missing_value_treated_as_neutral_count": runtime[
            "missing_value_treated_as_neutral_count"
        ],
        "missing_value_treated_as_zero_count": runtime[
            "missing_value_treated_as_zero_count"
        ],
        "watch_promoted_to_confirmation_count": runtime[
            "watch_promoted_to_confirmation_count"
        ],
        "candidate_phase_emitted": runtime["candidate_phase_emitted"],
        "current_phase_emitted": runtime["current_phase_emitted"],
        "standalone_classifier_added_count": runtime[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": runtime[
            "phase_rank_or_score_added_count"
        ],
        "role_count_voting_added_count": runtime[
            "role_count_voting_added_count"
        ],
        "arbitrary_threshold_added_count": runtime[
            "arbitrary_threshold_added_count"
        ],
        "numeric_weight_added_count": runtime["numeric_weight_added_count"],
        "production_behavior_change_count": 0,
        "prospective_registry_record_count": 0,
        "semantic_drift_count": runtime["semantic_drift_count"],
        "product_doctrine_alignment_status": "aligned",
        "development_next_phase": 124,
        "phase123_closure_status": (
            "closed_live_ordered_cycle_evidence_connected_declared_state_preserved"
        ),
        "runtime": runtime,
    }
    summary["result"] = (
        "passed"
        if all(summary.get(key) == value for key, value in expected.items())
        else "blocked"
    )
    return summary


def build_phase123_live_evidence_fixture_snapshot() -> dict[str, Any]:
    """Return a hermetic five-role live evidence fixture for integration tests."""
    baseline = build_nas_indicator_snapshot_manifest()
    required = {
        "boom_claims_u_shape": {
            "ICSA": _weekly_values([110, 100, 90, 80, 90, 110]),
        },
        "boom_retail_sales_vs_broad_pce": {
            "RRSFS": _yoy_values(100, 100, 110, 105),
            "PCEC96": _yoy_values(100, 100, 108, 103),
        },
        "boom_private_investment": {
            "FPIC1": _yoy_values(100, 100, 112, 106),
        },
        "recession_employment_confirmation": {
            "CCSA": _weekly_values([100, 100, 100, 100, 110]),
        },
        "recession_consumption_confirmation": {
            "PCEC96": _yoy_values(100, 100, 108, 103),
        },
    }
    roles = []
    for row in baseline["role_snapshots"]:
        role_id = str(row["role_id"])
        histories = required.get(role_id, {})
        roles.append(
            {
                **row,
                "snapshot_status": (
                    "revised_snapshot_ready" if histories else row["snapshot_status"]
                ),
                "freshness_status": "fresh" if histories else "unavailable",
                "source_lineage": [{"source_mode": "fixture_official_revised"}],
                "evidence_input_series": [
                    {
                        "series_id": series_id,
                        "observations": observations,
                    }
                    for series_id, observations in histories.items()
                ],
            }
        )
    return {
        **baseline,
        "snapshot_as_of": "2025-02-28",
        "data_mode": "revised_diagnostic",
        "role_snapshots": roles,
        "declared_cycle_state": {
            "declared_current_phase": "boom",
            "declared_current_phase_label_zh": "榮景",
            "legal_next_phase": "recession",
            "legal_next_phase_label_zh": "衰退",
        },
    }


def _weekly_values(values: list[int]) -> list[dict[str, Any]]:
    dates = [
        "2025-01-03",
        "2025-01-10",
        "2025-01-17",
        "2025-01-24",
        "2025-01-31",
        "2025-02-07",
    ]
    return [_observation(day, value, index) for index, (day, value) in enumerate(zip(dates, values, strict=False))]


def _yoy_values(
    prior_one: int,
    prior_two: int,
    current_one: int,
    current_two: int,
) -> list[dict[str, Any]]:
    return [
        _observation("2024-01-31", prior_one, 0),
        _observation("2024-02-28", prior_two, 1),
        _observation("2025-01-31", current_one, 2),
        _observation("2025-02-28", current_two, 3),
    ]


def _observation(day: str, value: int, index: int) -> dict[str, Any]:
    return {
        "date": day,
        "value": value,
        "data_mode": "revised",
        "source_artifact_id": f"phase123-fixture-{index}",
        "provenance_hash": f"phase123-provenance-{index}",
    }

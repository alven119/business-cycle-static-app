from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from business_cycle.indicators.batch_scoring import IndicatorBatchScoreSummary
from business_cycle.indicators.scoring import IndicatorScoreResult
from business_cycle.phases.batch_scoring import PhaseBatchScoreSummary
from business_cycle.phases.specs import PhaseScoreResult
from business_cycle.phases.state_machine import CurrentPhaseDecision
from business_cycle.pipeline.snapshot import build_cycle_snapshot, write_cycle_snapshot_json


def indicator_score(indicator_id: str, score: float = 80.0) -> IndicatorScoreResult:
    return IndicatorScoreResult(
        indicator_id=indicator_id,
        score=score,
        confidence=0.9,
        as_of="2024-12-31",
        method="synthetic",
        reason_zh="synthetic",
        details={},
    )


def phase_score(phase_id: str, score: float = 80.0) -> PhaseScoreResult:
    return PhaseScoreResult(
        phase_id=phase_id,
        phase_name_zh=phase_id,
        score=score,
        confidence=0.85,
        available_weight=1.0,
        missing_indicators=[],
        contributing_indicators=[],
        stage_hint=None,
        reason_zh="synthetic",
        details={},
    )


def current_decision(
    status: str = "confirmed",
    confidence: float = 0.8,
    blocked_phase_ids: list[str] | None = None,
) -> CurrentPhaseDecision:
    return CurrentPhaseDecision(
        current_phase_id="growth",
        current_phase_name_zh="成長期",
        decision_status=status,
        previous_phase_id="recovery",
        candidate_phase_id="growth",
        candidate_score=80.0,
        candidate_confidence=0.85,
        current_score=70.0,
        confidence=confidence,
        allowed_next_phase_id="growth",
        blocked_phase_ids=blocked_phase_ids or [],
        reason_zh="synthetic",
        details={"ranked_phase_scores": []},
    )


def indicator_summary(failed: int = 0) -> IndicatorBatchScoreSummary:
    failures = [
        {"indicator_id": "missing", "error_type": "MissingObservations", "message": "missing"}
    ][:failed]
    return IndicatorBatchScoreSummary(
        total_indicators=3,
        scored_indicators=2,
        failed_indicators=failed,
        results=[indicator_score("b_indicator"), indicator_score("a_indicator")],
        failures=failures,
    )


def phase_summary(failed: int = 0) -> PhaseBatchScoreSummary:
    failures = [{"phase_id": "bad", "error_type": "ValueError", "message": "bad"}][:failed]
    return PhaseBatchScoreSummary(
        total_phases=4,
        scored_phases=3,
        failed_phases=failed,
        results=[
            phase_score("growth", 70),
            phase_score("recession", 30),
            phase_score("recovery", 80),
        ],
        failures=failures,
    )


def contains_key(value: Any, key: str) -> bool:
    if isinstance(value, dict):
        return key in value or any(contains_key(item, key) for item in value.values())
    if isinstance(value, list):
        return any(contains_key(item, key) for item in value)
    return False


def test_build_cycle_snapshot_integrates_outputs() -> None:
    snapshot = build_cycle_snapshot(indicator_summary(), phase_summary(), current_decision())

    assert snapshot.summary["current_phase_id"] == "growth"
    assert snapshot.current_phase_decision["decision_status"] == "confirmed"
    assert snapshot.phase_scores
    assert snapshot.indicator_scores


def test_summary_counts_are_correct() -> None:
    snapshot = build_cycle_snapshot(indicator_summary(failed=1), phase_summary(failed=1), current_decision())

    assert snapshot.summary["total_indicators"] == 3
    assert snapshot.summary["scored_indicators"] == 2
    assert snapshot.summary["failed_indicators"] == 1
    assert snapshot.summary["total_phases"] == 4
    assert snapshot.summary["scored_phases"] == 3
    assert snapshot.summary["failed_phases"] == 1


def test_indicator_scores_are_ordered_by_indicator_id() -> None:
    snapshot = build_cycle_snapshot(indicator_summary(), phase_summary(), current_decision())

    assert [entry["indicator_id"] for entry in snapshot.indicator_scores] == [
        "a_indicator",
        "b_indicator",
    ]


def test_phase_scores_use_deterministic_phase_order() -> None:
    snapshot = build_cycle_snapshot(indicator_summary(), phase_summary(), current_decision())

    assert [entry["phase_id"] for entry in snapshot.phase_scores] == [
        "recession",
        "recovery",
        "growth",
    ]


def test_failed_indicators_warning() -> None:
    snapshot = build_cycle_snapshot(indicator_summary(failed=1), phase_summary(), current_decision())

    assert any("failed_indicators=1" in warning for warning in snapshot.warnings)


def test_failed_phases_warning() -> None:
    snapshot = build_cycle_snapshot(indicator_summary(), phase_summary(failed=1), current_decision())

    assert any("failed_phases=1" in warning for warning in snapshot.warnings)


def test_insufficient_evidence_warning() -> None:
    snapshot = build_cycle_snapshot(
        indicator_summary(),
        phase_summary(),
        current_decision(status="insufficient_evidence"),
    )

    assert any("insufficient_evidence" in warning for warning in snapshot.warnings)


def test_blocked_phase_ids_warning() -> None:
    snapshot = build_cycle_snapshot(
        indicator_summary(),
        phase_summary(),
        current_decision(blocked_phase_ids=["recession"]),
    )

    assert any("blocked_phase_ids=recession" in warning for warning in snapshot.warnings)
    assert snapshot.summary["blocked_phase_count"] == 1


def test_low_confidence_warning() -> None:
    snapshot = build_cycle_snapshot(indicator_summary(), phase_summary(), current_decision(confidence=0.4))

    assert any("confidence is low" in warning for warning in snapshot.warnings)


def test_snapshot_does_not_include_investment_advice() -> None:
    snapshot = build_cycle_snapshot(indicator_summary(), phase_summary(), current_decision())

    assert not contains_key(snapshot.__dict__, "investment_advice")


def test_write_cycle_snapshot_json_writes_valid_json(tmp_path: Path) -> None:
    snapshot = build_cycle_snapshot(indicator_summary(), phase_summary(), current_decision(), as_of="2024-12-31")
    output_path = write_cycle_snapshot_json(snapshot, tmp_path / "cycle_snapshot.json")

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["as_of"] == "2024-12-31"
    assert payload["summary"]["current_phase_id"] == "growth"
    assert not contains_key(payload, "investment_advice")

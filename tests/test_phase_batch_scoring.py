from __future__ import annotations

import json
from pathlib import Path

from business_cycle.indicators.scoring import IndicatorScoreResult
from business_cycle.phases.batch_scoring import (
    score_phase_batch_safe,
    serialize_phase_score_result,
    write_phase_scores_json,
)
from business_cycle.phases.specs import PhaseIndicatorWeight, PhaseScoringSpec


def indicator_score(indicator_id: str, score: float = 80.0, confidence: float = 1.0) -> IndicatorScoreResult:
    return IndicatorScoreResult(
        indicator_id=indicator_id,
        score=score,
        confidence=confidence,
        as_of="2024-12-31",
        method="synthetic",
        reason_zh="synthetic",
        details={},
    )


def phase_spec(phase_id: str) -> PhaseScoringSpec:
    return PhaseScoringSpec(
        phase_id=phase_id,
        phase_name_zh=phase_id,
        description_zh="test",
        indicators=[PhaseIndicatorWeight("x", 1.0, "core")],
        minimum_available_weight=0.7,
        confidence_policy={},
        early_mid_late_thresholds={"early": 55.0, "mid": 70.0, "late": 82.0},
    )


def test_batch_scores_multiple_phases() -> None:
    summary = score_phase_batch_safe(
        {"recovery": phase_spec("recovery"), "growth": phase_spec("growth")},
        {"x": indicator_score("x")},
    )

    assert summary.total_phases == 2
    assert summary.scored_phases == 2
    assert summary.failed_phases == 0


def test_single_phase_failure_does_not_stop_batch() -> None:
    bad_spec = PhaseScoringSpec(
        phase_id="bad",
        phase_name_zh="bad",
        description_zh="bad",
        indicators=[PhaseIndicatorWeight("x", "bad-weight", "core")],  # type: ignore[arg-type]
        minimum_available_weight=0.7,
        confidence_policy={},
        early_mid_late_thresholds={},
    )
    summary = score_phase_batch_safe(
        {"bad": bad_spec, "recovery": phase_spec("recovery")},
        {"x": indicator_score("x")},
    )

    assert summary.scored_phases == 1
    assert summary.failed_phases == 1
    assert summary.failures[0]["phase_id"] == "bad"


def test_results_are_ordered_by_phase_id() -> None:
    summary = score_phase_batch_safe(
        {"recovery": phase_spec("recovery"), "growth": phase_spec("growth")},
        {"x": indicator_score("x")},
    )

    assert [result.phase_id for result in summary.results] == ["growth", "recovery"]


def test_failure_contains_phase_id_error_type_and_message() -> None:
    bad_spec = PhaseScoringSpec(
        phase_id="bad",
        phase_name_zh="bad",
        description_zh="bad",
        indicators=[PhaseIndicatorWeight("x", "bad-weight", "core")],  # type: ignore[arg-type]
        minimum_available_weight=0.7,
        confidence_policy={},
        early_mid_late_thresholds={},
    )
    summary = score_phase_batch_safe({"bad": bad_spec}, {"x": indicator_score("x")})

    assert summary.failures[0]["phase_id"] == "bad"
    assert summary.failures[0]["error_type"]
    assert summary.failures[0]["message"]


def test_serialize_phase_score_result_is_json_serializable() -> None:
    summary = score_phase_batch_safe({"recovery": phase_spec("recovery")}, {"x": indicator_score("x")})
    payload = serialize_phase_score_result(summary.results[0])

    json.dumps(payload)
    assert payload["phase_id"] == "recovery"
    assert payload["contributing_indicators"][0]["phase_signal_score"] == 80.0
    assert "current_phase" not in payload


def test_write_phase_scores_json_writes_file(tmp_path: Path) -> None:
    summary = score_phase_batch_safe({"recovery": phase_spec("recovery")}, {"x": indicator_score("x")})
    output_path = write_phase_scores_json(summary, tmp_path / "phase_scores.json")

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["summary"] == {
        "total_phases": 1,
        "scored_phases": 1,
        "failed_phases": 0,
    }
    assert payload["results"][0]["phase_id"] == "recovery"
    assert "current_phase" not in payload


def test_summary_counts_are_correct() -> None:
    summary = score_phase_batch_safe(
        {"recovery": phase_spec("recovery"), "growth": phase_spec("growth")},
        {},
    )

    assert summary.total_phases == 2
    assert summary.scored_phases == 2
    assert summary.failed_phases == 0

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import scripts.build_cycle_snapshot as snapshot_script
from business_cycle.indicators.batch_scoring import IndicatorBatchScoreSummary, write_indicator_scores_json
from business_cycle.indicators.scoring import IndicatorScoreResult
from business_cycle.phases.batch_scoring import PhaseBatchScoreSummary, write_phase_scores_json
from business_cycle.phases.specs import PhaseScoreResult
from business_cycle.phases.state_machine import CurrentPhaseDecision, write_current_phase_decision_json


def indicator_score(indicator_id: str) -> IndicatorScoreResult:
    return IndicatorScoreResult(
        indicator_id=indicator_id,
        score=80.0,
        confidence=0.9,
        as_of="2024-12-31",
        method="synthetic",
        reason_zh="synthetic",
        details={},
    )


def phase_score(phase_id: str, score: float) -> PhaseScoreResult:
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


def decision() -> CurrentPhaseDecision:
    return CurrentPhaseDecision(
        current_phase_id="growth",
        current_phase_name_zh="成長期",
        decision_status="confirmed",
        previous_phase_id="recovery",
        candidate_phase_id="growth",
        candidate_score=80.0,
        candidate_confidence=0.85,
        current_score=70.0,
        confidence=0.8,
        allowed_next_phase_id="growth",
        blocked_phase_ids=[],
        reason_zh="synthetic",
        details={},
    )


def write_inputs(tmp_path: Path) -> tuple[Path, Path, Path]:
    indicator_path = write_indicator_scores_json(
        IndicatorBatchScoreSummary(
            total_indicators=2,
            scored_indicators=2,
            failed_indicators=0,
            results=[indicator_score("b"), indicator_score("a")],
            failures=[],
        ),
        tmp_path / "indicator_scores.json",
    )
    phase_path = write_phase_scores_json(
        PhaseBatchScoreSummary(
            total_phases=2,
            scored_phases=2,
            failed_phases=0,
            results=[phase_score("growth", 80), phase_score("recovery", 70)],
            failures=[],
        ),
        tmp_path / "phase_scores.json",
    )
    decision_path = write_current_phase_decision_json(
        decision(),
        tmp_path / "current_phase_decision.json",
    )
    return indicator_path, phase_path, decision_path


def contains_key(value: Any, key: str) -> bool:
    if isinstance(value, dict):
        return key in value or any(contains_key(item, key) for item in value.values())
    if isinstance(value, list):
        return any(contains_key(item, key) for item in value)
    return False


def test_cli_reads_three_inputs_and_writes_snapshot(tmp_path: Path) -> None:
    indicator_path, phase_path, decision_path = write_inputs(tmp_path)
    output_path = tmp_path / "cycle_snapshot.json"

    exit_code = snapshot_script.main(
        [
            "--indicator-scores-path",
            str(indicator_path),
            "--phase-scores-path",
            str(phase_path),
            "--current-phase-decision-path",
            str(decision_path),
            "--output-path",
            str(output_path),
        ]
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert payload["summary"]["current_phase_id"] == "growth"
    assert payload["current_phase_decision"]["decision_status"] == "confirmed"


def test_missing_input_json_exits_with_clear_error(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _, phase_path, decision_path = write_inputs(tmp_path)

    with pytest.raises(SystemExit) as exc_info:
        snapshot_script.main(
            [
                "--indicator-scores-path",
                str(tmp_path / "missing.json"),
                "--phase-scores-path",
                str(phase_path),
                "--current-phase-decision-path",
                str(decision_path),
            ]
        )

    assert exc_info.value.code == 1
    assert "Indicator scores JSON does not exist" in capsys.readouterr().err


def test_as_of_is_written_to_snapshot(tmp_path: Path) -> None:
    indicator_path, phase_path, decision_path = write_inputs(tmp_path)
    output_path = tmp_path / "cycle_snapshot.json"

    snapshot_script.main(
        [
            "--indicator-scores-path",
            str(indicator_path),
            "--phase-scores-path",
            str(phase_path),
            "--current-phase-decision-path",
            str(decision_path),
            "--output-path",
            str(output_path),
            "--as-of",
            "2024-12-31",
        ]
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["as_of"] == "2024-12-31"


def test_output_does_not_include_investment_advice(tmp_path: Path) -> None:
    indicator_path, phase_path, decision_path = write_inputs(tmp_path)
    output_path = tmp_path / "cycle_snapshot.json"

    snapshot_script.main(
        [
            "--indicator-scores-path",
            str(indicator_path),
            "--phase-scores-path",
            str(phase_path),
            "--current-phase-decision-path",
            str(decision_path),
            "--output-path",
            str(output_path),
        ]
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert not contains_key(payload, "investment_advice")

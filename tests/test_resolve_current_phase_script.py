from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.resolve_current_phase as resolve_script
from business_cycle.phases.batch_scoring import PhaseBatchScoreSummary, write_phase_scores_json
from business_cycle.phases.specs import PhaseScoreResult


def phase_score(phase_id: str, score: float, confidence: float = 0.90) -> PhaseScoreResult:
    return PhaseScoreResult(
        phase_id=phase_id,
        phase_name_zh=phase_id,
        score=score,
        confidence=confidence,
        available_weight=1.0,
        missing_indicators=[],
        contributing_indicators=[],
        stage_hint=None,
        reason_zh="synthetic",
        details={},
    )


def write_phase_scores(path: Path) -> Path:
    summary = PhaseBatchScoreSummary(
        total_phases=4,
        scored_phases=4,
        failed_phases=0,
        results=[
            phase_score("recession", 40),
            phase_score("recovery", 70),
            phase_score("growth", 80),
            phase_score("boom", 55),
        ],
        failures=[],
    )
    return write_phase_scores_json(summary, path)


def test_cli_reads_phase_scores_and_writes_decision(tmp_path: Path) -> None:
    phase_scores_path = write_phase_scores(tmp_path / "phase_scores.json")
    output_path = tmp_path / "current_phase_decision.json"

    exit_code = resolve_script.main(
        [
            "--phase-scores-path",
            str(phase_scores_path),
            "--output-path",
            str(output_path),
        ]
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert payload["decision_status"] in {"initial_estimate", "insufficient_evidence"}
    assert "current_phase_id" in payload
    assert "investment_advice" not in payload


def test_previous_phase_id_is_used(tmp_path: Path) -> None:
    phase_scores_path = write_phase_scores(tmp_path / "phase_scores.json")
    output_path = tmp_path / "current_phase_decision.json"

    resolve_script.main(
        [
            "--phase-scores-path",
            str(phase_scores_path),
            "--output-path",
            str(output_path),
            "--previous-phase-id",
            "recovery",
        ]
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["previous_phase_id"] == "recovery"
    assert payload["allowed_next_phase_id"] == "growth"


def test_missing_phase_scores_json_exits_with_clear_error(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as exc_info:
        resolve_script.main(["--phase-scores-path", str(tmp_path / "missing.json")])

    assert exc_info.value.code == 1
    assert "Phase scores JSON does not exist" in capsys.readouterr().err


def test_output_contains_status_and_current_phase_id(tmp_path: Path) -> None:
    phase_scores_path = write_phase_scores(tmp_path / "phase_scores.json")
    output_path = tmp_path / "current_phase_decision.json"

    resolve_script.main(
        [
            "--phase-scores-path",
            str(phase_scores_path),
            "--output-path",
            str(output_path),
        ]
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert "decision_status" in payload
    assert "current_phase_id" in payload

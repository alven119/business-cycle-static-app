from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.score_phases as score_script
from business_cycle.indicators.batch_scoring import (
    IndicatorBatchScoreSummary,
    write_indicator_scores_json,
)
from business_cycle.indicators.scoring import IndicatorScoreResult


def indicator_score(indicator_id: str, score: float, confidence: float) -> IndicatorScoreResult:
    return IndicatorScoreResult(
        indicator_id=indicator_id,
        score=score,
        confidence=confidence,
        as_of="2024-12-31",
        method="synthetic",
        reason_zh="synthetic",
        details={},
    )


def write_indicator_scores(path: Path) -> Path:
    summary = IndicatorBatchScoreSummary(
        total_indicators=4,
        scored_indicators=4,
        failed_indicators=0,
        results=[
            indicator_score("initial_jobless_claims", 82, 0.9),
            indicator_score("real_retail_sales", 78, 0.85),
            indicator_score("durable_goods_orders", 72, 0.8),
            indicator_score("unemployment_rate", 60, 0.75),
        ],
        failures=[],
    )
    return write_indicator_scores_json(summary, path)


def test_cli_reads_indicator_scores_and_phase_spec(tmp_path: Path) -> None:
    indicator_scores_path = write_indicator_scores(tmp_path / "indicator_scores.json")
    output_path = tmp_path / "phase_scores.json"

    exit_code = score_script.main(
        [
            "--indicator-scores-path",
            str(indicator_scores_path),
            "--phase-specs-path",
            "specs/phases/recovery.yaml",
            "--output-path",
            str(output_path),
        ]
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert payload["summary"]["scored_phases"] == 1
    assert payload["results"][0]["phase_id"] == "recovery"
    assert "current_phase" not in payload


def test_phase_id_filter_is_applied(tmp_path: Path) -> None:
    indicator_scores_path = write_indicator_scores(tmp_path / "indicator_scores.json")
    output_path = tmp_path / "phase_scores.json"

    score_script.main(
        [
            "--indicator-scores-path",
            str(indicator_scores_path),
            "--phase-specs-path",
            "specs/phases",
            "--output-path",
            str(output_path),
            "--phase-id",
            "recovery",
        ]
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["summary"]["total_phases"] == 1
    assert payload["results"][0]["phase_id"] == "recovery"


def test_as_of_is_written_to_result_details(tmp_path: Path) -> None:
    indicator_scores_path = write_indicator_scores(tmp_path / "indicator_scores.json")
    output_path = tmp_path / "phase_scores.json"

    score_script.main(
        [
            "--indicator-scores-path",
            str(indicator_scores_path),
            "--phase-specs-path",
            "specs/phases/recovery.yaml",
            "--output-path",
            str(output_path),
            "--as-of",
            "2024-12-31",
        ]
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["results"][0]["details"]["as_of"] == "2024-12-31"


def test_missing_indicator_scores_json_exits_with_clear_error(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as exc_info:
        score_script.main(
            [
                "--indicator-scores-path",
                str(tmp_path / "missing.json"),
                "--phase-specs-path",
                "specs/phases/recovery.yaml",
            ]
        )

    assert exc_info.value.code == 1
    assert "Indicator scores JSON does not exist" in capsys.readouterr().err


def test_load_indicator_scores_json_rejects_missing_fields(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text(json.dumps({"results": [{"indicator_id": "x"}]}), encoding="utf-8")

    with pytest.raises(ValueError, match="missing required field"):
        score_script.load_indicator_scores_json(path)


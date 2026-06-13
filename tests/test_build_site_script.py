from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.build_site as build_site


def synthetic_snapshot() -> dict:
    return {
        "generated_at": "2026-06-14T00:00:00+00:00",
        "as_of": "2024-12-31",
        "current_phase_decision": {
            "current_phase_id": "recovery",
            "current_phase_name_zh": "復甦期",
            "decision_status": "hold_current",
            "previous_phase_id": "recovery",
            "candidate_phase_id": "growth",
            "candidate_score": 70.0,
            "candidate_confidence": 0.8,
            "current_score": 72.0,
            "confidence": 0.75,
            "allowed_next_phase_id": "growth",
            "blocked_phase_ids": [],
            "reason_zh": "synthetic reason",
            "details": {},
        },
        "phase_scores": [],
        "indicator_scores": [],
        "summary": {"current_phase_id": "recovery", "decision_status": "hold_current"},
        "warnings": [],
        "failures": {"indicator_failures": [], "phase_failures": []},
    }


def test_cli_reads_snapshot_and_writes_static_site(tmp_path: Path) -> None:
    snapshot_path = tmp_path / "cycle_snapshot.json"
    output_dir = tmp_path / "public"
    snapshot_path.write_text(json.dumps(synthetic_snapshot(), ensure_ascii=False), encoding="utf-8")

    exit_code = build_site.main(
        [
            "--snapshot-path",
            str(snapshot_path),
            "--output-dir",
            str(output_dir),
        ]
    )

    assert exit_code == 0
    assert (output_dir / "index.html").exists()
    assert (output_dir / "data" / "cycle_snapshot.json").exists()


def test_missing_snapshot_exits_with_clear_error(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as exc_info:
        build_site.main(
            [
                "--snapshot-path",
                str(tmp_path / "missing.json"),
                "--output-dir",
                str(tmp_path / "public"),
            ]
        )

    assert exc_info.value.code == 1
    assert "Cycle snapshot JSON does not exist" in capsys.readouterr().err


def test_output_html_has_disclaimer_without_advice_language(tmp_path: Path) -> None:
    snapshot_path = tmp_path / "cycle_snapshot.json"
    output_dir = tmp_path / "public"
    snapshot_path.write_text(json.dumps(synthetic_snapshot(), ensure_ascii=False), encoding="utf-8")

    build_site.main(
        [
            "--snapshot-path",
            str(snapshot_path),
            "--output-dir",
            str(output_dir),
        ]
    )

    html = (output_dir / "index.html").read_text(encoding="utf-8")
    assert "不構成投資建議" in html
    assert "買進" not in html
    assert "賣出" not in html
    assert "FRED_API_KEY" not in html

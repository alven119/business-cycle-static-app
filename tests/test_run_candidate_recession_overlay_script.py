from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.run_candidate_recession_overlay as overlay_script
from business_cycle.backtests import CandidateRecessionOverlayError


def test_run_candidate_recession_overlay_cli_succeeds(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output = tmp_path / "overlay.json"
    monkeypatch.setattr(overlay_script, "build_candidate_recession_overlay_report", fake_build_report)

    exit_code = overlay_script.main(["--experiment-id", "test_overlay", "--output", str(output)])

    stdout = capsys.readouterr().out
    assert exit_code == 0
    assert "experiment_id=test_overlay" in stdout
    assert "scenario_count=1" in stdout
    assert output.exists()
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["experiment_id"] == "test_overlay"


def test_run_candidate_recession_overlay_cli_accepts_custom_spec(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = tmp_path / "overlay.json"
    received: dict[str, str] = {}

    def fake_builder(**kwargs):  # type: ignore[no-untyped-def]
        received["spec_path"] = str(kwargs["spec_path"])
        return fake_build_report(**kwargs)

    monkeypatch.setattr(overlay_script, "build_candidate_recession_overlay_report", fake_builder)

    exit_code = overlay_script.main(["--spec", "custom.yaml", "--output", str(output)])

    assert exit_code == 0
    assert received["spec_path"] == "custom.yaml"


def test_run_candidate_recession_overlay_missing_spec_fails(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def fake_builder(**_kwargs):  # type: ignore[no-untyped-def]
        raise CandidateRecessionOverlayError("candidate recession overlay spec does not exist")

    monkeypatch.setattr(overlay_script, "build_candidate_recession_overlay_report", fake_builder)

    with pytest.raises(SystemExit) as exc_info:
        overlay_script.main(["--spec", "missing.yaml"])

    assert exc_info.value.code == 1
    assert "candidate recession overlay spec does not exist" in capsys.readouterr().err


def test_run_candidate_recession_overlay_reuse_existing(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output = tmp_path / "overlay.json"
    output.write_text(json.dumps(fake_build_report(experiment_id="reuse")), encoding="utf-8")

    exit_code = overlay_script.main(["--reuse-existing", "--output", str(output)])

    stdout = capsys.readouterr().out
    assert exit_code == 0
    assert "experiment_id=reuse" in stdout


def test_run_candidate_recession_overlay_force_recomputes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output = tmp_path / "overlay.json"
    output.write_text(json.dumps(fake_build_report(experiment_id="old")), encoding="utf-8")
    monkeypatch.setattr(overlay_script, "build_candidate_recession_overlay_report", fake_build_report)

    exit_code = overlay_script.main(["--reuse-existing", "--force", "--experiment-id", "new", "--output", str(output)])

    stdout = capsys.readouterr().out
    assert exit_code == 0
    assert "experiment_id=new" in stdout


def fake_build_report(**kwargs):  # type: ignore[no-untyped-def]
    experiment_id = kwargs.get("experiment_id", "candidate_recession_overlay_v1")
    return {
        "experiment_id": experiment_id,
        "scenario_count": 1,
        "scenario_summaries": [],
        "acceptance_summary": {
            "pass_count": 1,
            "warning_count": 0,
            "fail_count": 0,
            "blocked_covid_2019_false_confirmed": True,
            "kept_gfc_confirmed": True,
            "kept_covid_2020_confirmed": True,
            "out_of_sample_false_confirmed_count": 0,
        },
        "caveats_zh": ["不構成投資建議。"],
    }

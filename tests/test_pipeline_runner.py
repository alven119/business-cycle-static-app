from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from business_cycle.pipeline import runner
from business_cycle.pipeline.runner import run_cycle_pipeline


def test_pipeline_runner_calls_steps_in_order(tmp_path: Path) -> None:
    calls: list[tuple[str, list[str]]] = []

    def fake_runner(step_name: str, args: list[str]) -> int:
        calls.append((step_name, args))
        return 0

    result = run_cycle_pipeline(output_dir=tmp_path, step_runner=fake_runner)

    assert result.success is True
    assert [name for name, _ in calls] == [
        "score_indicators",
        "score_phases",
        "resolve_current_phase",
        "build_cycle_snapshot",
    ]
    assert result.indicator_scores_path == tmp_path / "indicator_scores.json"
    assert result.phase_scores_path == tmp_path / "phase_scores.json"
    assert result.current_phase_decision_path == tmp_path / "current_phase_decision.json"
    assert result.cycle_snapshot_path == tmp_path / "cycle_snapshot.json"


def test_pipeline_runner_passes_previous_phase_to_resolver(tmp_path: Path) -> None:
    calls: dict[str, list[str]] = {}

    def fake_runner(step_name: str, args: list[str]) -> int:
        calls[step_name] = args
        return 0

    run_cycle_pipeline(previous_phase_id="recovery", output_dir=tmp_path, step_runner=fake_runner)

    assert "--previous-phase-id" in calls["resolve_current_phase"]
    assert "recovery" in calls["resolve_current_phase"]


def test_pipeline_runner_passes_as_of_to_relevant_steps(tmp_path: Path) -> None:
    calls: dict[str, list[str]] = {}

    def fake_runner(step_name: str, args: list[str]) -> int:
        calls[step_name] = args
        return 0

    run_cycle_pipeline(as_of="2024-12-31", output_dir=tmp_path, step_runner=fake_runner)

    assert "--as-of" in calls["score_indicators"]
    assert "--as-of" in calls["score_phases"]
    assert "--as-of" in calls["build_cycle_snapshot"]
    assert "--as-of" not in calls["resolve_current_phase"]


def test_pipeline_runner_stops_on_failure(tmp_path: Path) -> None:
    calls: list[str] = []

    def fake_runner(step_name: str, args: list[str]) -> int:
        calls.append(step_name)
        return 1 if step_name == "score_phases" else 0

    result = run_cycle_pipeline(output_dir=tmp_path, step_runner=fake_runner)

    assert result.success is False
    assert result.message == "Pipeline step failed: score_phases exit_code=1"
    assert calls == ["score_indicators", "score_phases"]


def test_pipeline_runner_update_data_runs_first_and_passes_filters(tmp_path: Path) -> None:
    calls: dict[str, list[str]] = {}

    def fake_runner(step_name: str, args: list[str]) -> int:
        calls[step_name] = args
        return 0

    run_cycle_pipeline(
        update_data=True,
        force_refresh=True,
        indicator_ids=["unemployment_rate"],
        phase_ids=["recovery"],
        output_dir=tmp_path,
        step_runner=fake_runner,
    )

    assert list(calls)[0] == "update_catalog_data"
    assert "--force-refresh" in calls["update_catalog_data"]
    assert "unemployment_rate" in calls["update_catalog_data"]
    assert "unemployment_rate" in calls["score_indicators"]
    assert "recovery" in calls["score_phases"]


def test_pipeline_runner_does_not_include_dashboard_or_investment_advice_steps(tmp_path: Path) -> None:
    calls: list[str] = []

    def fake_runner(step_name: str, args: list[str]) -> int:
        calls.append(step_name)
        return 0

    result = run_cycle_pipeline(output_dir=tmp_path, step_runner=fake_runner)

    assert result.success is True
    assert "dashboard" not in " ".join(calls)
    assert "investment_advice" not in " ".join(calls)


def test_default_step_runner_uses_subprocess_script_path(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    calls = []

    def fake_run(cmd, cwd, env, check):  # type: ignore[no-untyped-def]
        calls.append({"cmd": cmd, "cwd": cwd, "env": env, "check": check})
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(runner.subprocess, "run", fake_run)

    exit_code = runner._default_step_runner("score_indicators", ["--output-path", "out.json"])

    assert exit_code == 0
    assert calls[0]["cmd"][0] == sys.executable
    assert calls[0]["cmd"][1].endswith("scripts/score_indicators.py")
    assert "--output-path" in calls[0]["cmd"]
    assert calls[0]["cwd"] == runner._project_root()
    assert str(runner._project_root() / "src") in calls[0]["env"]["PYTHONPATH"]
    assert calls[0]["check"] is False

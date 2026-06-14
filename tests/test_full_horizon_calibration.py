from __future__ import annotations

import json
from pathlib import Path

from business_cycle.backtests import run_full_horizon_calibration


def fake_experiment_runner(**kwargs) -> dict:  # noqa: ANN003
    output_dir = Path(kwargs["output_dir"])
    experiment_id = kwargs["experiment_id"]
    scenario_id = kwargs.get("scenario_id") or "all"
    summary_path = output_dir / experiment_id / "calibration_summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "experiment_id": experiment_id,
        "data_mode": "revised",
        "max_periods": kwargs.get("max_periods"),
        "scenario_count": 1,
        "scenarios": [
            {
                "scenario_id": scenario_id,
                "display_name_zh": "測試案例",
                "experiment": {"first_recession_current_as_of": None},
            }
        ],
        "aggregate": {"scenario_with_failures_count": 0},
        "caveats_zh": ["使用修訂後歷史資料。", "不構成投資建議。"],
        "output_path": str(summary_path),
    }
    summary_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return payload


def fake_review_writer(**kwargs) -> Path:  # noqa: ANN003
    output = Path(kwargs["output_path"])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(
            {
                "scenario_count": 1,
                "aggregate": {
                    "pass_count": 1,
                    "warning_count": 0,
                    "fail_count": 0,
                    "needs_longer_horizon_count": 0,
                    "early_false_recession_count": 0,
                },
                "caveats_zh": ["使用修訂後歷史資料。", "不構成投資建議。"],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return output


def failing_experiment_runner(**_kwargs) -> dict:  # noqa: ANN003
    raise RuntimeError("synthetic full-horizon failure")


def test_full_horizon_calibration_runs_without_max_periods(tmp_path: Path) -> None:
    controls_path = tmp_path / "controls.yaml"
    controls_path.write_text("transition_controls:\n  version: 1\n  enabled: true\n", encoding="utf-8")

    summary = run_full_horizon_calibration(
        experiment_id="test",
        controls_config_path=controls_path,
        output_dir=tmp_path / "calibration",
        experiment_runner=fake_experiment_runner,
        review_writer=fake_review_writer,
    )

    assert summary["max_periods"] is None
    assert summary["full_horizon"] is True
    assert Path(summary["acceptance_review_path"]).exists()
    assert "不構成投資建議。" in json.loads(Path(summary["output_path"]).read_text(encoding="utf-8"))["caveats_zh"]


def test_full_horizon_calibration_scenario_id_runs_one(tmp_path: Path) -> None:
    controls_path = tmp_path / "controls.yaml"
    controls_path.write_text("transition_controls:\n  version: 1\n  enabled: true\n", encoding="utf-8")

    summary = run_full_horizon_calibration(
        experiment_id="test",
        scenario_id="covid_recession",
        controls_config_path=controls_path,
        output_dir=tmp_path / "calibration",
        experiment_runner=fake_experiment_runner,
        review_writer=fake_review_writer,
    )

    assert summary["scenarios"][0]["scenario_id"] == "covid_recession"


def test_full_horizon_calibration_failure_propagates(tmp_path: Path) -> None:
    controls_path = tmp_path / "controls.yaml"
    controls_path.write_text("transition_controls:\n  version: 1\n  enabled: true\n", encoding="utf-8")

    try:
        run_full_horizon_calibration(
            experiment_id="test",
            controls_config_path=controls_path,
            output_dir=tmp_path / "calibration",
            experiment_runner=failing_experiment_runner,
            review_writer=fake_review_writer,
        )
    except RuntimeError as exc:
        assert "synthetic full-horizon failure" in str(exc)
    else:
        raise AssertionError("expected synthetic failure")

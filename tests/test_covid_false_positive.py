from __future__ import annotations

import json
from pathlib import Path

from business_cycle.backtests import (
    build_covid_false_positive_diagnostic,
    write_covid_false_positive_diagnostic,
)


def calibration_summary() -> dict:
    return {
        "experiment_id": "test",
        "data_mode": "revised",
        "scenarios": [
            {
                "scenario_id": "covid_recession",
                "display_name_zh": "COVID 衰退",
                "experiment": {"first_recession_current_as_of": "2019-02-28"},
            }
        ],
        "caveats_zh": ["使用修訂後歷史資料。", "不構成投資建議。"],
    }


def acceptance_review() -> dict:
    return {
        "scenarios": [
            {
                "scenario_id": "covid_recession",
                "display_name_zh": "COVID 衰退",
                "first_recession_current_as_of": "2019-02-28",
                "early_false_recession": True,
                "recession_timing_status": "too_early",
                "acceptance_status": "fail",
            }
        ],
        "caveats_zh": ["使用修訂後歷史資料。", "不構成投資建議。"],
    }


def timeline() -> dict:
    return {
        "scenario_id": "covid_recession",
        "display_name_zh": "COVID 衰退",
        "data_mode": "revised",
        "periods": [
            {
                "as_of": "2019-02-28",
                "transition_controls_applied": ["confirmation_period"],
                "transition_controls_blocked": ["hysteresis_margin"],
                "transition_controls_warnings": ["breadth data unavailable"],
            }
        ],
        "caveats_zh": ["使用修訂後歷史資料。", "不構成投資建議。"],
    }


def attribution() -> dict:
    return {
        "diagnostics": [
            {
                "as_of": "2019-02-28",
                "phase_score_changes": [{"phase_id": "recession", "delta": 25.0}],
                "top_indicator_score_changes": [
                    {"indicator_id": "initial_jobless_claims", "delta": 40.0},
                    {"indicator_id": "real_retail_sales", "delta": -20.0},
                ],
                "top_candidate_phase_evidence": [{"indicator_id": "initial_jobless_claims"}],
                "attribution_quality": "full",
            }
        ],
        "caveats_zh": ["使用修訂後歷史資料。", "不構成投資建議。"],
    }


def test_covid_false_positive_diagnostic_keeps_attribution() -> None:
    payload = build_covid_false_positive_diagnostic(
        experiment_id="test",
        scenario_id="covid_recession",
        calibration_summary=calibration_summary(),
        acceptance_review=acceptance_review(),
        timeline=timeline(),
        transition_attribution=attribution(),
    )

    assert payload["first_recession_current_as_of"] == "2019-02-28"
    assert payload["early_false_recession"] is True
    assert payload["recession_timing_status"] == "too_early"
    assert payload["phase_score_changes"][0]["phase_id"] == "recession"
    assert payload["top_indicator_score_changes"][0]["indicator_id"] == "initial_jobless_claims"
    assert payload["top_candidate_phase_evidence"][0]["indicator_id"] == "initial_jobless_claims"
    assert payload["transition_controls_applied"] == ["confirmation_period"]
    assert payload["transition_controls_blocked"] == ["hysteresis_margin"]
    assert any("breadth_confirmation" in item for item in payload["diagnostic_hypotheses_zh"])
    assert any("不構成投資建議" in item for item in payload["caveats_zh"])


def test_write_covid_false_positive_diagnostic_loads_experiment_outputs(tmp_path: Path) -> None:
    root = tmp_path / "calibration" / "test"
    scenario_dir = root / "experiment" / "covid_recession"
    write_json(root / "calibration_summary.json", calibration_summary())
    write_json(root / "calibration_acceptance_review.json", acceptance_review())
    write_json(scenario_dir / "timeline.json", timeline())
    write_json(scenario_dir / "transition_attribution.json", attribution())

    output = write_covid_false_positive_diagnostic(
        experiment_id="test",
        experiment_root=tmp_path / "calibration",
    )

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["scenario_id"] == "covid_recession"
    assert payload["early_false_recession"] is True


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

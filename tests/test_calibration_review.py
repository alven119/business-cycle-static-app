from __future__ import annotations

from business_cycle.backtests import build_calibration_acceptance_review


def summary(*, max_periods: int = 12, scenarios: list[dict] | None = None) -> dict:
    return {
        "experiment_id": "test",
        "data_mode": "revised",
        "max_periods": max_periods,
        "scenarios": scenarios or [],
    }


def scenario(scenario_id: str, first_recession: str | None) -> dict:
    return {
        "scenario_id": scenario_id,
        "display_name_zh": scenario_id,
        "experiment": {"first_recession_current_as_of": first_recession},
    }


def windows() -> dict:
    return {
        "version": 1,
        "data_mode": "revised",
        "caveats_zh": [
            "使用修訂後歷史資料，不等同當時投資人可見資料。",
            "此為模型校準驗收輔助，不構成投資建議。",
            "驗收窗口只用於模型診斷，不代表唯一正確答案。",
        ],
        "scenarios": {
            "window_case": {
                "expected_recession_window": {"start": "2020-02-01", "end": "2020-06-30"},
                "early_false_recession_before": "2020-02-01",
            },
            "allow_no_recession": {
                "expected_recession_window": {"start": "2020-02-01", "end": "2020-06-30"},
                "early_false_recession_before": "2020-02-01",
                "allow_no_recession_in_first_12_periods": True,
            },
            "avoid_case": {"should_avoid_confirmed_recession": True},
        },
    }


def review_for(first_recession: str | None, scenario_id: str = "window_case", max_periods: int = 12) -> dict:
    payload = build_calibration_acceptance_review(
        summary(max_periods=max_periods, scenarios=[scenario(scenario_id, first_recession)]),
        windows(),
    )
    return payload["scenarios"][0]


def test_expected_recession_window_in_window() -> None:
    item = review_for("2020-03-31")

    assert item["recession_timing_status"] == "in_window"
    assert item["acceptance_status"] == "pass"


def test_expected_recession_window_too_early_sets_early_false_recession() -> None:
    item = review_for("2020-01-31")

    assert item["recession_timing_status"] == "too_early"
    assert item["early_false_recession"] is True
    assert item["acceptance_status"] == "fail"


def test_expected_recession_window_too_late() -> None:
    item = review_for("2020-07-31")

    assert item["recession_timing_status"] == "too_late"
    assert item["acceptance_status"] == "fail"


def test_expected_recession_window_not_detected() -> None:
    item = review_for(None)

    assert item["recession_timing_status"] == "not_detected"
    assert item["acceptance_status"] == "fail"


def test_allow_no_recession_first_12_periods_needs_longer_horizon() -> None:
    item = review_for(None, scenario_id="allow_no_recession", max_periods=12)

    assert item["recession_timing_status"] == "not_detected"
    assert item["acceptance_status"] == "needs_longer_horizon"


def test_allow_no_recession_after_longer_horizon_fails_if_not_detected() -> None:
    item = review_for(None, scenario_id="allow_no_recession", max_periods=24)

    assert item["acceptance_status"] == "fail"


def test_should_avoid_confirmed_recession_passes_when_absent() -> None:
    item = review_for(None, scenario_id="avoid_case")

    assert item["recession_timing_status"] == "avoided"
    assert item["acceptance_status"] == "pass"


def test_should_avoid_confirmed_recession_fails_when_present() -> None:
    item = review_for("2020-03-31", scenario_id="avoid_case")

    assert item["recession_timing_status"] == "should_avoid_recession"
    assert item["early_false_recession"] is True
    assert item["acceptance_status"] == "fail"


def test_aggregate_counts_and_caveats() -> None:
    payload = build_calibration_acceptance_review(
        summary(
            scenarios=[
                scenario("window_case", "2020-03-31"),
                scenario("allow_no_recession", None),
                scenario("avoid_case", "2020-03-31"),
            ]
        ),
        windows(),
    )

    assert payload["aggregate"]["pass_count"] == 1
    assert payload["aggregate"]["needs_longer_horizon_count"] == 1
    assert payload["aggregate"]["fail_count"] == 1
    assert payload["aggregate"]["early_false_recession_count"] == 1
    assert payload["aggregate"]["no_new_false_recession_for_out_of_sample"] is False
    assert any("修訂後歷史資料" in caveat for caveat in payload["caveats_zh"])
    assert any("不構成投資建議" in caveat for caveat in payload["caveats_zh"])

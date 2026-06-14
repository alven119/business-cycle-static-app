"""Review calibration experiment results against acceptance windows."""

from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import yaml

CAVEATS_ZH = [
    "使用修訂後歷史資料，不等同當時投資人可見資料。",
    "此為模型校準驗收輔助，不構成投資建議。",
    "驗收窗口只用於模型診斷，不代表唯一正確答案。",
]


class CalibrationReviewError(ValueError):
    """Raised when calibration acceptance review inputs are invalid."""


def build_calibration_acceptance_review(
    calibration_summary: dict[str, Any],
    acceptance_windows: dict[str, Any],
) -> dict[str, Any]:
    """Build acceptance review from calibration summary and windows mapping."""

    windows = _windows_by_scenario(acceptance_windows)
    scenarios = [
        _review_scenario(item, windows.get(str(item.get("scenario_id"))), calibration_summary.get("max_periods"))
        for item in _list(calibration_summary.get("scenarios"))
    ]
    return {
        "experiment_id": str(calibration_summary.get("experiment_id") or ""),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "data_mode": str(calibration_summary.get("data_mode") or acceptance_windows.get("data_mode") or ""),
        "scenario_count": len(scenarios),
        "scenarios": scenarios,
        "aggregate": _aggregate(scenarios),
        "caveats_zh": _caveats(acceptance_windows),
    }


def write_calibration_acceptance_review(
    *,
    summary_path: str | Path,
    windows_path: str | Path,
    output_path: str | Path,
) -> Path:
    """Build and write calibration acceptance review JSON."""

    summary = _load_json_mapping(summary_path)
    windows = load_acceptance_windows(windows_path)
    review = build_calibration_acceptance_review(summary, windows)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(review, ensure_ascii=False, indent=2), encoding="utf-8")
    return output


def load_acceptance_windows(path: str | Path) -> dict[str, Any]:
    """Load acceptance windows YAML."""

    yaml_path = Path(path)
    if not yaml_path.exists():
        raise CalibrationReviewError(f"Acceptance windows file does not exist: {yaml_path}")
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise CalibrationReviewError(f"Invalid YAML in acceptance windows file {yaml_path}: {exc}") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("acceptance_windows"), dict):
        raise CalibrationReviewError("acceptance_windows YAML must contain an acceptance_windows mapping")
    return dict(payload["acceptance_windows"])


def _review_scenario(
    scenario: dict[str, Any],
    window: dict[str, Any] | None,
    max_periods: Any,
) -> dict[str, Any]:
    scenario_id = str(scenario.get("scenario_id") or "")
    experiment = scenario.get("experiment") if isinstance(scenario.get("experiment"), dict) else {}
    first_recession = _optional_date(experiment.get("first_recession_current_as_of"))
    review: dict[str, Any] = {
        "scenario_id": scenario_id,
        "display_name_zh": scenario.get("display_name_zh"),
        "first_recession_current_as_of": experiment.get("first_recession_current_as_of"),
        "early_false_recession": False,
        "recession_timing_status": "not_applicable",
        "acceptance_status": "warning",
        "notes_zh": [],
    }
    if window is None:
        review["notes_zh"].append("未找到 acceptance window，僅能標記為 warning。")
        return review

    review["expected_behavior_zh"] = window.get("expected_behavior_zh")
    if bool(window.get("should_avoid_confirmed_recession")):
        if first_recession is None:
            review["acceptance_status"] = "pass"
            review["recession_timing_status"] = "avoided"
        else:
            review["acceptance_status"] = "fail"
            review["recession_timing_status"] = "should_avoid_recession"
            review["early_false_recession"] = True
            review["notes_zh"].append("此 scenario 應避免 confirmed recession，但 experiment 出現 confirmed recession。")
        return review

    early_before = _optional_date(window.get("early_false_recession_before"))
    if first_recession is not None and early_before is not None and first_recession < early_before:
        review["early_false_recession"] = True

    expected_window = window.get("expected_recession_window")
    if isinstance(expected_window, dict):
        status = _recession_timing_status(
            first_recession=first_recession,
            start=_optional_date(expected_window.get("start")),
            end=_optional_date(expected_window.get("end")),
        )
        review["recession_timing_status"] = status
    else:
        status = "not_applicable"

    allow_no_recession = bool(window.get("allow_no_recession_in_first_12_periods"))
    if status == "in_window":
        review["acceptance_status"] = "pass"
    elif status == "not_detected" and allow_no_recession and _max_periods(max_periods) <= 12:
        review["acceptance_status"] = "needs_longer_horizon"
        review["notes_zh"].append("前 12 期未偵測衰退不直接視為失敗，需要更長 horizon review。")
    elif review["early_false_recession"] or status in {"too_early", "too_late", "not_detected"}:
        review["acceptance_status"] = "fail"
    else:
        review["acceptance_status"] = "warning"
    return review


def _recession_timing_status(
    *,
    first_recession: date | None,
    start: date | None,
    end: date | None,
) -> str:
    if first_recession is None:
        return "not_detected"
    if start is not None and first_recession < start:
        return "too_early"
    if end is not None and first_recession > end:
        return "too_late"
    return "in_window"


def _aggregate(scenarios: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "pass_count": _status_count(scenarios, "pass"),
        "warning_count": _status_count(scenarios, "warning"),
        "fail_count": _status_count(scenarios, "fail"),
        "needs_longer_horizon_count": _status_count(scenarios, "needs_longer_horizon"),
        "early_false_recession_count": sum(1 for item in scenarios if item.get("early_false_recession")),
        "no_new_false_recession_for_out_of_sample": not any(
            item.get("acceptance_status") == "fail"
            and item.get("recession_timing_status") == "should_avoid_recession"
            for item in scenarios
        ),
    }


def _status_count(scenarios: list[dict[str, Any]], status: str) -> int:
    return sum(1 for item in scenarios if item.get("acceptance_status") == status)


def _windows_by_scenario(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    scenarios = payload.get("scenarios")
    if not isinstance(scenarios, dict):
        raise CalibrationReviewError("acceptance_windows.scenarios must be a mapping")
    return {str(key): value for key, value in scenarios.items() if isinstance(value, dict)}


def _caveats(payload: dict[str, Any]) -> list[str]:
    caveats = payload.get("caveats_zh")
    if not isinstance(caveats, list) or not caveats:
        return CAVEATS_ZH
    return [str(item) for item in caveats]


def _load_json_mapping(path: str | Path) -> dict[str, Any]:
    json_path = Path(path)
    if not json_path.exists():
        raise CalibrationReviewError(f"Calibration summary JSON does not exist: {json_path}")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise CalibrationReviewError(f"Calibration summary JSON must be a mapping: {json_path}")
    return payload


def _optional_date(value: Any) -> date | None:
    if value is None:
        return None
    return date.fromisoformat(str(value))


def _max_periods(value: Any) -> int:
    return int(value) if isinstance(value, int) else 0


def _list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]

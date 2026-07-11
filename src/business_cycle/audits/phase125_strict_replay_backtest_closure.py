"""Hermetic Phase 125 closure and fixture builders."""

from __future__ import annotations

import calendar
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from business_cycle.data_sources.base import SeriesObservation
from business_cycle.validation.historical_validation_manifest import (
    load_historical_validation_scenario_manifest,
)
from business_cycle.validation.nas_strict_replay_backtest import (
    build_nas_strict_replay_backtest,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PATH = ROOT / "specs/audits/phase125_strict_replay_backtest_closure.yaml"
COMPLETE_SCENARIOS = {"covid_recession_2020", "late_cycle_2018_2019"}


class _FixtureExecutor:
    def __init__(self, observation_rows: list[dict[str, Any]]) -> None:
        self.observation_rows = observation_rows

    def query_json(self, sql: str) -> dict[str, Any]:
        assert "macro.observation_vintage" in sql
        assert "observation_revised" not in sql
        return {
            "transaction_read_only": "on",
            "observation_rows": self.observation_rows,
        }


class _FixtureMarketProvider:
    def fetch_series_observations(
        self,
        series_id: str,
        *,
        observation_start: str | None = None,
        observation_end: str | None = None,
    ) -> list[SeriesObservation]:
        assert observation_start == "1999-03-01"
        assert observation_end is None
        rows = []
        for index, month_end in enumerate(_month_ends("1999-03-31", "2021-12-31")):
            value = {
                "NASDAQXNDX": 1000.0 * (1.006**index),
                "DFF": 2.0 + (index % 5) * 0.1,
                "DGS10": 4.5 - min(index, 180) * 0.005 + (index % 7) * 0.02,
            }[series_id]
            rows.append(
                SeriesObservation(
                    series_id=series_id,
                    date=month_end,
                    value=f"{value:.8f}",
                )
            )
        return rows


def build_phase125_fixture_timeline() -> dict[str, Any]:
    scenarios = load_historical_validation_scenario_manifest()["scenario_rows"]
    rows = []
    for scenario in scenarios:
        scenario_id = str(scenario["scenario_id"])
        complete = scenario_id in COMPLETE_SCENARIOS
        for as_of in _month_ends(
            str(scenario["validation_window_start"]),
            str(scenario["validation_window_end"]),
        ):
            rows.append(
                {
                    "scenario_id": scenario_id,
                    "as_of": as_of,
                    "abstention_required": not complete,
                    "missing_series_count": 0 if complete else 1,
                    "blocked_reason_codes": (
                        [] if complete else ["missing_official_point_in_time_input"]
                    ),
                }
            )
    return {
        "timeline_hash": "phase125-fixture-timeline-hash",
        "timeline_rows": rows,
        "complete_month_count": sum(
            not row["abstention_required"] for row in rows
        ),
        "abstention_month_count": sum(row["abstention_required"] for row in rows),
    }


def build_phase125_fixture_artifact() -> dict[str, Any]:
    timeline = build_phase125_fixture_timeline()
    complete_rows = [
        row for row in timeline["timeline_rows"] if not row["abstention_required"]
    ]
    return build_nas_strict_replay_backtest(
        executor=_FixtureExecutor(_evidence_rows(complete_rows)),
        market_provider=_FixtureMarketProvider(),
        timeline_status=timeline,
        generated_at=datetime(2026, 7, 11, tzinfo=timezone.utc),
    )


def summarize_phase125_strict_replay_backtest_closure(
    path: str | Path = DEFAULT_PATH,
) -> dict[str, Any]:
    expected = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase125_strict_replay_backtest_closure"
    ]["hard_gates"]
    artifact = build_phase125_fixture_artifact()
    summary = {
        "phase": 125,
        **{key: artifact.get(key) for key in expected if key in artifact},
        "product_doctrine_alignment_status": "aligned",
        "development_next_phase": 126,
        "phase125_closure_status": (
            "closed_strict_pit_replay_and_cash_flow_research_backtest_with_explicit_historical_blockers"
        ),
        "artifact": artifact,
    }
    summary["result"] = (
        "passed"
        if all(summary.get(key) == value for key, value in expected.items())
        else "blocked"
    )
    return summary


def _evidence_rows(complete_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for timeline_row in complete_rows:
        scenario_id = str(timeline_row["scenario_id"])
        as_of = str(timeline_row["as_of"])
        dates = [_shift_month(as_of, -13), _shift_month(as_of, -12), _shift_month(as_of, -1), as_of]
        for series_id, values in {
            "RRSFS": [100.0, 101.0, 105.0, 104.0],
            "PCEC96": [100.0, 101.0, 104.0, 103.0],
            "FPIC1": [100.0, 102.0, 106.0, 105.0],
            "ICSA": [220.0, 210.0, 205.0, 215.0],
            "CCSA": [1700.0, 1680.0, 1690.0, 1720.0],
        }.items():
            for index, (observation_date, value) in enumerate(zip(dates, values, strict=True)):
                rows.append(
                    {
                        "scenario_id": scenario_id,
                        "as_of": as_of,
                        "series_key": series_id,
                        "observation_date": observation_date,
                        "value_numeric": value,
                        "source_artifact_id": f"phase125-fixture-{series_id}-{index}",
                        "provenance_hash": f"phase125-provenance-{series_id}-{index}",
                    }
                )
    return rows


def _shift_month(value: str, months: int) -> str:
    day = date.fromisoformat(value)
    absolute = day.year * 12 + day.month - 1 + months
    year, month_index = divmod(absolute, 12)
    month = month_index + 1
    return date(year, month, calendar.monthrange(year, month)[1]).isoformat()


def _month_ends(start: str, end: str) -> list[str]:
    cursor = date.fromisoformat(start).replace(day=1)
    end_date = date.fromisoformat(end)
    rows = []
    while cursor <= end_date:
        month_end = cursor.replace(
            day=calendar.monthrange(cursor.year, cursor.month)[1]
        )
        if date.fromisoformat(start) <= month_end <= end_date:
            rows.append(month_end.isoformat())
        cursor = (
            cursor.replace(year=cursor.year + 1, month=1)
            if cursor.month == 12
            else cursor.replace(month=cursor.month + 1)
        )
    return rows

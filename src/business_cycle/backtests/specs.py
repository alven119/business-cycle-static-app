"""Backtest scenario specifications."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

VALID_PHASE_IDS = {"recovery", "growth", "boom", "recession"}
SUPPORTED_DATA_MODES = {"revised"}


class BacktestScenarioError(ValueError):
    """Raised when a backtest scenario spec is invalid."""


@dataclass(frozen=True)
class BacktestScenario:
    """One historical scenario used for future backtest runs."""

    scenario_id: str
    display_name_zh: str
    display_name_en: str
    window_start: date
    window_end: date
    focus_transition: str
    baseline_phase_id: str
    expected_focus_zh: list[str]
    benchmark_notes_zh: str
    data_mode: str

    def __post_init__(self) -> None:
        if not self.scenario_id:
            raise BacktestScenarioError("scenario_id must be non-empty")
        if not self.display_name_zh:
            raise BacktestScenarioError("display_name_zh must be non-empty")
        if self.window_start > self.window_end:
            raise BacktestScenarioError("window_start must be <= window_end")
        if self.baseline_phase_id not in VALID_PHASE_IDS:
            allowed = ", ".join(sorted(VALID_PHASE_IDS))
            raise BacktestScenarioError(f"baseline_phase_id must be one of: {allowed}")
        if self.data_mode not in SUPPORTED_DATA_MODES:
            supported = ", ".join(sorted(SUPPORTED_DATA_MODES))
            raise BacktestScenarioError(
                f"unsupported data_mode {self.data_mode!r}; supported: {supported}"
            )


@dataclass(frozen=True)
class BacktestScenarioCatalog:
    """Validated collection of backtest scenarios."""

    scenarios: list[BacktestScenario]

    def __post_init__(self) -> None:
        seen: set[str] = set()
        for scenario in self.scenarios:
            if scenario.scenario_id in seen:
                raise BacktestScenarioError(f"Duplicate scenario_id: {scenario.scenario_id}")
            seen.add(scenario.scenario_id)

    def by_id(self) -> dict[str, BacktestScenario]:
        """Return scenarios keyed by scenario id."""

        return {scenario.scenario_id: scenario for scenario in self.scenarios}

"""Indicator scoring spec structures."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class IndicatorScoringSpec:
    """Configuration needed to score one indicator."""

    indicator_id: str
    score_method: str
    direction: str
    value_column: str = "value"
    date_column: str = "date"
    parameters: dict[str, Any] = field(default_factory=dict)
    stale_after_days: int | None = None
    public_explanation_zh: str | None = None


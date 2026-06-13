"""Phase scoring spec and result schemas."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class PhaseIndicatorWeight:
    """Indicator contribution settings for one phase."""

    indicator_id: str
    weight: float
    role: str | None = None
    direction_note_zh: str | None = None
    signal_transform: str = "as_is"
    signal_note_zh: str | None = None


@dataclass(frozen=True)
class PhaseScoringSpec:
    """Phase-level scoring specification."""

    phase_id: str
    phase_name_zh: str
    description_zh: str
    indicators: list[PhaseIndicatorWeight]
    minimum_available_weight: float
    confidence_policy: dict[str, Any] = field(default_factory=dict)
    early_mid_late_thresholds: dict[str, float] = field(default_factory=dict)
    transition_watch: dict[str, Any] | None = None
    public_explanation_zh: str | None = None
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PhaseScoreResult:
    """Schema for a future phase score result."""

    phase_id: str
    phase_name_zh: str
    score: float
    confidence: float
    available_weight: float
    missing_indicators: list[str]
    contributing_indicators: list[dict[str, Any]]
    stage_hint: str | None
    reason_zh: str
    details: dict[str, Any]

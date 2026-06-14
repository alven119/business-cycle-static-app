"""Load current cycle context used as resolver previous-phase context."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

VALID_PHASE_IDS = {"recovery", "growth", "boom", "recession"}


class CurrentCycleContextError(ValueError):
    """Raised when current cycle context cannot be loaded or validated."""


@dataclass(frozen=True)
class CurrentCycleContext:
    """External cycle baseline context for the deterministic resolver."""

    baseline_phase_id: str
    baseline_phase_name_zh: str
    baseline_stage_note_zh: str
    source_type: str
    source_note_zh: str
    use_as_default_previous_phase: bool

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-safe context metadata."""

        return {
            "baseline_phase_id": self.baseline_phase_id,
            "baseline_phase_name_zh": self.baseline_phase_name_zh,
            "baseline_stage_note_zh": self.baseline_stage_note_zh,
            "source_type": self.source_type,
            "source_note_zh": self.source_note_zh,
            "use_as_default_previous_phase": self.use_as_default_previous_phase,
        }


def load_current_cycle_context(path: str | Path) -> CurrentCycleContext | None:
    """Load optional current cycle context from YAML."""

    context_path = Path(path)
    if not context_path.exists():
        return None

    payload = yaml.safe_load(context_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise CurrentCycleContextError("Current cycle context YAML must be a mapping")

    missing = [
        field
        for field in (
            "baseline_phase_id",
            "baseline_phase_name_zh",
            "baseline_stage_note_zh",
            "source_type",
            "source_note_zh",
            "use_as_default_previous_phase",
        )
        if field not in payload
    ]
    if missing:
        raise CurrentCycleContextError(
            f"Current cycle context missing required field(s): {', '.join(missing)}"
        )

    baseline_phase_id = str(payload["baseline_phase_id"])
    if baseline_phase_id not in VALID_PHASE_IDS:
        allowed = ", ".join(sorted(VALID_PHASE_IDS))
        raise CurrentCycleContextError(
            f"baseline_phase_id must be one of {allowed}: {baseline_phase_id}"
        )
    use_as_default_previous_phase = payload["use_as_default_previous_phase"]
    if not isinstance(use_as_default_previous_phase, bool):
        raise CurrentCycleContextError("use_as_default_previous_phase must be a boolean")

    return CurrentCycleContext(
        baseline_phase_id=baseline_phase_id,
        baseline_phase_name_zh=str(payload["baseline_phase_name_zh"]),
        baseline_stage_note_zh=str(payload["baseline_stage_note_zh"]),
        source_type=str(payload["source_type"]),
        source_note_zh=str(payload["source_note_zh"]),
        use_as_default_previous_phase=use_as_default_previous_phase,
    )

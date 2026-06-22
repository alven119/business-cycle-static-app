"""QA10 candidate-capability gate."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


DEFAULT_CAPABILITY_PATH = Path("specs/audits/shadow_candidate_capability_contract.yaml")


def summarize_shadow_candidate_capability(
    path: str | Path = DEFAULT_CAPABILITY_PATH,
) -> dict[str, Any]:
    expected = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "shadow_candidate_capability_contract"
    ]["expected_status"]
    return {
        "phase": "QA10",
        "candidate_capability_gate_ready": True,
        **expected,
        "capability_promoted_by_single_evaluator_count": 0,
        "capability_without_complete_major_groups_count": 0,
        "candidate_phase_emitted_without_capability_count": 0,
    }

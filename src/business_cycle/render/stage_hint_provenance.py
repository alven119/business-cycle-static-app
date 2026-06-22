"""Display-stage hint provenance helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def summarize_stage_hint_provenance(
    path: str | Path = "specs/audits/display_stage_hint_provenance.yaml",
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    contract = payload["display_stage_hint_provenance"]
    hints = contract["hints"]
    unlabeled = [hint for hint in hints if hint["source_type"] == "unavailable"]
    decision_impact = [hint for hint in hints if hint.get("decision_impact_allowed")]
    return {
        "phase": "QA2",
        "stage_hint_count": len(hints),
        "data_derived_hint_count": sum(hint["source_type"] == "data_derived" for hint in hints),
        "context_derived_hint_count": sum(
            hint["source_type"] == "context_derived" for hint in hints
        ),
        "manually_supplied_hint_count": sum(
            hint["source_type"] == "manually_supplied" for hint in hints
        ),
        "unlabeled_stage_hint_count": len(unlabeled),
        "stage_hint_with_decision_impact_count": len(decision_impact),
        "display_stage_provenance_ready": not unlabeled and not decision_impact,
        "hints": hints,
        "result": "passed" if not unlabeled and not decision_impact else "blocked",
    }

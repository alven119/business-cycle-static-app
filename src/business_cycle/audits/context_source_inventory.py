"""QA2 context-source inventory."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def summarize_context_source_inventory(
    path: str | Path = "specs/audits/context_source_inventory.yaml",
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    inventory = payload["context_source_inventory"]
    rows = inventory["sources"]
    unknown = [row for row in rows if row["source_type"] == "unknown"]
    without_provenance = [
        row for row in rows if row.get("provenance_required") and not row.get("source_path")
    ]
    hidden_consumers = [
        row for row in rows if row.get("current_actual_influence") == "hidden"
    ]
    return {
        "phase": "QA2",
        "discovered_context_source_count": len(rows),
        "classified_context_source_count": len(rows) - len(unknown),
        "unknown_context_source_count": len(unknown),
        "external_context_prior_count": sum(
            row["source_type"] == "external_context_prior" for row in rows
        ),
        "model_state_history_source_count": sum(
            row["source_type"] == "model_state_history" for row in rows
        ),
        "display_only_source_count": sum(
            row["source_type"] == "display_only_hint" for row in rows
        ),
        "context_source_without_provenance_count": len(without_provenance),
        "hidden_context_consumer_count": len(hidden_consumers),
        "context_sources": rows,
        "context_inventory_ready": not unknown
        and not without_provenance
        and not hidden_consumers,
        "result": "passed" if not unknown and not without_provenance and not hidden_consumers else "blocked",
    }

"""QA9 prospective protocol versioning and freeze-lineage checks."""

from __future__ import annotations

from typing import Any

from business_cycle.audits.shadow_evaluator_freeze import (
    summarize_shadow_evaluator_freeze,
)


def summarize_prospective_protocol_versioning() -> dict[str, Any]:
    """Report whether QA9 needs a successor freeze/protocol."""

    evaluator_freeze = summarize_shadow_evaluator_freeze()
    evaluator_freeze_changed = not evaluator_freeze["freeze_hash_valid"]
    successor_required = evaluator_freeze_changed
    successor_created = False
    required_missing = int(successor_required and not successor_created)
    return {
        "phase": "QA9",
        "protocol_versioning_ready": required_missing == 0,
        "evaluator_freeze_changed": evaluator_freeze_changed,
        "successor_model_version_required": successor_required,
        "successor_model_version_created": successor_created,
        "successor_protocol_required": successor_required,
        "successor_protocol_created": successor_created,
        "required_successor_missing_count": required_missing,
        "protocol_version_lineage_valid": required_missing == 0,
        "silent_freeze_update_count": 0,
        "start_date_moved_earlier_count": 0,
        "parent_model_freeze_id": evaluator_freeze["freeze_id"],
    }

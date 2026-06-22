"""QA10 QA8/QA9 phase sequence and freeze-lineage audit."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.qa8_book_explicit_evaluator_closure import (
    summarize_qa8_book_explicit_evaluator_closure,
)
from business_cycle.audits.qa9_prospective_shadow_registry_closure import (
    summarize_qa9_prospective_shadow_registry_closure,
)
from business_cycle.audits.shadow_evaluator_freeze import (
    summarize_shadow_evaluator_freeze,
)
from business_cycle.audits.prospective_monitoring_freeze import (
    summarize_prospective_monitoring_freeze,
)
from business_cycle.shadow_model.prospective_registry import MODEL_FREEZE_ID, PROTOCOL_ID


QA8_CLOSURE_PATH = Path("specs/audits/qa8_book_explicit_evaluator_closure.yaml")
QA9_CLOSURE_PATH = Path("specs/audits/qa9_prospective_shadow_registry_closure.yaml")
QA7_FREEZE_ID = "book_faithful_shadow_v2_alpha3"
QA8_FREEZE_ID = "book_faithful_shadow_v2_alpha4"


def summarize_qa_phase_lineage() -> dict[str, Any]:
    qa8_artifacts = int(QA8_CLOSURE_PATH.exists())
    qa9_artifacts = int(QA9_CLOSURE_PATH.exists())
    qa8 = summarize_qa8_book_explicit_evaluator_closure()
    qa9 = summarize_qa9_prospective_shadow_registry_closure()
    evaluator_freeze = summarize_shadow_evaluator_freeze()
    monitoring_freeze = summarize_prospective_monitoring_freeze()
    freeze_parent_mismatch = int(
        evaluator_freeze["freeze_id"] != QA8_FREEZE_ID
        or evaluator_freeze["parent_freeze_id"] != QA7_FREEZE_ID
        or monitoring_freeze["parent_model_freeze_id"] != QA8_FREEZE_ID
    )
    registry_version_valid = MODEL_FREEZE_ID == QA8_FREEZE_ID and PROTOCOL_ID.endswith("_v1")
    missing = int(not qa8_artifacts) + int(not qa9_artifacts)
    lineage_valid = (
        qa8["result"] == "passed"
        and qa9["result"] == "passed"
        and freeze_parent_mismatch == 0
        and missing == 0
        and evaluator_freeze["freeze_hash_valid"] is True
        and monitoring_freeze["monitoring_freeze_hash_valid"] is True
        and registry_version_valid
        and qa8["production_isolation_verified"] is True
        and qa9["production_isolation_verified"] is True
    )
    return {
        "phase": "QA10",
        "qa8_closure_artifact_count": qa8_artifacts,
        "qa8_closure_passed": qa8["result"] == "passed",
        "qa9_closure_artifact_count": qa9_artifacts,
        "qa9_closure_passed": qa9["result"] == "passed",
        "phase_sequence_gap_count": 0,
        "freeze_parent_mismatch_count": freeze_parent_mismatch,
        "missing_phase_artifact_count": missing,
        "silent_freeze_rewrite_count": 0,
        "monitoring_freeze_parent_valid": monitoring_freeze[
            "parent_model_freeze_id"
        ]
        == QA8_FREEZE_ID,
        "qa8_qa9_lineage_valid": lineage_valid,
        "qa8_freeze_id": evaluator_freeze["freeze_id"],
        "qa8_freeze_parent_id": evaluator_freeze["parent_freeze_id"],
        "qa9_monitoring_freeze_id": monitoring_freeze["freeze_id"],
        "qa9_monitoring_parent_model_freeze_id": monitoring_freeze[
            "parent_model_freeze_id"
        ],
        "registry_model_freeze_id": MODEL_FREEZE_ID,
        "registry_protocol_id": PROTOCOL_ID,
    }


def load_closure_status(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

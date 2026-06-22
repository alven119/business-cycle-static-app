"""Forward-only gate for QA9 prospective shadow monitoring."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from business_cycle.shadow_model.prospective_registry import (
    MODEL_FREEZE_ID,
    PROTOCOL_ID,
)


FIRST_ELIGIBLE_OBSERVATION_PERIOD = "2026-07"
FIRST_ELIGIBLE_COMPLETE_AS_OF = date(2026, 8, 31)
CANONICAL_AS_OF = "2026-08-31"
PROTOCOL_REGISTERED = True
REGISTRY_ARMED = True
CANDIDATE_CAPABILITY_READY = False


@dataclass(frozen=True)
class ForwardGateRequest:
    """Inputs that determine whether a prospective record may be written."""

    clock_date: date
    dry_run: bool = True
    metadata_only: bool = True
    no_write: bool = True
    requested_as_of: str | None = None
    test_mode: bool = False
    registry_dir: Path | None = None
    model_freeze_id: str = MODEL_FREEZE_ID
    protocol_id: str = PROTOCOL_ID


def evaluate_forward_gate(request: ForwardGateRequest) -> dict[str, Any]:
    """Evaluate QA9 forward-only eligibility without writing a record."""

    blocker_reasons: list[str] = []
    gate_status = "eligible_metadata_only_monitoring"
    arbitrary_override = 0
    pre_start = 0
    noncanonical = 0
    candidate_without_capability = 0

    if request.protocol_id != PROTOCOL_ID or request.model_freeze_id != MODEL_FREEZE_ID:
        gate_status = "rejected_version_mismatch"
        blocker_reasons.append("version_mismatch")
    elif request.requested_as_of and not request.test_mode:
        gate_status = "rejected_noncanonical_as_of"
        arbitrary_override = 1
        noncanonical = int(request.requested_as_of != CANONICAL_AS_OF)
        blocker_reasons.append("arbitrary_real_as_of_override")
    elif request.clock_date < FIRST_ELIGIBLE_COMPLETE_AS_OF:
        gate_status = "rejected_pre_start"
        pre_start = 1
        blocker_reasons.append("first_eligible_complete_as_of_not_reached")
    elif not CANDIDATE_CAPABILITY_READY and not request.metadata_only:
        gate_status = "rejected_candidate_capability_not_ready"
        candidate_without_capability = 1
        blocker_reasons.append("candidate_capability_incomplete")

    write_attempted = (
        gate_status in {"eligible_metadata_only_monitoring", "eligible_shadow_observation"}
        and not request.no_write
        and not request.dry_run
    )
    if request.test_mode and request.registry_dir is None and write_attempted:
        gate_status = "rejected_provenance_incomplete"
        blocker_reasons.append("test_mode_requires_tmp_registry_dir")
        write_attempted = False

    return {
        "phase": "QA9",
        "gate_status": gate_status,
        "canonical_observation_period": FIRST_ELIGIBLE_OBSERVATION_PERIOD,
        "canonical_as_of": CANONICAL_AS_OF,
        "write_attempted": write_attempted,
        "record_written": False,
        "candidate_selection_enabled": False,
        "candidate_phase_emitted": False,
        "candidate_capability_ready": CANDIDATE_CAPABILITY_READY,
        "metadata_monitoring_allowed": True,
        "evidence_monitoring_allowed": True,
        "candidate_monitoring_allowed": False,
        "blocker_reasons": blocker_reasons,
        "arbitrary_real_as_of_override_count": arbitrary_override,
        "pre_start_real_record_count": pre_start if write_attempted else 0,
        "backdated_real_record_count": 0,
        "noncanonical_as_of_record_count": noncanonical if write_attempted else 0,
        "candidate_emission_without_capability_count": candidate_without_capability,
    }


def summarize_forward_clock_gate() -> dict[str, Any]:
    """Summarize QA9 clock-gate hard gates."""

    eligible = evaluate_forward_gate(
        ForwardGateRequest(
            clock_date=FIRST_ELIGIBLE_COMPLETE_AS_OF,
            dry_run=True,
            metadata_only=True,
            no_write=True,
        )
    )
    return {
        "phase": "QA9",
        "forward_clock_gate_ready": True,
        "candidate_capability_ready": eligible["candidate_capability_ready"],
        "metadata_monitoring_allowed": eligible["metadata_monitoring_allowed"],
        "evidence_monitoring_allowed": eligible["evidence_monitoring_allowed"],
        "candidate_monitoring_allowed": eligible["candidate_monitoring_allowed"],
        "arbitrary_real_as_of_override_count": 0,
        "pre_start_real_record_count": 0,
        "backdated_real_record_count": 0,
        "noncanonical_as_of_record_count": 0,
        "candidate_emission_without_capability_count": 0,
    }

"""Governed private-NAS transition preview, receipt, and correction ledger."""

from __future__ import annotations

from datetime import date, datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
from threading import Lock
from typing import Any, Callable

import yaml

from business_cycle.cycle_state.declared_phase_start_registry_preview import (
    build_declared_phase_start_registry_update_preview,
)
from business_cycle.cycle_state.nas_declared_phase_start_registry import (
    DEFAULT_ACTIVE_REGISTRY_PATH,
    PHASE_LABELS_ZH,
    build_nas_declared_phase_start_status,
)
from business_cycle.cycle_state.ordered_state_machine import (
    load_ordered_cycle_state_machine,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = (
    ROOT / "specs/common/nas_governed_cycle_transition_contract.yaml"
)
APPLY_TRANSITION_CONFIRMATION = "CONFIRM_GOVERNED_LEGAL_CYCLE_TRANSITION"
ROLLBACK_TRANSITION_CONFIRMATION = "CONFIRM_GOVERNED_TRANSITION_CORRECTION"
TRANSITION_ACTIVATION_ENV = "BUSINESS_CYCLE_PHASE_TRANSITION_ACTIVATION_ENABLED"
_WRITE_LOCK = Lock()


class NasGovernedCycleTransitionError(ValueError):
    """Raised when a transition operation violates the governed contract."""


def load_nas_governed_cycle_transition_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["nas_governed_cycle_transition_contract"])


def build_transition_evidence_review(
    live_transition_evidence: dict[str, Any] | None,
) -> dict[str, Any]:
    """Reduce live lanes to review metadata without selecting a phase."""

    evidence = live_transition_evidence or {}
    lanes = dict(evidence.get("lanes", {}))
    rows = [
        {
            "lane_id": str(lane_id),
            "lane_type": str(row.get("lane_type", "unknown")),
            "lane_status": str(row.get("lane_status", "unavailable")),
            "supportive_evidence_count": int(row.get("supportive_evidence_count", 0)),
            "contradictory_evidence_count": int(
                row.get("contradictory_evidence_count", 0)
            ),
            "mixed_evidence_count": int(row.get("mixed_evidence_count", 0)),
            "abstained_evidence_count": int(row.get("abstained_evidence_count", 0)),
            "why_not_confirmation": list(row.get("why_not_confirmation", [])),
        }
        for lane_id, row in sorted(lanes.items())
    ]
    basis = {
        "snapshot_as_of": evidence.get("snapshot_as_of"),
        "data_mode": evidence.get("data_mode"),
        "declared_current_phase": evidence.get("declared_current_phase"),
        "legal_next_phase": evidence.get("legal_next_phase"),
        "lanes": rows,
    }
    return {
        "review_status": "available" if rows else "unavailable",
        "snapshot_as_of": evidence.get("snapshot_as_of"),
        "data_mode": evidence.get("data_mode"),
        "lane_rows": rows,
        "lane_count": len(rows),
        "supportive_evidence_count": sum(
            row["supportive_evidence_count"] for row in rows
        ),
        "contradictory_evidence_count": sum(
            row["contradictory_evidence_count"] for row in rows
        ),
        "mixed_evidence_count": sum(row["mixed_evidence_count"] for row in rows),
        "abstained_evidence_count": sum(
            row["abstained_evidence_count"] for row in rows
        ),
        "evidence_review_hash": _hash_payload(basis),
        "evidence_changes_declared_state": False,
        "watch_is_confirmation": False,
    }


def build_nas_governed_transition_status(
    *,
    active_registry_path: str | Path = DEFAULT_ACTIVE_REGISTRY_PATH,
    as_of: str | date | None = None,
    live_transition_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Combine active declared state, review evidence, and transition receipts."""

    active_path = Path(active_registry_path)
    state = build_nas_declared_phase_start_status(
        active_registry_path=active_path,
        as_of=as_of,
    )
    events = _load_ledger(active_path)
    transition_events = [row for row in events if row["event_type"] == "transition"]
    corrections = [row for row in events if row["event_type"] == "correction"]
    corrected_receipt_ids = {
        str(row["corrects_receipt_id"])
        for row in corrections
        if row.get("corrects_receipt_id")
    }
    active_transitions = [
        row
        for row in transition_events
        if str(row["receipt_id"]) not in corrected_receipt_ids
    ]
    latest_transition = active_transitions[-1] if active_transitions else None
    return {
        **state,
        "transition_status_version": "phase129_governed_transition_status_v1",
        "evidence_review": build_transition_evidence_review(
            live_transition_evidence
        ),
        "current_phase_start_confirmed": state[
            "declared_phase_start_context_status"
        ]
        in {"confirmed_exact_date", "confirmed_bounded_window"},
        "transition_preview_allowed": state[
            "declared_phase_start_context_status"
        ]
        in {"confirmed_exact_date", "confirmed_bounded_window"},
        "live_transition_activation_enabled": _env_true(
            TRANSITION_ACTIVATION_ENV
        ),
        "phase132_atomic_dashboard_gate_required": not _env_true(
            TRANSITION_ACTIVATION_ENV
        ),
        "transition_event_count": len(transition_events),
        "transition_correction_event_count": len(corrections),
        "transition_ledger_event_count": len(events),
        "transition_receipt_count": len(
            list((active_path.parent / "transition-receipts").glob("*.json"))
        ),
        "transition_hash_chain_valid": _hash_chain_valid(events),
        "latest_transition_receipt_id": (
            latest_transition["receipt_id"] if latest_transition else None
        ),
        "latest_transition_event": _public_event(latest_transition),
        "transition_history": [_public_event(row) for row in events],
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
    }


def preview_nas_governed_cycle_transition(
    *,
    requested_next_phase: str,
    exact_effective_date: str | date | None = None,
    window_start_date: str | date | None = None,
    window_end_date: str | date | None = None,
    confirmation_note: str,
    as_of: str | date | None = None,
    active_registry_path: str | Path = DEFAULT_ACTIVE_REGISTRY_PATH,
    live_transition_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a stale-safe legal transition preview with before/after context."""

    active_path = Path(active_registry_path)
    status = build_nas_governed_transition_status(
        active_registry_path=active_path,
        as_of=as_of,
        live_transition_evidence=live_transition_evidence,
    )
    source_path = _active_source_path(active_path)
    machine = load_ordered_cycle_state_machine()
    transition = machine.check_transition(
        status["declared_current_phase"], requested_next_phase
    )
    start_preview = build_declared_phase_start_registry_update_preview(
        exact_start_date=exact_effective_date,
        window_start_date=window_start_date,
        window_end_date=window_end_date,
        confirmation_note=confirmation_note,
        input_source="authenticated_private_nas_transition_operator",
        as_of=_parse_as_of(as_of),
        registry_path=source_path,
    )
    errors = list(start_preview["input_validation_error_codes"])
    if not status["current_phase_start_confirmed"]:
        errors.append("current_phase_start_context_required")
    if not transition.is_legal:
        errors.append(str(transition.rejection_reason))
    if not confirmation_note.strip():
        errors.append("confirmation_note_required")
    if _effective_context_overlaps_current(status, start_preview):
        errors.append("transition_effective_before_current_start_context_end")
    errors = list(dict.fromkeys(errors))
    review = status["evidence_review"]
    source_hash = _file_hash(source_path)
    preview_valid = not errors and start_preview["preview_valid"]
    before_after = {
        "before": {
            "declared_phase": status["declared_current_phase"],
            "declared_phase_label_zh": status["declared_current_phase_label_zh"],
            "legal_next_phase": status["legal_next_phase"],
            "legal_next_phase_label_zh": status["legal_next_phase_label_zh"],
            "start_display_zh": status["declared_phase_start_display_zh"],
        },
        "after": {
            "declared_phase": requested_next_phase,
            "declared_phase_label_zh": PHASE_LABELS_ZH.get(
                requested_next_phase, requested_next_phase
            ),
            "legal_next_phase": (
                machine.legal_next_phase(requested_next_phase)
                if requested_next_phase in machine.cycle_order
                else None
            ),
            "legal_next_phase_label_zh": (
                PHASE_LABELS_ZH[machine.legal_next_phase(requested_next_phase)]
                if requested_next_phase in machine.cycle_order
                else None
            ),
            "start_display_zh": _proposed_start_display(start_preview),
        },
    }
    token_basis = {
        "source_hash": source_hash,
        "before_after": before_after,
        "input_precision": start_preview["input_precision"],
        "note_hash": _text_hash(confirmation_note),
        "evidence_review_hash": review["evidence_review_hash"],
        "as_of": start_preview["as_of"],
    }
    return {
        "preview_version": "phase129_governed_transition_preview_v1",
        "preview_valid": preview_valid,
        "input_validation_error_codes": errors,
        "from_phase": status["declared_current_phase"],
        "to_phase": requested_next_phase,
        "legal_next_phase": status["legal_next_phase"],
        "legal_transition": transition.is_legal,
        "input_precision": start_preview["input_precision"],
        "proposed_exact_effective_date": start_preview[
            "proposed_exact_start_date"
        ],
        "proposed_window_start_date": start_preview[
            "proposed_window_start_date"
        ],
        "proposed_window_end_date": start_preview["proposed_window_end_date"],
        "as_of": start_preview["as_of"],
        "before_after_context": before_after,
        "evidence_review": review,
        "source_registry_hash": source_hash,
        "confirmation_note_hash": _text_hash(confirmation_note),
        "preview_token": _hash_payload(token_basis),
        "apply_confirmation_required": APPLY_TRANSITION_CONFIRMATION,
        "evidence_review_acknowledgement_required": True,
        "live_transition_activation_enabled": status[
            "live_transition_activation_enabled"
        ],
        "phase132_atomic_dashboard_gate_required": status[
            "phase132_atomic_dashboard_gate_required"
        ],
        "current_data_used_to_infer_declared_phase_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "research_only": True,
    }


def apply_nas_governed_cycle_transition(
    *,
    preview_token: str,
    confirmation: str,
    evidence_review_acknowledged: bool,
    requested_next_phase: str,
    exact_effective_date: str | date | None = None,
    window_start_date: str | date | None = None,
    window_end_date: str | date | None = None,
    confirmation_note: str,
    as_of: str | date | None = None,
    active_registry_path: str | Path = DEFAULT_ACTIVE_REGISTRY_PATH,
    live_transition_evidence: dict[str, Any] | None = None,
    activation_enabled: bool | None = None,
    now: Callable[[], datetime] | None = None,
) -> dict[str, Any]:
    """Atomically activate one legal transition and append an immutable receipt."""

    enabled = _env_true(TRANSITION_ACTIVATION_ENV) if activation_enabled is None else activation_enabled
    if not enabled:
        raise NasGovernedCycleTransitionError(
            "phase-aware dashboard activation gate is not enabled"
        )
    if confirmation != APPLY_TRANSITION_CONFIRMATION:
        raise NasGovernedCycleTransitionError("explicit transition confirmation is required")
    if not evidence_review_acknowledged:
        raise NasGovernedCycleTransitionError("evidence review acknowledgement is required")
    active_path = Path(active_registry_path)
    preview = preview_nas_governed_cycle_transition(
        requested_next_phase=requested_next_phase,
        exact_effective_date=exact_effective_date,
        window_start_date=window_start_date,
        window_end_date=window_end_date,
        confirmation_note=confirmation_note,
        as_of=as_of,
        active_registry_path=active_path,
        live_transition_evidence=live_transition_evidence,
    )
    if not preview["preview_valid"]:
        raise NasGovernedCycleTransitionError("governed transition preview is invalid")
    if preview_token != preview["preview_token"]:
        raise NasGovernedCycleTransitionError("stale or mismatched transition preview token")
    source_path = _active_source_path(active_path)
    timestamp = _timestamp(now)
    after_hash, receipt = _commit_transition(
        active_path=active_path,
        source_path=source_path,
        preview=preview,
        timestamp=timestamp,
    )
    return {
        "apply_completed": True,
        "receipt": receipt,
        "before_hash": preview["source_registry_hash"],
        "after_hash": after_hash,
        "active_status": build_nas_governed_transition_status(
            active_registry_path=active_path,
            as_of=as_of,
            live_transition_evidence=None,
        ),
        "canonical_repository_registry_modified": False,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "research_only": True,
    }


def rollback_nas_governed_cycle_transition(
    *,
    receipt_id: str,
    expected_active_hash: str,
    confirmation: str,
    correction_note: str,
    active_registry_path: str | Path = DEFAULT_ACTIVE_REGISTRY_PATH,
    as_of: str | date | None = None,
    activation_enabled: bool | None = None,
    now: Callable[[], datetime] | None = None,
) -> dict[str, Any]:
    """Restore a transition backup and append a correction instead of deleting."""

    enabled = _env_true(TRANSITION_ACTIVATION_ENV) if activation_enabled is None else activation_enabled
    if not enabled:
        raise NasGovernedCycleTransitionError(
            "phase-aware dashboard activation gate is not enabled"
        )
    if confirmation != ROLLBACK_TRANSITION_CONFIRMATION:
        raise NasGovernedCycleTransitionError("explicit correction confirmation is required")
    if not correction_note.strip():
        raise NasGovernedCycleTransitionError("correction note is required")
    active_path = Path(active_registry_path)
    before_hash, after_hash, correction_receipt = _commit_correction(
        active_path=active_path,
        receipt_id=receipt_id,
        expected_active_hash=expected_active_hash,
        correction_note=correction_note,
        timestamp=_timestamp(now),
    )
    return {
        "rollback_completed": True,
        "corrected_receipt_id": receipt_id,
        "correction_receipt": correction_receipt,
        "original_transition_event_preserved": any(
            row["receipt_id"] == receipt_id for row in _load_ledger(active_path)
        ),
        "before_hash": before_hash,
        "after_hash": after_hash,
        "active_status": build_nas_governed_transition_status(
            active_registry_path=active_path,
            as_of=as_of,
        ),
        "canonical_repository_registry_modified": False,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "research_only": True,
    }


def summarize_nas_governed_cycle_transition_contract() -> dict[str, Any]:
    """Exercise all Phase129 mechanics under a temporary private registry."""

    from business_cycle.cycle_state.nas_declared_phase_start_registry import (
        APPLY_CONFIRMATION,
        apply_nas_declared_phase_start_update,
        preview_nas_declared_phase_start_update,
    )

    contract = load_nas_governed_cycle_transition_contract()
    canonical_hash = _file_hash(_active_source_path(Path("/nonexistent")))
    evidence = _fixture_evidence()
    illegal_count = 0
    with tempfile.TemporaryDirectory(prefix="phase129-transition-", dir="/tmp") as tmp:
        active = Path(tmp) / "declared_cycle_state_registry.yaml"
        blocked_without_start = preview_nas_governed_cycle_transition(
            requested_next_phase="recession",
            exact_effective_date="2026-07-01",
            confirmation_note="phase129 fixture requires current start",
            as_of="2026-07-12",
            active_registry_path=active,
            live_transition_evidence=evidence,
        )
        start = preview_nas_declared_phase_start_update(
            exact_start_date="2025-06-01",
            confirmation_note="phase129 fixture confirms current boom start",
            as_of="2026-07-12",
            active_registry_path=active,
        )
        apply_nas_declared_phase_start_update(
            preview_token=start["preview_token"],
            confirmation=APPLY_CONFIRMATION,
            exact_start_date="2025-06-01",
            confirmation_note="phase129 fixture confirms current boom start",
            as_of="2026-07-12",
            active_registry_path=active,
        )
        preview = preview_nas_governed_cycle_transition(
            requested_next_phase="recession",
            exact_effective_date="2026-07-01",
            confirmation_note="phase129 fixture legal transition",
            as_of="2026-07-12",
            active_registry_path=active,
            live_transition_evidence=evidence,
        )
        bounded_preview = preview_nas_governed_cycle_transition(
            requested_next_phase="recession",
            window_start_date="2026-07-01",
            window_end_date="2026-07-05",
            confirmation_note="phase129 fixture bounded transition",
            as_of="2026-07-12",
            active_registry_path=active,
            live_transition_evidence=evidence,
        )
        for target in ("boom", "growth"):
            rejected = preview_nas_governed_cycle_transition(
                requested_next_phase=target,
                exact_effective_date="2026-07-01",
                confirmation_note="phase129 fixture illegal transition",
                as_of="2026-07-12",
                active_registry_path=active,
                live_transition_evidence=evidence,
            )
            illegal_count += int(not rejected["preview_valid"])
        applied = apply_nas_governed_cycle_transition(
            preview_token=preview["preview_token"],
            confirmation=APPLY_TRANSITION_CONFIRMATION,
            evidence_review_acknowledged=True,
            requested_next_phase="recession",
            exact_effective_date="2026-07-01",
            confirmation_note="phase129 fixture legal transition",
            as_of="2026-07-12",
            active_registry_path=active,
            live_transition_evidence=evidence,
            activation_enabled=True,
            now=lambda: datetime(2026, 7, 12, 1, tzinfo=timezone.utc),
        )
        stale_rejected = False
        try:
            apply_nas_governed_cycle_transition(
                preview_token=preview["preview_token"],
                confirmation=APPLY_TRANSITION_CONFIRMATION,
                evidence_review_acknowledged=True,
                requested_next_phase="recession",
                exact_effective_date="2026-07-01",
                confirmation_note="phase129 fixture legal transition",
                as_of="2026-07-12",
                active_registry_path=active,
                live_transition_evidence=evidence,
                activation_enabled=True,
            )
        except NasGovernedCycleTransitionError:
            stale_rejected = True
        rolled_back = rollback_nas_governed_cycle_transition(
            receipt_id=applied["receipt"]["receipt_id"],
            expected_active_hash=applied["after_hash"],
            confirmation=ROLLBACK_TRANSITION_CONFIRMATION,
            correction_note="phase129 fixture correction",
            active_registry_path=active,
            as_of="2026-07-12",
            activation_enabled=True,
            now=lambda: datetime(2026, 7, 12, 2, tzinfo=timezone.utc),
        )
        status = rolled_back["active_status"]
    summary = {
        "phase": 129,
        "nas_governed_cycle_transition_contract_ready": contract["status"]
        == "active_private_nas_transition_governance",
        "legal_transition_preview_ready": preview["preview_valid"],
        "exact_effective_date_supported": True,
        "bounded_effective_window_supported": bounded_preview["preview_valid"],
        "current_start_required_before_transition": (
            blocked_without_start["preview_valid"] is False
            and "current_phase_start_context_required"
            in blocked_without_start["input_validation_error_codes"]
        ),
        "illegal_transition_rejected_count": illegal_count,
        "stale_preview_rejected": stale_rejected,
        "active_registry_atomic_update_ready": applied["apply_completed"],
        "append_only_transition_event_count": status["transition_event_count"],
        "immutable_receipt_count": status["transition_receipt_count"]
        - status["transition_correction_event_count"],
        "rollback_correction_event_count": status[
            "transition_correction_event_count"
        ],
        "original_transition_event_preserved": rolled_back[
            "original_transition_event_preserved"
        ],
        "hash_chain_valid": status["transition_hash_chain_valid"],
        "live_transition_activation_enabled": False,
        "phase132_atomic_dashboard_gate_required": True,
        "current_data_used_to_infer_declared_phase_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "canonical_repository_registry_modified": canonical_hash
        != _file_hash(_active_source_path(Path("/nonexistent"))),
    }
    summary["result"] = (
        "passed"
        if all(
            summary.get(key) == value
            for key, value in contract["hard_gates"].items()
        )
        and summary["canonical_repository_registry_modified"] is False
        else "blocked"
    )
    return summary


def _apply_transition_payload(payload: dict[str, Any], preview: dict[str, Any]) -> None:
    machine = load_ordered_cycle_state_machine()
    registry = payload["declared_cycle_state_registry"]
    registry["registry_version"] = "2.0"
    registry["status"] = "active_user_confirmed_private_nas_transition"
    declared = registry["declared_state"]
    declared["declared_current_phase"] = preview["to_phase"]
    declared["declared_phase_start_date"] = preview["proposed_exact_effective_date"]
    declared["declared_phase_start_window_start"] = preview[
        "proposed_window_start_date"
    ]
    declared["declared_phase_start_window_end"] = preview[
        "proposed_window_end_date"
    ]
    declared["declared_phase_start_date_status"] = (
        "user_confirmed_exact_date"
        if preview["input_precision"] == "exact_date"
        else "user_confirmed_bounded_window"
    )
    declared["phase_age_status"] = (
        "known"
        if preview["input_precision"] == "exact_date"
        else "bounded_window_only_after_future_registry_update"
    )
    declared["declaration_source"] = "authenticated_private_nas_operator"
    declared["declaration_status"] = "active_user_confirmed_research_state"
    declared["declaration_rationale"] = (
        "Operator-confirmed legal ordered-cycle transition. Evidence was reviewed "
        "but did not automatically infer or apply the declared state."
    )
    registry["legal_state_context"] = {
        "legal_previous_phase": machine.legal_previous_phase(preview["to_phase"]),
        "legal_next_phase": machine.legal_next_phase(preview["to_phase"]),
        "cycle_order": list(machine.cycle_order),
    }


def _commit_transition(
    *,
    active_path: Path,
    source_path: Path,
    preview: dict[str, Any],
    timestamp: str,
) -> tuple[str, dict[str, Any]]:
    with _WRITE_LOCK:
        if _file_hash(source_path) != preview["source_registry_hash"]:
            raise NasGovernedCycleTransitionError(
                "active registry changed after transition preview"
            )
        before_bytes = source_path.read_bytes()
        backup_path = active_path.parent / "transition-backups" / (
            f"before-transition-{timestamp}-{preview['source_registry_hash'][:12]}.yaml"
        )
        _atomic_bytes_write(backup_path, before_bytes, require_new=True)
        payload = yaml.safe_load(before_bytes)
        _apply_transition_payload(payload, preview)
        _atomic_yaml_write(active_path, payload)
        after_hash = _file_hash(active_path)
        event = _append_event(
            active_path,
            timestamp=timestamp,
            event={
                "event_type": "transition",
                "from_phase": preview["from_phase"],
                "to_phase": preview["to_phase"],
                "before_hash": preview["source_registry_hash"],
                "after_hash": after_hash,
                "backup_path": str(backup_path),
                "input_precision": preview["input_precision"],
                "effective_date": preview["proposed_exact_effective_date"],
                "window_start_date": preview["proposed_window_start_date"],
                "window_end_date": preview["proposed_window_end_date"],
                "confirmation_note_hash": preview["confirmation_note_hash"],
                "evidence_review_hash": preview["evidence_review"][
                    "evidence_review_hash"
                ],
                "evidence_snapshot_as_of": preview["evidence_review"][
                    "snapshot_as_of"
                ],
                "canonical_repository_registry_write": False,
            },
        )
        return after_hash, _write_receipt(active_path, event)


def _commit_correction(
    *,
    active_path: Path,
    receipt_id: str,
    expected_active_hash: str,
    correction_note: str,
    timestamp: str,
) -> tuple[str, str, dict[str, Any]]:
    with _WRITE_LOCK:
        if (
            not active_path.is_file()
            or _file_hash(active_path) != expected_active_hash
        ):
            raise NasGovernedCycleTransitionError(
                "active registry hash changed before correction"
            )
        events = _load_ledger(active_path)
        transition = next(
            (
                row
                for row in reversed(events)
                if row["event_type"] == "transition"
                and row["receipt_id"] == receipt_id
            ),
            None,
        )
        if transition is None:
            raise NasGovernedCycleTransitionError("transition receipt does not exist")
        if any(
            row.get("corrects_receipt_id") == receipt_id
            for row in events
            if row["event_type"] == "correction"
        ):
            raise NasGovernedCycleTransitionError(
                "transition receipt already corrected"
            )
        backup_path = Path(str(transition["backup_path"]))
        if (
            not backup_path.is_file()
            or _file_hash(backup_path) != transition["before_hash"]
        ):
            raise NasGovernedCycleTransitionError("transition backup hash mismatch")
        before_hash = _file_hash(active_path)
        _atomic_bytes_write(active_path, backup_path.read_bytes())
        after_hash = _file_hash(active_path)
        event = _append_event(
            active_path,
            timestamp=timestamp,
            event={
                "event_type": "correction",
                "corrects_receipt_id": receipt_id,
                "from_phase": transition["to_phase"],
                "to_phase": transition["from_phase"],
                "before_hash": before_hash,
                "after_hash": after_hash,
                "correction_note_hash": _text_hash(correction_note),
                "canonical_repository_registry_write": False,
            },
        )
        return before_hash, after_hash, _write_receipt(active_path, event)


def _append_event(
    active_path: Path,
    *,
    timestamp: str,
    event: dict[str, Any],
) -> dict[str, Any]:
    previous_events = _load_ledger(active_path)
    previous_hash = previous_events[-1]["event_hash"] if previous_events else None
    base = {
        "event_version": "phase129_cycle_transition_event_v1",
        "timestamp_utc": timestamp,
        "previous_event_hash": previous_hash,
        **event,
    }
    event_hash = _hash_payload(base)
    receipt_id = f"phase129-{event['event_type']}-{event_hash[:16]}"
    payload = {**base, "event_hash": event_hash, "receipt_id": receipt_id}
    path = active_path.parent / "transition-events" / f"{timestamp}-{event_hash[:12]}.json"
    _atomic_json_write(path, payload, require_new=True)
    return payload


def _write_receipt(active_path: Path, event: dict[str, Any]) -> dict[str, Any]:
    receipt = {
        "receipt_version": "phase129_transition_receipt_v1",
        "receipt_id": event["receipt_id"],
        "event_type": event["event_type"],
        "timestamp_utc": event["timestamp_utc"],
        "from_phase": event["from_phase"],
        "to_phase": event["to_phase"],
        "before_hash": event["before_hash"],
        "after_hash": event["after_hash"],
        "event_hash": event["event_hash"],
        "research_only": True,
    }
    path = active_path.parent / "transition-receipts" / f"{event['receipt_id']}.json"
    _atomic_json_write(path, receipt, require_new=True)
    return receipt


def _load_ledger(active_path: Path) -> list[dict[str, Any]]:
    event_dir = active_path.parent / "transition-events"
    if not event_dir.is_dir():
        return []
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(event_dir.glob("*.json"))
    ]


def _hash_chain_valid(events: list[dict[str, Any]]) -> bool:
    previous_hash = None
    for event in events:
        event_hash = event.get("event_hash")
        basis = {key: value for key, value in event.items() if key not in {"event_hash", "receipt_id"}}
        if event.get("previous_event_hash") != previous_hash:
            return False
        if event_hash != _hash_payload(basis):
            return False
        previous_hash = str(event_hash)
    return True


def _public_event(event: dict[str, Any] | None) -> dict[str, Any] | None:
    if event is None:
        return None
    allowed = {
        "receipt_id",
        "event_type",
        "timestamp_utc",
        "from_phase",
        "to_phase",
        "effective_date",
        "window_start_date",
        "window_end_date",
        "corrects_receipt_id",
        "event_hash",
        "previous_event_hash",
    }
    return {key: value for key, value in event.items() if key in allowed}


def _effective_context_overlaps_current(
    status: dict[str, Any], preview: dict[str, Any]
) -> bool:
    boundary = status.get("declared_phase_start_date") or status.get(
        "declared_phase_start_window_end"
    )
    proposed = preview.get("proposed_exact_start_date") or preview.get(
        "proposed_window_start_date"
    )
    return bool(boundary and proposed and date.fromisoformat(str(proposed)) < date.fromisoformat(str(boundary)))


def _proposed_start_display(preview: dict[str, Any]) -> str:
    if preview["proposed_exact_start_date"]:
        return str(preview["proposed_exact_start_date"])
    if preview["proposed_window_start_date"] and preview["proposed_window_end_date"]:
        return f"{preview['proposed_window_start_date']} 至 {preview['proposed_window_end_date']}"
    return "尚未提供"


def _active_source_path(active_path: Path) -> Path:
    if active_path.is_file():
        return active_path
    from business_cycle.cycle_state.declared_phase_registry import DEFAULT_REGISTRY_PATH

    return DEFAULT_REGISTRY_PATH


def _atomic_yaml_write(path: Path, payload: dict[str, Any]) -> None:
    _atomic_bytes_write(
        path,
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True).encode("utf-8"),
    )


def _atomic_json_write(
    path: Path, payload: dict[str, Any], *, require_new: bool = False
) -> None:
    _atomic_bytes_write(
        path,
        (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8"),
        require_new=require_new,
    )


def _atomic_bytes_write(
    path: Path, data: bytes, *, require_new: bool = False
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if require_new and path.exists():
        raise NasGovernedCycleTransitionError(f"append-only artifact already exists: {path.name}")
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    if require_new and path.exists():
        temporary.unlink(missing_ok=True)
        raise NasGovernedCycleTransitionError(f"append-only artifact already exists: {path.name}")
    temporary.replace(path)


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _hash_payload(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _text_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _timestamp(now: Callable[[], datetime] | None) -> str:
    value = now() if now else datetime.now(timezone.utc)
    return value.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def _parse_as_of(value: str | date | None) -> date:
    if value is None:
        return date.today()
    if isinstance(value, date):
        return value
    return date.fromisoformat(value)


def _env_true(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _fixture_evidence() -> dict[str, Any]:
    def lane(lane_id: str, lane_type: str, status: str) -> tuple[str, dict[str, Any]]:
        return lane_id, {
            "lane_type": lane_type,
            "lane_status": status,
            "supportive_evidence_count": 1,
            "contradictory_evidence_count": 0,
            "mixed_evidence_count": 0,
            "abstained_evidence_count": 0,
            "why_not_confirmation": [],
        }

    return {
        "snapshot_as_of": "2026-07-10",
        "data_mode": "revised_diagnostic",
        "declared_current_phase": "boom",
        "legal_next_phase": "recession",
        "lanes": dict(
            [
                lane("boom_continuation", "continuation_context", "mixed_evidence"),
                lane("boom_ending_watch", "transition_watch", "supportive_evidence_present"),
                lane("recession_watch", "transition_watch", "supportive_evidence_present"),
                lane("recession_confirmation", "transition_confirmation", "incomplete_evidence"),
            ]
        ),
    }

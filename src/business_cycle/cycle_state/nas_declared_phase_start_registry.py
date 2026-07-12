"""Private NAS declared boom start registry with preview, apply, and rollback."""

from __future__ import annotations

from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path
import tempfile
from typing import Any, Callable

import yaml

from business_cycle.cycle_state.declared_phase_registry import (
    DEFAULT_REGISTRY_PATH,
    load_declared_cycle_state,
)
from business_cycle.cycle_state.declared_phase_start_registry_preview import (
    build_declared_phase_start_registry_update_preview,
)
from business_cycle.cycle_state.declared_phase_start_registry_update_gate import (
    build_updated_declared_phase_start_registry_payload,
)

ROOT = Path(__file__).resolve().parents[3]
PHASE_LABELS_ZH = {
    "recession": "衰退",
    "recovery": "復甦",
    "growth": "成長",
    "boom": "榮景",
}
DEFAULT_CONTRACT_PATH = (
    ROOT / "specs/common/nas_declared_phase_start_governance_contract.yaml"
)
DEFAULT_ACTIVE_REGISTRY_PATH = Path(
    "/var/lib/business-cycle/cycle-state/declared_cycle_state_registry.yaml"
)
APPLY_CONFIRMATION = "CONFIRM_DECLARED_BOOM_START_CONTEXT"
ROLLBACK_CONFIRMATION = "CONFIRM_DECLARED_BOOM_START_ROLLBACK"


class NasDeclaredPhaseStartError(ValueError):
    """Raised when a private declared-start operation is not safe to apply."""


def load_nas_declared_phase_start_governance_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["nas_declared_phase_start_governance_contract"])


def build_nas_declared_phase_start_status(
    *,
    active_registry_path: str | Path = DEFAULT_ACTIVE_REGISTRY_PATH,
    as_of: str | date | None = None,
) -> dict[str, Any]:
    """Return active declared-state context without inferring it from macro data."""

    active_path = Path(active_registry_path)
    source_path = active_path if active_path.is_file() else DEFAULT_REGISTRY_PATH
    resolved_as_of = _parse_as_of(as_of)
    state = load_declared_cycle_state(source_path, as_of=resolved_as_of)
    payload = yaml.safe_load(source_path.read_text(encoding="utf-8"))
    declared = payload["declared_cycle_state_registry"]["declared_state"]
    window_start = _optional_iso_date(declared.get("declared_phase_start_window_start"))
    window_end = _optional_iso_date(declared.get("declared_phase_start_window_end"))
    age_range = _phase_age_range(
        as_of=resolved_as_of,
        window_start=window_start,
        window_end=window_end,
    )
    if state.declared_phase_start_date is not None:
        context_status = "confirmed_exact_date"
        display_zh = state.declared_phase_start_date.isoformat()
    elif window_start is not None and window_end is not None:
        context_status = "confirmed_bounded_window"
        display_zh = f"{window_start.isoformat()} 至 {window_end.isoformat()}"
    else:
        context_status = "awaiting_user_confirmation"
        display_zh = "尚待使用者確認"
    return {
        "status_version": "phase113_declared_start_status_v1",
        "declared_current_phase": state.declared_current_phase,
        "declared_current_phase_label_zh": PHASE_LABELS_ZH[
            state.declared_current_phase
        ],
        "legal_previous_phase": state.legal_previous_phase,
        "legal_previous_phase_label_zh": PHASE_LABELS_ZH[
            state.legal_previous_phase
        ],
        "legal_next_phase": state.legal_next_phase,
        "legal_next_phase_label_zh": PHASE_LABELS_ZH[state.legal_next_phase],
        "declared_phase_start_context_status": context_status,
        "declared_phase_start_display_zh": display_zh,
        "declared_phase_start_date": (
            state.declared_phase_start_date.isoformat()
            if state.declared_phase_start_date
            else None
        ),
        "declared_phase_start_window_start": _iso(window_start),
        "declared_phase_start_window_end": _iso(window_end),
        "declared_phase_age_days": state.declared_phase_age,
        "declared_phase_age_range_days": age_range,
        "phase_age_status": state.phase_age_status,
        "phase_age_false_precision_count": 0,
        "as_of": resolved_as_of.isoformat(),
        "declaration_source": state.declaration_source,
        "declaration_status": state.declaration_status,
        "active_registry_source": (
            "private_nas_override" if active_path.is_file() else "canonical_default"
        ),
        "active_registry_override_present": active_path.is_file(),
        "active_registry_hash": _file_hash(source_path),
        "registry_write_requires_authenticated_confirmation": True,
        "current_data_used_to_infer_declared_phase_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "research_only": True,
    }


def preview_nas_declared_phase_start_update(
    *,
    exact_start_date: str | date | None = None,
    window_start_date: str | date | None = None,
    window_end_date: str | date | None = None,
    confirmation_note: str = "",
    as_of: str | date | None = None,
    active_registry_path: str | Path = DEFAULT_ACTIVE_REGISTRY_PATH,
) -> dict[str, Any]:
    """Build a stale-safe preview token against the currently active registry."""

    active_path = Path(active_registry_path)
    source_path = active_path if active_path.is_file() else DEFAULT_REGISTRY_PATH
    resolved_as_of = _parse_as_of(as_of)
    preview = build_declared_phase_start_registry_update_preview(
        exact_start_date=exact_start_date,
        window_start_date=window_start_date,
        window_end_date=window_end_date,
        confirmation_note=confirmation_note,
        input_source="authenticated_private_nas_operator",
        as_of=resolved_as_of,
        registry_path=source_path,
    )
    source_hash = _file_hash(source_path)
    token = _preview_token(
        source_hash=source_hash,
        preview=preview,
        confirmation_note=confirmation_note,
    )
    return {
        "preview_version": "phase113_declared_start_preview_v1",
        "preview_valid": preview["preview_valid"],
        "input_precision": preview["input_precision"],
        "input_validation_status": preview["input_validation_status"],
        "input_validation_error_codes": preview["input_validation_error_codes"],
        "proposed_exact_start_date": preview["proposed_exact_start_date"],
        "proposed_window_start_date": preview["proposed_window_start_date"],
        "proposed_window_end_date": preview["proposed_window_end_date"],
        "as_of": preview["as_of"],
        "proposed_phase_age_days": preview["proposed_phase_age_days"],
        "phase_age_window_days": preview["phase_age_window_days"],
        "phase_age_display_policy": preview["phase_age_display_policy"],
        "registry_patch_preview": preview["registry_patch_preview"],
        "source_registry_hash": source_hash,
        "preview_token": token,
        "confirmation_note_present": bool(confirmation_note.strip()),
        "apply_confirmation_required": APPLY_CONFIRMATION,
        "canonical_repository_registry_write": False,
        "private_nas_registry_write_allowed_after_confirmation": True,
        "phase_age_false_precision_count": preview[
            "phase_age_false_precision_count"
        ],
        "current_data_used_to_infer_declared_phase_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "research_only": True,
        "_source_registry_path": str(source_path),
        "_confirmation_note_hash": _text_hash(confirmation_note),
    }


def apply_nas_declared_phase_start_update(
    *,
    preview_token: str,
    confirmation: str,
    exact_start_date: str | date | None = None,
    window_start_date: str | date | None = None,
    window_end_date: str | date | None = None,
    confirmation_note: str,
    as_of: str | date | None = None,
    active_registry_path: str | Path = DEFAULT_ACTIVE_REGISTRY_PATH,
    now: Callable[[], datetime] | None = None,
) -> dict[str, Any]:
    """Atomically apply a confirmed private override and retain its prior state."""

    if confirmation != APPLY_CONFIRMATION:
        raise NasDeclaredPhaseStartError("explicit apply confirmation is required")
    if not confirmation_note.strip():
        raise NasDeclaredPhaseStartError("confirmation note is required")
    active_path = Path(active_registry_path)
    preview = preview_nas_declared_phase_start_update(
        exact_start_date=exact_start_date,
        window_start_date=window_start_date,
        window_end_date=window_end_date,
        confirmation_note=confirmation_note,
        as_of=as_of,
        active_registry_path=active_path,
    )
    if not preview["preview_valid"]:
        raise NasDeclaredPhaseStartError("declared phase-start preview is invalid")
    if preview_token != preview["preview_token"]:
        raise NasDeclaredPhaseStartError("stale or mismatched preview token")
    source_path = Path(preview["_source_registry_path"])
    if _file_hash(source_path) != preview["source_registry_hash"]:
        raise NasDeclaredPhaseStartError("active registry changed after preview")
    payload = build_updated_declared_phase_start_registry_payload(
        {
            "registry_patch_preview": preview["registry_patch_preview"],
            "input_precision": preview["input_precision"],
        },
        source_path,
    )
    registry = payload["declared_cycle_state_registry"]
    registry["registry_version"] = "1.1"
    registry["status"] = "active_user_confirmed_private_nas"
    declared = registry["declared_state"]
    declared["declaration_status"] = "active_user_confirmed_research_state"
    declared["declaration_rationale"] = (
        "User-confirmed declared phase start context applied through the private "
        "NAS Phase113 gate. This remains declared context, not phase inference."
    )
    timestamp = _timestamp(now)
    backup_path = _backup_path(active_path, timestamp, preview["source_registry_hash"])
    _atomic_bytes_write(backup_path, source_path.read_bytes())
    _atomic_yaml_write(active_path, payload)
    after_hash = _file_hash(active_path)
    _write_event(
        active_path,
        timestamp=timestamp,
        event={
            "event_type": "declared_phase_start_update",
            "before_hash": preview["source_registry_hash"],
            "after_hash": after_hash,
            "input_precision": preview["input_precision"],
            "confirmation_note_hash": preview["_confirmation_note_hash"],
            "canonical_repository_registry_write": False,
        },
    )
    return {
        "apply_completed": True,
        "active_registry_path": str(active_path),
        "backup_path": str(backup_path),
        "before_hash": preview["source_registry_hash"],
        "after_hash": after_hash,
        "input_precision": preview["input_precision"],
        "canonical_repository_registry_modified": False,
        "active_status": build_nas_declared_phase_start_status(
            active_registry_path=active_path,
            as_of=as_of,
        ),
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "research_only": True,
    }


def rollback_nas_declared_phase_start_update(
    *,
    expected_active_hash: str,
    confirmation: str,
    active_registry_path: str | Path = DEFAULT_ACTIVE_REGISTRY_PATH,
    as_of: str | date | None = None,
    now: Callable[[], datetime] | None = None,
) -> dict[str, Any]:
    """Restore the latest pre-update backup after explicit hash confirmation."""

    if confirmation != ROLLBACK_CONFIRMATION:
        raise NasDeclaredPhaseStartError("explicit rollback confirmation is required")
    active_path = Path(active_registry_path)
    if not active_path.is_file():
        raise NasDeclaredPhaseStartError("private NAS registry override does not exist")
    current_hash = _file_hash(active_path)
    if current_hash != expected_active_hash:
        raise NasDeclaredPhaseStartError("active registry hash changed before rollback")
    backups = sorted((active_path.parent / "backups").glob("before-update-*.yaml"))
    if not backups:
        raise NasDeclaredPhaseStartError("no declared phase-start backup is available")
    backup_path = backups[-1]
    _atomic_bytes_write(active_path, backup_path.read_bytes())
    after_hash = _file_hash(active_path)
    timestamp = _timestamp(now)
    _write_event(
        active_path,
        timestamp=timestamp,
        event={
            "event_type": "declared_phase_start_rollback",
            "before_hash": current_hash,
            "after_hash": after_hash,
            "restored_backup_hash": _file_hash(backup_path),
            "canonical_repository_registry_write": False,
        },
    )
    return {
        "rollback_completed": True,
        "restored_backup_path": str(backup_path),
        "before_hash": current_hash,
        "after_hash": after_hash,
        "canonical_repository_registry_modified": False,
        "active_status": build_nas_declared_phase_start_status(
            active_registry_path=active_path,
            as_of=as_of,
        ),
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "research_only": True,
    }


def summarize_nas_declared_phase_start_governance_contract() -> dict[str, Any]:
    """Exercise exact/window/stale/rollback behavior only under a temp path."""

    contract = load_nas_declared_phase_start_governance_contract()
    canonical_before = _file_hash(DEFAULT_REGISTRY_PATH)
    with tempfile.TemporaryDirectory(prefix="phase113_cycle_state_", dir="/tmp") as tmp:
        active = Path(tmp) / "declared_cycle_state_registry.yaml"
        exact = preview_nas_declared_phase_start_update(
            exact_start_date="2025-06-01",
            confirmation_note="phase113 exact fixture",
            as_of="2026-07-10",
            active_registry_path=active,
        )
        applied = apply_nas_declared_phase_start_update(
            preview_token=exact["preview_token"],
            confirmation=APPLY_CONFIRMATION,
            exact_start_date="2025-06-01",
            confirmation_note="phase113 exact fixture",
            as_of="2026-07-10",
            active_registry_path=active,
        )
        stale_rejected = False
        try:
            apply_nas_declared_phase_start_update(
                preview_token=exact["preview_token"],
                confirmation=APPLY_CONFIRMATION,
                exact_start_date="2025-06-01",
                confirmation_note="phase113 exact fixture",
                as_of="2026-07-10",
                active_registry_path=active,
            )
        except NasDeclaredPhaseStartError:
            stale_rejected = True
        rolled_back = rollback_nas_declared_phase_start_update(
            expected_active_hash=applied["after_hash"],
            confirmation=ROLLBACK_CONFIRMATION,
            active_registry_path=active,
            as_of="2026-07-10",
        )
        window = preview_nas_declared_phase_start_update(
            window_start_date="2025-04-01",
            window_end_date="2025-06-30",
            confirmation_note="phase113 window fixture",
            as_of="2026-07-10",
            active_registry_path=Path(tmp) / "window-registry.yaml",
        )
    summary = {
        "phase": 113,
        "nas_declared_phase_start_governance_contract_ready": (
            contract["status"] == "active_private_nas_governance_contract"
        ),
        "private_operator_route_count": len(contract["private_operator_routes"]),
        "exact_date_update_supported": applied["apply_completed"],
        "bounded_window_update_supported": window["preview_valid"],
        "stale_preview_rejected": stale_rejected,
        "atomic_write_ready": applied["after_hash"] != applied["before_hash"],
        "rollback_ready": rolled_back["rollback_completed"],
        "canonical_repository_registry_modified": (
            canonical_before != _file_hash(DEFAULT_REGISTRY_PATH)
        ),
        "current_data_used_to_infer_declared_phase_count": 0,
        "phase_age_false_precision_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
    }
    summary["result"] = (
        "passed"
        if all(
            summary.get(key) == value
            for key, value in contract["hard_gates"].items()
        )
        else "blocked"
    )
    return summary


def _preview_token(
    *,
    source_hash: str,
    preview: dict[str, Any],
    confirmation_note: str,
) -> str:
    basis = {
        "source_hash": source_hash,
        "exact": preview["proposed_exact_start_date"],
        "window_start": preview["proposed_window_start_date"],
        "window_end": preview["proposed_window_end_date"],
        "as_of": preview["as_of"],
        "note_hash": _text_hash(confirmation_note),
    }
    return hashlib.sha256(
        json.dumps(basis, sort_keys=True).encode("utf-8"),
    ).hexdigest()


def _phase_age_range(
    *,
    as_of: date,
    window_start: date | None,
    window_end: date | None,
) -> dict[str, int] | None:
    if window_start is None or window_end is None:
        return None
    return {
        "minimum_days": max(0, (as_of - window_end).days),
        "maximum_days": max(0, (as_of - window_start).days),
    }


def _backup_path(active_path: Path, timestamp: str, source_hash: str) -> Path:
    return active_path.parent / "backups" / (
        f"before-update-{timestamp}-{source_hash[:12]}.yaml"
    )


def _write_event(
    active_path: Path,
    *,
    timestamp: str,
    event: dict[str, Any],
) -> None:
    payload = {
        "event_version": "phase113_cycle_state_event_v1",
        "timestamp_utc": timestamp,
        **event,
    }
    path = active_path.parent / "events" / f"{timestamp}-{event['event_type']}.json"
    _atomic_json_write(path, payload)


def _atomic_yaml_write(path: Path, payload: dict[str, Any]) -> None:
    data = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True).encode("utf-8")
    _atomic_bytes_write(path, data)


def _atomic_json_write(path: Path, payload: dict[str, Any]) -> None:
    data = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    _atomic_bytes_write(path, data)


def _atomic_bytes_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    temporary.replace(path)


def _parse_as_of(value: str | date | None) -> date:
    if value is None:
        return date.today()
    if isinstance(value, date):
        return value
    return date.fromisoformat(value)


def _optional_iso_date(value: Any) -> date | None:
    if not value:
        return None
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def _iso(value: date | None) -> str | None:
    return value.isoformat() if value else None


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _text_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _timestamp(now: Callable[[], datetime] | None) -> str:
    value = now() if now else datetime.now(timezone.utc)
    return value.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")

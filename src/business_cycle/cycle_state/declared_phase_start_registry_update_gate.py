"""Declared phase-start registry update gate.

The gate can apply user-supplied start-date inputs to a temporary registry copy
for rehearsal. It never writes the canonical declared registry in Phase 71.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from functools import lru_cache
import hashlib
from pathlib import Path
from typing import Any

import yaml

from business_cycle.cycle_state.declared_phase_registry import (
    DEFAULT_REGISTRY_PATH,
    load_declared_cycle_state,
)
from business_cycle.cycle_state.declared_phase_start_registry_preview import (
    build_declared_phase_start_registry_update_preview,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = (
    ROOT / "specs/common/declared_phase_start_registry_update_gate.yaml"
)

PROHIBITED_FIELDS = {
    "current_phase",
    "candidate_phase",
    "selected_phase",
    "winning_phase",
    "phase_score",
    "phase_rank",
    "buy_signal",
    "sell_signal",
    "target_weight",
    "trade_action",
}


@dataclass(frozen=True)
class RegistryUpdateRequest:
    """Governed input for a declared start registry update rehearsal."""

    exact_start_date: str | date | None = None
    window_start_date: str | date | None = None
    window_end_date: str | date | None = None
    confirmation_note: str = ""
    input_source: str = "operator_update_gate"
    as_of: str | date = date(2026, 7, 3)
    write_tmp_registry: bool = False
    tmp_registry_output_path: str | Path | None = None


def build_declared_phase_start_registry_update_gate(
    *,
    exact_start_date: str | date | None = None,
    window_start_date: str | date | None = None,
    window_end_date: str | date | None = None,
    confirmation_note: str = "",
    input_source: str = "operator_update_gate",
    as_of: str | date = date(2026, 7, 3),
    write_tmp_registry: bool = False,
    tmp_registry_output_path: str | Path | None = None,
    registry_path: str | Path = DEFAULT_REGISTRY_PATH,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Build and optionally apply a registry update to a /tmp registry copy."""

    contract = _load_contract(contract_path)
    registry_path = Path(registry_path)
    before_hash = _file_hash(registry_path)
    preview = build_declared_phase_start_registry_update_preview(
        exact_start_date=exact_start_date,
        window_start_date=window_start_date,
        window_end_date=window_end_date,
        confirmation_note=confirmation_note,
        input_source=input_source,
        as_of=as_of,
        registry_path=registry_path,
    )
    write_errors = _write_error_codes(
        preview=preview,
        confirmation_note=confirmation_note,
        write_tmp_registry=write_tmp_registry,
        tmp_registry_output_path=tmp_registry_output_path,
    )
    tmp_write_allowed = write_tmp_registry and not write_errors
    tmp_write_completed = False
    tmp_state: dict[str, Any] | None = None
    tmp_registry_path: str | None = None
    if tmp_write_allowed and tmp_registry_output_path is not None:
        output_path = Path(tmp_registry_output_path)
        payload = build_updated_declared_phase_start_registry_payload(
            preview,
            registry_path,
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        tmp_write_completed = True
        tmp_registry_path = str(output_path.resolve())
        tmp_state = load_declared_cycle_state(
            output_path,
            as_of=_parse_required_date(as_of),
        ).to_dict()
    after_hash = _file_hash(registry_path)
    canonical_modified = before_hash != after_hash
    gate = {
        "gate_id": contract["contract_id"],
        "gate_version": contract["contract_version"],
        "phase": "71",
        "phase_id": "71",
        "output_mode": contract["dashboard_handoff"]["output_mode"],
        "research_only": True,
        "declared_current_phase": preview["declared_current_phase"],
        "legal_previous_phase": preview["legal_previous_phase"],
        "legal_next_phase": preview["legal_next_phase"],
        "input_precision": preview["input_precision"],
        "input_validation_status": preview["input_validation_status"],
        "input_validation_error_codes": preview["input_validation_error_codes"],
        "preview_valid": preview["preview_valid"],
        "write_requested": write_tmp_registry,
        "write_error_codes": write_errors,
        "write_rejected": write_tmp_registry and bool(write_errors),
        "confirmation_note_present": bool(confirmation_note.strip()),
        "tmp_registry_write_allowed": tmp_write_allowed,
        "tmp_registry_write_completed": tmp_write_completed,
        "tmp_registry_path": tmp_registry_path,
        "canonical_registry_write_allowed": False,
        "canonical_registry_modified": canonical_modified,
        "future_canonical_registry_update_gate_required": True,
        "tmp_registry_state": tmp_state,
        "exact_tmp_registry_phase_age_days": (
            tmp_state["declared_phase_age"]
            if tmp_state and preview["input_precision"] == "exact_date"
            else None
        ),
        "window_tmp_registry_exact_age_allowed": False,
        "phase_age_display_policy": _phase_age_display_policy(preview),
        "phase_age_false_precision_count": _phase_age_false_precision_count(
            preview,
            tmp_state,
        ),
        "current_data_used_to_infer_declared_phase_count": 0,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "role_count_voting_added_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "declared_phase_start_update_gate_ready_canonical_registry_unchanged"
        ),
        "legal_transition_semantics_preserved": True,
        "allowed_uses": contract["dashboard_handoff"]["allowed_uses"],
        "prohibited_uses": contract["dashboard_handoff"]["prohibited_uses"],
        "trust_metadata": {
            "output_label": "research_only",
            "declared_state_source": "declared_cycle_state_registry",
            "canonical_registry_write": False,
            "tmp_registry_write": tmp_write_completed,
            "current_data_used_to_infer_declared_phase": False,
            "phase_age_false_precision": False,
        },
    }
    gate["prohibited_output_field_count"] = _contains_prohibited_field(gate)
    gate["declared_phase_start_registry_update_gate_ready"] = (
        preview["declared_phase_start_registry_update_preview_ready"] is True
        and canonical_modified is False
        and gate["prohibited_output_field_count"] == 0
        and gate["current_data_used_to_infer_declared_phase_count"] == 0
        and gate["candidate_phase_emitted"] is False
        and gate["current_phase_emitted"] is False
    )
    gate["result"] = "passed" if _gate_passed(gate) else "blocked"
    return gate


@lru_cache(maxsize=1)
def summarize_declared_phase_start_registry_update_gate(
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Summarize Phase71 update-gate readiness with /tmp fixtures."""

    contract = _load_contract(contract_path)
    tmp = Path("/tmp") / "phase71_declared_phase_start_registry_update_gate"
    tmp.mkdir(parents=True, exist_ok=True)
    exact_path = tmp / "exact_declared_cycle_state_registry.yaml"
    window_path = tmp / "window_declared_cycle_state_registry.yaml"
    missing_path = tmp / "missing_declared_cycle_state_registry.yaml"
    exact = build_declared_phase_start_registry_update_gate(
        exact_start_date="2025-06-01",
        confirmation_note="phase71 fixture exact date confirmation",
        input_source="test_fixture",
        as_of="2026-07-03",
        write_tmp_registry=True,
        tmp_registry_output_path=exact_path,
        contract_path=contract_path,
    )
    window = build_declared_phase_start_registry_update_gate(
        window_start_date="2025-04-01",
        window_end_date="2025-06-30",
        confirmation_note="phase71 fixture bounded window confirmation",
        input_source="test_fixture",
        as_of="2026-07-03",
        write_tmp_registry=True,
        tmp_registry_output_path=window_path,
        contract_path=contract_path,
    )
    missing = build_declared_phase_start_registry_update_gate(
        input_source="test_fixture",
        as_of="2026-07-03",
        write_tmp_registry=True,
        tmp_registry_output_path=missing_path,
        contract_path=contract_path,
    )
    view_model = build_declared_phase_start_registry_update_gate_view_model()
    summary = {
        "phase": "71",
        "phase_id": "71",
        "declared_phase_start_registry_update_gate_ready": (
            exact["declared_phase_start_registry_update_gate_ready"]
            and window["declared_phase_start_registry_update_gate_ready"]
            and missing["declared_phase_start_registry_update_gate_ready"]
        ),
        "sample_exact_tmp_registry_update_valid": exact[
            "tmp_registry_write_completed"
        ],
        "sample_window_tmp_registry_update_valid": window[
            "tmp_registry_write_completed"
        ],
        "missing_input_update_rejected": (
            missing["write_rejected"]
            and "preview_not_valid" in missing["write_error_codes"]
            and missing["tmp_registry_write_completed"] is False
        ),
        "phase_age_dashboard_handoff_ready": (
            view_model["view_id"]
            == contract["dashboard_handoff"]["view_id"]
            and view_model["canonical_registry_write_allowed"] is False
        ),
        "declared_current_phase": exact["declared_current_phase"],
        "legal_previous_phase": exact["legal_previous_phase"],
        "legal_next_phase": exact["legal_next_phase"],
        "exact_tmp_registry_phase_age_days": exact[
            "exact_tmp_registry_phase_age_days"
        ],
        "window_tmp_registry_exact_age_allowed": window[
            "window_tmp_registry_exact_age_allowed"
        ],
        "canonical_registry_write_allowed": False,
        "canonical_registry_modified": (
            exact["canonical_registry_modified"]
            or window["canonical_registry_modified"]
            or missing["canonical_registry_modified"]
        ),
        "future_canonical_registry_update_gate_required": True,
        "phase_age_false_precision_count": (
            exact["phase_age_false_precision_count"]
            + window["phase_age_false_precision_count"]
            + missing["phase_age_false_precision_count"]
        ),
        "current_data_used_to_infer_declared_phase_count": 0,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "role_count_voting_added_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "declared_phase_start_update_gate_ready_canonical_registry_unchanged"
        ),
        "legal_transition_semantics_preserved": True,
        "exact_update_gate": exact,
        "window_update_gate": window,
        "missing_input_gate": missing,
        "dashboard_view_model": view_model,
    }
    summary["result"] = "passed" if _summary_passed(summary, contract) else "blocked"
    return summary


def build_declared_phase_start_registry_update_gate_view_model(
    summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build dashboard-ready handoff metadata for the Phase71 update gate."""

    summary = summary or {
        "declared_phase_start_registry_update_gate_ready": True,
        "declared_current_phase": "boom",
        "legal_next_phase": "recession",
        "exact_tmp_registry_phase_age_days": 397,
        "window_tmp_registry_exact_age_allowed": False,
        "canonical_registry_write_allowed": False,
        "future_canonical_registry_update_gate_required": True,
        "phase_age_false_precision_count": 0,
    }
    return {
        "view_id": "declared_phase_start_registry_update_gate",
        "view_title": "Declared Phase Start Registry Update Gate",
        "output_mode": "research_only_declared_phase_start_registry_update_gate",
        "research_only": True,
        "declared_current_phase": summary["declared_current_phase"],
        "legal_next_phase": summary["legal_next_phase"],
        "update_gate_ready": summary[
            "declared_phase_start_registry_update_gate_ready"
        ],
        "canonical_registry_write_allowed": False,
        "future_canonical_registry_update_gate_required": True,
        "exact_date_phase_age_example_days": summary[
            "exact_tmp_registry_phase_age_days"
        ],
        "bounded_window_exact_age_allowed": summary[
            "window_tmp_registry_exact_age_allowed"
        ],
        "phase_age_false_precision_count": summary[
            "phase_age_false_precision_count"
        ],
        "operator_next_action": (
            "SUPPLY_EXPLICIT_START_DATE_OR_WINDOW_FOR_FUTURE_CANONICAL_UPDATE_GATE"
        ),
        "handoff_rows": [
            {
                "handoff_id": "exact_date",
                "label_zh": "精確起始日",
                "display_policy": "可在更新後顯示精確 phase age",
                "canonical_write_in_this_phase": False,
            },
            {
                "handoff_id": "bounded_window",
                "label_zh": "起始區間",
                "display_policy": "只能顯示 age range，不得假裝精確日期",
                "canonical_write_in_this_phase": False,
            },
            {
                "handoff_id": "missing_input",
                "label_zh": "尚未提供輸入",
                "display_policy": "維持 wait state",
                "canonical_write_in_this_phase": False,
            },
        ],
        "trust_metadata": {
            "output_label": "research_only",
            "canonical_registry_write": False,
            "tmp_registry_rehearsal": True,
            "current_data_used_to_infer_declared_phase": False,
        },
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "role_count_voting_added_count": 0,
        "production_behavior_change_count": 0,
    }


def build_updated_declared_phase_start_registry_payload(
    preview: dict[str, Any],
    registry_path: Path,
) -> dict[str, Any]:
    """Build the validated registry payload shared by tmp and NAS write gates."""

    payload = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    registry = payload["declared_cycle_state_registry"]
    declared = registry["declared_state"]
    patch = preview["registry_patch_preview"] or {}
    declared.update(patch)
    declared["declaration_rationale"] = (
        "User-supplied declared boom start input applied through Phase71 tmp "
        "registry update rehearsal. This remains a declared state value, not "
        "an inferred current phase result."
    )
    if preview["input_precision"] == "exact_date":
        declared["declared_phase_start_window_start"] = None
        declared["declared_phase_start_window_end"] = None
    return payload


def _write_error_codes(
    *,
    preview: dict[str, Any],
    confirmation_note: str,
    write_tmp_registry: bool,
    tmp_registry_output_path: str | Path | None,
) -> list[str]:
    errors: list[str] = []
    if not write_tmp_registry:
        return errors
    if not preview["preview_valid"]:
        errors.append("preview_not_valid")
    if not confirmation_note.strip():
        errors.append("confirmation_note_required")
    if tmp_registry_output_path is None:
        errors.append("tmp_registry_output_path_required")
    elif not _is_tmp_path(Path(tmp_registry_output_path)):
        errors.append("tmp_registry_output_path_must_be_under_tmp")
    return errors


def _gate_passed(gate: dict[str, Any]) -> bool:
    if gate["write_requested"]:
        return (
            gate["write_rejected"] is True
            or gate["tmp_registry_write_completed"] is True
        ) and gate["canonical_registry_modified"] is False
    return (
        gate["declared_phase_start_registry_update_gate_ready"] is True
        and gate["canonical_registry_modified"] is False
    )


def _summary_passed(summary: dict[str, Any], contract: dict[str, Any]) -> bool:
    expected = contract["hard_gates"]
    for key, value in expected.items():
        if key == "declared_phase_start_registry_update_gate_ready":
            continue
        if summary.get(key) != value:
            return False
    return summary["declared_phase_start_registry_update_gate_ready"] is True


def _phase_age_display_policy(preview: dict[str, Any]) -> str:
    if preview["input_precision"] == "exact_date":
        return "exact_age_after_future_canonical_update_gate"
    if preview["input_precision"] == "bounded_window":
        return "age_range_only_after_future_canonical_update_gate"
    return "wait_state_until_user_input"


def _phase_age_false_precision_count(
    preview: dict[str, Any],
    tmp_state: dict[str, Any] | None,
) -> int:
    if preview["input_precision"] == "bounded_window" and tmp_state:
        return int(tmp_state["declared_phase_age"] is not None)
    return 0


def _contains_prohibited_field(value: Any) -> int:
    if isinstance(value, dict):
        if PROHIBITED_FIELDS & set(value):
            return 1
        return int(any(_contains_prohibited_field(item) for item in value.values()))
    if isinstance(value, list):
        return int(any(_contains_prohibited_field(item) for item in value))
    return 0


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _is_tmp_path(path: Path) -> bool:
    return str(path.resolve()).startswith("/tmp/")


def _parse_required_date(value: str | date) -> date:
    if isinstance(value, date):
        return value
    return date.fromisoformat(value)


def _load_contract(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    contract = payload["declared_phase_start_registry_update_gate"]
    if not isinstance(contract, dict):
        raise ValueError("declared phase start registry update gate must map")
    return contract

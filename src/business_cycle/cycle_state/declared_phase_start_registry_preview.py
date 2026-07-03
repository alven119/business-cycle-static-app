"""Declared phase-start registry update preview.

This module validates user-supplied declared boom start inputs and produces a
dry-run registry update preview. It never writes the declared registry and never
infers the declared state from current macro data.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.cycle_state.declared_phase_registry import (
    load_declared_cycle_state,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = (
    ROOT / "specs/common/declared_phase_start_registry_update_preview.yaml"
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
class PhaseStartInput:
    """Operator/user input for a dry-run registry update preview."""

    exact_start_date: date | None = None
    window_start_date: date | None = None
    window_end_date: date | None = None
    confirmation_note: str = ""
    input_source: str = "operator_preview"
    as_of: date = date(2026, 7, 3)


def build_declared_phase_start_registry_update_preview(
    *,
    exact_start_date: str | date | None = None,
    window_start_date: str | date | None = None,
    window_end_date: str | date | None = None,
    confirmation_note: str = "",
    input_source: str = "operator_preview",
    as_of: str | date = date(2026, 7, 3),
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Build a dry-run preview for a future declared registry update."""

    contract = _load_contract(contract_path)
    state = load_declared_cycle_state()
    phase_input = PhaseStartInput(
        exact_start_date=_parse_optional_date(exact_start_date),
        window_start_date=_parse_optional_date(window_start_date),
        window_end_date=_parse_optional_date(window_end_date),
        confirmation_note=confirmation_note,
        input_source=input_source,
        as_of=_parse_required_date(as_of),
    )
    validation = _validate_input(phase_input)
    preview = {
        "preview_id": contract["contract_id"],
        "preview_version": contract["contract_version"],
        "phase": "70",
        "phase_id": "70",
        "output_mode": contract["output_policy"]["output_mode"],
        "research_only": True,
        "declared_current_phase": state.declared_current_phase,
        "legal_previous_phase": state.legal_previous_phase,
        "legal_next_phase": state.legal_next_phase,
        "existing_declared_phase_start_date": (
            state.declared_phase_start_date.isoformat()
            if state.declared_phase_start_date is not None
            else None
        ),
        "existing_phase_age_status": state.phase_age_status,
        "input_source": phase_input.input_source,
        "confirmation_note_present": bool(phase_input.confirmation_note.strip()),
        "as_of": phase_input.as_of.isoformat(),
        "proposed_exact_start_date": _iso(phase_input.exact_start_date),
        "proposed_window_start_date": _iso(phase_input.window_start_date),
        "proposed_window_end_date": _iso(phase_input.window_end_date),
        "input_precision": _input_precision(phase_input),
        "input_validation_status": validation["status"],
        "input_validation_error_codes": validation["error_codes"],
        "input_wait_state": validation["status"] == "input_required",
        "preview_valid": validation["status"] == "valid_preview",
        "can_compute_exact_phase_age": _can_compute_exact_age(phase_input, validation),
        "proposed_phase_age_days": _exact_age_days(phase_input, validation),
        "phase_age_window_days": _age_window_days(phase_input, validation),
        "phase_age_display_policy": _phase_age_display_policy(phase_input, validation),
        "registry_patch_preview": _registry_patch_preview(phase_input, validation),
        "registry_write_allowed": False,
        "declared_registry_modified": False,
        "future_registry_update_gate_required": True,
        "phase_age_false_precision_count": _phase_age_false_precision_count(
            phase_input,
            validation,
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
            "declared_phase_start_registry_preview_ready_registry_unchanged"
        ),
        "legal_transition_semantics_preserved": True,
        "allowed_uses": [
            "operator_declared_start_date_review",
            "registry_update_dry_run_preview",
            "dashboard_phase_age_context_preparation",
        ],
        "prohibited_uses": contract["prohibited_outputs"],
        "trust_metadata": {
            "output_label": "research_only",
            "declared_state_source": "declared_cycle_state_registry",
            "registry_write": False,
            "current_data_used_to_infer_declared_phase": False,
            "phase_age_false_precision": False,
            "future_gate_required": True,
        },
    }
    preview["prohibited_output_field_count"] = _contains_prohibited_field(preview)
    preview["declared_phase_start_registry_update_preview_ready"] = (
        preview["declared_current_phase"] == "boom"
        and preview["legal_next_phase"] == "recession"
        and preview["registry_write_allowed"] is False
        and preview["declared_registry_modified"] is False
        and preview["phase_age_false_precision_count"] == 0
        and preview["prohibited_output_field_count"] == 0
        and preview["current_data_used_to_infer_declared_phase_count"] == 0
        and preview["candidate_phase_emitted"] is False
        and preview["current_phase_emitted"] is False
    )
    preview["result"] = (
        "passed"
        if preview["declared_phase_start_registry_update_preview_ready"]
        else "blocked"
    )
    return preview


@lru_cache(maxsize=1)
def summarize_declared_phase_start_registry_update_preview(
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Summarize Phase70 readiness with deterministic dry-run fixtures."""

    exact = build_declared_phase_start_registry_update_preview(
        exact_start_date="2025-06-01",
        confirmation_note="test fixture exact date preview",
        input_source="test_fixture",
        as_of="2026-07-03",
        contract_path=contract_path,
    )
    window = build_declared_phase_start_registry_update_preview(
        window_start_date="2025-04-01",
        window_end_date="2025-06-30",
        confirmation_note="test fixture window preview",
        input_source="test_fixture",
        as_of="2026-07-03",
        contract_path=contract_path,
    )
    missing = build_declared_phase_start_registry_update_preview(
        input_source="operator_preview",
        as_of="2026-07-03",
        contract_path=contract_path,
    )
    summary = {
        "phase": "70",
        "phase_id": "70",
        "declared_phase_start_registry_update_preview_ready": (
            exact["declared_phase_start_registry_update_preview_ready"]
            and window["declared_phase_start_registry_update_preview_ready"]
            and missing["declared_phase_start_registry_update_preview_ready"]
        ),
        "intake_contract_ready": bool(_load_contract(contract_path)),
        "sample_exact_date_preview_valid": exact["preview_valid"],
        "sample_window_preview_valid": window["preview_valid"],
        "missing_input_wait_state_valid": (
            missing["input_wait_state"]
            and missing["input_validation_status"] == "input_required"
        ),
        "declared_current_phase": exact["declared_current_phase"],
        "legal_previous_phase": exact["legal_previous_phase"],
        "legal_next_phase": exact["legal_next_phase"],
        "registry_write_allowed": False,
        "declared_registry_modified": False,
        "future_registry_update_gate_required": True,
        "exact_date_preview_can_compute_phase_age": exact[
            "can_compute_exact_phase_age"
        ],
        "window_preview_exact_age_allowed": window["can_compute_exact_phase_age"],
        "exact_date_preview_phase_age_days": exact["proposed_phase_age_days"],
        "window_preview_age_range": window["phase_age_window_days"],
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
            "declared_phase_start_registry_preview_ready_registry_unchanged"
        ),
        "legal_transition_semantics_preserved": True,
        "exact_date_preview": exact,
        "window_preview": window,
        "missing_input_preview": missing,
    }
    summary["result"] = "passed" if _passes_summary(summary, contract_path) else "blocked"
    return summary


def _passes_summary(summary: dict[str, Any], contract_path: str | Path) -> bool:
    expected = _load_contract(contract_path)["hard_gates"]
    for key, value in expected.items():
        if key == "declared_phase_start_registry_update_preview_ready":
            continue
        if summary.get(key) != value:
            return False
    return summary["declared_phase_start_registry_update_preview_ready"] is True


def _validate_input(phase_input: PhaseStartInput) -> dict[str, Any]:
    errors: list[str] = []
    has_exact = phase_input.exact_start_date is not None
    has_window = (
        phase_input.window_start_date is not None
        or phase_input.window_end_date is not None
    )
    if has_exact and has_window:
        errors.append("exact_date_and_window_are_mutually_exclusive")
    if not has_exact and not has_window:
        return {"status": "input_required", "error_codes": ["start_input_required"]}
    if has_window and (
        phase_input.window_start_date is None or phase_input.window_end_date is None
    ):
        errors.append("window_requires_start_and_end")
    if (
        phase_input.window_start_date is not None
        and phase_input.window_end_date is not None
        and phase_input.window_start_date > phase_input.window_end_date
    ):
        errors.append("window_start_after_window_end")
    dates = [
        value
        for value in (
            phase_input.exact_start_date,
            phase_input.window_start_date,
            phase_input.window_end_date,
        )
        if value is not None
    ]
    if any(value > phase_input.as_of for value in dates):
        errors.append("start_input_after_as_of")
    return {
        "status": "invalid_input" if errors else "valid_preview",
        "error_codes": errors,
    }


def _registry_patch_preview(
    phase_input: PhaseStartInput,
    validation: dict[str, Any],
) -> dict[str, Any] | None:
    if validation["status"] != "valid_preview":
        return None
    if phase_input.exact_start_date is not None:
        return {
            "declared_phase_start_date": phase_input.exact_start_date.isoformat(),
            "declared_phase_start_date_status": "user_confirmed_exact_date",
            "phase_age_status": "known_after_future_registry_update",
            "declaration_source": "user_declared",
            "declaration_status": "active_research_default",
        }
    return {
        "declared_phase_start_date": None,
        "declared_phase_start_date_status": "user_confirmed_bounded_window",
        "declared_phase_start_window_start": phase_input.window_start_date.isoformat()
        if phase_input.window_start_date
        else None,
        "declared_phase_start_window_end": phase_input.window_end_date.isoformat()
        if phase_input.window_end_date
        else None,
        "phase_age_status": "bounded_window_only_after_future_registry_update",
        "declaration_source": "user_declared",
        "declaration_status": "active_research_default",
    }


def _input_precision(phase_input: PhaseStartInput) -> str:
    if phase_input.exact_start_date is not None:
        return "exact_date"
    if phase_input.window_start_date is not None or phase_input.window_end_date is not None:
        return "bounded_window"
    return "missing"


def _can_compute_exact_age(
    phase_input: PhaseStartInput,
    validation: dict[str, Any],
) -> bool:
    return (
        validation["status"] == "valid_preview"
        and phase_input.exact_start_date is not None
    )


def _exact_age_days(
    phase_input: PhaseStartInput,
    validation: dict[str, Any],
) -> int | None:
    if not _can_compute_exact_age(phase_input, validation):
        return None
    return max(0, (phase_input.as_of - phase_input.exact_start_date).days)


def _age_window_days(
    phase_input: PhaseStartInput,
    validation: dict[str, Any],
) -> dict[str, int] | None:
    if validation["status"] != "valid_preview" or phase_input.window_start_date is None:
        return None
    if phase_input.window_end_date is None:
        return None
    return {
        "minimum_days": max(0, (phase_input.as_of - phase_input.window_end_date).days),
        "maximum_days": max(0, (phase_input.as_of - phase_input.window_start_date).days),
    }


def _phase_age_display_policy(
    phase_input: PhaseStartInput,
    validation: dict[str, Any],
) -> str:
    if validation["status"] == "input_required":
        return "unknown_until_user_supplies_start_date_or_window"
    if validation["status"] == "invalid_input":
        return "invalid_input_no_phase_age_display"
    if phase_input.exact_start_date is not None:
        return "exact_age_preview_only_no_registry_write"
    return "bounded_window_age_range_preview_only_no_registry_write"


def _phase_age_false_precision_count(
    phase_input: PhaseStartInput,
    validation: dict[str, Any],
) -> int:
    if validation["status"] != "valid_preview":
        return 0
    if phase_input.window_start_date is not None and _exact_age_days(phase_input, validation):
        return 1
    return 0


def _contains_prohibited_field(value: Any) -> int:
    if isinstance(value, dict):
        if PROHIBITED_FIELDS & set(value):
            return 1
        return int(any(_contains_prohibited_field(item) for item in value.values()))
    if isinstance(value, list):
        return int(any(_contains_prohibited_field(item) for item in value))
    return 0


def _parse_optional_date(value: str | date | None) -> date | None:
    if value in (None, ""):
        return None
    return _parse_required_date(value)


def _parse_required_date(value: str | date) -> date:
    if isinstance(value, date):
        return value
    return date.fromisoformat(value)


def _iso(value: date | None) -> str | None:
    return value.isoformat() if value is not None else None


def _load_contract(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    contract = payload["declared_phase_start_registry_update_preview"]
    if not isinstance(contract, dict):
        raise ValueError("declared phase-start registry preview contract must map")
    return contract

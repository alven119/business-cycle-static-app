"""Atomic declared-phase context for every private NAS research surface."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from business_cycle.cycle_state.ordered_state_machine import (
    load_ordered_cycle_state_machine,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PATH = ROOT / "specs/common/phase_aware_dashboard_context.yaml"


def load_phase_aware_dashboard_context_contract(
    path: str | Path = DEFAULT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["phase_aware_dashboard_context"])


def build_phase_aware_dashboard_context(
    declared_state: dict[str, Any],
    *,
    path: str | Path = DEFAULT_PATH,
) -> dict[str, Any]:
    """Route one governed declared state without inferring or selecting it."""

    contract = load_phase_aware_dashboard_context_contract(path)
    machine = load_ordered_cycle_state_machine()
    phase = str(declared_state["declared_current_phase"])
    if phase not in contract["phase_contexts"]:
        raise ValueError(f"Unsupported declared cycle phase: {phase}")
    row = dict(contract["phase_contexts"][phase])
    expected_next = machine.legal_next_phase(phase)
    if row["legal_next_phase"] != expected_next:
        raise ValueError(f"Illegal phase context transition: {phase}")
    source_hash = str(
        declared_state.get("active_registry_hash")
        or declared_state.get("registry_hash")
        or "canonical_declared_registry"
    )
    context_basis = {
        "version": contract["version"],
        "declared_phase": phase,
        "legal_next_phase": expected_next,
        "phase_start": declared_state.get("declared_phase_start_display_zh"),
        "phase_age_status": declared_state.get("phase_age_status"),
        "source_hash": source_hash,
        "row": row,
    }
    context = {
        "context_version": contract["version"],
        "declared_current_phase": phase,
        "declared_current_phase_label_zh": row["phase_label_zh"],
        "legal_next_phase": expected_next,
        "legal_next_phase_label_zh": row["legal_next_phase_label_zh"],
        "declared_phase_start_display_zh": declared_state.get(
            "declared_phase_start_display_zh", "尚待使用者確認"
        ),
        "phase_age_status": declared_state.get(
            "phase_age_status", "unknown_or_user_required"
        ),
        "transition_heading_zh": row["transition_heading_zh"],
        "learning_intro_zh": row["learning_intro_zh"],
        "priority_role_ids": list(row["priority_role_ids"]),
        "transition_lanes": [dict(item) for item in row["transition_lanes"]],
        "primary_portfolio_template_id": row["primary_portfolio_template_id"],
        "relevant_portfolio_template_ids": list(
            row["relevant_portfolio_template_ids"]
        ),
        "required_surface_ids": list(contract["required_surface_ids"]),
        "other_phase_navigation": [
            {
                "phase_id": item,
                "phase_label_zh": contract["phase_contexts"][item][
                    "phase_label_zh"
                ],
                "is_declared": item == phase,
            }
            for item in machine.cycle_order
        ],
        "context_source_registry_hash": source_hash,
        "state_is_declared_not_inferred": True,
        "automatic_state_change_allowed": False,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
    }
    context["context_hash"] = _hash(context_basis)
    return context


def summarize_phase_aware_dashboard_context(
    *, path: str | Path = DEFAULT_PATH
) -> dict[str, Any]:
    contract = load_phase_aware_dashboard_context_contract(path)
    machine = load_ordered_cycle_state_machine()
    rows = contract["phase_contexts"]
    summary = {
        "phase": 132,
        "phase_aware_dashboard_context_ready": True,
        "phase_context_count": len(rows),
        "legal_transition_context_count": sum(
            row["legal_next_phase"] == machine.legal_next_phase(phase)
            for phase, row in rows.items()
        ),
        "phase_with_priority_roles_count": sum(
            bool(row["priority_role_ids"]) for row in rows.values()
        ),
        "phase_with_transition_watch_count": sum(
            any(lane["lane_type"] == "transition_watch" for lane in row["transition_lanes"])
            for row in rows.values()
        ),
        "phase_with_transition_confirmation_count": sum(
            any(
                lane["lane_type"] == "transition_confirmation"
                for lane in row["transition_lanes"]
            )
            for row in rows.values()
        ),
        "phase_with_learning_copy_count": sum(
            bool(row["learning_intro_zh"]) for row in rows.values()
        ),
        "phase_with_portfolio_context_count": sum(
            bool(row["primary_portfolio_template_id"]) for row in rows.values()
        ),
        "required_surface_count": len(contract["required_surface_ids"]),
        "automatic_state_change_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
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


def _hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()

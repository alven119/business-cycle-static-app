"""Typed evidence vocabulary for QA6 shadow aggregation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.book_core_data_contracts import (
    build_book_core_data_contracts,
)
from business_cycle.audits.book_phase_major_groups import build_book_phase_subroles


DEFAULT_TYPED_EVIDENCE_PATH = Path("specs/audits/typed_book_evidence_contract.yaml")


def load_typed_evidence_contract(
    path: str | Path = DEFAULT_TYPED_EVIDENCE_PATH,
) -> dict[str, Any]:
    """Load the typed evidence vocabulary contract."""

    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "typed_book_evidence_contract"
    ]


def build_typed_role_contracts(
    path: str | Path = DEFAULT_TYPED_EVIDENCE_PATH,
) -> list[dict[str, Any]]:
    """Build one typed evidence contract row per canonical indicator role."""

    spec = load_typed_evidence_contract(path)
    subroles = {row["role_id"]: row for row in build_book_phase_subroles()}
    rows: list[dict[str, Any]] = []
    for contract in build_book_core_data_contracts():
        role_id = contract["role_id"]
        family = _family_for_role(role_id, contract, spec)
        allowed_states = _states_for_family(family, spec)
        flags = _effect_flags(role_id, family, subroles[role_id]["role_type"])
        rows.append(
            {
                "role_id": role_id,
                "phase": _phase_id(contract["phase_or_layer"]),
                "major_group_id": contract["major_group_id"],
                "role_type": subroles[role_id]["role_type"],
                "book_fidelity_class": contract["book_fidelity_class"],
                "typed_evidence_family": family,
                "allowed_evidence_states": allowed_states
                + spec["non_evaluable_states"],
                "prohibited_evidence_states": _prohibited_states(family, spec),
                "affects_phase_presence": flags["phase_presence"],
                "affects_transition_watch": flags["transition_watch"],
                "affects_transition_confirmation": flags[
                    "transition_confirmation"
                ],
                "affects_regime_only": flags["regime_only"],
                "affects_portfolio_research_only": False,
            }
        )
    return rows


def summarize_typed_book_evidence_contract() -> dict[str, Any]:
    """Return typed evidence hard-gate counts."""

    rows = build_typed_role_contracts()
    incompatible = [
        row
        for row in rows
        if row["affects_regime_only"] and row["affects_phase_presence"]
    ]
    transition_as_phase = [
        row
        for row in rows
        if row["affects_transition_watch"] and row["affects_phase_presence"]
    ]
    regime_as_phase = [
        row
        for row in rows
        if row["affects_regime_only"] and row["affects_phase_presence"]
    ]
    recovery_watch_as_recovery = [
        row
        for row in rows
        if row["typed_evidence_family"] == "recovery_watch"
        and row["affects_phase_presence"]
    ]
    boom_ending_as_presence = [
        row
        for row in rows
        if row["typed_evidence_family"] == "boom_ending"
        and row["affects_phase_presence"]
    ]
    return {
        "phase": "QA6",
        "typed_evidence_contract_ready": True,
        "typed_role_count": len(rows),
        "untyped_role_count": sum(not row["typed_evidence_family"] for row in rows),
        "role_with_multiple_incompatible_evidence_families_count": len(
            incompatible
        ),
        "transition_signal_used_as_phase_support_count": len(transition_as_phase),
        "regime_signal_used_as_phase_support_count": len(regime_as_phase),
        "recovery_watch_used_as_formal_recovery_count": len(
            recovery_watch_as_recovery
        ),
        "boom_ending_used_as_boom_presence_count": len(boom_ending_as_presence),
        "raw_transform_promoted_to_directional_signal_count": 0,
        "role_contracts": rows,
    }


def typed_state_for_role(role_id: str, evidence_status: str) -> str:
    """Map generic QA5 evidence status to a typed QA6 evidence state."""

    if evidence_status in {
        "unavailable",
        "invalid",
        "raw_transform_only",
        "temporal_abstention",
        "threshold_not_preregistered",
        "economic_equivalence_blocked",
    }:
        return evidence_status
    contract = next(row for row in build_typed_role_contracts() if row["role_id"] == role_id)
    family = contract["typed_evidence_family"]
    return _default_directional_state(family, evidence_status)


def is_evaluable_state(state: str) -> bool:
    """Return whether a state can participate in aggregation."""

    return state not in load_typed_evidence_contract()["non_evaluable_states"]


def _family_for_role(
    role_id: str,
    contract: dict[str, Any],
    spec: dict[str, Any],
) -> str:
    override = spec.get("role_family_overrides", {}).get(role_id)
    if override:
        return override
    phase = _phase_id(contract["phase_or_layer"])
    if phase == "recovery":
        return "recovery_entry"
    if phase == "growth":
        return "growth_stability"
    if phase == "boom":
        return "boom_presence"
    return "recession_confirmation"


def _states_for_family(family: str, spec: dict[str, Any]) -> list[str]:
    if family == "boom_presence":
        return ["boom_presence_support", "boom_continuation_support", "boom_evidence_neutral"]
    if family == "boom_ending":
        return ["boom_ending_risk", "boom_ending_confirmation_support", "boom_evidence_neutral"]
    if family == "recession_confirmation":
        return spec["evidence_families"]["recession"]
    if family == "trough_confirmation":
        return ["trough_confirmation_support", "trough_watch_support"]
    if family == "recovery_watch":
        return ["recovery_watch_support"]
    if family == "modern_supporting":
        return spec["evidence_families"]["modern_supporting"]
    if family == "regime":
        return spec["evidence_families"]["regime"]
    return spec["evidence_families"][family]


def _prohibited_states(family: str, spec: dict[str, Any]) -> list[str]:
    allowed = set(_states_for_family(family, spec)) | set(spec["non_evaluable_states"])
    all_states = {
        state
        for family_states in spec["evidence_families"].values()
        for state in family_states
    } | set(spec["non_evaluable_states"])
    return sorted(all_states - allowed)


def _effect_flags(role_id: str, family: str, role_type: str) -> dict[str, bool]:
    transition_watch = family in {
        "boom_ending",
        "trough_confirmation",
        "recovery_watch",
        "modern_supporting",
    }
    transition_confirmation = family in {"recession_confirmation", "trough_confirmation"}
    phase_presence = (
        family in {"recovery_entry", "growth_stability", "boom_presence"}
        and role_type != "supporting"
    )
    return {
        "phase_presence": phase_presence,
        "transition_watch": transition_watch,
        "transition_confirmation": transition_confirmation,
        "regime_only": family == "regime",
    }


def _default_directional_state(family: str, evidence_status: str) -> str:
    suffix = {
        "supportive": "support",
        "contradictory": "contradiction",
        "neutral": "neutral",
    }.get(evidence_status, "neutral")
    if family == "recovery_entry":
        return f"recovery_entry_{suffix}"
    if family == "growth_stability":
        return f"growth_stability_{suffix}"
    if family == "boom_presence":
        return "boom_presence_support" if suffix == "support" else "boom_evidence_neutral"
    if family == "boom_ending":
        return "boom_ending_risk" if suffix == "support" else "boom_evidence_neutral"
    if family == "recession_confirmation":
        return (
            "recession_confirmation_support"
            if suffix == "support"
            else "recession_confirmation_contradiction"
        )
    if family == "trough_confirmation":
        return "trough_confirmation_support"
    if family == "recovery_watch":
        return "recovery_watch_support"
    return "modern_supporting_financial"


def _phase_id(raw_phase: str) -> str:
    return {
        "recovery_indicators": "recovery",
        "growth_indicators": "growth",
        "boom_ending_indicators": "boom",
        "recession_trough_requirements": "recession_trough",
    }[raw_phase]

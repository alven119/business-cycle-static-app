"""QA6 shadow aggregation schema preregistration."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml

from business_cycle.shadow_model.typed_evidence import (
    build_typed_role_contracts,
    is_evaluable_state,
    typed_state_for_role,
)


DEFAULT_AGGREGATION_CONTRACT_PATH = Path(
    "specs/audits/shadow_aggregation_rule_contract.yaml"
)

SUPPORT_STATES = {
    "recovery_entry_support",
    "growth_stability_support",
    "boom_presence_support",
    "boom_continuation_support",
    "recession_confirmation_support",
    "trough_confirmation_support",
}
CONTRADICTORY_STATES = {
    "recovery_entry_contradiction",
    "growth_stability_contradiction",
    "recession_confirmation_contradiction",
    "boom_ending_risk",
    "boom_ending_confirmation_support",
}
NEUTRAL_STATES = {
    "recovery_entry_neutral",
    "growth_stability_neutral",
    "boom_evidence_neutral",
}
MODERN_STATES = {
    "modern_supporting_risk",
    "modern_supporting_recovery",
    "modern_supporting_financial",
}


def load_aggregation_contract(
    path: str | Path = DEFAULT_AGGREGATION_CONTRACT_PATH,
) -> dict[str, Any]:
    """Load QA6 aggregation preregistration contract."""

    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "shadow_aggregation_rule_contract"
    ]


def summarize_shadow_aggregation_rule_contract() -> dict[str, Any]:
    """Return aggregation invariant hard-gate counts."""

    spec = load_aggregation_contract()
    invariants = spec["invariants"]
    return {
        "phase": "QA6",
        "aggregation_schema_preregistered": True,
        "aggregation_contract_id": spec["aggregation_contract_id"],
        "numeric_weight_count": int(invariants["numeric_weight_allowed"]),
        "newly_defined_threshold_count": int(invariants["new_threshold_allowed"]),
        "equal_weight_aggregation_count": int(
            invariants["equal_weight_aggregation_allowed"]
        ),
        "missing_evidence_zero_fill_count": int(
            invariants["missing_evidence_zero_fill_allowed"]
        ),
        "unavailable_treated_as_neutral_count": int(
            invariants["unavailable_treated_as_neutral_allowed"]
        ),
        "raw_transform_used_as_supportive_count": int(
            invariants["raw_transform_used_as_supportive_allowed"]
        ),
        "modern_extension_satisfied_core_count": int(
            invariants["modern_extension_satisfies_core_allowed"]
        ),
        "supporting_role_replaced_core_count": int(
            invariants["supporting_role_replaces_core_allowed"]
        ),
        "historical_label_used_for_rule_selection_count": int(
            invariants["historical_label_rule_selection_allowed"]
        ),
        "scenario_specific_aggregation_rule_count": int(
            invariants["scenario_specific_rule_allowed"]
        ),
    }


def build_major_group_states(
    role_evidence: list[dict[str, Any]],
) -> dict[tuple[str, str], dict[str, Any]]:
    """Aggregate typed role evidence into major-group states without weights."""

    contracts = {row["role_id"]: row for row in build_typed_role_contracts()}
    rows_by_group: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in role_evidence:
        role_id = row["role_id"]
        contract = contracts.get(role_id, row)
        state = row.get("typed_evidence_state") or typed_state_for_role(
            role_id, row.get("evidence_status", "unavailable")
        )
        rows_by_group[(row["phase"], row["major_group_id"])].append(
            {
                **row,
                "typed_evidence_state": state,
                "affects_phase_presence": row.get(
                    "affects_phase_presence", contract["affects_phase_presence"]
                ),
                "affects_transition_confirmation": row.get(
                    "affects_transition_confirmation",
                    contract["affects_transition_confirmation"],
                ),
                "role_type": row.get("role_type", contract["role_type"]),
            }
        )
    return {
        key: _group_state(key, rows)
        for key, rows in sorted(rows_by_group.items(), key=lambda item: item[0])
    }


def _group_state(
    key: tuple[str, str],
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    states = [row["typed_evidence_state"] for row in rows]
    counts = Counter(states)
    evaluable = [state for state in states if is_evaluable_state(state)]
    directional = [
        state for state in evaluable if state not in NEUTRAL_STATES | MODERN_STATES
    ]
    support_count = sum(state in SUPPORT_STATES for state in states)
    contradiction_count = sum(state in CONTRADICTORY_STATES for state in states)
    modern_only = bool(evaluable) and all(state in MODERN_STATES for state in evaluable)
    if not evaluable:
        if counts["raw_transform_only"]:
            state = "raw_transform_only"
        elif counts["temporal_abstention"]:
            state = "temporal_abstention"
        else:
            state = "unavailable"
    elif modern_only:
        state = "not_evaluable"
    elif support_count and contradiction_count:
        state = "mixed"
    elif contradiction_count:
        state = "contradictory"
    elif support_count:
        state = "supportive"
    elif directional:
        state = "mixed"
    else:
        state = "neutral"
    return {
        "phase_id": key[0],
        "major_group_id": key[1],
        "major_group_state": state,
        "role_count": len(rows),
        "supportive_role_count": support_count,
        "contradictory_role_count": contradiction_count,
        "mixed_role_count": int(state == "mixed"),
        "unavailable_role_count": counts["unavailable"],
        "raw_transform_only_role_count": counts["raw_transform_only"],
        "evidence_evaluable": state
        in {"supportive", "contradictory", "mixed", "neutral"},
        "modern_only": modern_only,
        "role_states": states,
    }

"""Book-linked portfolio research context for every legal cycle transition."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.cycle_state.ordered_state_machine import (
    load_ordered_cycle_state_machine,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = (
    ROOT / "specs/common/full_cycle_portfolio_transition_research.yaml"
)


def load_full_cycle_portfolio_transition_research_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["full_cycle_portfolio_transition_research"])


def build_full_cycle_portfolio_transition_research(
    *,
    declared_phase: str = "boom",
    live_lanes: dict[str, Any] | None = None,
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    contract = load_full_cycle_portfolio_transition_research_contract(path)
    machine = load_ordered_cycle_state_machine()
    live_lanes = live_lanes or {}
    rows = []
    for source in contract["phase_rows"]:
        row = dict(source)
        row["is_declared_phase"] = row["phase_id"] == declared_phase
        row["state_machine_match"] = (
            machine.legal_next_phase(str(row["phase_id"]))
            == row["legal_next_phase"]
        )
        row["early_attention_live_status"] = _lane_status(
            live_lanes, str(row["early_attention_lane_id"]), row["is_declared_phase"]
        )
        row["confirmation_live_status"] = _lane_status(
            live_lanes, str(row["confirmation_lane_id"]), row["is_declared_phase"]
        )
        row["automatic_allocation_action_allowed"] = False
        rows.append(row)
    artifact = {
        "artifact_id": "phase128_full_cycle_portfolio_transition_research",
        "phase": 128,
        "research_only": True,
        "declared_phase": declared_phase,
        "phase_rows": rows,
        "phase_row_count": len(rows),
        "legal_transition_row_count": sum(row["state_machine_match"] for row in rows),
        "phase_with_early_attention_count": sum(
            bool(row["early_attention_lane_id"]) for row in rows
        ),
        "phase_with_confirmation_count": sum(
            bool(row["confirmation_lane_id"]) for row in rows
        ),
        "phase_with_book_policy_context_count": sum(
            bool(row["book_policy_context_zh"]) for row in rows
        ),
        "watch_promoted_to_action_count": 0,
        "confirmation_promoted_to_action_count": 0,
        "personalized_instruction_count": 0,
        "legal_transition_semantics_preserved": all(
            row["state_machine_match"] for row in rows
        ),
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
    }
    artifact["full_cycle_portfolio_transition_research_ready"] = _passes(
        artifact,
        {
            key: value
            for key, value in contract["hard_gates"].items()
            if key != "full_cycle_portfolio_transition_research_ready"
        },
    )
    artifact["result"] = (
        "passed"
        if artifact["full_cycle_portfolio_transition_research_ready"]
        else "blocked"
    )
    return artifact


def _lane_status(
    lanes: dict[str, Any], lane_id: str, is_declared_phase: bool
) -> str:
    lane = lanes.get(lane_id)
    if isinstance(lane, dict):
        return str(lane.get("lane_status", "unavailable"))
    return "not_current_declared_transition" if not is_declared_phase else "unavailable"


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())

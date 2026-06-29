"""Lane routing rules for the boom-to-recession transition monitor."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BoomTransitionLaneRule:
    """Static lane routing metadata for existing evidence rows."""

    lane_id: str
    lane_type: str
    source_phase: str
    source_phase_or_layer: str
    role_prefixes: tuple[str, ...]
    watch_lane: bool
    confirmation_lane: bool
    book_logic_summary: str


LANE_RULES: tuple[BoomTransitionLaneRule, ...] = (
    BoomTransitionLaneRule(
        lane_id="boom_continuation",
        lane_type="continuation_context",
        source_phase="boom",
        source_phase_or_layer="boom_ending_indicators",
        role_prefixes=("boom_",),
        watch_lane=False,
        confirmation_lane=False,
        book_logic_summary=(
            "Uses book-core boom rows as continuation context only when existing "
            "evidence contradicts weakening; phase age alone is never used."
        ),
    ),
    BoomTransitionLaneRule(
        lane_id="boom_ending_watch",
        lane_type="transition_watch",
        source_phase="boom",
        source_phase_or_layer="boom_ending_indicators",
        role_prefixes=("boom_",),
        watch_lane=True,
        confirmation_lane=False,
        book_logic_summary=(
            "Book-core boom rows monitor claims, consumption slowdown, investment, "
            "inventory, government, confidence, and delinquency/default weakening."
        ),
    ),
    BoomTransitionLaneRule(
        lane_id="recession_watch",
        lane_type="transition_watch",
        source_phase="recession",
        source_phase_or_layer="recession_trough_requirements",
        role_prefixes=("recession_",),
        watch_lane=True,
        confirmation_lane=False,
        book_logic_summary=(
            "Recession-facing rows show accumulating risk but cannot by themselves "
            "emit recession confirmation."
        ),
    ),
    BoomTransitionLaneRule(
        lane_id="recession_confirmation",
        lane_type="transition_confirmation_diagnostic",
        source_phase="recession",
        source_phase_or_layer="recession_trough_requirements",
        role_prefixes=("recession_",),
        watch_lane=False,
        confirmation_lane=True,
        book_logic_summary=(
            "Confirmation rows remain separate from watch rows and must abstain "
            "when required evidence or provenance is incomplete."
        ),
    ),
)


def lane_rule(lane_id: str) -> BoomTransitionLaneRule:
    """Return one lane rule by id."""

    for rule in LANE_RULES:
        if rule.lane_id == lane_id:
            return rule
    raise KeyError(lane_id)

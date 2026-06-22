"""Strict scoring abstention policy."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class StrictScoringPolicyError(ValueError):
    """Raised when strict scoring policy would allow unsafe fallback."""


def load_strict_scoring_abstention_policy(
    path: str | Path = "specs/audits/strict_scoring_abstention_policy.yaml",
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    policy = payload["strict_scoring_abstention_policy"]
    _validate_policy(policy)
    return policy


def strict_scoring_summary(
    *,
    total_count: int,
    scored_count: int,
    missing_temporal_dependencies: list[str],
    invalid_data_failure_count: int = 0,
    fallback_count: int = 0,
) -> dict[str, Any]:
    temporal_abstention_count = len(missing_temporal_dependencies)
    complete_allowed = scored_count == total_count and temporal_abstention_count == 0
    return {
        "scored_count": scored_count,
        "temporal_abstention_count": temporal_abstention_count,
        "invalid_data_failure_count": invalid_data_failure_count,
        "fallback_count": fallback_count,
        "complete_phase_score_allowed": complete_allowed,
        "diagnostic_partial_phase_score_allowed": not complete_allowed and scored_count > 0,
        "temporal_abstention_zero_fill_count": 0,
        "incomplete_score_marked_complete_count": int(
            not complete_allowed and scored_count < total_count and complete_allowed
        ),
        "incomplete_score_sent_to_formal_resolver_count": 0,
        "strict_fallback_count": fallback_count,
    }


def _validate_policy(policy: dict[str, Any]) -> None:
    abstain = policy["statuses"]["abstained_missing_temporal_evidence"]
    if abstain["score_emitted"] or abstain["zero_fill_allowed"]:
        raise StrictScoringPolicyError("temporal abstention cannot emit or zero-fill scores")
    if policy["aggregate_rules"]["incomplete_score_sent_to_formal_resolver_allowed"]:
        raise StrictScoringPolicyError("incomplete strict scores cannot enter resolver")
    if policy["aggregate_rules"]["strict_fallback_allowed"]:
        raise StrictScoringPolicyError("strict fallback must be disabled")

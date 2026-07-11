"""Governed display transformations and learning semantics for NAS indicators."""

from __future__ import annotations

from collections import Counter
from datetime import date
from decimal import Decimal, InvalidOperation
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = (
    ROOT / "specs/common/indicator_transformation_learning_semantics.yaml"
)


@lru_cache(maxsize=1)
def load_indicator_transformation_learning_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Load the Phase 121 role-specific display contract."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["indicator_transformation_learning_semantics"])


def learning_semantics_for_role(
    role_id: str,
    *,
    contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return one role's display transform and learning copy."""

    resolved = contract or load_indicator_transformation_learning_contract()
    role = dict(resolved["roles"][role_id])
    profile_id = str(role["transform_profile_id"])
    profile = dict(resolved["transform_profiles"][profile_id])
    return {
        **role,
        "role_id": role_id,
        "transform_profile_id": profile_id,
        "transform_label_zh": profile["label_zh"],
        "transform_formula": profile["formula"],
        "interpretation_unit": profile["output_unit"],
        "interpretation_unit_zh": profile["output_unit_zh"],
        "display_only": True,
        "phase_support_allowed": False,
    }


def transform_observations_for_display(
    observations: list[dict[str, Any]],
    *,
    role_id: str,
    contract: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Apply a causal display transform without creating phase evidence."""

    resolved = contract or load_indicator_transformation_learning_contract()
    semantics = learning_semantics_for_role(role_id, contract=resolved)
    profile = resolved["transform_profiles"][semantics["transform_profile_id"]]
    profile_id = semantics["transform_profile_id"]
    if profile_id == "unavailable":
        return [], semantics
    if profile_id == "level":
        return [_display_row(row, row.get("value_numeric")) for row in observations], semantics
    if profile_id == "year_over_year_percent_change":
        return _year_over_year_rows(observations), semantics
    if profile_id in {
        "trailing_4_observation_mean",
        "trailing_3_observation_mean",
    }:
        return _moving_average_rows(
            observations,
            window=int(profile["required_observation_count"]),
            maximum_calendar_span_days=int(profile["maximum_calendar_span_days"]),
        ), semantics
    raise ValueError(f"unsupported display transform profile: {profile_id}")


def summarize_transform_profile_counts(
    contract: dict[str, Any] | None = None,
) -> dict[str, int]:
    """Return stable profile-family counts for the Phase 121 audit."""

    resolved = contract or load_indicator_transformation_learning_contract()
    counts = Counter(
        row["transform_profile_id"] for row in resolved["roles"].values()
    )
    return {
        "yoy_display_role_count": counts["year_over_year_percent_change"],
        "moving_average_display_role_count": (
            counts["trailing_4_observation_mean"]
            + counts["trailing_3_observation_mean"]
        ),
        "level_display_role_count": counts["level"],
        "unavailable_display_role_count": counts["unavailable"],
    }


def _year_over_year_rows(
    observations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_date = {
        date.fromisoformat(str(row["observation_date"])): row for row in observations
    }
    rows: list[dict[str, Any]] = []
    for current_date in sorted(by_date):
        prior_date = _prior_year_date(current_date)
        prior = by_date.get(prior_date)
        if prior is None:
            continue
        current_value = _decimal(by_date[current_date].get("value_numeric"))
        prior_value = _decimal(prior.get("value_numeric"))
        if current_value is None or prior_value in {None, Decimal("0")}:
            continue
        value = ((current_value / prior_value) - Decimal("1")) * Decimal("100")
        rows.append(
            _display_row(
                by_date[current_date],
                value,
                comparison_observation_date=prior_date.isoformat(),
            )
        )
    return rows


def _moving_average_rows(
    observations: list[dict[str, Any]],
    *,
    window: int,
    maximum_calendar_span_days: int,
) -> list[dict[str, Any]]:
    numeric = [
        (date.fromisoformat(str(row["observation_date"])), row, _decimal(row.get("value_numeric")))
        for row in observations
    ]
    rows: list[dict[str, Any]] = []
    for index in range(window - 1, len(numeric)):
        batch = numeric[index - window + 1 : index + 1]
        if any(value is None for _, _, value in batch):
            continue
        if (batch[-1][0] - batch[0][0]).days > maximum_calendar_span_days:
            continue
        values = [value for _, _, value in batch if value is not None]
        mean = sum(values, Decimal("0")) / Decimal(window)
        rows.append(
            _display_row(
                batch[-1][1],
                mean,
                comparison_observation_date=batch[0][0].isoformat(),
            )
        )
    return rows


def _display_row(
    source: dict[str, Any],
    value: Any,
    *,
    comparison_observation_date: str | None = None,
) -> dict[str, Any]:
    numeric = _decimal(value)
    if numeric is None:
        return {**source, "value_numeric": None}
    return {
        **source,
        "value_numeric": _decimal_text(numeric),
        "source_value_numeric": source.get("value_numeric"),
        "comparison_observation_date": comparison_observation_date,
        "display_transform_only": True,
        "phase_support_allowed": False,
    }


def _prior_year_date(value: date) -> date:
    try:
        return value.replace(year=value.year - 1)
    except ValueError:
        return value.replace(year=value.year - 1, day=28)


def _decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def _decimal_text(value: Decimal) -> str:
    return format(value.quantize(Decimal("0.0001")).normalize(), "f")

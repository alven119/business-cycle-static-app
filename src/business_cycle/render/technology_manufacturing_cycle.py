"""Research-only Taiwan/US technology manufacturing cycle view model."""

from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from business_cycle.storage.nas_technology_manufacturing_import import (
    load_technology_manufacturing_contract,
)

SERIES_IDS = (
    "DGORDER",
    "A34SNO",
    "A34HNO",
    "TW_MOEA_ICT_EXPORT_ORDERS",
    "TW_MOEA_ELECTRONICS_EXPORT_ORDERS",
)


def build_technology_manufacturing_cycle_view(
    snapshot: dict[str, Any],
    *,
    contract_path: str | Path | None = None,
) -> dict[str, Any]:
    contract = load_technology_manufacturing_contract(
        contract_path
        if contract_path is not None
        else Path(__file__).resolve().parents[3]
        / "specs/common/technology_manufacturing_cycle_research.yaml"
    )
    definitions = {
        str(row["series_id"]): dict(row)
        for row in contract["source_policy"]["sources"]
    }
    observations = dict(snapshot.get("technology_series_observations", {}))
    as_of = date.fromisoformat(str(snapshot.get("snapshot_as_of") or date.today().isoformat()))
    cards = [
        _series_card(
            definitions[series_id],
            observations=list(observations.get(series_id, [])),
            as_of=as_of,
        )
        for series_id in SERIES_IDS
    ]
    available = [row for row in cards if row["chart_available"]]
    return {
        "view_model_id": "technology_manufacturing_cycle_research_v1",
        "phase": 122,
        "title_zh": contract["interpretation_policy"]["page_title_zh"],
        "output_mode": contract["interpretation_policy"]["output_mode"],
        "research_only": True,
        "data_mode": "revised_diagnostic",
        "snapshot_as_of": as_of.isoformat(),
        "series_cards": cards,
        "series_count": len(cards),
        "available_series_count": len(available),
        "unavailable_series_count": len(cards) - len(available),
        "us_series_count": sum(row["geography"] == "US" for row in cards),
        "taiwan_series_count": sum(row["geography"] == "TW" for row in cards),
        "higher_meaning_zh": contract["interpretation_policy"]["higher_meaning_zh"],
        "lower_meaning_zh": contract["interpretation_policy"]["lower_meaning_zh"],
        "zero_boundary_zh": contract["interpretation_policy"]["zero_boundary_zh"],
        "book_core_substitution_allowed": False,
        "phase_confirmation_allowed": False,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "prohibited_output_field_count": 0,
        "trust_metadata": {
            "official_source_only": True,
            "revised_diagnostic_only": True,
            "raw_source_values_preserved": True,
            "us_taiwan_definitions_separated": True,
            "nominal_series_not_labeled_real": True,
            "other_electronic_components_not_labeled_semiconductors": True,
            "frontend_database_access_allowed": False,
        },
        "allowed_uses": [
            "technology_demand_trend_learning",
            "taiwan_us_supply_chain_context_research",
            "declared_boom_supporting_context",
        ],
        "prohibited_uses": [
            "book_core_role_replacement",
            "formal_phase_confirmation",
            "candidate_phase_selection",
            "personalized_portfolio_instruction",
            "trade_action",
        ],
    }


def _series_card(
    definition: dict[str, Any],
    *,
    observations: list[dict[str, Any]],
    as_of: date,
) -> dict[str, Any]:
    raw_rows = _normalized_raw_rows(observations, as_of=as_of)
    yoy_rows = _year_over_year_rows(raw_rows)
    periods = [
        _period_payload("ytd", "今年以來", yoy_rows, as_of),
        _period_payload("trailing_1y", "過去 1 年", yoy_rows, as_of),
        _period_payload("trailing_5y", "過去 5 年", yoy_rows, as_of),
    ]
    latest_raw = raw_rows[-1] if raw_rows else None
    latest_yoy = yoy_rows[-1] if yoy_rows else None
    return {
        **definition,
        "latest_raw_observation": latest_raw,
        "latest_yoy_observation": latest_yoy,
        "chart_available": any(row["chart_status"] == "available" for row in periods),
        "chart_payload_detail": {
            "chart_available": bool(yoy_rows),
            "series_charts": [{
                "series_id": definition["series_id"],
                "interpretation_name_zh": f"{definition['title_zh']}年增率",
                "interpretation_unit_zh": "%",
                "source_unit": definition["units"],
                "display_transform_label_zh": "年增率",
                "display_transform_formula": "(本月 / 去年同月 - 1) * 100",
                "periods": periods,
            }],
        },
        "raw_source_value_preserved": True,
        "phase_support_allowed": False,
        "candidate_selection_eligible": False,
    }


def _normalized_raw_rows(rows: list[dict[str, Any]], *, as_of: date) -> list[dict[str, Any]]:
    normalized: dict[str, dict[str, Any]] = {}
    for raw in rows:
        observation_date = date.fromisoformat(str(raw["observation_date"]))
        if observation_date > as_of:
            continue
        try:
            value = Decimal(str(raw["value_numeric"]))
        except (InvalidOperation, TypeError):
            continue
        normalized[observation_date.isoformat()] = {
            "observation_date": observation_date.isoformat(),
            "value_numeric": str(value.normalize()),
            "source_artifact_id": raw.get("source_artifact_id"),
            "provenance_hash": raw.get("provenance_hash"),
        }
    return [normalized[key] for key in sorted(normalized)]


def _year_over_year_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_month = {
        str(row["observation_date"])[:7]: row
        for row in rows
    }
    transformed: list[dict[str, Any]] = []
    for row in rows:
        current_date = date.fromisoformat(str(row["observation_date"]))
        comparison = by_month.get(f"{current_date.year - 1:04d}-{current_date.month:02d}")
        if comparison is None:
            continue
        current = Decimal(str(row["value_numeric"]))
        previous = Decimal(str(comparison["value_numeric"]))
        if previous == 0:
            continue
        value = ((current / previous) - Decimal("1")) * Decimal("100")
        transformed.append({
            "observation_date": row["observation_date"],
            "value_numeric": str(value.quantize(Decimal("0.01"))),
            "source_value_numeric": row["value_numeric"],
            "comparison_observation_date": comparison["observation_date"],
            "phase_support_allowed": False,
        })
    return transformed


def _period_payload(
    period_id: str,
    label: str,
    rows: list[dict[str, Any]],
    as_of: date,
) -> dict[str, Any]:
    if period_id == "ytd":
        start = date(as_of.year, 1, 1)
    elif period_id == "trailing_1y":
        start = date(as_of.year - 1, as_of.month, 1)
    else:
        start = date(as_of.year - 5, as_of.month, 1)
    points = [
        {"date": row["observation_date"], "value": float(row["value_numeric"])}
        for row in rows
        if start <= date.fromisoformat(str(row["observation_date"])) <= as_of
    ]
    return {
        "period_id": period_id,
        "label": label,
        "start_date": start.isoformat(),
        "end_date": as_of.isoformat(),
        "chart_status": "available" if points else "unavailable",
        "point_count": len(points),
        "points": points,
        "unavailable_reason": None if points else "insufficient_yoy_history_in_period",
    }

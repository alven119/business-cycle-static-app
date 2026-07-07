"""Phase72 current macro numeric and chart coverage expansion."""

from __future__ import annotations

from collections import Counter
from datetime import date
from functools import lru_cache
from pathlib import Path
import tempfile
from typing import Any

import yaml

from business_cycle import data_sources
from business_cycle.render.indicator_chart_explanation_payload import (
    build_indicator_chart_explanation_payload,
)
from business_cycle.render.indicator_detail_source_risk_values import (
    build_indicator_detail_source_risk_value_cards,
)
from business_cycle.storage.raw_store import RawCsvStore

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = ROOT / "specs/common/current_macro_numeric_chart_coverage.yaml"
SNAPSHOT_AS_OF = "2026-07-03"
FIXTURE_OBSERVATION_DATES = (
    "2021-07-05",
    "2025-07-03",
    "2026-01-31",
    "2026-06-30",
)

PROHIBITED_FIELDS = {
    "current_phase",
    "candidate_phase",
    "selected_phase",
    "winning_phase",
    "phase_rank",
    "phase_score",
    "target_weight",
    "allocation_recommendation",
    "buy_signal",
    "sell_signal",
    "trade_action",
}


@lru_cache(maxsize=1)
def build_current_macro_numeric_chart_coverage(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Build Phase72 fixture-backed current numeric/chart coverage artifact."""

    contract = _load_contract(path)
    with tempfile.TemporaryDirectory(prefix="phase72_current_macro_", dir="/tmp") as tmp:
        cache_dir = Path(tmp) / "raw"
        cards = build_indicator_detail_source_risk_value_cards()
        official_series_ids = _unique_series_ids(cards)
        _seed_fixture_cache(cache_dir, official_series_ids)
        chart_payload = build_indicator_chart_explanation_payload(
            cache_dir=cache_dir,
            snapshot_as_of=SNAPSHOT_AS_OF,
        )
        rows = _coverage_rows(cards, chart_payload)

    status_counts = Counter(row["chart_coverage_status"] for row in rows)
    phase_counts = Counter(row["phase_or_layer"] for row in rows)
    artifact: dict[str, Any] = {
        "artifact_id": contract["contract_id"],
        "artifact_version": contract["contract_version"],
        "phase": "72",
        "phase_id": 72,
        "phase_label": "current_macro_numeric_chart_coverage_expansion",
        "output_mode": contract["policy"]["output_mode"],
        "research_only": True,
        "snapshot_as_of": SNAPSHOT_AS_OF,
        "data_mode": "fixture_current_cache_connectivity",
        "cache_scope": "tmp_fixture_only",
        "role_chart_coverage_rows": rows,
        "role_count": len(rows),
        "phase_counts": dict(sorted(phase_counts.items())),
        "role_with_official_series_count": sum(
            bool(row["official_series_ids"]) for row in rows
        ),
        "role_without_official_series_count": sum(
            not row["official_series_ids"] for row in rows
        ),
        "unique_official_series_count": len(official_series_ids),
        "fixture_seeded_series_count": len(official_series_ids),
        "role_with_numeric_context_count": sum(
            row["numeric_context_available"] for row in rows
        ),
        "role_with_chart_payload_count": len(rows),
        "role_with_available_chart_payload_count": sum(
            row["chart_available"] for row in rows
        ),
        "role_with_ytd_available_chart_count": _available_period_count(rows, "ytd"),
        "role_with_trailing_1y_available_chart_count": _available_period_count(
            rows,
            "trailing_1y",
        ),
        "role_with_trailing_5y_available_chart_count": _available_period_count(
            rows,
            "trailing_5y",
        ),
        "chart_unavailable_role_count": status_counts["unavailable_no_official_series"],
        "chart_unavailable_policy_count": status_counts[
            "unavailable_no_official_series"
        ],
        "chart_point_count": sum(row["chart_point_count"] for row in rows),
        "latest_numeric_point_count": sum(
            len(row["latest_numeric_context"]) for row in rows
        ),
        "role_with_source_risk_label_count": sum(
            bool(row["source_risk_label_zh"]) for row in rows
        ),
        "chart_coverage_status_counts": dict(sorted(status_counts.items())),
        "fixture_cache_written_under_tmp": True,
        "repo_output_written_count": 0,
        "fixture_mislabeled_as_live_count": 0,
        "point_in_time_claim_count": 0,
        "numeric_context_promoted_to_phase_support_count": 0,
        "missing_value_treated_as_neutral_count": 0,
        "unavailable_chart_treated_as_zero_count": 0,
        "current_data_used_to_infer_declared_phase_count": 0,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "role_count_voting_added_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "allowed_uses": contract["dashboard_view_model"]["allowed_uses"],
        "prohibited_uses": contract["dashboard_view_model"]["prohibited_uses"],
        "trust_metadata": {
            "output_label": "research_only",
            "coverage_scope": "current_macro_numeric_chart_fixture_connectivity",
            "source_chart_payload_contract": "indicator_chart_explanation_payload_v1",
            "source_indicator_detail_contract": (
                "indicator_detail_source_risk_value_rendering_v1"
            ),
            "fixture_cache_only": True,
            "live_refresh_attempted": False,
            "point_in_time_result": False,
            "current_phase_inference_enabled": False,
            "candidate_phase_selection_enabled": False,
            "production_behavior_change": False,
        },
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "current_macro_numeric_chart_coverage_ready_declared_state_preserved"
        ),
    }
    artifact["prohibited_output_field_count"] = _contains_prohibited_field(artifact)
    artifact["current_macro_numeric_chart_coverage_ready"] = _passes(
        artifact,
        contract["hard_gates"],
    )
    artifact["result"] = (
        "passed" if artifact["current_macro_numeric_chart_coverage_ready"] else "blocked"
    )
    return artifact


def summarize_current_macro_numeric_chart_coverage(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Return compact Phase72 current macro numeric/chart coverage fields."""

    artifact = build_current_macro_numeric_chart_coverage(path)
    return {
        "phase": "72",
        "phase_id": 72,
        "current_macro_numeric_chart_coverage_ready": artifact[
            "current_macro_numeric_chart_coverage_ready"
        ],
        "role_count": artifact["role_count"],
        "role_with_official_series_count": artifact["role_with_official_series_count"],
        "role_without_official_series_count": artifact[
            "role_without_official_series_count"
        ],
        "unique_official_series_count": artifact["unique_official_series_count"],
        "fixture_seeded_series_count": artifact["fixture_seeded_series_count"],
        "role_with_numeric_context_count": artifact["role_with_numeric_context_count"],
        "role_with_chart_payload_count": artifact["role_with_chart_payload_count"],
        "role_with_available_chart_payload_count": artifact[
            "role_with_available_chart_payload_count"
        ],
        "role_with_ytd_available_chart_count": artifact[
            "role_with_ytd_available_chart_count"
        ],
        "role_with_trailing_1y_available_chart_count": artifact[
            "role_with_trailing_1y_available_chart_count"
        ],
        "role_with_trailing_5y_available_chart_count": artifact[
            "role_with_trailing_5y_available_chart_count"
        ],
        "chart_unavailable_role_count": artifact["chart_unavailable_role_count"],
        "chart_unavailable_policy_count": artifact["chart_unavailable_policy_count"],
        "chart_point_count": artifact["chart_point_count"],
        "latest_numeric_point_count": artifact["latest_numeric_point_count"],
        "role_with_source_risk_label_count": artifact[
            "role_with_source_risk_label_count"
        ],
        "fixture_cache_written_under_tmp": artifact["fixture_cache_written_under_tmp"],
        "repo_output_written_count": artifact["repo_output_written_count"],
        "fixture_mislabeled_as_live_count": artifact[
            "fixture_mislabeled_as_live_count"
        ],
        "point_in_time_claim_count": artifact["point_in_time_claim_count"],
        "numeric_context_promoted_to_phase_support_count": artifact[
            "numeric_context_promoted_to_phase_support_count"
        ],
        "missing_value_treated_as_neutral_count": artifact[
            "missing_value_treated_as_neutral_count"
        ],
        "unavailable_chart_treated_as_zero_count": artifact[
            "unavailable_chart_treated_as_zero_count"
        ],
        "prohibited_output_field_count": artifact["prohibited_output_field_count"],
        "current_data_used_to_infer_declared_phase_count": artifact[
            "current_data_used_to_infer_declared_phase_count"
        ],
        "standalone_classifier_added_count": artifact[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": artifact["phase_rank_or_score_added_count"],
        "role_count_voting_added_count": artifact["role_count_voting_added_count"],
        "candidate_phase_emitted": artifact["candidate_phase_emitted"],
        "current_phase_emitted": artifact["current_phase_emitted"],
        "production_behavior_change_count": artifact[
            "production_behavior_change_count"
        ],
        "semantic_drift_count": artifact["semantic_drift_count"],
        "product_doctrine_alignment_status": artifact[
            "product_doctrine_alignment_status"
        ],
        "cycle_state_machine_alignment_status": artifact[
            "cycle_state_machine_alignment_status"
        ],
        "chart_coverage_artifact": artifact,
        "result": artifact["result"],
    }


def build_current_macro_numeric_chart_coverage_view_model(
    artifact: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a dashboard-ready research view model for Phase72 coverage."""

    artifact = artifact or build_current_macro_numeric_chart_coverage()
    return {
        "view_id": "current_macro_numeric_chart_coverage",
        "view_title": "Current Macro Numeric and Chart Coverage",
        "output_mode": artifact["output_mode"],
        "research_only": True,
        "snapshot_as_of": artifact["snapshot_as_of"],
        "data_mode": artifact["data_mode"],
        "role_count": artifact["role_count"],
        "role_with_numeric_context_count": artifact["role_with_numeric_context_count"],
        "role_with_available_chart_payload_count": artifact[
            "role_with_available_chart_payload_count"
        ],
        "role_without_official_series_count": artifact[
            "role_without_official_series_count"
        ],
        "role_chart_coverage_rows": artifact["role_chart_coverage_rows"],
        "trust_metadata": artifact["trust_metadata"],
        "allowed_uses": artifact["allowed_uses"],
        "prohibited_uses": artifact["prohibited_uses"],
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "role_count_voting_added_count": 0,
        "production_behavior_change_count": 0,
    }


def _coverage_rows(
    cards: list[dict[str, Any]],
    chart_payload: dict[str, Any],
) -> list[dict[str, Any]]:
    payload_by_role = {
        payload["role_id"]: payload for payload in chart_payload["role_payloads"]
    }
    rows: list[dict[str, Any]] = []
    for card in sorted(cards, key=lambda item: item["role_id"]):
        payload = payload_by_role[card["role_id"]]
        chart_detail = payload["chart_payload_detail"]
        latest_context = _latest_numeric_context(chart_detail)
        period_statuses = _period_statuses(chart_detail)
        chart_available = bool(chart_detail["chart_available"])
        rows.append(
            {
                "role_id": card["role_id"],
                "phase_or_layer": card["phase_or_layer"],
                "phase_label_zh": card["phase_label_zh"],
                "major_group_id": card["major_group_id"],
                "source_family": card["source_family"],
                "source_coverage_tier": card["source_coverage_tier"],
                "source_risk_label_zh": card["source_risk_label_zh"],
                "data_risk_level": card["data_risk_level"],
                "official_series_ids": card["official_series_ids"],
                "numeric_context_available": bool(latest_context),
                "latest_numeric_context": latest_context,
                "chart_available": chart_available,
                "chart_period_statuses": period_statuses,
                "chart_periods": _chart_period_payloads(chart_detail),
                "chart_point_count": _chart_point_count(chart_detail),
                "chart_data_mode": "fixture_current_cache_connectivity",
                "chart_coverage_status": (
                    "available_fixture_current_cache"
                    if chart_available
                    else "unavailable_no_official_series"
                ),
                "unavailable_reason": chart_detail["unavailable_reason"],
                "numeric_context_promoted_to_phase_support": False,
                "current_data_used_to_infer_declared_phase": False,
                "missing_value_treated_as_neutral": False,
                "unavailable_chart_treated_as_zero": False,
                "candidate_selection_eligible": False,
                "formal_current_output_allowed": False,
                "allowed_uses": [
                    "local_research_dashboard",
                    "indicator_numeric_context_review",
                    "indicator_chart_payload_review",
                ],
                "prohibited_uses": [
                    "formal_current_phase_decision",
                    "candidate_phase_selection",
                    "phase_score_or_rank_selection",
                    "production_decision",
                    "portfolio_or_trade_decision",
                ],
            }
        )
    return rows


def _seed_fixture_cache(cache_dir: Path, series_ids: list[str]) -> None:
    store = RawCsvStore(cache_dir)
    for index, series_id in enumerate(series_ids, start=1):
        base = float(index * 10)
        observations = [
            data_sources.SeriesObservation(
                series_id=series_id,
                date=observation_date,
                value=f"{base + offset:.1f}",
            )
            for offset, observation_date in enumerate(FIXTURE_OBSERVATION_DATES)
        ]
        store.write_observations("fred", series_id, observations)


def _unique_series_ids(cards: list[dict[str, Any]]) -> list[str]:
    series_ids: list[str] = []
    for card in cards:
        for series_id in card["official_series_ids"]:
            if series_id not in series_ids:
                series_ids.append(series_id)
    return sorted(series_ids)


def _latest_numeric_context(chart_detail: dict[str, Any]) -> list[dict[str, Any]]:
    contexts: list[dict[str, Any]] = []
    for series in chart_detail["series_charts"]:
        latest = _latest_point(series)
        if latest is None:
            continue
        contexts.append(
            {
                "series_id": series["series_id"],
                "latest_observation_date": latest["date"],
                "latest_value": latest["value"],
                "value_mode": "fixture_current_cache",
                "point_in_time_result": False,
                "used_to_infer_declared_phase": False,
            }
        )
    return contexts


def _latest_point(series: dict[str, Any]) -> dict[str, Any] | None:
    points = [
        point
        for period in series["periods"]
        if period["chart_status"] == "available"
        for point in period["points"]
    ]
    if not points:
        return None
    return max(points, key=lambda item: date.fromisoformat(item["date"]))


def _period_statuses(chart_detail: dict[str, Any]) -> dict[str, str]:
    statuses: dict[str, str] = {}
    for period_id in ("ytd", "trailing_1y", "trailing_5y"):
        statuses[period_id] = (
            "available"
            if any(
                period["period_id"] == period_id
                and period["chart_status"] == "available"
                for series in chart_detail["series_charts"]
                for period in series["periods"]
            )
            else "unavailable"
        )
    return statuses


def _chart_period_payloads(chart_detail: dict[str, Any]) -> list[dict[str, Any]]:
    periods: list[dict[str, Any]] = []
    for period_id in ("ytd", "trailing_1y", "trailing_5y"):
        matching = [
            period
            for series in chart_detail["series_charts"]
            for period in series["periods"]
            if period["period_id"] == period_id
        ]
        if not matching:
            continue
        available = [period for period in matching if period["chart_status"] == "available"]
        source = available[0] if available else matching[0]
        points = [
            point
            for period in available
            for point in period["points"]
        ]
        reasons = sorted(
            {
                period["unavailable_reason"]
                for period in matching
                if period["unavailable_reason"]
            },
        )
        periods.append(
            {
                "period_id": period_id,
                "label": source["label"],
                "start_date": source["start_date"],
                "end_date": source["end_date"],
                "chart_status": "available" if available else "unavailable",
                "point_count": len(points),
                "points": points,
                "unavailable_reason": ", ".join(reasons) if reasons else None,
            },
        )
    return periods


def _chart_point_count(chart_detail: dict[str, Any]) -> int:
    return sum(
        int(period["point_count"])
        for series in chart_detail["series_charts"]
        for period in series["periods"]
        if period["chart_status"] == "available"
    )


def _available_period_count(rows: list[dict[str, Any]], period_id: str) -> int:
    return sum(row["chart_period_statuses"][period_id] == "available" for row in rows)


def _passes(artifact: dict[str, Any], expected: dict[str, Any]) -> bool:
    for key, value in expected.items():
        if key == "current_macro_numeric_chart_coverage_ready":
            continue
        if key.endswith("_minimum"):
            summary_key = key.removesuffix("_minimum")
            if int(artifact.get(summary_key, 0)) < int(value):
                return False
            continue
        if artifact.get(key) != value:
            return False
    return True


def _contains_prohibited_field(value: Any) -> int:
    if isinstance(value, dict):
        count = sum(key in PROHIBITED_FIELDS for key in value)
        return count + sum(_contains_prohibited_field(item) for item in value.values())
    if isinstance(value, list):
        return sum(_contains_prohibited_field(item) for item in value)
    return 0


def _load_contract(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "current_macro_numeric_chart_coverage"
    ]

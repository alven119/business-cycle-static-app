"""Phase74 local current-cache bridge for dashboard numeric/chart context."""

from __future__ import annotations

from collections import Counter
from datetime import date
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
DEFAULT_CONTRACT_PATH = ROOT / "specs/common/local_current_cache_dashboard_bridge.yaml"
DEFAULT_LOCAL_CACHE_ROOT = Path("data/raw/fred_current_cache")
TMP_ROOT = Path("/tmp")
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


def build_local_current_cache_dashboard_bridge(
    *,
    cache_dir: str | Path | None = None,
    snapshot_as_of: str = SNAPSHOT_AS_OF,
    seed_tmp_cache_when_missing: bool = True,
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Build a research-only dashboard bridge from explicit local current cache."""

    contract = _load_contract(path)
    if cache_dir is None and seed_tmp_cache_when_missing:
        with tempfile.TemporaryDirectory(
            prefix="phase74_local_current_cache_",
            dir="/tmp",
        ) as tmp:
            tmp_cache_dir = Path(tmp) / "fred_current_cache"
            cards = build_indicator_detail_source_risk_value_cards()
            _seed_local_cache_rehearsal(tmp_cache_dir, _unique_series_ids(cards))
            return _build_bridge_from_cache(
                contract,
                cache_dir=tmp_cache_dir,
                snapshot_as_of=snapshot_as_of,
                cache_scope="tmp_seeded_local_current_cache_rehearsal",
                cache_dir_kind="tmp",
                tmp_seeded_rehearsal=True,
            )

    resolved_cache_dir = _validated_cache_dir(cache_dir) if cache_dir else None
    return _build_bridge_from_cache(
        contract,
        cache_dir=resolved_cache_dir,
        snapshot_as_of=snapshot_as_of,
        cache_scope=(
            "explicit_local_current_cache"
            if resolved_cache_dir is not None
            else "local_current_cache_not_supplied"
        ),
        cache_dir_kind=_cache_dir_kind(resolved_cache_dir),
        tmp_seeded_rehearsal=False,
    )


def summarize_local_current_cache_dashboard_bridge(
    *,
    cache_dir: str | Path | None = None,
    snapshot_as_of: str = SNAPSHOT_AS_OF,
    seed_tmp_cache_when_missing: bool = True,
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Return compact Phase74 bridge readiness fields."""

    artifact = build_local_current_cache_dashboard_bridge(
        cache_dir=cache_dir,
        snapshot_as_of=snapshot_as_of,
        seed_tmp_cache_when_missing=seed_tmp_cache_when_missing,
        path=path,
    )
    return {
        "phase": "74",
        "phase_id": 74,
        "local_current_cache_dashboard_bridge_ready": artifact[
            "local_current_cache_dashboard_bridge_ready"
        ],
        "local_current_cache_input_supported": artifact[
            "local_current_cache_input_supported"
        ],
        "tmp_seeded_local_current_cache_rehearsal_ready": artifact[
            "tmp_seeded_local_current_cache_rehearsal_ready"
        ],
        "role_count": artifact["role_count"],
        "role_with_official_series_count": artifact["role_with_official_series_count"],
        "role_without_official_series_count": artifact[
            "role_without_official_series_count"
        ],
        "unique_official_series_count": artifact["unique_official_series_count"],
        "local_cache_series_file_found_count": artifact[
            "local_cache_series_file_found_count"
        ],
        "role_with_local_cache_numeric_context_count": artifact[
            "role_with_local_cache_numeric_context_count"
        ],
        "role_with_available_local_cache_chart_count": artifact[
            "role_with_available_local_cache_chart_count"
        ],
        "role_with_ytd_available_local_cache_chart_count": artifact[
            "role_with_ytd_available_local_cache_chart_count"
        ],
        "role_with_trailing_1y_available_local_cache_chart_count": artifact[
            "role_with_trailing_1y_available_local_cache_chart_count"
        ],
        "role_with_trailing_5y_available_local_cache_chart_count": artifact[
            "role_with_trailing_5y_available_local_cache_chart_count"
        ],
        "local_cache_unavailable_role_count": artifact[
            "local_cache_unavailable_role_count"
        ],
        "local_cache_chart_point_count": artifact["local_cache_chart_point_count"],
        "cache_scope": artifact["cache_scope"],
        "cache_dir_kind": artifact["cache_dir_kind"],
        "data_mode": artifact["data_mode"],
        "repo_output_written_count": artifact["repo_output_written_count"],
        "local_cache_written_by_bridge_count": artifact[
            "local_cache_written_by_bridge_count"
        ],
        "fixture_mislabeled_as_live_count": artifact[
            "fixture_mislabeled_as_live_count"
        ],
        "local_cache_value_mislabeled_as_point_in_time_count": artifact[
            "local_cache_value_mislabeled_as_point_in_time_count"
        ],
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
        "local_current_cache_bridge_artifact": artifact,
        "result": artifact["result"],
    }


def build_local_current_cache_dashboard_bridge_view_model(
    artifact: dict[str, Any] | None = None,
    *,
    cache_dir: str | Path | None = None,
    snapshot_as_of: str = SNAPSHOT_AS_OF,
    seed_tmp_cache_when_missing: bool = True,
) -> dict[str, Any]:
    """Build a dashboard-ready view model with the Phase72-compatible shape."""

    artifact = artifact or build_local_current_cache_dashboard_bridge(
        cache_dir=cache_dir,
        snapshot_as_of=snapshot_as_of,
        seed_tmp_cache_when_missing=seed_tmp_cache_when_missing,
    )
    return {
        "view_id": "current_macro_numeric_chart_coverage",
        "view_title": "Local Current Cache Numeric and Chart Bridge",
        "output_mode": artifact["output_mode"],
        "research_only": True,
        "snapshot_as_of": artifact["snapshot_as_of"],
        "data_mode": artifact["data_mode"],
        "cache_scope": artifact["cache_scope"],
        "cache_dir_kind": artifact["cache_dir_kind"],
        "role_count": artifact["role_count"],
        "role_with_numeric_context_count": artifact[
            "role_with_local_cache_numeric_context_count"
        ],
        "role_with_available_chart_payload_count": artifact[
            "role_with_available_local_cache_chart_count"
        ],
        "role_without_official_series_count": artifact[
            "role_without_official_series_count"
        ],
        "role_chart_coverage_rows": artifact["role_chart_coverage_rows"],
        "trust_metadata": artifact["trust_metadata"],
        "allowed_uses": artifact["allowed_uses"],
        "prohibited_uses": artifact["prohibited_uses"],
        "phase74_local_current_cache_bridge_ready": artifact[
            "local_current_cache_dashboard_bridge_ready"
        ],
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "role_count_voting_added_count": 0,
        "production_behavior_change_count": 0,
    }


def seed_local_current_cache_rehearsal(cache_dir: str | Path) -> dict[str, Any]:
    """Seed tmp-path tests with current-cache-shaped CSV files."""

    cache_root = _validated_cache_dir(cache_dir)
    cards = build_indicator_detail_source_risk_value_cards()
    series_ids = _unique_series_ids(cards)
    _seed_local_cache_rehearsal(cache_root, series_ids)
    return {
        "cache_dir": str(cache_root),
        "seeded_series_count": len(series_ids),
        "seeded_cache_under_tmp": _cache_dir_kind(cache_root) == "tmp",
    }


def _build_bridge_from_cache(
    contract: dict[str, Any],
    *,
    cache_dir: Path | None,
    snapshot_as_of: str,
    cache_scope: str,
    cache_dir_kind: str,
    tmp_seeded_rehearsal: bool,
) -> dict[str, Any]:
    cards = build_indicator_detail_source_risk_value_cards()
    official_series_ids = _unique_series_ids(cards)
    chart_payload = build_indicator_chart_explanation_payload(
        cache_dir=cache_dir,
        snapshot_as_of=snapshot_as_of,
    )
    rows = _coverage_rows(cards, chart_payload)
    status_counts = Counter(row["chart_coverage_status"] for row in rows)
    phase_counts = Counter(row["phase_or_layer"] for row in rows)
    data_mode = (
        "revised_tmp_seeded_local_current_cache_rehearsal"
        if tmp_seeded_rehearsal
        else "revised_explicit_local_current_cache"
        if cache_dir is not None
        else "local_current_cache_not_supplied"
    )
    artifact: dict[str, Any] = {
        "artifact_id": contract["contract_id"],
        "artifact_version": contract["contract_version"],
        "phase": "74",
        "phase_id": 74,
        "phase_label": "local_current_cache_dashboard_bridge",
        "output_mode": contract["policy"]["output_mode"],
        "research_only": True,
        "snapshot_as_of": snapshot_as_of,
        "data_mode": data_mode,
        "cache_scope": cache_scope,
        "cache_dir_kind": cache_dir_kind,
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
        "local_cache_series_file_found_count": _cache_file_found_count(
            cache_dir,
            official_series_ids,
        ),
        "role_with_local_cache_numeric_context_count": sum(
            row["numeric_context_available"] for row in rows
        ),
        "role_with_available_local_cache_chart_count": sum(
            row["chart_available"] for row in rows
        ),
        "role_with_ytd_available_local_cache_chart_count": _available_period_count(
            rows,
            "ytd",
        ),
        "role_with_trailing_1y_available_local_cache_chart_count": (
            _available_period_count(rows, "trailing_1y")
        ),
        "role_with_trailing_5y_available_local_cache_chart_count": (
            _available_period_count(rows, "trailing_5y")
        ),
        "local_cache_unavailable_role_count": sum(
            not row["chart_available"] for row in rows
        ),
        "local_cache_chart_point_count": sum(row["chart_point_count"] for row in rows),
        "chart_coverage_status_counts": dict(sorted(status_counts.items())),
        "local_current_cache_input_supported": True,
        "tmp_seeded_local_current_cache_rehearsal_ready": cache_dir is not None,
        "repo_output_written_count": 0,
        "local_cache_written_by_bridge_count": 0,
        "fixture_mislabeled_as_live_count": 0,
        "local_cache_value_mislabeled_as_point_in_time_count": 0,
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
            "coverage_scope": cache_scope,
            "source_chart_payload_contract": "indicator_chart_explanation_payload_v1",
            "source_current_data_refresh_contract": "phase40_current_data_refresh_contract",
            "local_cache_values_are_revised_latest": True,
            "live_refresh_attempted_by_bridge": False,
            "tmp_seeded_rehearsal": tmp_seeded_rehearsal,
            "point_in_time_result": False,
            "current_phase_inference_enabled": False,
            "candidate_phase_selection_enabled": False,
            "production_behavior_change": False,
            "cache_display_label": (
                "tmp seeded local-cache rehearsal"
                if tmp_seeded_rehearsal
                else "explicit ignored local current cache"
                if cache_dir is not None
                else "local current cache not supplied"
            ),
            "value_caveat": (
                "local cache values are revised/latest context, not point-in-time "
                "evidence and not phase support"
            ),
        },
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "local_current_cache_bridge_ready_declared_state_preserved"
        ),
    }
    artifact["prohibited_output_field_count"] = _contains_prohibited_field(artifact)
    artifact["local_current_cache_dashboard_bridge_ready"] = _passes(
        artifact,
        contract["hard_gates"],
    )
    artifact["result"] = (
        "passed"
        if artifact["local_current_cache_dashboard_bridge_ready"]
        else "blocked"
    )
    return artifact


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
                "chart_period_statuses": _period_statuses(chart_detail),
                "chart_periods": _chart_period_payloads(chart_detail),
                "chart_point_count": _chart_point_count(chart_detail),
                "chart_data_mode": "revised_local_current_cache_context",
                "chart_coverage_status": _chart_coverage_status(
                    has_official_series=bool(card["official_series_ids"]),
                    chart_available=chart_available,
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
                    "current_numeric_context_review",
                    "current_chart_payload_review",
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


def _seed_local_cache_rehearsal(cache_dir: Path, series_ids: list[str]) -> None:
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
                "value_mode": "revised_local_current_cache_context",
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
        available = [
            period for period in matching if period["chart_status"] == "available"
        ]
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


def _chart_coverage_status(
    *,
    has_official_series: bool,
    chart_available: bool,
) -> str:
    if chart_available:
        return "available_local_current_cache"
    if not has_official_series:
        return "unavailable_no_official_series"
    return "unavailable_local_current_cache_missing"


def _available_period_count(rows: list[dict[str, Any]], period_id: str) -> int:
    return sum(row["chart_period_statuses"][period_id] == "available" for row in rows)


def _cache_file_found_count(cache_dir: Path | None, series_ids: list[str]) -> int:
    if cache_dir is None:
        return 0
    store = RawCsvStore(cache_dir)
    return sum(store.exists("fred", series_id) for series_id in series_ids)


def _validated_cache_dir(cache_dir: str | Path) -> Path:
    path = Path(cache_dir)
    resolved = path.resolve()
    if resolved == TMP_ROOT.resolve() or TMP_ROOT.resolve() in resolved.parents:
        return path
    try:
        resolved.relative_to(DEFAULT_LOCAL_CACHE_ROOT.resolve())
    except ValueError as exc:
        raise ValueError(
            "local current cache must be under /tmp or data/raw/fred_current_cache"
        ) from exc
    return path


def _cache_dir_kind(cache_dir: Path | None) -> str:
    if cache_dir is None:
        return "none"
    resolved = cache_dir.resolve()
    if resolved == TMP_ROOT.resolve() or TMP_ROOT.resolve() in resolved.parents:
        return "tmp"
    try:
        resolved.relative_to(DEFAULT_LOCAL_CACHE_ROOT.resolve())
    except ValueError:
        return "unsupported"
    return "ignored_local_current_cache"


def _passes(artifact: dict[str, Any], expected: dict[str, Any]) -> bool:
    for key, value in expected.items():
        if key == "local_current_cache_dashboard_bridge_ready":
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
        "local_current_cache_dashboard_bridge"
    ]

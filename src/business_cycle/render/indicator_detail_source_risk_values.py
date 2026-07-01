"""Phase56 indicator-detail source-risk and value-context cards."""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.macro_indicator_coverage_readiness_matrix import (
    build_macro_indicator_coverage_readiness_rows,
)
from business_cycle.current.composite_transition_surface_values import (
    build_composite_transition_surface_value_rows,
)
from business_cycle.current.current_data_refresh import (
    build_current_data_refresh_manifest,
)
from business_cycle.current.current_freshness_semantics import (
    freshness_rows_by_series,
    summarize_current_freshness_semantics,
)
from business_cycle.current.official_macro_source_wiring import (
    resolve_official_series_ids,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = (
    ROOT / "specs/common/indicator_detail_source_risk_value_rendering.yaml"
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

SOURCE_RISK_LABELS_ZH = {
    "low": "低：官方或近官方資料路徑已明確。",
    "low_medium": "低到中：官方資料可用，但仍需轉換或 release 對齊。",
    "medium": "中：需要 composite、rule semantics 或資料模式對齊。",
    "medium_high": "中高：目前只能作 supporting context，不能補 book-core。",
    "high_until_license_confirmed": "高：直接來源需要授權、授權確認或使用者自備資料。",
}


@lru_cache(maxsize=1)
def build_indicator_detail_source_risk_value_cards(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> list[dict[str, Any]]:
    """Build one research-only indicator detail card per Phase55 macro role."""

    _load_contract(path)
    manifest = build_current_data_refresh_manifest(
        no_live_fetch=True,
        allow_fixture_fallback=True,
    )
    freshness = summarize_current_freshness_semantics(refresh_manifest=manifest)
    freshness_by_series = freshness_rows_by_series(freshness)
    value_rows = {
        row["role_id"]: row
        for row in build_composite_transition_surface_value_rows(
            refresh_manifest=manifest,
        )
    }
    cards: list[dict[str, Any]] = []
    for coverage in build_macro_indicator_coverage_readiness_rows():
        role_id = coverage["role_id"]
        value_row = value_rows.get(role_id)
        official_series = _official_series(coverage, value_row=value_row)
        latest_context = _latest_observation_context(
            official_series,
            value_row=value_row,
            freshness_by_series=freshness_by_series,
            coverage=coverage,
        )
        numeric_value_count = sum(
            item.get("latest_value") is not None for item in latest_context
        )
        card = {
            "role_id": role_id,
            "phase_or_layer": coverage["phase_or_layer"],
            "phase_label_zh": coverage["phase_label_zh"],
            "major_group_id": coverage["major_group_id"],
            "gap_type": coverage["gap_type"],
            "source_family": coverage["source_family"],
            "source_coverage_tier": coverage["source_coverage_tier"],
            "source_risk_visible": True,
            "source_risk_label_zh": SOURCE_RISK_LABELS_ZH[
                coverage["data_risk_level"]
            ],
            "data_risk_level": coverage["data_risk_level"],
            "substitution_degree": coverage["substitution_degree"],
            "coverage_status": coverage["coverage_status"],
            "dashboard_display_status": coverage["dashboard_display_status"],
            "evidence_usability_status": coverage["evidence_usability_status"],
            "official_series_ids": official_series,
            "latest_observation_context": latest_context,
            "numeric_value_loaded_count": numeric_value_count,
            "value_context_visible": True,
            "value_context_status": _value_context_status(
                coverage=coverage,
                latest_context=latest_context,
                value_row=value_row,
            ),
            "freshness_context_visible": True,
            "freshness_context_summary": _freshness_context_summary(
                coverage=coverage,
                latest_context=latest_context,
            ),
            "release_timing_context_visible": True,
            "release_timing_context": _release_timing_context(
                coverage=coverage,
                latest_context=latest_context,
            ),
            "transformation_context_visible": True,
            "transformation_semantics_status": _transformation_status(
                coverage,
                value_row=value_row,
            ),
            "why_not_evidence_visible": True,
            "why_not_evidence_zh": _why_not_evidence(coverage, value_row=value_row),
            "dashboard_explanation_zh": coverage["dashboard_explanation_zh"],
            "next_gap_zh": coverage["next_gap_zh"],
            "supporting_proxy_only": coverage["supporting_proxy_only"],
            "user_authorized_input_required": coverage[
                "user_authorized_input_required"
            ],
            "book_core_replacement_allowed": coverage[
                "book_core_replacement_allowed"
            ],
            "supporting_proxy_can_replace_book_core": False,
            "silent_substitution": False,
            "alternative_promoted_to_core": False,
            "false_resolution": False,
            "phase_support_added": False,
            "candidate_selection_eligible": False,
            "formal_current_output_allowed": False,
            "allowed_uses": [
                "local_research_dashboard",
                "indicator_detail_explanation",
                "source_risk_explanation",
                "freshness_and_release_review",
            ],
            "prohibited_uses": [
                "formal_current_phase_decision",
                "candidate_phase_selection",
                "phase_score_or_rank_selection",
                "production_decision",
                "portfolio_or_trade_decision",
            ],
        }
        card["prohibited_output_field_count"] = _contains_prohibited_field(card)
        cards.append(card)
    return cards


@lru_cache(maxsize=1)
def summarize_indicator_detail_source_risk_value_rendering(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Summarize Phase56 indicator detail hard gates."""

    contract = _load_contract(path)
    expected = contract["hard_gates"]
    cards = build_indicator_detail_source_risk_value_cards(path)
    phase_counts = Counter(card["phase_or_layer"] for card in cards)
    view_model = build_indicator_detail_source_risk_value_view_model(cards)
    summary: dict[str, Any] = {
        "indicator_detail_source_risk_value_rendering_ready": False,
        "phase": "56",
        "phase_id": "56",
        "indicator_detail_source_risk_ready": all(
            card["source_risk_visible"] and bool(card["source_risk_label_zh"])
            for card in cards
        ),
        "indicator_detail_value_context_ready": all(
            card["value_context_visible"] and bool(card["value_context_status"])
            for card in cards
        ),
        "indicator_detail_card_count": len(cards),
        "phase_count": len(phase_counts),
        "phase_with_indicator_detail_count": sum(
            count > 0 for count in phase_counts.values()
        ),
        "phase_counts": dict(sorted(phase_counts.items())),
        "source_risk_visible_card_count": sum(
            card["source_risk_visible"] for card in cards
        ),
        "freshness_context_visible_card_count": sum(
            card["freshness_context_visible"] for card in cards
        ),
        "release_timing_context_visible_card_count": sum(
            card["release_timing_context_visible"] for card in cards
        ),
        "value_context_visible_card_count": sum(
            card["value_context_visible"] for card in cards
        ),
        "transformation_context_visible_card_count": sum(
            card["transformation_context_visible"] for card in cards
        ),
        "why_not_evidence_visible_card_count": sum(
            card["why_not_evidence_visible"] for card in cards
        ),
        "authorized_input_missing_card_count": sum(
            card["user_authorized_input_required"] for card in cards
        ),
        "supporting_proxy_only_card_count": sum(
            card["supporting_proxy_only"] for card in cards
        ),
        "numeric_value_loaded_card_count": sum(
            card["numeric_value_loaded_count"] > 0 for card in cards
        ),
        "proxy_promoted_to_book_core_count": sum(
            card["supporting_proxy_can_replace_book_core"] for card in cards
        ),
        "silent_substitution_count": sum(card["silent_substitution"] for card in cards),
        "false_resolution_count": sum(card["false_resolution"] for card in cards),
        "prohibited_output_field_count": sum(
            card["prohibited_output_field_count"] for card in cards
        )
        + _contains_prohibited_field(view_model),
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "dashboard_view_model_ready": _view_model_ready(view_model, cards),
        "dashboard_view_model": view_model,
        "cards": cards,
    }
    summary["indicator_detail_source_risk_value_rendering_ready"] = _passes(
        summary,
        expected,
    )
    summary["result"] = (
        "passed"
        if summary["indicator_detail_source_risk_value_rendering_ready"]
        else "blocked"
    )
    return summary


def build_indicator_detail_source_risk_value_view_model(
    cards: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a research-only dashboard view model for indicator detail cards."""

    cards = cards or build_indicator_detail_source_risk_value_cards()
    return {
        "view_id": "indicator_detail_source_risk_value_cards",
        "view_title": "Indicator Detail Source Risk and Value Context",
        "output_mode": "research_only_indicator_detail_context",
        "research_only": True,
        "card_count": len(cards),
        "cards": cards,
        "trust_metadata": {
            "output_label": "research_only",
            "coverage_scope": "indicator_detail_source_value_context",
            "current_phase_inference_enabled": False,
            "candidate_phase_selection_enabled": False,
            "production_behavior_change": False,
            "numeric_value_required_for_display": False,
        },
        "allowed_uses": [
            "local_research_dashboard",
            "indicator_detail_explanation",
            "source_risk_explanation",
            "freshness_and_release_review",
        ],
        "prohibited_uses": [
            "formal_current_phase_decision",
            "candidate_phase_selection",
            "production_decision",
            "portfolio_or_trade_decision",
        ],
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "phase_rank_or_score_added_count": 0,
        "standalone_classifier_added_count": 0,
    }


def _official_series(
    coverage: dict[str, Any],
    *,
    value_row: dict[str, Any] | None,
) -> list[str]:
    if value_row is not None:
        return list(value_row["official_source_series_ids"])
    return resolve_official_series_ids(tuple(coverage["required_series_ids"]))


def _latest_observation_context(
    series_ids: list[str],
    *,
    value_row: dict[str, Any] | None,
    freshness_by_series: dict[str, dict[str, Any]],
    coverage: dict[str, Any],
) -> list[dict[str, Any]]:
    if value_row is not None:
        return [
            _merge_value_and_freshness_context(
                item,
                freshness_by_series=freshness_by_series,
            )
            for item in value_row["series_context"]
        ]
    if not series_ids:
        return [
            {
                "series_id": "authorized_or_unresolved_input",
                "metadata_ready": False,
                "source_mode": "missing_until_authorized_input"
                if coverage["user_authorized_input_required"]
                else "missing_until_source_contract",
                "frequency": "unknown",
                "release_family": "unknown",
                "latest_observation_date": None,
                "latest_value": None,
                "value_source": "not_loaded",
                "freshness_status": "missing_source",
                "freshness_reason": "authorized user input or source contract required",
                "expected_reference_period": "unknown",
                "observed_reference_period": "unknown",
            }
        ]
    return [
        _freshness_only_context(series_id, freshness_by_series=freshness_by_series)
        for series_id in series_ids
    ]


def _merge_value_and_freshness_context(
    item: dict[str, Any],
    *,
    freshness_by_series: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    freshness = freshness_by_series.get(item["series_id"], {})
    return {
        **item,
        "freshness_status": freshness.get("freshness_status", "unknown"),
        "freshness_reason": freshness.get("freshness_reason", "not in refresh manifest"),
        "expected_reference_period": freshness.get(
            "expected_reference_period",
            "unknown",
        ),
        "observed_reference_period": freshness.get(
            "observed_reference_period",
            "unknown",
        ),
    }


def _freshness_only_context(
    series_id: str,
    *,
    freshness_by_series: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    freshness = freshness_by_series.get(series_id, {})
    return {
        "series_id": series_id,
        "metadata_ready": bool(freshness),
        "source_mode": freshness.get("source_mode", "missing"),
        "frequency": freshness.get("frequency", "unknown"),
        "release_family": freshness.get("release_family", "unknown"),
        "latest_observation_date": freshness.get("latest_observation_date"),
        "latest_value": None,
        "value_source": "metadata_only",
        "freshness_status": freshness.get("freshness_status", "missing_source"),
        "freshness_reason": freshness.get(
            "freshness_reason",
            "series is not present in current refresh manifest",
        ),
        "expected_reference_period": freshness.get(
            "expected_reference_period",
            "unknown",
        ),
        "observed_reference_period": freshness.get(
            "observed_reference_period",
            "unknown",
        ),
    }


def _value_context_status(
    *,
    coverage: dict[str, Any],
    latest_context: list[dict[str, Any]],
    value_row: dict[str, Any] | None,
) -> str:
    if coverage["user_authorized_input_required"]:
        return "authorized_private_or_user_input_required_no_numeric_value"
    if coverage["supporting_proxy_only"]:
        return "supporting_proxy_context_visible_not_book_core_value"
    if value_row is not None:
        return str(value_row["value_context_status"])
    if any(item.get("latest_value") is not None for item in latest_context):
        return "numeric_value_context_loaded"
    if all(item.get("metadata_ready") for item in latest_context):
        return "source_metadata_visible_numeric_cache_missing"
    return "source_metadata_incomplete_abstain"


def _freshness_context_summary(
    *,
    coverage: dict[str, Any],
    latest_context: list[dict[str, Any]],
) -> dict[str, Any]:
    statuses = Counter(item["freshness_status"] for item in latest_context)
    return {
        "freshness_status_counts": dict(sorted(statuses.items())),
        "freshness_context_status": (
            "authorized_input_missing"
            if coverage["user_authorized_input_required"]
            else "visible"
        ),
        "fresh_enough_series_count": statuses.get(
            "fresh_enough_for_current_research",
            0,
        ),
        "stale_or_missing_series_count": sum(
            count
            for status, count in statuses.items()
            if status
            in {
                "missing_source",
                "genuinely_stale",
                "source_disabled_for_current_refresh",
                "unavailable_for_current_mode",
            }
        ),
    }


def _release_timing_context(
    *,
    coverage: dict[str, Any],
    latest_context: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "release_context_status": (
            "authorized_input_required"
            if coverage["user_authorized_input_required"]
            else "visible"
        ),
        "series_release_rows": [
            {
                "series_id": item["series_id"],
                "frequency": item["frequency"],
                "release_family": item["release_family"],
                "expected_reference_period": item["expected_reference_period"],
                "observed_reference_period": item["observed_reference_period"],
                "latest_observation_date": item["latest_observation_date"],
                "source_mode": item["source_mode"],
            }
            for item in latest_context
        ],
    }


def _transformation_status(
    coverage: dict[str, Any],
    *,
    value_row: dict[str, Any] | None,
) -> str:
    if value_row is not None:
        return str(value_row["transformation_semantics_status"])
    if coverage["supporting_proxy_only"]:
        return "supporting_proxy_display_only_not_book_core_transformation"
    if coverage["user_authorized_input_required"]:
        return "awaiting_authorized_input_before_transformation"
    if coverage["coverage_status"] == "source_wired_current_value_or_rule_gap_visible":
        return "source_path_visible_transformation_or_rule_gap_remaining"
    return "transformation_or_rule_semantics_pending"


def _why_not_evidence(
    coverage: dict[str, Any],
    *,
    value_row: dict[str, Any] | None,
) -> str:
    if value_row is not None:
        return str(value_row["explicit_abstention_reason"])
    if coverage["supporting_proxy_only"]:
        return "此指標目前只能作 supporting context，不能替代 book-core evidence。"
    if coverage["user_authorized_input_required"]:
        return "直接資料需要授權或使用者自備輸入，未提供前必須顯示缺口。"
    if coverage["coverage_status"] == "source_wired_current_value_or_rule_gap_visible":
        return "來源路徑已可見，但仍缺 current value、freshness 或 rule 對齊。"
    return "來源、轉換或 temporal rule 尚未完整，因此保留為 research detail。"


def _view_model_ready(view_model: dict[str, Any], cards: list[dict[str, Any]]) -> bool:
    return (
        view_model["view_id"] == "indicator_detail_source_risk_value_cards"
        and view_model["output_mode"] == "research_only_indicator_detail_context"
        and len(view_model["cards"]) == len(cards)
        and view_model["candidate_phase_emitted"] is False
        and view_model["current_phase_emitted"] is False
        and _contains_prohibited_field(view_model) == 0
    )


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(
        summary.get(key) == value
        for key, value in expected.items()
        if key != "indicator_detail_source_risk_value_rendering_ready"
    )


def _contains_prohibited_field(value: Any) -> int:
    if isinstance(value, dict):
        if PROHIBITED_FIELDS & set(value):
            return 1
        return int(any(_contains_prohibited_field(item) for item in value.values()))
    if isinstance(value, list):
        return int(any(_contains_prohibited_field(item) for item in value))
    return 0


def _load_contract(path: str | Path = DEFAULT_CONTRACT_PATH) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "indicator_detail_source_risk_value_rendering"
    ]

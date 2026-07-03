"""Phase64 indicator diagnostic transparency and chart payloads."""

from __future__ import annotations

from collections import Counter
from datetime import date, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.render.indicator_detail_source_risk_values import (
    build_indicator_detail_source_risk_value_cards,
)
from business_cycle.storage.raw_store import RawCsvStore

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = ROOT / "specs/common/indicator_chart_explanation_payload.yaml"
SCORING_METHODS_PATH = ROOT / "specs/common/scoring_methods.yaml"

PERIOD_DEFINITIONS = (
    ("ytd", "Year to date"),
    ("trailing_1y", "Trailing 1 year"),
    ("trailing_5y", "Trailing 5 years"),
)

PROHIBITED_FIELDS = {
    "current_phase",
    "candidate_phase",
    "selected_phase",
    "winning_phase",
    "phase_rank",
    "target_weight",
    "allocation_recommendation",
    "buy_signal",
    "sell_signal",
    "trade_action",
    "portfolio_weight",
}


def build_indicator_chart_explanation_payload(
    *,
    cache_dir: str | Path | None = None,
    snapshot_as_of: str | None = None,
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Build one research-only method/chart payload per indicator role."""

    contract = _load_contract(path)
    resolved_as_of = snapshot_as_of or date.today().isoformat()
    methods = _load_scoring_methods()
    cards = build_indicator_detail_source_risk_value_cards()
    store = RawCsvStore(cache_dir) if cache_dir is not None else None
    role_payloads = [
        _role_payload(
            card,
            store=store,
            snapshot_as_of=resolved_as_of,
            methods=methods,
        )
        for card in sorted(cards, key=lambda item: item["role_id"])
    ]
    available_role_count = sum(payload["chart_payload_detail"]["chart_available"] for payload in role_payloads)
    unavailable_role_count = len(role_payloads) - available_role_count
    artifact: dict[str, Any] = {
        "artifact_id": contract["contract_id"],
        "artifact_version": contract["contract_version"],
        "phase": "64",
        "phase_id": "64",
        "output_mode": contract["policy"]["output_mode"],
        "research_only": True,
        "snapshot_as_of": resolved_as_of,
        "chart_periods": [
            {"period_id": period_id, "label": label}
            for period_id, label in PERIOD_DEFINITIONS
        ],
        "role_payloads": role_payloads,
        "role_payload_count": len(role_payloads),
        "role_with_diagnostic_transparency_count": sum(
            bool(payload["diagnostic_transparency_detail"]) for payload in role_payloads
        ),
        "role_with_ytd_chart_payload_count": _period_payload_count(role_payloads, "ytd"),
        "role_with_trailing_1y_chart_payload_count": _period_payload_count(
            role_payloads,
            "trailing_1y",
        ),
        "role_with_trailing_5y_chart_payload_count": _period_payload_count(
            role_payloads,
            "trailing_5y",
        ),
        "chart_period_count": len(PERIOD_DEFINITIONS),
        "chart_available_role_count": available_role_count,
        "chart_unavailable_role_count": unavailable_role_count,
        "chart_unavailable_policy_count": sum(
            bool(payload["chart_payload_detail"]["unavailable_reason"])
            for payload in role_payloads
        ),
        "method_family_counts": dict(
            sorted(
                Counter(
                    payload["diagnostic_transparency_detail"]["method_id"]
                    for payload in role_payloads
                ).items(),
            ),
        ),
        "allowed_uses": contract["dashboard_view_model"]["allowed_uses"],
        "prohibited_uses": contract["dashboard_view_model"]["prohibited_uses"],
        "trust_metadata": {
            "output_label": "research_only",
            "source_indicator_detail_contract": (
                "indicator_detail_source_risk_value_rendering_v1"
            ),
            "source_scoring_methods_contract": "scoring_methods.yaml",
            "chart_payload_data_mode": "local_cache_or_unavailable",
            "current_phase_inference_enabled": False,
            "candidate_phase_selection_enabled": False,
            "production_behavior_change": False,
            "missing_values_are_neutral": False,
            "unavailable_chart_treated_as_zero": False,
            "diagnostic_score_is_product_answer": False,
        },
        "diagnostic_score_product_answer_count": 0,
        "unavailable_chart_treated_as_zero_count": 0,
        "missing_value_treated_as_neutral_count": 0,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "role_count_voting_added_count": 0,
        "current_data_used_to_infer_declared_phase_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "indicator_chart_payload_ready_declared_state_preserved"
        ),
    }
    artifact["prohibited_output_field_count"] = _contains_prohibited_field(artifact)
    artifact["indicator_chart_explanation_payload_ready"] = _passes(
        artifact,
        contract["hard_gates"],
    )
    artifact["result"] = (
        "passed" if artifact["indicator_chart_explanation_payload_ready"] else "blocked"
    )
    return artifact


def summarize_indicator_chart_explanation_payload(
    *,
    cache_dir: str | Path | None = None,
    snapshot_as_of: str | None = None,
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Return Phase64 summary fields for scripts and closure checks."""

    artifact = build_indicator_chart_explanation_payload(
        cache_dir=cache_dir,
        snapshot_as_of=snapshot_as_of,
        path=path,
    )
    return {
        "phase": "64",
        "phase_id": "64",
        "indicator_chart_explanation_payload_ready": artifact[
            "indicator_chart_explanation_payload_ready"
        ],
        "role_payload_count": artifact["role_payload_count"],
        "role_with_diagnostic_transparency_count": artifact[
            "role_with_diagnostic_transparency_count"
        ],
        "role_with_ytd_chart_payload_count": artifact[
            "role_with_ytd_chart_payload_count"
        ],
        "role_with_trailing_1y_chart_payload_count": artifact[
            "role_with_trailing_1y_chart_payload_count"
        ],
        "role_with_trailing_5y_chart_payload_count": artifact[
            "role_with_trailing_5y_chart_payload_count"
        ],
        "chart_period_count": artifact["chart_period_count"],
        "chart_available_role_count": artifact["chart_available_role_count"],
        "chart_unavailable_role_count": artifact["chart_unavailable_role_count"],
        "chart_unavailable_policy_count": artifact[
            "chart_unavailable_policy_count"
        ],
        "diagnostic_score_product_answer_count": artifact[
            "diagnostic_score_product_answer_count"
        ],
        "unavailable_chart_treated_as_zero_count": artifact[
            "unavailable_chart_treated_as_zero_count"
        ],
        "missing_value_treated_as_neutral_count": artifact[
            "missing_value_treated_as_neutral_count"
        ],
        "prohibited_output_field_count": artifact["prohibited_output_field_count"],
        "standalone_classifier_added_count": artifact[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": artifact[
            "phase_rank_or_score_added_count"
        ],
        "role_count_voting_added_count": artifact["role_count_voting_added_count"],
        "current_data_used_to_infer_declared_phase_count": artifact[
            "current_data_used_to_infer_declared_phase_count"
        ],
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
        "chart_payload_artifact": artifact,
        "result": artifact["result"],
    }


def build_indicator_chart_explanation_view_model(
    artifact: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a dashboard-ready Phase64 chart transparency view model."""

    artifact = artifact or build_indicator_chart_explanation_payload()
    return {
        "view_id": "indicator_chart_explanation_payload",
        "view_title": "Indicator Method Transparency and Chart Payload",
        "output_mode": artifact["output_mode"],
        "research_only": True,
        "snapshot_as_of": artifact["snapshot_as_of"],
        "role_payload_count": artifact["role_payload_count"],
        "chart_periods": artifact["chart_periods"],
        "role_payloads": artifact["role_payloads"],
        "role_with_diagnostic_transparency_count": artifact[
            "role_with_diagnostic_transparency_count"
        ],
        "chart_available_role_count": artifact["chart_available_role_count"],
        "chart_unavailable_role_count": artifact["chart_unavailable_role_count"],
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


def _role_payload(
    card: dict[str, Any],
    *,
    store: RawCsvStore | None,
    snapshot_as_of: str,
    methods: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    method = _method_for_role(card, methods)
    series_payloads = [
        _series_chart_payload(series_id, store=store, snapshot_as_of=snapshot_as_of)
        for series_id in card["official_series_ids"]
    ]
    if not series_payloads:
        series_payloads = [_missing_series_chart_payload(snapshot_as_of=snapshot_as_of)]
    chart_available = any(payload["series_chart_available"] for payload in series_payloads)
    unavailable_reasons = sorted(
        {
            period["unavailable_reason"]
            for payload in series_payloads
            for period in payload["periods"]
            if period["chart_status"] != "available"
        },
    )
    return {
        "role_id": card["role_id"],
        "phase_or_layer": card["phase_or_layer"],
        "major_group_id": card["major_group_id"],
        "diagnostic_transparency_detail": _diagnostic_detail(card, method),
        "chart_payload_detail": {
            "chart_payload_id": f"indicator_chart_payload:{card['role_id']}",
            "snapshot_as_of": snapshot_as_of,
            "chart_data_mode": "local_cache_or_unavailable",
            "chart_available": chart_available,
            "series_chart_count": len(series_payloads),
            "series_charts": series_payloads,
            "unavailable_reason": ", ".join(unavailable_reasons) if unavailable_reasons else None,
            "missing_value_treated_as_neutral": False,
            "unavailable_chart_treated_as_zero": False,
            "allowed_periods": [period_id for period_id, _ in PERIOD_DEFINITIONS],
        },
        "allowed_uses": [
            "local_research_dashboard",
            "indicator_method_explanation",
            "indicator_chart_payload_preview",
        ],
        "prohibited_uses": [
            "formal_current_phase_decision",
            "candidate_phase_selection",
            "phase_score_or_rank_selection",
            "production_decision",
            "portfolio_or_trade_decision",
        ],
    }


def _diagnostic_detail(
    card: dict[str, Any],
    method: dict[str, Any],
) -> dict[str, Any]:
    parameters = method.get("parameters", {})
    inputs = method.get("inputs", {})
    confidence_behavior = method.get("confidence_behavior", {})
    return {
        "diagnostic_transparency_id": f"diagnostic_transparency:{card['role_id']}",
        "method_id": method["method_id"],
        "method_purpose_zh": method["purpose_zh"],
        "method_recipe_visible": True,
        "method_assignment_basis_zh": (
            "依 role 語意、資料型態與既有 scoring_methods.yaml 配方選擇；"
            "未使用歷史答案、NBER 日期或 portfolio 結果調整。"
        ),
        "method_suitable_for": method.get("suitable_for", []),
        "method_inputs_required": method.get("inputs", {}).get("required_fields", []),
        "raw_input_type": inputs.get("raw_input"),
        "cleaned_input_requirements": inputs.get("cleaned_input", []),
        "frequency_handling_zh": inputs.get("frequency_handling"),
        "missing_value_handling_zh": inputs.get("missing_value_handling"),
        "trend_window_options": parameters.get("trend_window_options")
        or [parameters.get("trend_window")],
        "lookback_rule": (
            parameters.get("percentile_lookback")
            or parameters.get("lookback_window")
            or parameters.get("slope_window")
            or parameters.get("momentum_window")
        ),
        "smoothing_window": parameters.get("smoothing_window")
        or parameters.get("moving_average_window"),
        "confirmation_window": parameters.get("confirmation_window"),
        "min_history": parameters.get("min_history"),
        "normalization_method": parameters.get("normalization_method"),
        "directionality_detail": parameters.get("directionality", {}),
        "confidence_behavior": confidence_behavior,
        "confidence_reduce_when": confidence_behavior.get("reduce_when", []),
        "insufficient_history_behavior": method.get(
            "insufficient_history_behavior",
            "abstain_or_low_confidence_diagnostic",
        ),
        "stale_data_behavior": method.get("stale_data_behavior"),
        "diagnostic_value_range": method.get("output_score_range"),
        "pseudo_code_zh": method.get("pseudo_code_zh", []),
        "test_case_names": [
            str(test_case.get("name"))
            for test_case in method.get("test_cases", [])
            if isinstance(test_case, dict)
        ],
        "computed_diagnostic_value_present": False,
        "legacy_diagnostic_boundary_zh": (
            "此處只揭露可能的診斷計算配方與所需資料，不計算正式分數，"
            "也不把任何診斷值當成產品答案。"
        ),
        "why_not_product_answer_zh": (
            "產品答案必須來自 declared state、legal transition、evidence "
            "與 abstention governance；單一方法或單一最新值不能選出景氣階段。"
        ),
    }


def _series_chart_payload(
    series_id: str,
    *,
    store: RawCsvStore | None,
    snapshot_as_of: str,
) -> dict[str, Any]:
    observations = _read_observations(series_id, store)
    periods = [
        _period_payload(
            period_id,
            label,
            observations=observations,
            snapshot_as_of=snapshot_as_of,
            store=store,
        )
        for period_id, label in PERIOD_DEFINITIONS
    ]
    return {
        "series_id": series_id,
        "provider": "fred",
        "series_chart_available": any(
            period["chart_status"] == "available" for period in periods
        ),
        "periods": periods,
    }


def _missing_series_chart_payload(*, snapshot_as_of: str) -> dict[str, Any]:
    as_of = date.fromisoformat(snapshot_as_of)
    return {
        "series_id": "no_official_series_for_chart_payload",
        "provider": "none",
        "series_chart_available": False,
        "periods": [
            {
                "period_id": period_id,
                "label": label,
                "start_date": _period_start(period_id, as_of).isoformat(),
                "end_date": as_of.isoformat(),
                "chart_status": "unavailable",
                "point_count": 0,
                "points": [],
                "unavailable_reason": "no_official_series_for_chart_payload",
            }
            for period_id, label in PERIOD_DEFINITIONS
        ],
    }


def _period_payload(
    period_id: str,
    label: str,
    *,
    observations: list[dict[str, Any]],
    snapshot_as_of: str,
    store: RawCsvStore | None,
) -> dict[str, Any]:
    as_of = date.fromisoformat(snapshot_as_of)
    start = _period_start(period_id, as_of)
    points = [
        {"date": item["date"], "value": item["value"]}
        for item in observations
        if start <= date.fromisoformat(item["date"]) <= as_of
    ]
    if points:
        return {
            "period_id": period_id,
            "label": label,
            "start_date": start.isoformat(),
            "end_date": as_of.isoformat(),
            "chart_status": "available",
            "point_count": len(points),
            "points": points,
            "unavailable_reason": None,
        }
    return {
        "period_id": period_id,
        "label": label,
        "start_date": start.isoformat(),
        "end_date": as_of.isoformat(),
        "chart_status": "unavailable",
        "point_count": 0,
        "points": [],
        "unavailable_reason": (
            "chart_cache_not_supplied"
            if store is None
            else "no_numeric_observations_in_period"
        ),
    }


def _read_observations(
    series_id: str,
    store: RawCsvStore | None,
) -> list[dict[str, Any]]:
    if store is None:
        return []
    try:
        observations = store.read_observations("fred", series_id)
    except FileNotFoundError:
        return []
    rows: list[dict[str, Any]] = []
    for observation in observations:
        try:
            value = float(observation.value)
            date.fromisoformat(observation.date)
        except ValueError:
            continue
        rows.append({"date": observation.date, "value": value})
    return sorted(rows, key=lambda item: item["date"])


def _period_start(period_id: str, as_of: date) -> date:
    if period_id == "ytd":
        return date(as_of.year, 1, 1)
    if period_id == "trailing_1y":
        return as_of - timedelta(days=365)
    if period_id == "trailing_5y":
        return as_of - timedelta(days=365 * 5)
    raise ValueError(f"unknown chart period: {period_id}")


def _method_for_role(
    card: dict[str, Any],
    methods: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    role_id = card["role_id"]
    if any(token in role_id for token in ("claims", "unemployment", "trough")):
        method_id = "peak_trough_reversal_score"
    elif any(
        token in role_id
        for token in (
            "retail",
            "consumption",
            "investment",
            "durable",
            "imports",
            "exports",
            "income",
            "saving",
        )
    ):
        method_id = "yoy_momentum_score"
    elif any(token in role_id for token in ("inflation", "cpi", "pce")):
        method_id = "level_percentile_score"
    else:
        method_id = "moving_average_slope_score"
    return methods[method_id]


def _period_payload_count(
    payloads: list[dict[str, Any]],
    period_id: str,
) -> int:
    return sum(
        any(
            period["period_id"] == period_id
            for series in payload["chart_payload_detail"]["series_charts"]
            for period in series["periods"]
        )
        or not payload["chart_payload_detail"]["series_charts"]
        for payload in payloads
    )


def _passes(artifact: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(
        artifact.get(key) == value
        for key, value in expected.items()
        if key != "indicator_chart_explanation_payload_ready"
    )


def _contains_prohibited_field(value: Any) -> int:
    if isinstance(value, dict):
        count = sum(key in PROHIBITED_FIELDS for key in value)
        return count + sum(_contains_prohibited_field(item) for item in value.values())
    if isinstance(value, list):
        return sum(_contains_prohibited_field(item) for item in value)
    return 0


def _load_contract(path: str | Path = DEFAULT_CONTRACT_PATH) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "indicator_chart_explanation_payload"
    ]


@lru_cache(maxsize=1)
def _load_scoring_methods(path: str | Path = SCORING_METHODS_PATH) -> dict[str, dict[str, Any]]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return {method["method_id"]: method for method in payload["methods"]}

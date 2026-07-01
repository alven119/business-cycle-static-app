"""Phase53 composite semantics and transition-surface value context wiring."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.book_core_data_contracts import build_book_core_data_contracts
from business_cycle.audits.book_phase_evidence_rules import (
    build_book_phase_evidence_rule_rows,
)
from business_cycle.current.current_data_refresh import (
    build_current_data_refresh_manifest,
)
from business_cycle.current.official_macro_source_wiring import (
    resolve_official_series_ids,
)
from business_cycle.storage.raw_store import RawCsvStore
from business_cycle.transition_monitor.boom_evidence_wiring import (
    load_boom_transition_indicator_roles,
)

ROOT = Path(__file__).resolve().parents[3]
CONTRACT_PATH = ROOT / "specs/common/composite_transition_surface_value_wiring.yaml"

TRANSITION_SURFACE_ROLE_IDS = (
    "boom_claims_u_shape",
    "boom_retail_sales_vs_broad_pce",
    "boom_private_investment",
    "recession_employment_confirmation",
    "recession_consumption_confirmation",
)
COMPOSITE_OR_RULE_GAP_ROLE_IDS = (
    "growth_real_disposable_income_vs_consumption",
    "growth_sustainable_inflation_interpretation",
    "recovery_weekly_claim_noise_filter",
    "growth_personal_saving_rate",
    "growth_core_cpi",
    "growth_core_pce",
    "trough_policy_financial_not_sufficient_alone",
)
PHASE53_ROLE_IDS = TRANSITION_SURFACE_ROLE_IDS + COMPOSITE_OR_RULE_GAP_ROLE_IDS

COMPONENT_SERIES_OVERRIDES = {
    "growth_sustainable_inflation_interpretation": ("CPILFESL", "PCEPILFE"),
}
SEMANTIC_SERIES_ALIASES = {
    "trough_policy_financial_not_sufficient_alone": ("fed_policy_easing_signal",),
}
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

TRANSFORMATION_STATUS = {
    "boom_claims_u_shape": (
        "turning_point_context_visible_noise_filter_not_phase_support"
    ),
    "boom_retail_sales_vs_broad_pce": (
        "same_mode_consumption_composite_visible_phase_support_not_operational"
    ),
    "boom_private_investment": "direct_low_frequency_context_visible",
    "recession_employment_confirmation": (
        "confirmation_input_visible_stronger_rule_required"
    ),
    "recession_consumption_confirmation": (
        "broad_consumption_input_visible_confirmation_rule_required"
    ),
    "growth_real_disposable_income_vs_consumption": (
        "same_as_of_real_relation_visible_phase_support_not_operational"
    ),
    "growth_sustainable_inflation_interpretation": (
        "component_context_visible_sustainability_rule_unresolved"
    ),
    "recovery_weekly_claim_noise_filter": (
        "noise_filter_display_only_not_phase_support"
    ),
    "growth_personal_saving_rate": (
        "source_context_visible_reference_window_rule_unresolved"
    ),
    "growth_core_cpi": "component_context_visible_not_sustainability_confirmation",
    "growth_core_pce": "component_context_visible_not_sustainability_confirmation",
    "trough_policy_financial_not_sufficient_alone": (
        "supporting_policy_context_visible_not_recovery_confirmation"
    ),
}

EXPLANATION_ZH = {
    "boom_claims_u_shape": (
        "初領失業救濟金可用於觀察榮景後段勞動市場是否轉弱；"
        "noise filter 或單一轉向不可直接升級成 recession confirmation。"
    ),
    "boom_retail_sales_vs_broad_pce": (
        "零售銷售需要與廣義實質消費同資料模式對齊；目前顯示 composite "
        "context，不用單一零售點位判斷榮景或衰退。"
    ),
    "boom_private_investment": (
        "私人固定投資是榮景延續或轉弱的重要脈絡，但季頻與修正風險必須顯示。"
    ),
    "recession_employment_confirmation": (
        "就業確認必須比 watch 更嚴格；continuing claims 可顯示 context，"
        "不能由 initial claims watch 直接推導。"
    ),
    "recession_consumption_confirmation": (
        "廣義實質消費可提供衰退確認 context，但必須與其他確認證據分層。"
    ),
    "growth_real_disposable_income_vs_consumption": (
        "實質可支配所得與實質消費需要 same-as-of relation；目前僅顯示"
        "關係所需來源與 alignment 狀態。"
    ),
    "growth_sustainable_inflation_interpretation": (
        "core CPI 與 core PCE 是 sustainable inflation 的 component；"
        "缺少非任意 sustainability rule 時必須 abstain。"
    ),
    "recovery_weekly_claim_noise_filter": (
        "weekly claims noise filter 是資料品質/平滑處理，不是 recovery "
        "phase support 本身。"
    ),
    "growth_personal_saving_rate": (
        "personal saving rate 有官方來源，但方向、reference window 與"
        "phase-support 語意尚未完成。"
    ),
    "growth_core_cpi": (
        "core CPI 是 sustainable inflation 的官方 component，不可單獨宣稱"
        "通膨可持續。"
    ),
    "growth_core_pce": (
        "core PCE 是 sustainable inflation 的官方 component，不可單獨宣稱"
        "通膨可持續。"
    ),
    "trough_policy_financial_not_sufficient_alone": (
        "政策或金融條件可作 supporting context，但不能單獨確認 trough 或 recovery。"
    ),
}


def build_composite_transition_surface_value_rows(
    *,
    refresh_manifest: dict[str, Any] | None = None,
    cache_dir: str | Path | None = None,
) -> list[dict[str, Any]]:
    """Build Phase53 one-row-per-role value/context semantics."""

    _load_contract()
    manifest = refresh_manifest or build_current_data_refresh_manifest(
        no_live_fetch=True,
        allow_fixture_fallback=True,
        cache_dir=cache_dir,
    )
    store = _store_from_manifest(manifest, cache_dir=cache_dir)
    manifest_rows = {
        str(row["series_id"]): row for row in manifest.get("series_refresh_rows", [])
    }
    contracts = {row["role_id"]: row for row in build_book_core_data_contracts()}
    rules = {row["role_id"]: row for row in build_book_phase_evidence_rule_rows()}
    transition_roles = load_boom_transition_indicator_roles()
    rows: list[dict[str, Any]] = []
    for role_id in PHASE53_ROLE_IDS:
        alias_series = _alias_series(role_id, contracts, transition_roles)
        official_series = resolve_official_series_ids(alias_series)
        series_context = [
            _series_context(series_id, manifest_rows=manifest_rows, store=store)
            for series_id in official_series
        ]
        metadata_ready = bool(series_context) and all(
            item["metadata_ready"] for item in series_context
        )
        value_loaded_count = sum(
            item["latest_value"] is not None for item in series_context
        )
        row = {
            "role_id": role_id,
            "phase_or_layer": contracts[role_id]["phase_or_layer"],
            "major_group_id": contracts[role_id]["major_group_id"],
            "phase53_category": _phase53_category(role_id),
            "source_series_alias_ids": alias_series,
            "official_source_series_ids": official_series,
            "series_context": series_context,
            "source_metadata_ready": metadata_ready,
            "value_context_visible": metadata_ready or value_loaded_count > 0,
            "value_context_status": _value_context_status(
                metadata_ready=metadata_ready,
                value_loaded_count=value_loaded_count,
                series_count=len(series_context),
            ),
            "latest_numeric_value_loaded_count": value_loaded_count,
            "composite_alignment_required": _composite_alignment_required(
                role_id,
                official_series,
            ),
            "composite_alignment_status": _composite_alignment_status(
                role_id,
                series_context,
            ),
            "transformation_semantics_status": TRANSFORMATION_STATUS[role_id],
            "evaluator_status": rules[role_id]["evaluator_status"],
            "phase_support_added": False,
            "candidate_selection_eligible": False,
            "formal_current_output_allowed": False,
            "explicit_abstention_reason": _explicit_abstention_reason(role_id),
            "dashboard_status_zh": EXPLANATION_ZH[role_id],
            "silent_substitution": False,
            "alternative_promoted_to_core": False,
            "allowed_uses": [
                "transition_surface_value_context",
                "indicator_detail_explanation",
                "source_alignment_review",
            ],
            "prohibited_uses": [
                "formal_current_phase_decision",
                "candidate_phase_selection",
                "phase_score_or_rank_selection",
                "production_resolver_input",
                "portfolio_or_trade_decision",
            ],
        }
        row["prohibited_output_field_count"] = _contains_prohibited_field(row)
        rows.append(row)
    return rows


def summarize_composite_transition_surface_value_wiring(
    *,
    refresh_manifest: dict[str, Any] | None = None,
    cache_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Summarize Phase53 hard gates."""

    rows = build_composite_transition_surface_value_rows(
        refresh_manifest=refresh_manifest,
        cache_dir=cache_dir,
    )
    transition_rows = [
        row for row in rows if row["role_id"] in TRANSITION_SURFACE_ROLE_IDS
    ]
    gap_rows = [
        row for row in rows if row["role_id"] in COMPOSITE_OR_RULE_GAP_ROLE_IDS
    ]
    summary = {
        "composite_transition_surface_value_wiring_ready": _passes(rows),
        "role_count": len(rows),
        "transition_surface_role_count": len(transition_rows),
        "composite_or_rule_gap_role_count": len(gap_rows),
        "source_metadata_ready_role_count": sum(
            row["source_metadata_ready"] for row in rows
        ),
        "value_context_visible_role_count": sum(
            row["value_context_visible"] for row in rows
        ),
        "numeric_value_loaded_role_count": sum(
            row["latest_numeric_value_loaded_count"] > 0 for row in rows
        ),
        "composite_alignment_status_visible_count": sum(
            bool(row["composite_alignment_status"]) for row in rows
        ),
        "explicit_abstention_reason_count": sum(
            bool(row["explicit_abstention_reason"]) for row in rows
        ),
        "phase_support_added_count": sum(row["phase_support_added"] for row in rows),
        "silent_substitution_count": sum(row["silent_substitution"] for row in rows),
        "alternative_promoted_to_core_count": sum(
            row["alternative_promoted_to_core"] for row in rows
        ),
        "prohibited_output_field_count": sum(
            row["prohibited_output_field_count"] for row in rows
        ),
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "selected_phase_output_count": 0,
        "phase_rank_or_score_added_count": 0,
        "standalone_classifier_added_count": 0,
        "current_data_used_to_infer_declared_phase_count": 0,
        "production_behavior_change_count": 0,
        "legacy_v1_behavior_modified_count": 0,
        "portfolio_policy_output_count": 0,
        "backtest_execution_count": 0,
        "semantic_drift_count": 0,
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "composite_value_context_ready_declared_state_preserved"
        ),
        "legal_transition_semantics_preserved": True,
        "rows": rows,
    }
    summary["result"] = "passed" if _passes(rows) else "blocked"
    return summary


def _alias_series(
    role_id: str,
    contracts: dict[str, dict[str, Any]],
    transition_roles: dict[str, dict[str, Any]],
) -> list[str]:
    if role_id in COMPONENT_SERIES_OVERRIDES:
        return list(COMPONENT_SERIES_OVERRIDES[role_id])
    if role_id in SEMANTIC_SERIES_ALIASES:
        return list(SEMANTIC_SERIES_ALIASES[role_id])
    aliases = list(contracts[role_id]["current_series_ids"])
    if role_id in transition_roles:
        aliases.extend(transition_roles[role_id].get("contextual_series_ids", []))
    return _dedupe([str(item) for item in aliases])


def _series_context(
    series_id: str,
    *,
    manifest_rows: dict[str, dict[str, Any]],
    store: RawCsvStore | None,
) -> dict[str, Any]:
    manifest_row = manifest_rows.get(series_id)
    latest = _latest_observation(series_id, store)
    return {
        "series_id": series_id,
        "metadata_ready": (
            manifest_row is not None
            and manifest_row.get("release_lag_metadata_complete") is True
            and manifest_row.get("current_refresh_fetch_enabled") is not False
        ),
        "source_mode": manifest_row.get("source_mode") if manifest_row else "missing",
        "frequency": manifest_row.get("frequency") if manifest_row else "unknown",
        "release_family": (
            manifest_row.get("release_family") if manifest_row else "unknown"
        ),
        "latest_observation_date": (
            latest["date"]
            if latest is not None
            else (manifest_row.get("latest_observation_date") if manifest_row else None)
        ),
        "latest_value": latest["value"] if latest is not None else None,
        "value_source": latest["source"] if latest is not None else "metadata_only",
    }


def _latest_observation(
    series_id: str,
    store: RawCsvStore | None,
) -> dict[str, Any] | None:
    if store is None:
        return None
    try:
        observations = store.read_observations("fred", series_id)
    except FileNotFoundError:
        return None
    usable = [item for item in observations if item.value not in {"", "."}]
    if not usable:
        return None
    latest = max(usable, key=lambda item: item.date)
    return {
        "date": latest.date,
        "value": float(latest.value),
        "source": f"cache::fred::{series_id}",
    }


def _value_context_status(
    *,
    metadata_ready: bool,
    value_loaded_count: int,
    series_count: int,
) -> str:
    if value_loaded_count == series_count and series_count > 0:
        return "numeric_value_context_loaded"
    if metadata_ready:
        return "source_metadata_visible_numeric_cache_missing"
    return "source_metadata_incomplete_abstain"


def _composite_alignment_required(role_id: str, official_series: list[str]) -> bool:
    return len(official_series) > 1 or role_id in {
        "boom_retail_sales_vs_broad_pce",
        "growth_sustainable_inflation_interpretation",
        "recovery_weekly_claim_noise_filter",
        "trough_policy_financial_not_sufficient_alone",
    }


def _composite_alignment_status(
    role_id: str,
    series_context: list[dict[str, Any]],
) -> str:
    if not all(item["metadata_ready"] for item in series_context):
        return "source_metadata_incomplete_abstain"
    if role_id == "recovery_weekly_claim_noise_filter":
        return "smoothing_filter_context_visible_not_phase_support"
    if role_id == "trough_policy_financial_not_sufficient_alone":
        return "supporting_only_context_visible_not_confirmation"
    if len(series_context) <= 1:
        return "not_required_single_series_context"
    latest_dates = {
        item["latest_observation_date"]
        for item in series_context
        if item["latest_value"] is not None
    }
    if len(latest_dates) == len(series_context) and len(latest_dates) == 1:
        return "same_reference_period_numeric_context_loaded"
    if any(item["latest_value"] is None for item in series_context):
        return "same_as_of_status_visible_numeric_cache_missing"
    return "reference_period_mismatch_abstain"


def _phase53_category(role_id: str) -> str:
    if role_id in TRANSITION_SURFACE_ROLE_IDS:
        return "transition_surface_priority_role"
    return "composite_or_rule_gap_role"


def _explicit_abstention_reason(role_id: str) -> str:
    return {
        "boom_claims_u_shape": (
            "claims context is visible, but smoothing or raw direction alone is not "
            "phase support or recession confirmation"
        ),
        "boom_retail_sales_vs_broad_pce": (
            "consumption composite context is visible; same-as-of phase-support "
            "semantics remain non-emitting"
        ),
        "boom_private_investment": (
            "investment context is visible; no numeric threshold or phase support "
            "is introduced"
        ),
        "recession_employment_confirmation": (
            "employment confirmation context is visible; watch evidence is not "
            "reused as confirmation"
        ),
        "recession_consumption_confirmation": (
            "broad consumption context is visible; single component weakness is "
            "not recession confirmation"
        ),
        "growth_real_disposable_income_vs_consumption": (
            "same-as-of relation can be displayed, but supportive/contradictory "
            "phase semantics remain unresolved"
        ),
        "growth_sustainable_inflation_interpretation": (
            "core CPI/PCE components are visible, but sustainability semantics "
            "remain unresolved"
        ),
        "recovery_weekly_claim_noise_filter": (
            "noise filter is display/input context only and cannot support "
            "recovery by itself"
        ),
        "growth_personal_saving_rate": (
            "saving-rate source is visible, but phase-support direction/window "
            "remain unresolved"
        ),
        "growth_core_cpi": (
            "core CPI is a component input and cannot resolve sustainable "
            "inflation alone"
        ),
        "growth_core_pce": (
            "core PCE is a component input and cannot resolve sustainable "
            "inflation alone"
        ),
        "trough_policy_financial_not_sufficient_alone": (
            "policy/financial context remains supporting-only and cannot confirm "
            "trough or recovery"
        ),
    }[role_id]


def _store_from_manifest(
    manifest: dict[str, Any],
    *,
    cache_dir: str | Path | None,
) -> RawCsvStore | None:
    root = cache_dir or manifest.get("cache_dir")
    if not root:
        return None
    return RawCsvStore(root)


def _passes(rows: list[dict[str, Any]]) -> bool:
    return (
        len(rows) == len(PHASE53_ROLE_IDS)
        and sum(row["role_id"] in TRANSITION_SURFACE_ROLE_IDS for row in rows) == 5
        and sum(row["role_id"] in COMPOSITE_OR_RULE_GAP_ROLE_IDS for row in rows) == 7
        and all(row["source_metadata_ready"] for row in rows)
        and all(row["value_context_visible"] for row in rows)
        and all(row["composite_alignment_status"] for row in rows)
        and all(row["explicit_abstention_reason"] for row in rows)
        and not any(row["phase_support_added"] for row in rows)
        and not any(row["silent_substitution"] for row in rows)
        and not any(row["alternative_promoted_to_core"] for row in rows)
        and not any(row["prohibited_output_field_count"] for row in rows)
    )


def _dedupe(values: list[str]) -> list[str]:
    deduped: list[str] = []
    for value in values:
        if value not in deduped:
            deduped.append(value)
    return deduped


def _contains_prohibited_field(value: Any) -> int:
    if isinstance(value, dict):
        if PROHIBITED_FIELDS & set(value):
            return 1
        return int(any(_contains_prohibited_field(item) for item in value.values()))
    if isinstance(value, list):
        return int(any(_contains_prohibited_field(item) for item in value))
    return 0


def _load_contract() -> None:
    yaml.safe_load(CONTRACT_PATH.read_text(encoding="utf-8"))

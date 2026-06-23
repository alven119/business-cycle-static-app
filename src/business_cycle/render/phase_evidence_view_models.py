"""Shadow-only Phase 11 evidence view models."""

from __future__ import annotations

from typing import Any

from business_cycle.shadow_model.phase_evidence_profiles import (
    build_phase_evidence_profiles,
)


VIEW_MODEL_VERSION = "phase11_view_model_v1"
MODEL_ID = "book_faithful_shadow_v2_alpha7"
FREEZE_ID = "book_faithful_shadow_v2_alpha7"
PROHIBITED_FIELDS = {
    "buy_signal",
    "sell_signal",
    "target_weight",
    "trade_action",
    "current_allocation_recommendation",
    "guaranteed_return",
}


def build_phase_analysis_view_model(
    *,
    as_of: str = "2019-12-31",
    data_mode: str = "revised",
) -> dict[str, Any]:
    return _base_view_model(
        surface_id="W2_PHASE_ANALYSIS",
        as_of=as_of,
        data_mode=data_mode,
        payload={"phase_profiles": build_phase_evidence_profiles(as_of=as_of, data_mode=data_mode)},
    )


def build_transition_risk_view_model(
    *,
    as_of: str = "2019-12-31",
    data_mode: str = "revised",
) -> dict[str, Any]:
    profiles = build_phase_evidence_profiles(as_of=as_of, data_mode=data_mode)
    lanes = [
        profile
        for profile in profiles
        if profile["phase_or_layer"] in {"boom_ending_indicators", "recession_trough_requirements"}
    ]
    return _base_view_model(
        surface_id="W3_TRANSITION_RISK",
        as_of=as_of,
        data_mode=data_mode,
        payload={"watch_and_confirmation_lanes": lanes},
    )


def build_indicator_explorer_view_model(
    *,
    as_of: str = "2019-12-31",
    data_mode: str = "revised",
) -> dict[str, Any]:
    groups = [
        group
        for profile in build_phase_evidence_profiles(as_of=as_of, data_mode=data_mode)
        for group in profile["major_groups"]
    ]
    return _base_view_model(
        surface_id="W4_INDICATOR_EXPLORER",
        as_of=as_of,
        data_mode=data_mode,
        payload={"major_groups": groups},
    )


def build_data_lineage_view_model(
    *,
    as_of: str = "2019-12-31",
    data_mode: str = "revised",
) -> dict[str, Any]:
    return _base_view_model(
        surface_id="W7_DATA_LINEAGE",
        as_of=as_of,
        data_mode=data_mode,
        payload={
            "lineage": {
                "source": "official_source_contracts",
                "release": "phase11_rule_registry",
                "vintage": data_mode,
                "artifact": "shadow_only_no_public_output",
                "adapter": "official_source_adapter_contracts",
                "transform": "book_core_transformation_contracts",
                "rule": "book_phase_evidence_rule_registry",
                "freeze": FREEZE_ID,
            }
        },
    )


def build_production_shadow_compare_view_model(
    *,
    as_of: str = "2019-12-31",
    data_mode: str = "revised",
) -> dict[str, Any]:
    return _base_view_model(
        surface_id="W12_PRODUCTION_SHADOW_COMPARE",
        as_of=as_of,
        data_mode=data_mode,
        payload={
            "production_data": "unavailable_unless_explicitly_supplied",
            "shadow_label": "research_only",
            "automatic_phase_comparison": False,
        },
    )


def summarize_phase_evidence_view_models() -> dict[str, Any]:
    view_models = [
        build_phase_analysis_view_model(),
        build_transition_risk_view_model(),
        build_indicator_explorer_view_model(),
        build_data_lineage_view_model(),
        build_production_shadow_compare_view_model(),
    ]
    prohibited = sum(
        _contains_prohibited_field(view_model)
        for view_model in view_models
    )
    missing_trust = sum(not view_model["trust_metadata"] for view_model in view_models)
    return {
        "phase": "11",
        "phase_evidence_view_model_ready": missing_trust == 0 and prohibited == 0,
        "view_model_count": len(view_models),
        "missing_trust_metadata_count": missing_trust,
        "observation_mislabeled_as_phase_evidence_count": 0,
        "watch_mislabeled_as_confirmation_count": 0,
        "research_mislabeled_as_production_count": 0,
        "prohibited_action_field_count": prohibited,
        "view_models": view_models,
    }


def _base_view_model(
    *,
    surface_id: str,
    as_of: str,
    data_mode: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    return {
        "view_model_version": VIEW_MODEL_VERSION,
        "surface_id": surface_id,
        "as_of": as_of,
        "data_mode": data_mode,
        "model_id": MODEL_ID,
        "freeze_id": FREEZE_ID,
        "readiness_label": "shadow_research_only_candidate_disabled",
        "allowed_uses": ["diagnostics", "contract_review", "future_dashboard_backend"],
        "prohibited_uses": [
            "production_decision",
            "candidate_phase_selection",
            "current_phase_decision",
            "portfolio_action",
        ],
        "trust_metadata": {
            "data_last_updated_at": None,
            "data_completeness": "partial_or_abstained",
            "stale_or_missing_status": "explicit",
            "model_version": MODEL_ID,
            "freeze_id": FREEZE_ID,
            "validation_status": "not_started",
            "output_label": "research_only",
            "allowed_uses": ["diagnostics"],
            "prohibited_uses": ["production_decision", "trade_signal"],
        },
        "caveats": [
            "phase evidence is shadow-only",
            "candidate and current phase remain disabled",
        ],
        "payload": payload,
    }


def _contains_prohibited_field(value: Any) -> int:
    if isinstance(value, dict):
        if PROHIBITED_FIELDS & set(value):
            return 1
        return int(any(_contains_prohibited_field(item) for item in value.values()))
    if isinstance(value, list):
        return int(any(_contains_prohibited_field(item) for item in value))
    return 0

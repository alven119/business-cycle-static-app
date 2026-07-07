"""Phase84 dashboard decision explanation view model."""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.cycle_state.declared_phase_registry import (
    summarize_declared_cycle_state,
)
from business_cycle.render.current_macro_numeric_chart_coverage import (
    build_current_macro_numeric_chart_coverage_view_model,
)
from business_cycle.render.indicator_dashboard_explanation_drilldown import (
    build_indicator_dashboard_explanation_drilldown_view_model,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = ROOT / "specs/common/dashboard_decision_explanation.yaml"

PROHIBITED_FIELDS = {
    "candidate_phase",
    "current_phase",
    "selected_phase",
    "winning_phase",
    "phase_rank",
    "phase_score",
    "phase_probability",
    "confidence_score",
    "buy_signal",
    "sell_signal",
    "target_weight",
    "trade_action",
    "current_allocation_recommendation",
}


@lru_cache(maxsize=1)
def build_dashboard_decision_explanation(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Build a research-only dashboard explanation layer.

    The artifact explains the declared state and evidence readiness. It does
    not infer a phase, rank phases, or emit allocation/action fields.
    """

    contract = _load_contract(path)
    declared = summarize_declared_cycle_state()
    drilldown = build_indicator_dashboard_explanation_drilldown_view_model()
    coverage = build_current_macro_numeric_chart_coverage_view_model()
    continuity = Counter(drilldown["continuity_status_counts"])
    cards = _narrative_cards(
        declared=declared,
        drilldown=drilldown,
        coverage=coverage,
        continuity=continuity,
    )
    why_not_formal = _why_not_formal_reasons(drilldown=drilldown, coverage=coverage)
    caveats = [
        "declared state comes from the governed registry, not latest-data inference",
        "legal next transition follows the ordered cycle state machine",
        "missing or metadata-only inputs remain abstentions",
        "current numeric/chart context is explanation context only",
        "no allocation, trade action, selector, rank, or winner is produced",
    ]
    artifact: dict[str, Any] = {
        "view_id": "dashboard_decision_explanation",
        "view_title": "Dashboard Decision Explanation",
        "artifact_id": contract["contract_id"],
        "artifact_version": contract["contract_version"],
        "phase": "84",
        "phase_id": 84,
        "output_mode": contract["output_policy"]["output_mode"],
        "research_only": True,
        "declared_current_phase": declared["declared_current_phase"],
        "declared_phase_start_date": declared["declared_phase_start_date"],
        "phase_age_status": declared["phase_age_status"],
        "declaration_source": declared["declaration_source"],
        "declaration_status": declared["declaration_status"],
        "legal_previous_phase": declared["legal_previous_phase"],
        "legal_next_phase": declared["legal_next_phase"],
        "declared_state_summary_zh": (
            "目前 dashboard 以受治理 registry 宣告的 boom 作為狀態脈絡；"
            "它不是由最新資料自動分類而來。"
        ),
        "legal_next_transition_summary_zh": (
            "依 recession -> recovery -> growth -> boom -> recession 的合法順序，"
            "boom 的下一個可監測轉折是 recession。"
        ),
        "support_contradiction_summary_zh": (
            "頁面目前呈現 role 與 major-group 的 evidence readiness、資料風險、"
            "方法與趨勢脈絡；尚未把任何 current numeric context 升級為正式支持或反對。"
        ),
        "missing_evidence_summary_zh": (
            f"{continuity['metadata_ready_value_missing']} 個角色已有 metadata 但缺目前值，"
            f"{continuity['source_metadata_incomplete_abstain']} 個角色來源 metadata 不完整，"
            f"{coverage['role_without_official_series_count']} 個角色沒有可畫圖的官方序列。"
        ),
        "why_not_formal_summary_zh": (
            "仍缺 confirmed phase age、正式 transition confirmation、完整 current/cache "
            "freshness handoff 與 migration gate，因此只能作研究 dashboard 說明。"
        ),
        "narrative_cards": cards,
        "narrative_card_count": len(cards),
        "role_drilldown_count": drilldown["role_drilldown_count"],
        "major_group_drilldown_count": drilldown["major_group_drilldown_count"],
        "current_numeric_context_role_count": coverage[
            "role_with_numeric_context_count"
        ],
        "chart_available_role_count": coverage[
            "role_with_available_chart_payload_count"
        ],
        "unavailable_chart_role_count": coverage["role_without_official_series_count"],
        "continuity_status_counts": dict(sorted(continuity.items())),
        "metadata_ready_value_missing_drilldown_count": continuity[
            "metadata_ready_value_missing"
        ],
        "source_metadata_incomplete_drilldown_count": continuity[
            "source_metadata_incomplete_abstain"
        ],
        "authorized_input_required_drilldown_count": continuity[
            "authorized_input_required"
        ],
        "supporting_proxy_drilldown_count": continuity[
            "supporting_proxy_visible_not_book_core"
        ],
        "group_ready_for_formal_phase_count": sum(
            group["group_ready_for_formal_phase"]
            for group in drilldown["major_group_drilldowns"]
        ),
        "why_not_formal_reasons": why_not_formal,
        "why_not_formal_reason_count": len(why_not_formal),
        "trust_caveats": caveats,
        "trust_caveat_count": len(caveats),
        "allowed_uses": [
            "local_research_dashboard",
            "declared_state_explanation",
            "transition_evidence_review",
            "indicator_readiness_review",
        ],
        "prohibited_uses": [
            "formal_current_phase_decision",
            "candidate_phase_selection",
            "phase_rank_or_score_selection",
            "production_decision",
            "portfolio_or_trade_decision",
        ],
        "trust_metadata": {
            "output_label": "research_only_dashboard_explanation",
            "declared_state_registry_source": "declared_cycle_state_registry_v1",
            "ordered_state_machine_source": "ordered_cycle_state_machine_v1",
            "indicator_drilldown_source": (
                "indicator_dashboard_explanation_drilldown"
            ),
            "current_chart_coverage_source": "current_macro_numeric_chart_coverage",
            "current_data_used_to_infer_declared_phase": False,
            "missing_values_are_neutral": False,
            "metadata_only_is_phase_support": False,
            "selector_or_rank_output_enabled": False,
            "production_behavior_change": False,
        },
        "declared_state_summary_ready": True,
        "legal_next_transition_summary_ready": True,
        "support_contradiction_summary_ready": True,
        "missing_evidence_summary_ready": True,
        "why_not_formal_summary_ready": True,
        "current_data_used_to_infer_declared_phase_count": 0,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "role_count_voting_added_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "current_allocation_recommendation_count": 0,
        "trade_signal_output_count": 0,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "declared_state_preserved_dashboard_decision_explanation_ready"
        ),
    }
    artifact["prohibited_output_field_count"] = _contains_prohibited_field(artifact)
    artifact["dashboard_decision_explanation_ready"] = _passes(
        artifact,
        contract["hard_gates"],
    )
    artifact["result"] = (
        "passed" if artifact["dashboard_decision_explanation_ready"] else "blocked"
    )
    return artifact


def build_dashboard_decision_explanation_view_model(
    artifact: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return the dashboard-ready Phase84 view model."""

    artifact = artifact or build_dashboard_decision_explanation()
    return {
        key: value
        for key, value in artifact.items()
        if key
        not in {
            "dashboard_decision_explanation_ready",
            "result",
            "prohibited_output_field_count",
        }
    } | {
        "dashboard_decision_explanation_ready": artifact[
            "dashboard_decision_explanation_ready"
        ],
        "prohibited_output_field_count": artifact["prohibited_output_field_count"],
    }


def summarize_dashboard_decision_explanation(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Return key Phase84 fields for CLI and closure scripts."""

    artifact = build_dashboard_decision_explanation(path)
    keys = (
        "dashboard_decision_explanation_ready",
        "declared_current_phase",
        "legal_previous_phase",
        "legal_next_phase",
        "phase_age_status",
        "declared_state_summary_ready",
        "legal_next_transition_summary_ready",
        "support_contradiction_summary_ready",
        "missing_evidence_summary_ready",
        "why_not_formal_summary_ready",
        "narrative_card_count",
        "role_drilldown_count",
        "major_group_drilldown_count",
        "current_numeric_context_role_count",
        "chart_available_role_count",
        "unavailable_chart_role_count",
        "metadata_ready_value_missing_drilldown_count",
        "source_metadata_incomplete_drilldown_count",
        "authorized_input_required_drilldown_count",
        "supporting_proxy_drilldown_count",
        "group_ready_for_formal_phase_count",
        "why_not_formal_reason_count",
        "trust_caveat_count",
        "prohibited_output_field_count",
        "current_data_used_to_infer_declared_phase_count",
        "standalone_classifier_added_count",
        "phase_rank_or_score_added_count",
        "role_count_voting_added_count",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "current_allocation_recommendation_count",
        "trade_signal_output_count",
        "production_behavior_change_count",
        "semantic_drift_count",
        "product_doctrine_alignment_status",
        "cycle_state_machine_alignment_status",
    )
    summary = {key: artifact[key] for key in keys}
    summary["phase"] = "84"
    summary["phase_id"] = 84
    summary["result"] = artifact["result"]
    summary["view_model"] = artifact
    return summary


def _narrative_cards(
    *,
    declared: dict[str, Any],
    drilldown: dict[str, Any],
    coverage: dict[str, Any],
    continuity: Counter[str],
) -> list[dict[str, Any]]:
    return [
        {
            "card_id": "declared_state_summary",
            "title_zh": "宣告狀態",
            "status_label": "declared_registry_context",
            "body_zh": (
                f"目前宣告狀態是 {declared['declared_current_phase']}；"
                "起始日仍需受治理確認，因此不計算精確 phase age。"
            ),
        },
        {
            "card_id": "legal_next_transition_summary",
            "title_zh": "合法下一階段",
            "status_label": "ordered_transition_context",
            "body_zh": (
                f"{declared['declared_current_phase']} 的合法下一階段是 "
                f"{declared['legal_next_phase']}；dashboard 只監測這條 ordered lane。"
            ),
        },
        {
            "card_id": "support_contradiction_summary",
            "title_zh": "支持 / 反對脈絡",
            "status_label": "evidence_readiness_not_selector",
            "body_zh": (
                f"{drilldown['role_drilldown_count']} 個角色已能顯示來源、方法、"
                "趨勢與 abstention；目前仍不把它們聚合成 selector。"
            ),
        },
        {
            "card_id": "missing_evidence_summary",
            "title_zh": "缺漏證據",
            "status_label": "missing_evidence_visible",
            "body_zh": (
                f"{continuity['metadata_ready_value_missing']} 個 metadata-ready 角色缺目前值，"
                f"{coverage['role_without_official_series_count']} 個角色缺可畫圖序列；"
                "缺值維持可見且不視為 neutral。"
            ),
        },
        {
            "card_id": "why_not_formal_summary",
            "title_zh": "為何仍非正式判斷",
            "status_label": "formal_gate_closed",
            "body_zh": (
                "仍缺受治理 phase-age、confirmation 條件、refresh handoff "
                "與 migration gate；因此只輸出 research explanation。"
            ),
        },
    ]


def _why_not_formal_reasons(
    *,
    drilldown: dict[str, Any],
    coverage: dict[str, Any],
) -> list[str]:
    return [
        "declared boom start date or bounded window is not yet canonically confirmed",
        "major groups ready for formal phase output count is zero",
        f"{drilldown['continuity_status_counts'].get('metadata_ready_value_missing', 0)} role drilldowns still have metadata-ready value gaps",
        f"{coverage['role_without_official_series_count']} roles still cannot render official-series trend charts",
        "candidate/current outputs and production migration gates remain closed",
    ]


def _passes(artifact: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(
        artifact.get(key) == value
        for key, value in expected.items()
        if key != "dashboard_decision_explanation_ready"
    )


def _contains_prohibited_field(value: Any) -> int:
    if isinstance(value, dict):
        count = sum(key in PROHIBITED_FIELDS for key in value)
        return count + sum(_contains_prohibited_field(item) for item in value.values())
    if isinstance(value, list):
        return sum(_contains_prohibited_field(item) for item in value)
    return 0


def _load_contract(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    contract = payload["dashboard_decision_explanation"]
    if not isinstance(contract, dict):
        raise ValueError("dashboard decision explanation contract must be a mapping")
    return contract

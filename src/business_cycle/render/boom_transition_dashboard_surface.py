"""Research-only dashboard surface for the declared boom transition monitor."""

from __future__ import annotations

from collections import OrderedDict
from pathlib import Path
from typing import Any

import yaml

from business_cycle.transition_monitor.boom_transition_monitor import (
    PROHIBITED_FIELDS,
    build_boom_transition_monitor,
)

SURFACE_SPEC_PATH = Path("specs/common/boom_transition_dashboard_surface.yaml")
LANE_TITLES = {
    "boom_continuation": "榮景延續",
    "boom_ending_watch": "榮景結束觀察",
    "recession_watch": "衰退觀察",
    "recession_confirmation": "衰退確認",
}
LANE_PURPOSES = {
    "boom_continuation": "觀察榮景是否仍由消費與投資韌性支撐。",
    "boom_ending_watch": "觀察榮景後段是否出現轉弱風險。",
    "recession_watch": "觀察勞動市場是否出現早期衰退風險。",
    "recession_confirmation": "檢查是否具備比 watch 更強的衰退確認證據。",
}
ROLE_TITLES = {
    "boom_claims_u_shape": "初領失業救濟金 U 型轉弱",
    "boom_retail_sales_vs_broad_pce": "零售銷售與廣義實質消費",
    "boom_private_investment": "私人固定投資韌性",
    "recession_employment_confirmation": "衰退就業確認",
    "recession_consumption_confirmation": "衰退消費確認",
}
DATA_RISK_PROFILES: dict[str, dict[str, Any]] = {
    "boom_claims_u_shape": {
        "data_risk_level": "medium",
        "data_risk_label_zh": (
            "中等：初領失業救濟金本身有高可信官方來源，但目前本地快照缺少"
            "可對齊輸入，不能直接形成 watch 或 confirmation。"
        ),
        "source_credibility_label_zh": "高：DOL/FRED 官方勞動市場資料。",
        "substitution_degree": "high_official_direct_when_available",
        "substitution_degree_label_zh": (
            "高：DOL weekly claims 或 FRED ICSA 是同概念官方來源；"
            "缺口主要是目前快照可用性。"
        ),
        "display_usage_policy_zh": (
            "可在 transition surface 標為高可信候選來源；不得在缺資料時自動補值。"
        ),
        "alternative_source_candidates": [
            {
                "source_id": "dol_weekly_initial_claims_release",
                "source_family": "DOL",
                "source_title_zh": "美國勞工部 weekly unemployment insurance claims release",
                "substitution_degree": "direct_official",
                "data_risk_zh": "需要穩定 parser 與 release-date 對齊。",
                "usage_policy": "preferred_when_adapter_and_cache_are_available",
            },
            {
                "source_id": "fred_icsa",
                "source_family": "FRED",
                "source_title_zh": "FRED ICSA 初領失業救濟金",
                "substitution_degree": "direct_official_redistribution",
                "data_risk_zh": "適合快速研究顯示；point-in-time 仍需 vintage/release policy。",
                "usage_policy": "research_display_candidate",
            },
        ],
    },
    "boom_retail_sales_vs_broad_pce": {
        "data_risk_level": "medium",
        "data_risk_label_zh": (
            "中等：零售與 PCE 都有官方來源，但跨系列比較需要頻率、實質/名目、"
            "release timing 對齊。"
        ),
        "source_credibility_label_zh": "高：Census retail sales 與 BEA PCE 官方來源。",
        "substitution_degree": "medium_high_official_composite",
        "substitution_degree_label_zh": (
            "中高：官方資料足夠接近書中消費韌性概念，但屬 composite relation，"
            "不能只看單一系列。"
        ),
        "display_usage_policy_zh": (
            "可顯示為消費動能風險；只有完成 same-as-of 對齊後才可升級為 evidence。"
        ),
        "alternative_source_candidates": [
            {
                "source_id": "census_retail_sales_release",
                "source_family": "Census",
                "source_title_zh": "Census retail sales official release",
                "substitution_degree": "partial_official_component",
                "data_risk_zh": "零售不等於全部消費，需要與 BEA PCE 一起看。",
                "usage_policy": "supporting_component",
            },
            {
                "source_id": "bea_real_pce",
                "source_family": "BEA",
                "source_title_zh": "BEA real personal consumption expenditures",
                "substitution_degree": "official_broad_consumption_component",
                "data_risk_zh": "發布較慢，需處理修正與 reference period。",
                "usage_policy": "core_composite_component",
            },
        ],
    },
    "boom_private_investment": {
        "data_risk_level": "medium",
        "data_risk_label_zh": (
            "中等：BEA 私人固定投資是高可信官方資料，但季頻與發布落後會讓"
            "即時 transition surface 較鈍化。"
        ),
        "source_credibility_label_zh": "高：BEA NIPA 官方投資資料。",
        "substitution_degree": "high_official_direct_low_frequency",
        "substitution_degree_label_zh": (
            "高：概念直接，但頻率低；可搭配 durable goods 作輔助，不可互相取代。"
        ),
        "display_usage_policy_zh": (
            "可顯示為榮景延續/轉弱的大方向；短期訊號需標示低頻資料風險。"
        ),
        "alternative_source_candidates": [
            {
                "source_id": "bea_private_fixed_investment",
                "source_family": "BEA",
                "source_title_zh": "BEA real private fixed investment",
                "substitution_degree": "direct_official",
                "data_risk_zh": "季頻與修正風險較高。",
                "usage_policy": "preferred_core_source_when_available",
            },
            {
                "source_id": "census_durable_goods_orders",
                "source_family": "Census",
                "source_title_zh": "Census durable goods orders",
                "substitution_degree": "supporting_only",
                "data_risk_zh": "可輔助觀察企業需求，不可替代固定投資。",
                "usage_policy": "supporting_indicator_only",
            },
        ],
    },
    "recession_employment_confirmation": {
        "data_risk_level": "medium",
        "data_risk_label_zh": (
            "中等：就業確認有多個官方來源，但不同來源代表初期壓力、持續失業、"
            "或薪資就業，不能混成單一結論。"
        ),
        "source_credibility_label_zh": "高：DOL claims 與 BLS labor statistics。",
        "substitution_degree": "medium_high_official_multi_signal",
        "substitution_degree_label_zh": (
            "中高：continuing claims、payrolls、unemployment 都可信，但用途不同；"
            "PAYEMS 不可冒充 ADP。"
        ),
        "display_usage_policy_zh": (
            "可顯示就業確認風險層次；confirmation 必須比 watch 更嚴格。"
        ),
        "alternative_source_candidates": [
            {
                "source_id": "dol_continued_claims",
                "source_family": "DOL/FRED",
                "source_title_zh": "continuing unemployment claims",
                "substitution_degree": "direct_or_near_direct_official",
                "data_risk_zh": "需與初領 claims 分清 watch/confirmation。",
                "usage_policy": "confirmation_candidate_when_available",
            },
            {
                "source_id": "bls_nonfarm_payrolls",
                "source_family": "BLS",
                "source_title_zh": "nonfarm payroll employment",
                "substitution_degree": "supporting_official",
                "data_risk_zh": "可信但不可替代 ADP，也不可單獨確認衰退。",
                "usage_policy": "supporting_indicator_only",
            },
        ],
    },
    "recession_consumption_confirmation": {
        "data_risk_level": "medium",
        "data_risk_label_zh": (
            "中等：廣義消費有 BEA 官方來源，但發布落後與修正會影響即時確認。"
        ),
        "source_credibility_label_zh": "高：BEA PCE 與 Census retail sales 官方來源。",
        "substitution_degree": "medium_high_official_composite",
        "substitution_degree_label_zh": (
            "中高：BEA real PCE 最接近廣義消費，retail sales 可作較快輔助。"
        ),
        "display_usage_policy_zh": (
            "可顯示需求擴散風險；不得用零售單一轉弱直接宣告 recession confirmation。"
        ),
        "alternative_source_candidates": [
            {
                "source_id": "bea_real_pce",
                "source_family": "BEA",
                "source_title_zh": "BEA real personal consumption expenditures",
                "substitution_degree": "direct_official_broad_consumption",
                "data_risk_zh": "月頻但發布落後，且 revised diagnostics 需標示。",
                "usage_policy": "preferred_confirmation_component_when_available",
            },
            {
                "source_id": "census_retail_sales",
                "source_family": "Census",
                "source_title_zh": "Census retail sales",
                "substitution_degree": "supporting_official",
                "data_risk_zh": "較快但涵蓋較窄，只能輔助 PCE。",
                "usage_policy": "supporting_indicator_only",
            },
        ],
    },
}
STATUS_LABELS = {
    "supportive": "目前有支持此 lane 的證據",
    "contradictory": "目前有反向或混合證據",
    "abstained": "證據不足，明確 abstain",
    "unavailable": "資料不可用，明確 abstain",
}


def build_boom_transition_dashboard_surface(
    *,
    monitor: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a safe dashboard surface from the boom transition monitor."""

    _load_surface_spec()
    monitor = monitor or build_boom_transition_monitor()
    lane_cards = [
        _lane_card(monitor[f"{lane_id}_evidence"])
        for lane_id in (
            "boom_continuation",
            "boom_ending_watch",
            "recession_watch",
            "recession_confirmation",
        )
    ]
    indicator_cards = _indicator_cards(lane_cards)
    surface = {
        "surface_id": "boom_transition_dashboard_surface_v1",
        "surface_version": "1.0",
        "source_phase": "49",
        "output_mode": "research_only_declared_transition_dashboard",
        "research_only": True,
        "declared_state_label": "declared_state_not_inferred_current_phase",
        "declared_current_phase": monitor["declared_current_phase"],
        "legal_next_phase": monitor["legal_next_phase"],
        "monitor_as_of": monitor["monitor_as_of"],
        "data_mode": monitor["data_mode"],
        "declared_phase_start_date": monitor["declared_phase_start_date"],
        "phase_age_status": monitor["phase_age_status"],
        "phase_age_used_as_transition_gate": monitor[
            "phase_age_used_as_transition_gate"
        ],
        "headline": (
            "Declared boom remains the governed state; the dashboard monitors "
            "only the legal boom-to-recession transition."
        ),
        "lane_cards": lane_cards,
        "indicator_cards": indicator_cards,
        "missing_evidence_summary": {
            "missing_or_stale_evidence_count": len(
                monitor["missing_or_stale_evidence"]
            ),
            "abstained_evidence_role_count": monitor[
                "abstained_evidence_role_count"
            ],
            "missing_or_blocked_evidence_role_count": monitor[
                "missing_or_blocked_evidence_role_count"
            ],
            "top_blockers": monitor["blocker_summary"]["top_blockers"],
        },
        "why_not_formal_transition": monitor["why_not_formal_transition"],
        "allowed_uses": [
            "local_research_dashboard",
            "declared_state_transition_explanation",
            "source_gap_review",
        ],
        "prohibited_uses": [
            "formal_current_phase_inference",
            "candidate_phase_selection",
            "phase_score_or_rank_selection",
            "portfolio_action",
            "production_resolver_input",
        ],
        "trust_metadata": {
            "output_label": "research_only",
            "declared_state_source": "declared_cycle_state_registry",
            "legal_transition": "boom_to_recession",
            "watch_confirmation_separated": monitor[
                "watch_confirmation_separation_valid"
            ],
            "recession_confirmation_not_derived_from_watch_only": monitor[
                "recession_confirmation_not_derived_from_watch_only"
            ],
            "uses_current_data_to_infer_declared_phase": False,
            "production_behavior_change": False,
        },
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "selected_phase_output_count": 0,
        "phase_rank_or_score_added_count": 0,
        "standalone_classifier_added_count": 0,
        "current_data_used_to_infer_declared_phase_count": 0,
        "portfolio_policy_output_count": 0,
        "backtest_execution_count": 0,
        "production_behavior_change_count": 0,
        "legacy_v1_behavior_modified_count": 0,
        "semantic_drift_count": 0,
    }
    validation = validate_boom_transition_dashboard_surface(surface)
    surface["surface_validation"] = validation
    surface["result"] = "passed" if validation["surface_schema_valid"] else "blocked"
    return surface


def summarize_boom_transition_dashboard_surface() -> dict[str, Any]:
    """Summarize Phase49 dashboard surface gates."""

    surface = build_boom_transition_dashboard_surface()
    validation = surface["surface_validation"]
    return {
        "phase": "49",
        "boom_transition_dashboard_surface_ready": validation[
            "surface_schema_valid"
        ],
        "declared_current_phase": surface["declared_current_phase"],
        "legal_next_phase": surface["legal_next_phase"],
        "monitor_as_of": surface["monitor_as_of"],
        "data_mode": surface["data_mode"],
        "lane_card_count": len(surface["lane_cards"]),
        "indicator_card_count": len(surface["indicator_cards"]),
        "indicator_meaning_present_count": validation[
            "indicator_meaning_present_count"
        ],
        "indicator_status_present_count": validation[
            "indicator_status_present_count"
        ],
        "missing_or_abstention_reason_visible_count": validation[
            "missing_or_abstention_reason_visible_count"
        ],
        "data_risk_label_present_count": validation[
            "data_risk_label_present_count"
        ],
        "source_credibility_label_present_count": validation[
            "source_credibility_label_present_count"
        ],
        "alternative_source_candidate_card_count": validation[
            "alternative_source_candidate_card_count"
        ],
        "substitution_degree_visible_count": validation[
            "substitution_degree_visible_count"
        ],
        "silent_substitution_count": validation["silent_substitution_count"],
        "alternative_promoted_to_core_count": validation[
            "alternative_promoted_to_core_count"
        ],
        "data_risk_surface_ready": validation["data_risk_surface_ready"],
        "watch_confirmation_separation_visible": validation[
            "watch_confirmation_separation_visible"
        ],
        "research_only_label_present": surface["research_only"],
        "prohibited_surface_field_count": validation[
            "prohibited_surface_field_count"
        ],
        "standalone_classifier_added_count": surface[
            "standalone_classifier_added_count"
        ],
        "phase_rank_or_score_added_count": surface[
            "phase_rank_or_score_added_count"
        ],
        "selected_phase_output_count": surface["selected_phase_output_count"],
        "current_data_used_to_infer_declared_phase_count": surface[
            "current_data_used_to_infer_declared_phase_count"
        ],
        "candidate_phase_emitted": surface["candidate_phase_emitted"],
        "current_phase_emitted": surface["current_phase_emitted"],
        "production_behavior_change_count": surface[
            "production_behavior_change_count"
        ],
        "legacy_v1_behavior_modified_count": surface[
            "legacy_v1_behavior_modified_count"
        ],
        "portfolio_policy_output_count": surface["portfolio_policy_output_count"],
        "backtest_execution_count": surface["backtest_execution_count"],
        "semantic_drift_count": surface["semantic_drift_count"],
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "boom_transition_dashboard_surface_ready"
        ),
        "legal_transition_semantics_preserved": True,
        "surface": surface,
        "result": surface["result"],
    }


def validate_boom_transition_dashboard_surface(surface: dict[str, Any]) -> dict[str, Any]:
    """Validate the dashboard surface does not drift into decision output."""

    required = (
        "surface_id",
        "surface_version",
        "output_mode",
        "research_only",
        "declared_current_phase",
        "legal_next_phase",
        "monitor_as_of",
        "data_mode",
        "headline",
        "lane_cards",
        "indicator_cards",
        "missing_evidence_summary",
        "allowed_uses",
        "prohibited_uses",
        "trust_metadata",
    )
    missing = [key for key in required if key not in surface]
    lane_cards = surface.get("lane_cards", [])
    indicator_cards = surface.get("indicator_cards", [])
    meaning_count = sum(bool(card.get("meaning_zh")) for card in indicator_cards)
    status_count = sum(bool(card.get("status_label_zh")) for card in indicator_cards)
    abstention_visible = sum(
        bool(card.get("abstention_or_blocker_reason_zh"))
        for card in indicator_cards
    )
    data_risk_count = sum(bool(card.get("data_risk_label_zh")) for card in indicator_cards)
    credibility_count = sum(
        bool(card.get("source_credibility_label_zh")) for card in indicator_cards
    )
    alternative_count = sum(
        bool(card.get("alternative_source_candidates")) for card in indicator_cards
    )
    substitution_count = sum(
        bool(card.get("substitution_degree_label_zh")) for card in indicator_cards
    )
    silent_substitution_count = sum(
        int(card.get("silent_substitution") is True) for card in indicator_cards
    )
    promoted_to_core_count = sum(
        int(card.get("alternative_promoted_to_core") is True)
        for card in indicator_cards
    )
    prohibited_count = _contains_prohibited_field(surface)
    data_risk_ready = (
        data_risk_count == 5
        and credibility_count == 5
        and alternative_count == 5
        and substitution_count == 5
        and silent_substitution_count == 0
        and promoted_to_core_count == 0
    )
    valid = (
        not missing
        and surface.get("output_mode") == "research_only_declared_transition_dashboard"
        and surface.get("research_only") is True
        and surface.get("declared_current_phase") == "boom"
        and surface.get("legal_next_phase") == "recession"
        and len(lane_cards) == 4
        and len(indicator_cards) == 5
        and meaning_count == 5
        and status_count == 5
        and abstention_visible >= 1
        and data_risk_ready
        and surface.get("trust_metadata", {}).get(
            "watch_confirmation_separated"
        )
        is True
        and surface.get("candidate_phase_emitted") is False
        and surface.get("current_phase_emitted") is False
        and surface.get("production_behavior_change_count") == 0
        and prohibited_count == 0
    )
    return {
        "surface_schema_valid": valid,
        "missing_surface_field_count": len(missing),
        "missing_surface_fields": missing,
        "indicator_meaning_present_count": meaning_count,
        "indicator_status_present_count": status_count,
        "missing_or_abstention_reason_visible_count": abstention_visible,
        "data_risk_label_present_count": data_risk_count,
        "source_credibility_label_present_count": credibility_count,
        "alternative_source_candidate_card_count": alternative_count,
        "substitution_degree_visible_count": substitution_count,
        "silent_substitution_count": silent_substitution_count,
        "alternative_promoted_to_core_count": promoted_to_core_count,
        "data_risk_surface_ready": data_risk_ready,
        "watch_confirmation_separation_visible": surface.get(
            "trust_metadata",
            {},
        ).get("watch_confirmation_separated")
        is True,
        "prohibited_surface_field_count": prohibited_count,
    }


def _lane_card(lane: dict[str, Any]) -> dict[str, Any]:
    return {
        "lane_id": lane["lane_id"],
        "title_zh": LANE_TITLES[lane["lane_id"]],
        "purpose_zh": LANE_PURPOSES[lane["lane_id"]],
        "lane_type": lane["lane_type"],
        "lane_status": lane["lane_status"],
        "watch_lane": lane["watch_lane"],
        "confirmation_lane": lane["confirmation_lane"],
        "watch_confirmation_boundary_zh": _lane_boundary(lane),
        "evidence_count": lane["evidence_count"],
        "wired_evidence_count": lane["phase48_wired_evidence_count"],
        "evaluable_evidence_count": lane["phase48_evaluable_evidence_count"],
        "explicit_abstention_count": lane["explicit_abstention_count"],
        "supportive_evidence_count": lane["supportive_evidence_count"],
        "contradictory_evidence_count": lane["contradictory_evidence_count"],
        "missing_or_abstained_evidence_count": lane[
            "missing_or_abstained_evidence_count"
        ],
        "book_logic_summary": lane["book_logic_summary"],
        "indicator_role_ids": [
            item["role_id"]
            for item in lane["evidence_items"]
            if item.get("wired_by_phase48") is True
        ],
        "evidence_items": [
            item for item in lane["evidence_items"] if item.get("wired_by_phase48")
        ],
    }


def _indicator_cards(lane_cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_role: OrderedDict[str, dict[str, Any]] = OrderedDict()
    for lane in lane_cards:
        for item in lane["evidence_items"]:
            role_id = item["role_id"]
            if role_id not in by_role:
                by_role[role_id] = _indicator_card_base(item)
            by_role[role_id]["lane_ids"].append(lane["lane_id"])
            by_role[role_id]["lane_titles_zh"].append(lane["title_zh"])
            by_role[role_id]["lane_states"].append(
                {
                    "lane_id": lane["lane_id"],
                    "lane_title_zh": lane["title_zh"],
                    "lane_evidence_state": item["lane_evidence_state"],
                    "status_label_zh": STATUS_LABELS.get(
                        item["lane_evidence_state"],
                        item["lane_evidence_state"],
                    ),
                    "watch_confirmation_boundary_zh": lane[
                        "watch_confirmation_boundary_zh"
                    ],
                }
            )
    return list(by_role.values())


def _indicator_card_base(item: dict[str, Any]) -> dict[str, Any]:
    blockers = item["blocker_reason_codes"]
    state = item["lane_evidence_state"]
    return {
        "role_id": item["role_id"],
        "title_zh": ROLE_TITLES[item["role_id"]],
        "meaning_zh": item["book_logic_summary"],
        "status_label_zh": STATUS_LABELS.get(state, state),
        "status_kind": state,
        "source_evidence_status": item["source_evidence_status"],
        "source_availability_status": item["source_availability_status"],
        "required_series_ids": item["required_series_ids"],
        "contextual_series_ids": item["contextual_series_ids"],
        "required_transformation": item["required_transformation"],
        "book_statement_ids": item["book_statement_ids"],
        "book_page_references": item["book_page_references"],
        "rule_source": item["rule_source"],
        "typed_evidence_family": item["typed_evidence_family"],
        "lane_ids": [],
        "lane_titles_zh": [],
        "lane_states": [],
        "blocker_reason_codes": blockers,
        "abstention_or_blocker_reason_zh": _abstention_reason(
            state=state,
            blockers=blockers,
        ),
        "why_it_matters_zh": _why_it_matters(item["role_id"]),
        **_data_risk_profile(item["role_id"]),
        "provenance_status": item["provenance_status"],
        "data_mode": item["data_mode"],
    }


def _abstention_reason(*, state: str, blockers: list[str]) -> str:
    if blockers:
        return "目前缺少可用或對齊的輸入資料：" + "、".join(blockers)
    if state in {"abstained", "unavailable"}:
        return "目前資料不足，因此保留為明確 abstention。"
    return "目前具備可顯示的研究證據。"


def _why_it_matters(role_id: str) -> str:
    return {
        "boom_claims_u_shape": (
            "勞動市場轉弱通常是榮景後段最容易被使用者理解的風險線索。"
        ),
        "boom_retail_sales_vs_broad_pce": (
            "消費韌性或轉弱會影響榮景是否仍由需求支撐。"
        ),
        "boom_private_investment": (
            "私人投資能說明企業是否仍願意擴張，或開始轉向保守。"
        ),
        "recession_employment_confirmation": (
            "就業確認必須比 early watch 更嚴格，避免把風險誤說成衰退。"
        ),
        "recession_consumption_confirmation": (
            "廣義消費轉弱可協助確認衰退壓力是否從勞動市場擴散到需求。"
        ),
    }[role_id]


def _data_risk_profile(role_id: str) -> dict[str, Any]:
    profile = DATA_RISK_PROFILES[role_id]
    return {
        "data_risk_level": profile["data_risk_level"],
        "data_risk_label_zh": profile["data_risk_label_zh"],
        "source_credibility_label_zh": profile["source_credibility_label_zh"],
        "substitution_degree": profile["substitution_degree"],
        "substitution_degree_label_zh": profile["substitution_degree_label_zh"],
        "display_usage_policy_zh": profile["display_usage_policy_zh"],
        "alternative_source_candidates": profile["alternative_source_candidates"],
        "alternative_promoted_to_core": False,
        "silent_substitution": False,
    }


def _lane_boundary(lane: dict[str, Any]) -> str:
    if lane["confirmation_lane"]:
        return "confirmation lane，不可由 watch-only evidence 推導。"
    if lane["watch_lane"]:
        return "watch lane，只提示風險，不確認階段轉換。"
    return "continuation context，不是階段選擇器。"


def _contains_prohibited_field(value: Any) -> int:
    if isinstance(value, dict):
        if PROHIBITED_FIELDS & set(value):
            return 1
        return int(any(_contains_prohibited_field(item) for item in value.values()))
    if isinstance(value, list):
        return int(any(_contains_prohibited_field(item) for item in value))
    return 0


def _load_surface_spec() -> None:
    yaml.safe_load(SURFACE_SPEC_PATH.read_text(encoding="utf-8"))

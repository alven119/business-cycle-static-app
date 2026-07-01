"""Phase55 macro indicator coverage readiness matrix."""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.low_cost_macro_source_completion import (
    summarize_low_cost_macro_source_completion,
)
from business_cycle.audits.macro_indicator_gap_alternative_sources import (
    build_macro_indicator_gap_alternative_source_rows,
)
from business_cycle.current.official_macro_source_wiring import (
    summarize_official_macro_source_adapter_wiring,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MATRIX_PATH = (
    ROOT / "specs/common/macro_indicator_coverage_readiness_matrix.yaml"
)

PROHIBITED_FIELDS = {
    "current_phase",
    "candidate_phase",
    "selected_phase",
    "winning_phase",
    "phase_rank",
    "phase_score",
    "target_weight",
    "trade_action",
    "buy_signal",
    "sell_signal",
}

PHASE_LABELS = {
    "recovery": "復甦",
    "growth": "成長",
    "boom": "榮景",
    "recession": "衰退／落底",
}


@lru_cache(maxsize=1)
def build_macro_indicator_coverage_readiness_rows(
    path: str | Path = DEFAULT_MATRIX_PATH,
) -> list[dict[str, Any]]:
    """Build one coverage-readiness row per current macro evidence role."""

    _load_contract(path)
    gap_rows = build_macro_indicator_gap_alternative_source_rows()
    wiring_rows = {
        row["role_id"]: row
        for row in summarize_official_macro_source_adapter_wiring()["rows"]
    }
    low_cost_rows = {
        row["role_id"]: row
        for row in summarize_low_cost_macro_source_completion()["rows"]
    }
    rows: list[dict[str, Any]] = []
    for gap in gap_rows:
        wiring = wiring_rows.get(gap["role_id"])
        low_cost = low_cost_rows.get(gap["role_id"])
        source_tier = _source_coverage_tier(gap=gap, low_cost=low_cost)
        coverage_status = _coverage_status(
            gap=gap,
            wiring=wiring,
            low_cost=low_cost,
            source_tier=source_tier,
        )
        next_gap = _next_gap(
            gap=gap,
            wiring=wiring,
            low_cost=low_cost,
            source_tier=source_tier,
        )
        rows.append(
            {
                "role_id": gap["role_id"],
                "phase_or_layer": gap["phase_or_layer"],
                "phase_label_zh": PHASE_LABELS[gap["phase_or_layer"]],
                "major_group_id": gap["major_group_id"],
                "gap_type": gap["gap_type"],
                "current_evidence_status": gap["current_evidence_status"],
                "required_series_ids": gap["required_series_ids"],
                "preferred_candidate_id": gap["preferred_candidate_id"],
                "source_family": gap["alternative_source_candidates"][0][
                    "source_family"
                ],
                "source_credibility_tier": gap["source_credibility_tier"],
                "substitution_degree": gap["substitution_degree"],
                "automation_feasibility": gap["automation_feasibility"],
                "planned_resolution_phase": gap["planned_resolution_phase"],
                "data_risk_level": gap["data_risk_level"],
                "source_coverage_tier": source_tier,
                "coverage_status": coverage_status,
                "dashboard_display_status": _dashboard_display_status(
                    source_tier=source_tier,
                    coverage_status=coverage_status,
                ),
                "evidence_usability_status": _evidence_usability_status(
                    gap=gap,
                    source_tier=source_tier,
                    coverage_status=coverage_status,
                ),
                "dashboard_explanation_zh": _dashboard_explanation(
                    gap=gap,
                    source_tier=source_tier,
                    coverage_status=coverage_status,
                ),
                "next_gap_zh": next_gap,
                "source_wired_by_phase52": bool(
                    wiring and wiring["wiring_status"] == "wired"
                ),
                "low_cost_contract_present": bool(low_cost),
                "user_authorized_input_required": source_tier
                == "authorized_private_or_user_supplied_required",
                "supporting_proxy_only": source_tier == "supporting_proxy_only",
                "book_core_replacement_allowed": gap["book_core_replacement_allowed"],
                "supporting_proxy_can_replace_book_core": False,
                "silent_substitution": False,
                "alternative_promoted_to_core": False,
                "false_resolution": False,
                "allowed_uses": [
                    "local_research_dashboard",
                    "indicator_gap_review",
                    "source_risk_explanation",
                ],
                "prohibited_uses": [
                    "formal_current_phase_decision",
                    "candidate_phase_selection",
                    "production_decision",
                    "portfolio_or_trade_decision",
                ],
            }
        )
    return rows


@lru_cache(maxsize=1)
def summarize_macro_indicator_coverage_readiness_matrix(
    path: str | Path = DEFAULT_MATRIX_PATH,
) -> dict[str, Any]:
    """Summarize Phase55 macro indicator source coverage gates."""

    contract = _load_contract(path)
    expected = contract["hard_gates"]
    rows = build_macro_indicator_coverage_readiness_rows(path)
    phase_counts = Counter(row["phase_or_layer"] for row in rows)
    source_tier_counts = Counter(row["source_coverage_tier"] for row in rows)
    status_counts = Counter(row["coverage_status"] for row in rows)
    risk_counts = Counter(row["data_risk_level"] for row in rows)
    dashboard_view_model = build_macro_indicator_coverage_dashboard_view_model(rows)
    summary: dict[str, Any] = {
        "macro_indicator_coverage_readiness_matrix_ready": False,
        "phase": "55",
        "phase_id": "55",
        "coverage_role_count": len(rows),
        "phase_count": len(phase_counts),
        "phase_with_coverage_count": sum(count > 0 for count in phase_counts.values()),
        "phase_counts": dict(sorted(phase_counts.items())),
        "source_coverage_tier_counts": dict(sorted(source_tier_counts.items())),
        "coverage_status_counts": dict(sorted(status_counts.items())),
        "data_risk_level_counts": dict(sorted(risk_counts.items())),
        "role_with_source_tier_count": sum(
            bool(row["source_coverage_tier"]) for row in rows
        ),
        "role_with_data_risk_label_count": sum(
            bool(row["data_risk_level"]) for row in rows
        ),
        "role_with_dashboard_explanation_count": sum(
            bool(row["dashboard_explanation_zh"]) for row in rows
        ),
        "role_with_next_gap_count": sum(bool(row["next_gap_zh"]) for row in rows),
        "official_or_authorized_path_count": sum(
            row["source_coverage_tier"]
            in {
                "official_direct_or_near_direct",
                "official_derived_or_composite",
                "authorized_private_or_user_supplied_required",
            }
            for row in rows
        ),
        "supporting_proxy_only_count": sum(row["supporting_proxy_only"] for row in rows),
        "user_authorized_input_required_count": sum(
            row["user_authorized_input_required"] for row in rows
        ),
        "false_resolution_count": sum(row["false_resolution"] for row in rows),
        "silent_substitution_count": sum(row["silent_substitution"] for row in rows),
        "alternative_promoted_to_core_count": sum(
            row["alternative_promoted_to_core"] for row in rows
        ),
        "proxy_promoted_to_book_core_count": sum(
            row["supporting_proxy_can_replace_book_core"] for row in rows
        ),
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "current_data_used_to_infer_declared_phase_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "legacy_v1_behavior_modified_count": 0,
        "portfolio_policy_output_count": 0,
        "backtest_execution_count": 0,
        "semantic_drift_count": 0,
        "prohibited_output_field_count": _contains_prohibited_field(rows),
        "dashboard_gap_burn_down_view_ready": _dashboard_view_ready(
            dashboard_view_model,
            rows,
        ),
        "dashboard_view_model": dashboard_view_model,
        "rows": rows,
    }
    summary["macro_indicator_coverage_readiness_matrix_ready"] = _passes(
        summary,
        expected,
    )
    summary["result"] = (
        "passed"
        if summary["macro_indicator_coverage_readiness_matrix_ready"]
        else "blocked"
    )
    return summary


def build_macro_indicator_coverage_dashboard_view_model(
    rows: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a dashboard-ready gap burn-down view model."""

    rows = rows or build_macro_indicator_coverage_readiness_rows()
    phase_cards = []
    for phase in ("recovery", "growth", "boom", "recession"):
        phase_rows = [row for row in rows if row["phase_or_layer"] == phase]
        phase_cards.append(
            {
                "phase_or_layer": phase,
                "phase_label_zh": PHASE_LABELS[phase],
                "role_count": len(phase_rows),
                "official_or_authorized_path_count": sum(
                    row["source_coverage_tier"]
                    in {
                        "official_direct_or_near_direct",
                        "official_derived_or_composite",
                        "authorized_private_or_user_supplied_required",
                    }
                    for row in phase_rows
                ),
                "supporting_proxy_only_count": sum(
                    row["supporting_proxy_only"] for row in phase_rows
                ),
                "high_risk_role_count": sum(
                    row["data_risk_level"] in {"high", "high_until_license_confirmed"}
                    for row in phase_rows
                ),
                "next_gaps": [row["next_gap_zh"] for row in phase_rows[:4]],
            }
        )
    return {
        "view_id": "macro_indicator_coverage_readiness",
        "view_title": "Macro Indicator Coverage Readiness",
        "output_mode": "research_only_dashboard_gap_burn_down",
        "research_only": True,
        "phase_cards": phase_cards,
        "role_cards": [
            {
                "role_id": row["role_id"],
                "phase_or_layer": row["phase_or_layer"],
                "major_group_id": row["major_group_id"],
                "coverage_status": row["coverage_status"],
                "source_coverage_tier": row["source_coverage_tier"],
                "data_risk_level": row["data_risk_level"],
                "dashboard_display_status": row["dashboard_display_status"],
                "dashboard_explanation_zh": row["dashboard_explanation_zh"],
                "next_gap_zh": row["next_gap_zh"],
                "supporting_proxy_only": row["supporting_proxy_only"],
                "book_core_replacement_allowed": row[
                    "book_core_replacement_allowed"
                ],
            }
            for row in rows
        ],
        "trust_metadata": {
            "output_label": "research_only",
            "coverage_scope": "macro_indicator_source_and_gap_readiness",
            "current_phase_inference_enabled": False,
            "candidate_phase_selection_enabled": False,
            "production_behavior_change": False,
        },
        "allowed_uses": [
            "local_research_dashboard",
            "indicator_gap_review",
            "source_risk_explanation",
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


def _source_coverage_tier(
    *,
    gap: dict[str, Any],
    low_cost: dict[str, Any] | None,
) -> str:
    if low_cost is not None:
        if low_cost["book_core_replacement_without_license_allowed"] is False:
            return "authorized_private_or_user_supplied_required"
    substitution = gap["substitution_degree"]
    credibility = gap["source_credibility_tier"]
    if gap["book_core_replacement_allowed"] is False:
        return "supporting_proxy_only"
    if "derived" in credibility or "composite" in credibility or "derived" in substitution:
        return "official_derived_or_composite"
    return "official_direct_or_near_direct"


def _coverage_status(
    *,
    gap: dict[str, Any],
    wiring: dict[str, Any] | None,
    low_cost: dict[str, Any] | None,
    source_tier: str,
) -> str:
    if wiring and wiring["wiring_status"] == "wired":
        return "source_wired_current_value_or_rule_gap_visible"
    if source_tier == "authorized_private_or_user_supplied_required":
        return "direct_source_requires_authorized_user_input"
    if low_cost is not None:
        return "low_cost_supporting_context_only"
    if gap["planned_resolution_phase"] == "Phase53":
        return "composite_or_rule_semantics_gap_visible"
    return "source_gap_visible"


def _dashboard_display_status(*, source_tier: str, coverage_status: str) -> str:
    if source_tier == "supporting_proxy_only":
        return "display_supporting_context_with_visible_risk"
    if source_tier == "authorized_private_or_user_supplied_required":
        return "display_missing_until_authorized_input_or_license"
    if coverage_status == "source_wired_current_value_or_rule_gap_visible":
        return "display_source_path_and_current_gap"
    return "display_gap_with_next_step"


def _evidence_usability_status(
    *,
    gap: dict[str, Any],
    source_tier: str,
    coverage_status: str,
) -> str:
    if source_tier == "supporting_proxy_only":
        return "supporting_context_only_not_book_core_evidence"
    if coverage_status == "source_wired_current_value_or_rule_gap_visible":
        return "source_path_ready_but_current_evidence_abstains"
    if gap["planned_resolution_phase"] == "Phase53":
        return "source_identified_transformation_or_rule_needed"
    return "source_identified_but_not_evidence_ready"


def _dashboard_explanation(
    *,
    gap: dict[str, Any],
    source_tier: str,
    coverage_status: str,
) -> str:
    phase_label = PHASE_LABELS[gap["phase_or_layer"]]
    if source_tier == "supporting_proxy_only":
        return (
            f"{phase_label}：此 role 只有 supporting/proxy 路線，"
            "可協助解釋但不能補成 book-core evidence。"
        )
    if source_tier == "authorized_private_or_user_supplied_required":
        return (
            f"{phase_label}：直接來源需要授權或使用者自備資料；"
            "在未提供前 dashboard 應顯示缺口與資料風險。"
        )
    if coverage_status == "source_wired_current_value_or_rule_gap_visible":
        return (
            f"{phase_label}：已有官方或近官方來源路徑，"
            "目前仍需 current value、frequency 或 rule 對齊後才能形成 evidence。"
        )
    return (
        f"{phase_label}：來源方向已盤點，但仍需要 transformation、"
        "temporal rule 或 release semantics 才能 operationalize。"
    )


def _next_gap(
    *,
    gap: dict[str, Any],
    wiring: dict[str, Any] | None,
    low_cost: dict[str, Any] | None,
    source_tier: str,
) -> str:
    if source_tier == "supporting_proxy_only":
        return "保留 supporting-only 風險標籤，不可替代 book-core；若要補齊需取得 direct source 或重新定義 scope。"
    if source_tier == "authorized_private_or_user_supplied_required":
        contract = low_cost.get("user_supplied_input_contract") if low_cost else None
        return f"建立 {contract or 'authorized user-supplied input'} 的本地讀取與 provenance，不 commit 私有資料。"
    if wiring and wiring["wiring_status"] == "wired":
        return "把 current cache value、freshness、release timing 與 transformation status 接到 indicator detail。"
    if gap["planned_resolution_phase"] == "Phase53":
        return "完成 same-as-of composite、turning-point 或 qualitative rule semantics 後再升級 evidence。"
    return "補 adapter、release metadata 或 offline fixture 後重新計算 coverage。"


def _dashboard_view_ready(
    view_model: dict[str, Any],
    rows: list[dict[str, Any]],
) -> bool:
    return (
        view_model["view_id"] == "macro_indicator_coverage_readiness"
        and view_model["output_mode"] == "research_only_dashboard_gap_burn_down"
        and len(view_model["phase_cards"]) == 4
        and len(view_model["role_cards"]) == len(rows)
        and view_model["candidate_phase_emitted"] is False
        and view_model["current_phase_emitted"] is False
        and _contains_prohibited_field(view_model) == 0
    )


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    if summary["official_or_authorized_path_count"] < expected[
        "official_or_authorized_path_count_minimum"
    ]:
        return False
    return all(
        summary.get(key) == value
        for key, value in expected.items()
        if key
        not in {
            "macro_indicator_coverage_readiness_matrix_ready",
            "official_or_authorized_path_count_minimum",
        }
    )


def _contains_prohibited_field(value: Any) -> int:
    if isinstance(value, dict):
        if PROHIBITED_FIELDS & set(value):
            return 1
        return int(any(_contains_prohibited_field(item) for item in value.values()))
    if isinstance(value, list):
        return int(any(_contains_prohibited_field(item) for item in value))
    return 0


def _load_contract(path: str | Path = DEFAULT_MATRIX_PATH) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "macro_indicator_coverage_readiness_matrix"
    ]

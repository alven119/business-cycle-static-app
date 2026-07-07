"""Phase85 current data refresh UX view model."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from business_cycle.render.current_macro_numeric_chart_coverage import (
    build_current_macro_numeric_chart_coverage_view_model,
)
from business_cycle.render.indicator_dashboard_explanation_drilldown import (
    build_indicator_dashboard_explanation_drilldown_view_model,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = ROOT / "specs/common/current_data_refresh_ux.yaml"

PROHIBITED_FIELDS = {
    "candidate_phase",
    "current_phase",
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


def build_current_data_refresh_ux(
    *,
    current_macro_numeric_chart_coverage: dict[str, Any] | None = None,
    indicator_dashboard_explanation_drilldown: dict[str, Any] | None = None,
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Build a dashboard-ready refresh UX artifact without running live refresh."""

    contract = _load_contract(path)
    coverage = (
        current_macro_numeric_chart_coverage
        or build_current_macro_numeric_chart_coverage_view_model()
    )
    drilldown = (
        indicator_dashboard_explanation_drilldown
        or build_indicator_dashboard_explanation_drilldown_view_model()
    )
    rows = list(coverage["role_chart_coverage_rows"])
    latest_dates = sorted(
        {
            context["latest_observation_date"]
            for row in rows
            for context in row.get("latest_numeric_context", [])
        }
    )
    risk_counts = Counter(row["data_risk_level"] for row in rows)
    chart_counts = Counter(row["chart_coverage_status"] for row in rows)
    continuity_counts = drilldown["continuity_status_counts"]
    trust = coverage.get("trust_metadata", {})
    cache_scope = coverage.get("cache_scope") or trust.get(
        "coverage_scope",
        "fixture_current_cache_connectivity",
    )
    data_mode = coverage["data_mode"]
    artifact: dict[str, Any] = {
        "artifact_id": contract["contract_id"],
        "artifact_version": contract["contract_version"],
        "phase": "85",
        "phase_id": 85,
        "phase_label": "current_data_refresh_ux_hardened",
        "view_id": "current_data_refresh_ux",
        "view_title": "Current Data Refresh UX",
        "output_mode": contract["output_policy"]["output_mode"],
        "research_only": True,
        "snapshot_as_of": coverage["snapshot_as_of"],
        "data_mode": data_mode,
        "cache_scope": cache_scope,
        "refresh_mode_summary": _refresh_mode_summary(data_mode, cache_scope, trust),
        "last_update_summary": {
            "latest_visible_observation_date": latest_dates[-1] if latest_dates else None,
            "snapshot_as_of": coverage["snapshot_as_of"],
            "last_update_status": (
                "fixture_or_local_cache_timestamp_visible_not_live_refresh"
            ),
            "last_update_label_zh": (
                "目前頁面顯示的是 fixture/local cache 可見日期，不代表 live "
                "source 已在本 phase 更新。"
            ),
        },
        "freshness_summary": {
            "freshness_mode": "chart_payload_and_cache_visibility",
            "available_fixture_or_cache_role_count": chart_counts[
                "available_fixture_current_cache"
            ]
            + chart_counts["available_local_current_cache"],
            "unavailable_role_count": chart_counts["unavailable_no_official_series"],
            "metadata_ready_value_missing_drilldown_count": continuity_counts.get(
                "metadata_ready_value_missing",
                0,
            ),
            "source_metadata_incomplete_drilldown_count": continuity_counts.get(
                "source_metadata_incomplete_abstain",
                0,
            ),
            "authorized_input_required_drilldown_count": continuity_counts.get(
                "authorized_input_required",
                0,
            ),
            "freshness_label_zh": (
                "有數值的角色可作 dashboard 解釋；metadata-only、授權或 source "
                "不完整的角色維持可見缺口。"
            ),
        },
        "source_risk_refresh_summary": {
            "source_risk_status_counts": dict(sorted(risk_counts.items())),
            "source_risk_visible_role_count": len(rows),
            "elevated_source_risk_role_count": _elevated_source_risk_count(rows),
            "source_risk_label_zh": (
                "所有 role 均保留資料風險標籤；中高風險不會被當作正式可靠輸入。"
            ),
        },
        "refresh_cards": _refresh_cards(
            coverage=coverage,
            latest_visible_date=latest_dates[-1] if latest_dates else None,
            risk_rows=rows,
            continuity_counts=continuity_counts,
            cache_scope=cache_scope,
        ),
        "manual_refresh_handoff_steps": _manual_refresh_handoff_steps(),
        "trust_caveats": _trust_caveats(),
        "role_count": coverage["role_count"],
        "role_with_numeric_context_count": coverage[
            "role_with_numeric_context_count"
        ],
        "role_with_available_chart_payload_count": coverage[
            "role_with_available_chart_payload_count"
        ],
        "role_without_official_series_count": coverage[
            "role_without_official_series_count"
        ],
        "source_risk_visible_role_count": len(rows),
        "elevated_source_risk_role_count": _elevated_source_risk_count(rows),
        "metadata_ready_value_missing_drilldown_count": continuity_counts.get(
            "metadata_ready_value_missing",
            0,
        ),
        "source_metadata_incomplete_drilldown_count": continuity_counts.get(
            "source_metadata_incomplete_abstain",
            0,
        ),
        "authorized_input_required_drilldown_count": continuity_counts.get(
            "authorized_input_required",
            0,
        ),
        "live_refresh_executed_count": 0,
        "live_fetch_attempt_count": 0,
        "repository_output_count": 0,
        "point_in_time_claim_count": 0,
        "current_data_used_to_infer_declared_phase_count": 0,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "role_count_voting_added_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "allowed_uses": [
            "local_research_dashboard",
            "current_cache_status_review",
            "manual_refresh_handoff_review",
        ],
        "prohibited_uses": [
            "formal_current_phase_decision",
            "candidate_phase_selection",
            "production_decision",
            "portfolio_or_trade_decision",
        ],
        "trust_metadata": {
            "output_label": "research_only",
            "fixture_or_local_cache_only": True,
            "live_refresh_attempted": False,
            "live_refresh_executed": False,
            "point_in_time_result": False,
            "current_phase_inference_enabled": False,
            "candidate_phase_selection_enabled": False,
            "production_behavior_change": False,
        },
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "declared_state_preserved_current_data_refresh_ux_hardened"
        ),
    }
    artifact["refresh_ux_card_count"] = len(artifact["refresh_cards"])
    artifact["manual_refresh_handoff_step_count"] = len(
        artifact["manual_refresh_handoff_steps"],
    )
    artifact["refresh_trust_caveat_count"] = len(artifact["trust_caveats"])
    artifact["refresh_mode_summary_ready"] = bool(artifact["refresh_mode_summary"])
    artifact["last_update_summary_ready"] = bool(
        artifact["last_update_summary"]["last_update_status"],
    )
    artifact["freshness_summary_ready"] = bool(artifact["freshness_summary"])
    artifact["source_risk_refresh_summary_ready"] = bool(
        artifact["source_risk_refresh_summary"],
    )
    artifact["manual_refresh_handoff_ready"] = (
        artifact["manual_refresh_handoff_step_count"] == 5
    )
    artifact["prohibited_output_field_count"] = _contains_prohibited_field(artifact)
    artifact["current_data_refresh_ux_ready"] = _passes(
        artifact,
        contract["hard_gates"],
    )
    artifact["result"] = (
        "passed" if artifact["current_data_refresh_ux_ready"] else "blocked"
    )
    return artifact


def build_current_data_refresh_ux_view_model(
    artifact: dict[str, Any] | None = None,
    *,
    current_macro_numeric_chart_coverage: dict[str, Any] | None = None,
    indicator_dashboard_explanation_drilldown: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return the artifact shape consumed by the dashboard bundle."""

    artifact = artifact or build_current_data_refresh_ux(
        current_macro_numeric_chart_coverage=current_macro_numeric_chart_coverage,
        indicator_dashboard_explanation_drilldown=(
            indicator_dashboard_explanation_drilldown
        ),
    )
    return {
        key: artifact[key]
        for key in (
            "view_id",
            "view_title",
            "output_mode",
            "research_only",
            "snapshot_as_of",
            "data_mode",
            "cache_scope",
            "refresh_mode_summary",
            "last_update_summary",
            "freshness_summary",
            "source_risk_refresh_summary",
            "refresh_cards",
            "manual_refresh_handoff_steps",
            "trust_caveats",
            "role_count",
            "role_with_numeric_context_count",
            "role_with_available_chart_payload_count",
            "role_without_official_series_count",
            "source_risk_visible_role_count",
            "elevated_source_risk_role_count",
            "metadata_ready_value_missing_drilldown_count",
            "source_metadata_incomplete_drilldown_count",
            "authorized_input_required_drilldown_count",
            "live_refresh_executed_count",
            "live_fetch_attempt_count",
            "repository_output_count",
            "point_in_time_claim_count",
            "prohibited_output_field_count",
            "current_data_used_to_infer_declared_phase_count",
            "standalone_classifier_added_count",
            "phase_rank_or_score_added_count",
            "role_count_voting_added_count",
            "candidate_phase_emitted",
            "current_phase_emitted",
            "production_behavior_change_count",
            "semantic_drift_count",
            "allowed_uses",
            "prohibited_uses",
            "trust_metadata",
            "current_data_refresh_ux_ready",
        )
    }


def summarize_current_data_refresh_ux(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Return compact Phase85 refresh UX readiness fields."""

    artifact = build_current_data_refresh_ux(path=path)
    return {
        "phase": "85",
        "phase_id": 85,
        "current_data_refresh_ux_ready": artifact["current_data_refresh_ux_ready"],
        "refresh_mode_summary_ready": artifact["refresh_mode_summary_ready"],
        "last_update_summary_ready": artifact["last_update_summary_ready"],
        "freshness_summary_ready": artifact["freshness_summary_ready"],
        "source_risk_refresh_summary_ready": artifact[
            "source_risk_refresh_summary_ready"
        ],
        "manual_refresh_handoff_ready": artifact["manual_refresh_handoff_ready"],
        "refresh_ux_card_count": artifact["refresh_ux_card_count"],
        "manual_refresh_handoff_step_count": artifact[
            "manual_refresh_handoff_step_count"
        ],
        "refresh_trust_caveat_count": artifact["refresh_trust_caveat_count"],
        "role_count": artifact["role_count"],
        "role_with_numeric_context_count": artifact[
            "role_with_numeric_context_count"
        ],
        "role_with_available_chart_payload_count": artifact[
            "role_with_available_chart_payload_count"
        ],
        "role_without_official_series_count": artifact[
            "role_without_official_series_count"
        ],
        "source_risk_visible_role_count": artifact["source_risk_visible_role_count"],
        "elevated_source_risk_role_count": artifact[
            "elevated_source_risk_role_count"
        ],
        "metadata_ready_value_missing_drilldown_count": artifact[
            "metadata_ready_value_missing_drilldown_count"
        ],
        "source_metadata_incomplete_drilldown_count": artifact[
            "source_metadata_incomplete_drilldown_count"
        ],
        "authorized_input_required_drilldown_count": artifact[
            "authorized_input_required_drilldown_count"
        ],
        "live_refresh_executed_count": artifact["live_refresh_executed_count"],
        "live_fetch_attempt_count": artifact["live_fetch_attempt_count"],
        "repository_output_count": artifact["repository_output_count"],
        "point_in_time_claim_count": artifact["point_in_time_claim_count"],
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
        "current_data_refresh_ux_artifact": artifact,
        "result": artifact["result"],
    }


def _refresh_mode_summary(
    data_mode: str,
    cache_scope: str,
    trust: dict[str, Any],
) -> dict[str, Any]:
    return {
        "data_mode": data_mode,
        "cache_scope": cache_scope,
        "live_refresh_attempted": bool(trust.get("live_refresh_attempted", False)),
        "live_refresh_executed": False,
        "refresh_mode_label_zh": (
            "目前顯示 fixture/local cache connectivity；live refresh 需另行 "
            "opt-in 執行。"
        ),
    }


def _refresh_cards(
    *,
    coverage: dict[str, Any],
    latest_visible_date: str | None,
    risk_rows: list[dict[str, Any]],
    continuity_counts: dict[str, int],
    cache_scope: str,
) -> list[dict[str, Any]]:
    return [
        {
            "card_id": "refresh_mode",
            "title_zh": "資料模式",
            "status_label": coverage["data_mode"],
            "summary_zh": f"cache scope={cache_scope}; live refresh 未在本 phase 執行。",
        },
        {
            "card_id": "last_update",
            "title_zh": "最後可見資料日期",
            "status_label": latest_visible_date or "unavailable",
            "summary_zh": "此日期來自 fixture/local cache chart payload，不是正式發布監控。",
        },
        {
            "card_id": "freshness",
            "title_zh": "資料新鮮度",
            "status_label": (
                f"{coverage['role_with_available_chart_payload_count']} roles visible"
            ),
            "summary_zh": (
                f"{continuity_counts.get('metadata_ready_value_missing', 0)} 個 "
                "metadata-ready role 仍缺數值。"
            ),
        },
        {
            "card_id": "source_risk",
            "title_zh": "來源風險",
            "status_label": f"{_elevated_source_risk_count(risk_rows)} elevated roles",
            "summary_zh": "替代或授權風險仍顯示在指標層，不會被靜默當成完整資料。",
        },
        {
            "card_id": "manual_handoff",
            "title_zh": "手動更新交接",
            "status_label": "operator opt-in required",
            "summary_zh": "需要由操作者明確指定 local cache 或 opt-in refresh，dashboard 才重建。",
        },
    ]


def _manual_refresh_handoff_steps() -> list[dict[str, str]]:
    return [
        {
            "step_id": "review_cache_scope",
            "label_zh": "確認目前 dashboard 顯示的是 fixture、tmp cache 或 explicit local cache。",
        },
        {
            "step_id": "run_opt_in_refresh",
            "label_zh": "若需要更新，使用既有本機 refresh 指令並明確指定 ignored/local cache 位置。",
        },
        {
            "step_id": "rebuild_dashboard",
            "label_zh": "用 explicit cache 重新產生 dashboard，確認 data mode 與 cache scope 已標示。",
        },
        {
            "step_id": "review_freshness_and_risk",
            "label_zh": "檢查 freshness、last visible date、source risk 與 missing-role 摘要。",
        },
        {
            "step_id": "preserve_declared_registry",
            "label_zh": "不得因 refresh 結果改寫 declared registry 或輸出正式 phase 判斷。",
        },
    ]


def _trust_caveats() -> list[str]:
    return [
        "目前面板只解釋 fixture/local cache 狀態，不代表 live source 成功更新。",
        "latest/current value 是 revised/current dashboard context，不是 point-in-time result。",
        "metadata-only、授權與 source-incomplete role 必須保持可見缺口。",
        "source risk label 不會被平均或縮小成正式判斷信心。",
        "declared boom 與 legal next recession 仍由受治理 registry/state machine 提供。",
    ]


def _elevated_source_risk_count(rows: list[dict[str, Any]]) -> int:
    return sum(
        row["data_risk_level"] in {"medium", "medium_high", "high_until_license_confirmed"}
        for row in rows
    )


def _passes(artifact: dict[str, Any], expected: dict[str, Any]) -> bool:
    for key, value in expected.items():
        if key == "current_data_refresh_ux_ready":
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
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return payload["current_data_refresh_ux"]

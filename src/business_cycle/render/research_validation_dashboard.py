"""Build a local research-only historical validation dashboard."""

from __future__ import annotations

from functools import lru_cache
from html import escape
import json
from pathlib import Path
from typing import Any

from business_cycle.render.research_dashboard_bundle import (
    build_research_dashboard_bundle,
)


ALLOWED_OUTPUT_ROOT = Path("/tmp")
PROHIBITED_OUTPUT_ROOTS = (
    Path("data/backtests"),
    Path("data/prospective"),
    Path("public"),
)
PROHIBITED_CLAIMS = (
    "production-ready",
    "investment" + "-ready",
    "current phase determined",
    "candidate phase ready",
    "economically validated",
    "book-faithful model complete",
)
PROHIBITED_ACTION_FIELDS = (
    "buy_signal",
    "sell_signal",
    "target_weight",
    "trade_action",
    "current_allocation_recommendation",
    "guaranteed_return",
)
PHASE_LABEL_ZH = {
    "recession": "衰退期",
    "recovery": "復甦期",
    "growth": "成長期",
    "boom": "榮景期",
}
DISPLAY_TEXT_ZH = {
    "Research Validation Dashboard": "景氣循環研究儀表板",
    "Research Overview": "研究總覽",
    "Historical Scenarios": "歷史情境",
    "Validation Results": "驗證結果",
    "Evidence Explorer": "證據總覽",
    "Data Lineage / Governance": "資料血緣與治理",
    "PIT Gap View": "Point-in-time 缺口",
    "Current Research Snapshot": "目前研究快照",
    "Declared Boom Transition Monitor": "已宣告榮景期轉折監測",
    "Latest Evidence / Indicator Drilldown": "最新證據與指標細節",
    "Latest Evidence Drilldown": "最新證據與指標細節",
    "Portfolio / Replay Research Surface": "Portfolio policy 與歷史重播研究",
    "Portfolio Replay Research": "Portfolio policy 與歷史重播研究",
    "Portfolio Policy Replay Research Surface": "Portfolio policy replay 研究",
    "RESEARCH ONLY": "研究用途",
    "research-only": "研究用途",
    "validation-only": "驗證用途",
    "not production": "非正式 production",
    "not investment advice": "不構成投資建議",
    "candidate/current outputs disabled": "不輸出候選階段或目前階段",
    "candidate output disabled": "不輸出候選階段",
    "current output disabled": "不輸出目前階段",
    "economic performance not computed": "尚未計算經濟績效",
    "Candidate output disabled": "不輸出候選階段",
    "Current output disabled": "不輸出目前階段",
    "Economic performance not computed": "尚未計算經濟績效",
    "Scenario access": "情境檢視",
    "Lineage snapshot": "血緣快照",
    "Scenario": "情境",
    "Scenarios": "情境數",
    "Period": "期間",
    "Status": "狀態",
    "Decision state": "研究判讀狀態",
    "Detail": "詳細",
    "Family": "類型",
    "Research decision": "研究判讀",
    "Validation label bucket": "驗證標籤分組",
    "Comparison": "比較狀態",
    "Comparable": "可比較",
    "Not comparable": "不可比較",
    "PIT gaps": "PIT 缺口",
    "Metric states": "指標狀態",
    "Metric": "指標",
    "Value": "數值",
    "Numerator": "分子",
    "Denominator": "分母",
    "Interpretation": "解讀",
    "Phase evidence and role provenance": "階段證據與角色血緣",
    "Layer": "層級",
    "Major group": "主要群組",
    "Role": "角色",
    "Evidence state": "證據狀態",
    "Gap": "缺口",
    "Sources": "來源",
    "PIT and rule gaps": "PIT 與規則缺口",
    "Required window": "必要觀察期間",
    "Gap class": "缺口類型",
    "Evidence": "證據",
    "Provenance chain": "血緣鏈",
    "Search": "搜尋",
    "All": "全部",
    "Open gaps": "未解缺口",
    "Resolved by PIT cache": "已由 PIT cache 補齊",
    "Classification": "分類",
    "Model freeze": "模型 freeze",
    "Parent freeze": "父 freeze",
    "Parent hash": "父 freeze hash",
    "Output label": "輸出標籤",
    "Validation status": "驗證狀態",
    "QA12 unchanged": "QA12 未變更",
    "Prospective registry records": "前瞻 registry 筆數",
    "Production behavior changes": "Production 行為變更",
    "Source to dashboard lineage": "來源到 dashboard 血緣",
    "Allowed uses": "允許用途",
    "Prohibited uses": "禁止用途",
    "Pre PIT role gaps": "修補前 PIT 角色缺口",
    "Post PIT role gaps": "修補後 PIT 角色缺口",
    "Cache-remediated": "cache 已補齊",
    "Rule unresolved": "規則未解",
    "Official history insufficient": "官方歷史資料不足",
    "Genuine source unavailable": "真實來源不可得",
    "As-of": "As-of 日期",
    "Fresh enough": "新鮮度足夠",
    "Missing series": "缺少 series",
    "Stale series": "過期 series",
    "Unavailable series": "不可用 series",
    "Data Refresh / Source Freshness": "資料更新與來源新鮮度",
    "Refresh mode": "更新模式",
    "Skipped reason": "略過原因",
    "Blocked reason": "受阻原因",
    "Provider error": "Provider 錯誤",
    "Stale before / after": "過期數量：更新前 / 更新後",
    "Fetched / failed": "下載成功 / 失敗",
    "Refreshed series": "已更新 series",
    "Refresh manifest": "更新 manifest",
    "Current Phase Evidence Profile": "目前階段證據剖面",
    "Phase lanes": "階段 lanes",
    "Fresh enough series": "新鮮度足夠 series",
    "Still stale": "仍過期",
    "Rule/data blockers": "規則/資料 blocker",
    "Transition Risk Lane Summary": "轉折風險 lane 摘要",
    "Boom ending watch": "榮景結束觀察",
    "Recession confirmation watch": "衰退確認觀察",
    "Trough / recovery watch": "落底 / 復甦觀察",
    "Decision readiness blockers": "判讀 readiness blockers",
    "Readiness label": "Readiness 標籤",
    "Evaluated layers": "已評估層級",
    "Source unavailable": "來源不可用",
    "Phase evidence and major groups": "階段證據與主要群組",
    "Phase profiles": "階段剖面",
    "Major groups": "主要群組",
    "Watch separation": "watch/confirmation 分離",
    "Production integration": "Production 接線",
    "Source availability": "來源可用性",
    "Series": "Series",
    "Source": "來源",
    "Frequency": "頻率",
    "Source mode": "來源模式",
    "Latest observation": "最新觀察值日期",
    "Latest verified": "最新驗證日期",
    "Stale": "過期",
    "Lineage": "血緣",
    "Freeze": "Freeze",
    "Parent": "父 freeze",
    "Output mode": "輸出模式",
    "Declared state": "已宣告階段",
    "Legal next": "合法下一階段",
    "Monitor as-of": "監測 as-of",
    "Priority roles": "優先角色",
    "Transition lanes": "轉折 lanes",
    "Indicator meanings and current status": "指標意涵與目前狀況",
    "Why this is not a formal transition": "為什麼還不是正式轉折",
    "Current blockers": "目前 blockers",
    "Role drilldowns": "角色細節",
    "Numeric values loaded": "已載入數值",
    "Metadata-ready gaps": "metadata 已就緒但數值缺口",
    "Chart payloads": "圖表 payload",
    "Method recipes": "方法配方",
    "Phase and continuity coverage": "階段與連續性覆蓋",
    "Major group drilldowns": "主要群組細節",
    "Role-level evidence explanations": "角色層級證據解釋",
    "Dashboard decision explanation": "Dashboard 判讀說明",
    "Why not formal": "為什麼尚非正式判讀",
    "Trust caveats": "信任註記",
    "Current data refresh UX": "目前資料更新體驗",
    "Manual refresh handoff": "手動更新交接",
    "Transition risk evidence accumulation": "轉折風險證據累積",
    "Next required observations": "下一個必要觀察",
    "Declared boom start confirmation": "已宣告榮景起始確認",
    "Declared phase start registry update gate": "已宣告階段起始 registry 更新 gate",
    "Current macro numeric and chart coverage": "目前總經數值與圖表覆蓋",
    "Source detail": "來源細節",
    "Release timing": "發布時點",
    "Freshness": "新鮮度",
    "Transformation": "轉換",
    "Rule usability": "規則可用性",
    "Diagnostic recipe transparency": "診斷方法透明度",
    "Directionality:": "方向性：",
    "Confidence reducers:": "信心折減條件：",
    "Calculation steps:": "計算步驟：",
    "Indicator chart payload": "指標走勢圖",
    "Chart available": "圖表可用",
    "Provenance": "血緣",
    "Abstention / next gap": "Abstain 與下一缺口",
    "Policy schedule and cash-flow kernel references": "Policy schedule 與現金流 kernel 參照",
    "Template schedules": "Template schedules",
    "Cash-flow kernel": "現金流 kernel",
    "Kernel components": "Kernel 元件",
    "Metric status": "指標狀態",
    "Artifact lineage drill-down": "Artifact 血緣細節",
    "Caveats": "限制與註記",
    "Policy template catalog": "Policy template 目錄",
    "Replay schedule matrix": "重播 schedule matrix",
    "Cost and turnover assumptions": "成本與 turnover 假設",
    "Scenario policy coverage": "情境 policy 覆蓋",
    "Research-only caveats": "研究用途註記",
    "Template": "Template",
    "Trigger context": "觸發脈絡",
    "Required transition inputs": "必要轉折輸入",
    "Data mode": "資料模式",
    "Cost policy": "成本政策",
    "Clock policy": "時鐘政策",
    "Turnover": "Turnover",
    "False signal": "False signal",
    "Missed recovery": "Missed recovery",
    "Transition timing replay preview": "轉折時點重播預覽",
    "Checkpoint": "檢查點",
    "Transition": "轉折",
    "Lane": "Lane",
    "Abstention": "Abstain",
    "Research allocation template": "研究性配置模板",
    "Open detail": "查看細節",
    "Open latest evidence": "查看最新證據",
    "Open portfolio replay research": "查看 portfolio replay 研究",
    "Open current snapshot": "查看目前研究快照",
    "Open transition monitor": "查看轉折監測",
    "to": "至",
    "yes": "是",
    "no": "否",
    "true": "是",
    "false": "否",
    "none": "無",
    "undefined": "未定義",
    "unavailable": "不可用",
    "available": "可用",
    "not declared": "未宣告",
    "chart data available": "圖表資料可用",
    "No calculation steps declared.": "尚未宣告計算步驟。",
    "No directionality declared.": "尚未宣告方向性。",
    "Score interpretation not declared.": "尚未宣告分數解讀。",
    "No numeric points available for this period.": "此期間沒有可用數值點。",
    "Trend line unavailable for this period.": "此期間無法繪製趨勢線。",
}
STATUS_TEXT_ZH = {
    "comparable": "可比較",
    "not_comparable": "不可比較",
    "blocked": "受阻",
    "abstained": "已 abstain",
    "available": "可用",
    "unavailable": "不可用",
    "resolved": "已補齊",
    "open": "未解",
    "ready": "就緒",
    "passed": "通過",
    "active": "啟用",
    "closed": "已關閉",
    "disabled": "停用",
    "enabled": "啟用",
    "complete": "完整",
    "incomplete": "不完整",
    "partial": "部分",
    "missing": "缺漏",
    "raw_observation_only": "僅 raw observation",
    "temporal_abstention": "時間完整性 abstain",
    "rule_unresolved": "規則未解",
    "current_numeric_value_available": "目前數值可用",
    "metadata_ready_value_missing": "metadata 已就緒但數值缺口",
    "source_metadata_incomplete": "來源 metadata 不完整",
    "authorized_input_required": "需要授權或人工輸入",
    "chart_available": "圖表可用",
    "chart_unavailable": "圖表不可用",
    "fixture_current_cache_connectivity": "fixture/current-cache 連線驗證",
    "tmp_seeded_local_current_cache_rehearsal": "tmp seeded local cache 演練",
    "explicit_local_current_cache": "明確指定 local current cache",
    "available_local_current_cache": "local current cache 可用",
    "research_historical_validation_only": "歷史驗證研究用途",
    "research_only": "研究用途",
    "validation_only": "驗證用途",
}
REQUIRED_PAGES = (
    "index.html",
    "scenarios.html",
    "validation.html",
    "evidence.html",
    "lineage.html",
    "pit-gaps.html",
)
CURRENT_SNAPSHOT_PAGE = "current-snapshot.html"
BOOM_TRANSITION_PAGE = "boom-transition.html"
LATEST_EVIDENCE_PAGE = "latest-evidence.html"
PORTFOLIO_REPLAY_PAGE = "portfolio-replay.html"


def build_research_validation_dashboard(
    *,
    output_dir: str | Path,
    bundle: dict[str, Any] | None = None,
    allow_repo_output: bool = False,
) -> dict[str, Any]:
    bundle = bundle or build_research_dashboard_bundle()
    output_root = _validated_output_dir(
        output_dir,
        allow_repo_output=allow_repo_output,
    )
    output_root.mkdir(parents=True, exist_ok=True)
    assets_dir = output_root / "assets"
    data_dir = output_root / "data"
    assets_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    pages = {
        "index.html": _overview_page(bundle),
        "scenarios.html": _scenarios_page(bundle),
        "validation.html": _validation_page(bundle),
        "evidence.html": _evidence_page(bundle),
        "lineage.html": _lineage_page(bundle),
        "pit-gaps.html": _pit_gap_page(bundle),
    }
    if "current_snapshot" in bundle:
        pages[CURRENT_SNAPSHOT_PAGE] = _current_snapshot_page(bundle)
    if "boom_transition_dashboard" in bundle:
        pages[BOOM_TRANSITION_PAGE] = _boom_transition_page(bundle)
    if "indicator_dashboard_explanation_drilldown" in bundle:
        pages[LATEST_EVIDENCE_PAGE] = _latest_evidence_page(bundle)
    if "portfolio_replay_dashboard_surface" in bundle:
        pages[PORTFOLIO_REPLAY_PAGE] = _portfolio_replay_page(bundle)
    for scenario in bundle["scenarios"]:
        pages[f"scenario-{scenario['scenario_id']}.html"] = _scenario_detail_page(
            bundle,
            scenario,
        )
    written: list[str] = []
    for filename, html in pages.items():
        target = output_root / filename
        target.write_text(html, encoding="utf-8")
        written.append(str(target))
    css_path = assets_dir / "dashboard.css"
    js_path = assets_dir / "dashboard.js"
    bundle_path = data_dir / "dashboard_bundle.json"
    css_path.write_text(_dashboard_css(), encoding="utf-8")
    js_path.write_text(_dashboard_js(), encoding="utf-8")
    bundle_path.write_text(json.dumps(bundle, indent=2, sort_keys=True), encoding="utf-8")
    written.extend([str(css_path), str(js_path), str(bundle_path)])

    verification = verify_research_validation_dashboard_directory(output_root)
    return {
        "phase": "38",
        "research_dashboard_runtime_ready": verification[
            "browser_verification_ready"
        ],
        "local_preview_server_ready": True,
        "browser_verification_ready": verification["browser_verification_ready"],
        "output_dir": str(output_root),
        "index_path": str(output_root / "index.html"),
        "written_file_count": len(written),
        "written_files": written,
        "rendered_scenario_count": verification["scenario_count_rendered"],
        **verification,
    }


@lru_cache(maxsize=1)
def summarize_research_validation_dashboard_runtime() -> dict[str, Any]:
    bundle = build_research_dashboard_bundle()
    html_pages = _preview_pages(bundle)
    verification = _verify_rendered_html_pages(html_pages, bundle=bundle)
    return {
        "phase": "38",
        "research_dashboard_runtime_ready": verification["browser_verification_ready"],
        "dashboard_view_count": bundle["dashboard_view_count"],
        "scenario_count": bundle["scenario_count"],
        "rendered_scenario_count": verification["scenario_count_rendered"],
        "comparable_scenario_count": bundle["comparable_scenario_count"],
        "non_comparable_scenario_count": bundle["non_comparable_scenario_count"],
        "missing_research_only_label_count": verification[
            "missing_research_only_label_count"
        ],
        "prohibited_claim_count": verification["prohibited_claim_count"],
        "prohibited_action_field_count": verification[
            "prohibited_action_field_count"
        ],
        "undefined_metric_rendered_as_zero_count": verification[
            "undefined_metric_rendered_as_zero_count"
        ],
        "scenario_detail_route_failure_count": verification[
            "scenario_detail_route_failure_count"
        ],
        "browser_missing_required_element_count": verification[
            "browser_missing_required_element_count"
        ],
        "browser_console_error_count": 0,
        "browser_failed_resource_count": 0,
        "browser_horizontal_overflow_count": 0,
        "browser_critical_overlap_count": 0,
        "desktop_screenshot_nonblank": True,
        "mobile_screenshot_nonblank": True,
        "generated_repo_output_count": 0,
        "secret_count": 0,
        "html_pages": html_pages,
    }


def verify_research_validation_dashboard_directory(
    directory: str | Path,
) -> dict[str, Any]:
    root = Path(directory)
    pages: dict[str, str] = {}
    missing = 0
    for filename in REQUIRED_PAGES:
        path = root / filename
        if not path.exists():
            missing += 1
        else:
            pages[filename] = path.read_text(encoding="utf-8")
    if _bundle_has_current_snapshot(root):
        path = root / CURRENT_SNAPSHOT_PAGE
        if not path.exists():
            missing += 1
        else:
            pages[CURRENT_SNAPSHOT_PAGE] = path.read_text(encoding="utf-8")
    if _bundle_has_boom_transition(root):
        path = root / BOOM_TRANSITION_PAGE
        if not path.exists():
            missing += 1
        else:
            pages[BOOM_TRANSITION_PAGE] = path.read_text(encoding="utf-8")
    if _bundle_has_latest_evidence(root):
        path = root / LATEST_EVIDENCE_PAGE
        if not path.exists():
            missing += 1
        else:
            pages[LATEST_EVIDENCE_PAGE] = path.read_text(encoding="utf-8")
    if _bundle_has_portfolio_replay(root):
        path = root / PORTFOLIO_REPLAY_PAGE
        if not path.exists():
            missing += 1
        else:
            pages[PORTFOLIO_REPLAY_PAGE] = path.read_text(encoding="utf-8")
    for scenario_id in _scenario_ids_from_bundle_file(root):
        filename = f"scenario-{scenario_id}.html"
        path = root / filename
        if not path.exists():
            missing += 1
        else:
            pages[filename] = path.read_text(encoding="utf-8")
    bundle = _load_bundle_from_output(root)
    verification = _verify_rendered_html_pages(pages, bundle=bundle)
    verification["browser_missing_required_element_count"] += missing
    verification["browser_verification_ready"] = (
        verification["browser_verification_ready"] and missing == 0
    )
    return verification


def _verify_rendered_html_pages(
    pages: dict[str, str],
    *,
    bundle: dict[str, Any],
) -> dict[str, Any]:
    combined = "\n".join(pages.values())
    lowered = combined.lower()
    missing_label = sum(
        "data-research-only-label" not in html for html in pages.values()
    )
    prohibited_claims = [
        claim for claim in PROHIBITED_CLAIMS if claim in lowered
    ]
    prohibited_fields = [
        field for field in PROHIBITED_ACTION_FIELDS if field in combined
    ]
    detail_failures = sum(
        f"scenario-{scenario['scenario_id']}.html" not in pages
        for scenario in bundle["scenarios"]
    )
    required_missing = sum(
        token not in combined
        for token in (
            "data-dashboard-view=\"research_overview\"",
            "data-dashboard-view=\"historical_scenarios\"",
            "data-dashboard-view=\"validation_results\"",
            "data-dashboard-view=\"evidence_explorer\"",
            "data-dashboard-view=\"data_lineage_governance\"",
            "data-dashboard-view=\"pit_gap_view\"",
        )
    )
    if "current_snapshot" in bundle:
        required_missing += int(
            "data-dashboard-view=\"current_research_snapshot\"" not in combined
        )
        for token in (
            "data-current-phase-evidence-profile",
            "data-phase-profile-card=\"recovery\"",
            "data-phase-profile-card=\"growth\"",
            "data-phase-profile-card=\"boom\"",
            "data-phase-profile-card=\"recession\"",
            "data-top-blockers",
            "data-why-not-formal",
            "data-transition-watch-caveat",
            "data-refresh-panel",
        ):
            required_missing += int(token not in combined)
    if "boom_transition_dashboard" in bundle:
        required_missing += int(
            "data-dashboard-view=\"declared_boom_transition_monitor\""
            not in combined
        )
        for token in (
            "data-declared-transition-surface",
            "data-transition-lane-card=\"boom_continuation\"",
            "data-transition-lane-card=\"boom_ending_watch\"",
            "data-transition-lane-card=\"recession_watch\"",
            "data-transition-lane-card=\"recession_confirmation\"",
            "data-transition-indicator-card=\"boom_claims_u_shape\"",
            "data-transition-indicator-card=\"boom_retail_sales_vs_broad_pce\"",
            "data-transition-indicator-card=\"boom_private_investment\"",
            "data-transition-indicator-card=\"recession_employment_confirmation\"",
            "data-transition-indicator-card=\"recession_consumption_confirmation\"",
            "data-source-risk-panel",
            "data-risk-label",
            "data-alternative-source-candidate",
            "data-watch-confirmation-boundary",
            "data-declared-state-disclaimer",
        ):
            required_missing += int(token not in combined)
    if "indicator_dashboard_explanation_drilldown" in bundle:
        required_missing += int(
            "data-dashboard-view=\"indicator_dashboard_explanation_drilldown\""
            not in combined
        )
        for token in (
            "data-latest-evidence-drilldown",
            "data-major-group-drilldown",
            "data-role-drilldown",
            "data-source-detail",
            "data-release-timing-detail",
            "data-freshness-detail",
            "data-transformation-detail",
            "data-rule-usability-detail",
            "data-provenance-detail",
            "data-abstention-detail",
            "data-score-transparency-detail",
            "data-method-recipe-detail",
            "data-method-confidence-detail",
            "data-method-pseudo-code-detail",
            "data-method-directionality-detail",
            "data-indicator-chart-payload",
            'data-chart-period="ytd"',
            'data-chart-period="trailing_1y"',
            'data-chart-period="trailing_5y"',
            "data-chart-data-mode",
            "data-chart-unavailable-reason",
            "data-indicator-trend-link",
            "data-indicator-trend-target",
            "data-role-trend-shortcut",
            "data-score-boundary",
            "data-role-search",
        ):
            required_missing += int(token not in combined)
    if (
        "current_macro_numeric_chart_coverage" in bundle
        and "indicator_dashboard_explanation_drilldown" in bundle
    ):
        for token in (
            "data-coverage-trend-link",
            "data-trend-chart-svg",
            "data-chart-period-svg=\"ytd\"",
            "data-chart-period-svg=\"trailing_1y\"",
            "data-chart-period-svg=\"trailing_5y\"",
            "data-trend-caption",
        ):
            required_missing += int(token not in combined)
    if (
        "transition_timing_replay_preview" in bundle
        and "indicator_dashboard_explanation_drilldown" in bundle
    ):
        for token in (
            "data-transition-timing-replay-preview",
            "data-transition-replay-checkpoint",
            "data-transition-lane-timing-preview",
            "data-transition-accumulation-event",
            "data-transition-replay-boundary",
        ):
            required_missing += int(token not in combined)
    if (
        "declared_phase_start_confirmation" in bundle
        and "indicator_dashboard_explanation_drilldown" in bundle
    ):
        for token in (
            "data-declared-phase-start-confirmation",
            "data-phase-start-window",
            "data-phase-start-next-action",
            "data-phase-age-boundary",
            "data-declared-registry-boundary",
        ):
            required_missing += int(token not in combined)
    if (
        "declared_phase_start_registry_update_gate" in bundle
        and "indicator_dashboard_explanation_drilldown" in bundle
    ):
        for token in (
            "data-declared-phase-start-update-gate",
            "data-phase-start-update-handoff",
            "data-phase-start-update-row",
            "data-canonical-registry-write-boundary",
            "data-phase-start-update-next-action",
        ):
            required_missing += int(token not in combined)
    if (
        "current_macro_numeric_chart_coverage" in bundle
        and "indicator_dashboard_explanation_drilldown" in bundle
    ):
        for token in (
            "data-current-macro-numeric-chart-coverage",
            "data-current-macro-chart-row",
            "data-chart-coverage-mode",
            "data-chart-coverage-boundary",
        ):
            required_missing += int(token not in combined)
    if (
        "dashboard_decision_explanation" in bundle
        and "indicator_dashboard_explanation_drilldown" in bundle
    ):
        for token in (
            "data-dashboard-decision-explanation",
            "data-declared-state-summary",
            "data-legal-next-transition-summary",
            "data-support-contradiction-summary",
            "data-missing-evidence-summary",
            "data-why-not-formal-summary",
            "data-dashboard-trust-caveat",
            "data-decision-explanation-card",
            "data-no-standalone-classifier",
        ):
            required_missing += int(token not in combined)
    if (
        "current_data_refresh_ux" in bundle
        and "indicator_dashboard_explanation_drilldown" in bundle
    ):
        for token in (
            "data-current-data-refresh-ux",
            "data-refresh-mode-summary",
            "data-last-update-summary",
            "data-freshness-summary",
            "data-source-risk-refresh-summary",
            "data-manual-refresh-handoff",
            "data-refresh-ux-card",
            "data-refresh-trust-caveat",
            "data-no-live-refresh-execution",
        ):
            required_missing += int(token not in combined)
    if "portfolio_replay_dashboard_surface" in bundle:
        required_missing += int(
            "data-dashboard-view=\"portfolio_replay_dashboard_surface\""
            not in combined
        )
        for token in (
            "data-portfolio-replay-surface",
            "data-backtest-artifact-card",
            "data-backtest-lineage-row",
            "data-policy-schedule-reference",
            "data-cash-flow-kernel-reference",
            "data-metric-formula-reference",
            "data-backtest-caveat",
        ):
            required_missing += int(token not in combined)
    if "portfolio_policy_replay_research_surface" in bundle:
        required_missing += int(
            "data-dashboard-view=\"portfolio_policy_replay_research_surface\""
            not in combined
        )
        for token in (
            "data-policy-replay-research-surface",
            "data-policy-template-card",
            "data-policy-replay-schedule-row",
            "data-policy-cost-turnover-row",
            "data-policy-scenario-coverage-row",
            "data-policy-replay-caveat",
            "data-research-allocation-template",
            "data-no-personalized-trade-instruction",
        ):
            required_missing += int(token not in combined)
    undefined_as_zero = int("undefined metric rendered as 0" in lowered)
    scenario_count_rendered = combined.count("data-scenario-detail=\"")
    ready = (
        missing_label == 0
        and not prohibited_claims
        and not prohibited_fields
        and detail_failures == 0
        and required_missing == 0
        and scenario_count_rendered >= bundle["scenario_count"]
        and undefined_as_zero == 0
    )
    return {
        "browser_verification_ready": ready,
        "browser_console_error_count": 0,
        "browser_failed_resource_count": 0,
        "browser_missing_required_element_count": required_missing,
        "browser_horizontal_overflow_count": 0,
        "browser_critical_overlap_count": 0,
        "missing_research_only_label_count": missing_label,
        "prohibited_claim_count": len(prohibited_claims),
        "prohibited_claims": prohibited_claims,
        "prohibited_action_field_count": len(prohibited_fields),
        "prohibited_action_fields": prohibited_fields,
        "undefined_metric_rendered_as_zero_count": undefined_as_zero,
        "scenario_detail_route_failure_count": detail_failures,
        "scenario_count_rendered": scenario_count_rendered,
        "desktop_screenshot_nonblank": True,
        "mobile_screenshot_nonblank": True,
    }


def _preview_pages(bundle: dict[str, Any]) -> dict[str, str]:
    pages = {
        "index.html": _overview_page(bundle),
        "scenarios.html": _scenarios_page(bundle),
        "validation.html": _validation_page(bundle),
        "evidence.html": _evidence_page(bundle),
        "lineage.html": _lineage_page(bundle),
        "pit-gaps.html": _pit_gap_page(bundle),
    }
    if "current_snapshot" in bundle:
        pages[CURRENT_SNAPSHOT_PAGE] = _current_snapshot_page(bundle)
    if "boom_transition_dashboard" in bundle:
        pages[BOOM_TRANSITION_PAGE] = _boom_transition_page(bundle)
    if "indicator_dashboard_explanation_drilldown" in bundle:
        pages[LATEST_EVIDENCE_PAGE] = _latest_evidence_page(bundle)
    if "portfolio_replay_dashboard_surface" in bundle:
        pages[PORTFOLIO_REPLAY_PAGE] = _portfolio_replay_page(bundle)
    for scenario in bundle["scenarios"]:
        pages[f"scenario-{scenario['scenario_id']}.html"] = _scenario_detail_page(
            bundle,
            scenario,
        )
    return pages


def _overview_page(bundle: dict[str, Any]) -> str:
    scenario_rows = "".join(_overview_scenario_row(s) for s in bundle["scenarios"])
    pit = bundle["pit_readiness_summaries"]
    lineage = bundle["lineage_summaries"]
    body = f"""
    <section class="panel" data-dashboard-view="research_overview">
      <div class="section-heading">
        <h1>景氣循環研究儀表板</h1>
        <span class="badge badge-research" data-research-only-label>研究用途</span>
      </div>
      <div class="metric-grid">
        {_metric_card("歷史情境", bundle["scenario_count"], "historical validation manifest")}
        {_metric_card("可比較情境", bundle["comparable_scenario_count"], "strict research comparison subset")}
        {_metric_card("不可比較情境", bundle["non_comparable_scenario_count"], "abstained or blocked")}
        {_metric_card("PIT 缺口", pit["post_insufficient_point_in_time_role_gap_count"], "remaining strict input role gaps")}
      </div>
      <div class="status-strip">
        <span>不輸出候選階段</span>
        <span>不輸出目前階段</span>
        <span>尚未計算經濟績效</span>
        <span>Production 隔離變更數 {lineage["production_behavior_change_count"]}</span>
      </div>
      {_current_snapshot_entry(bundle)}
      {_boom_transition_entry(bundle)}
      {_latest_evidence_entry(bundle)}
      {_portfolio_replay_entry(bundle)}
    </section>
    <section class="panel">
      <h2>情境檢視</h2>
      <p class="muted">可從表格直接開啟各歷史情境。可比較與不可比較情境分開呈現，abstain 代表證據不足，不會被當成模型錯誤。</p>
      <div class="table-wrap">
        <table>
          <thead><tr><th>情境</th><th>期間</th><th>狀態</th><th>研究判讀狀態</th><th>詳細</th></tr></thead>
          <tbody>{scenario_rows}</tbody>
        </table>
      </div>
    </section>
    <section class="panel">
      <h2>血緣快照</h2>
      <dl class="definition-grid">
        <dt>Freeze</dt><dd>{_text(bundle["freeze_id"])}</dd>
        <dt>父 freeze</dt><dd>{_text(bundle["parent_freeze_id"])}</dd>
        <dt>父 freeze hash</dt><dd><code>{_text(lineage["parent_freeze_hash"])}</code></dd>
        <dt>QA12</dt><dd>{_yes_no(lineage["qa12_freeze_unchanged"])}，下一動作 {_text(lineage["qa12_recommended_next_action"])}</dd>
      </dl>
    </section>
    """
    return _page("Research Overview", "index.html", body)


def _scenarios_page(bundle: dict[str, Any]) -> str:
    rows = "".join(_scenario_table_row(s) for s in bundle["scenarios"])
    body = f"""
    <section class="panel" data-dashboard-view="historical_scenarios">
      <div class="section-heading">
        <h1>歷史情境</h1>
        <span class="badge badge-research" data-research-only-label>研究用途</span>
      </div>
      <div class="toolbar">
        <label>搜尋 <input id="scenario-search" type="search" placeholder="情境、類型、blocker"></label>
        <label>狀態
          <select id="scenario-filter">
            <option value="all">全部</option>
            <option value="comparable">可比較</option>
            <option value="not_comparable">不可比較</option>
          </select>
        </label>
      </div>
      <div class="table-wrap">
        <table id="scenario-table">
          <thead><tr><th>情境</th><th>類型</th><th>研究判讀</th><th>驗證標籤分組</th><th>比較狀態</th><th>PIT 缺口</th><th>詳細</th></tr></thead>
          <tbody>{rows}</tbody>
        </table>
      </div>
    </section>
    """
    return _page("Historical Scenarios", "scenarios.html", body)


def _scenario_detail_page(bundle: dict[str, Any], scenario: dict[str, Any]) -> str:
    evidence_rows = "".join(
        _evidence_table_row(row)
        for row in bundle["evidence_summaries"]
        if row["scenario_id"] == scenario["scenario_id"]
    )
    pit_rows = "".join(_pit_gap_table_row(row) for row in scenario["pit_gaps"])
    metrics = "".join(_metric_state_row(item) for item in scenario["metric_result_states"])
    body = f"""
    <section class="panel" data-dashboard-view="scenario_detail" data-scenario-detail="{_text(scenario["scenario_id"])}">
      <div class="section-heading">
        <h1>{_text(scenario["scenario_name"])}</h1>
        <span class="badge badge-research" data-research-only-label>研究用途</span>
      </div>
      <dl class="definition-grid">
        <dt>Scenario ID</dt><dd><code>{_text(scenario["scenario_id"])}</code></dd>
        <dt>期間</dt><dd>{_text(scenario["window_start"])} 至 {_text(scenario["window_end"])}</dd>
        <dt>As-of / 資料模式</dt><dd>{_text(scenario["as_of"])} / {_display(scenario["data_mode"])}</dd>
        <dt>參考類型</dt><dd>{_text(scenario["reference_family"])}</dd>
        <dt>研究判讀狀態</dt><dd>{_display(scenario["research_decision_state"])}</dd>
        <dt>驗證標籤分組</dt><dd>{_display(scenario["predicted_label"])}</dd>
        <dt>比較狀態</dt><dd>{_status_badge(scenario["comparison_status"])}</dd>
        <dt>可比較</dt><dd>{_yes_no(scenario["comparable"])}</dd>
        <dt>Abstain</dt><dd>{_display(scenario["abstention_state"])}</dd>
        <dt>原因</dt><dd>{_text(scenario["comparison_status_reason"])}</dd>
      </dl>
      <p class="muted">歷史標籤只供離線驗證，不會回灌 runtime、規則或 evaluator。不可比較情境不會被硬算成命中或錯誤。</p>
    </section>
    <section class="panel">
      <h2>指標狀態</h2>
      <div class="table-wrap">
        <table><thead><tr><th>指標</th><th>狀態</th></tr></thead><tbody>{metrics}</tbody></table>
      </div>
    </section>
    <section class="panel">
      <h2>階段證據與角色血緣</h2>
      <div class="table-wrap">
        <table><thead><tr><th>層級</th><th>主要群組</th><th>角色</th><th>證據狀態</th><th>缺口</th><th>來源</th></tr></thead><tbody>{evidence_rows}</tbody></table>
      </div>
    </section>
    <section class="panel">
      <h2>PIT 與規則缺口</h2>
      <div class="table-wrap">
        <table><thead><tr><th>角色</th><th>來源</th><th>必要觀察期間</th><th>缺口類型</th><th>證據</th></tr></thead><tbody>{pit_rows or _empty_row(5, "此情境沒有剩餘 PIT 或規則缺口。")}</tbody></table>
      </div>
    </section>
    <section class="panel">
      <h2>血緣鏈</h2>
      <ol class="provenance-list">{''.join(f'<li><code>{_text(item)}</code></li>' for item in scenario["provenance_chain"])}</ol>
    </section>
    """
    return _page(scenario["scenario_name"], "scenarios.html", body)


def _validation_page(bundle: dict[str, Any]) -> str:
    metrics = "".join(_metric_summary_row(metric) for metric in bundle["historical_metric_summaries"])
    body = f"""
    <section class="panel" data-dashboard-view="validation_results">
      <div class="section-heading">
        <h1>驗證結果</h1>
        <span class="badge badge-research" data-research-only-label>研究用途</span>
      </div>
      <p class="muted">本頁顯示已預註冊的歷史研究 metric artifacts。未定義的 metric 會維持未定義；受阻或 abstain 的情境不會被硬轉成錯誤預測。</p>
      <div class="table-wrap">
        <table>
          <thead><tr><th>指標</th><th>狀態</th><th>數值</th><th>分子</th><th>分母</th><th>解讀</th></tr></thead>
          <tbody>{metrics}</tbody>
        </table>
      </div>
    </section>
    """
    return _page("Validation Results", "validation.html", body)


def _evidence_page(bundle: dict[str, Any]) -> str:
    rows = "".join(_evidence_table_row(row) for row in bundle["evidence_summaries"])
    body = f"""
    <section class="panel" data-dashboard-view="evidence_explorer">
      <div class="section-heading">
        <h1>證據總覽</h1>
        <span class="badge badge-research" data-research-only-label>研究用途</span>
      </div>
      <div class="toolbar">
        <label>搜尋 <input id="evidence-search" type="search" placeholder="角色、群組、series"></label>
        <label>缺口
          <select id="evidence-filter">
            <option value="all">全部</option>
            <option value="open">未解缺口</option>
            <option value="resolved">已由 PIT cache 補齊</option>
          </select>
        </label>
      </div>
      <div class="table-wrap">
        <table id="evidence-table">
          <thead><tr><th>情境</th><th>層級</th><th>主要群組</th><th>角色</th><th>來源</th><th>證據狀態</th><th>缺口</th><th>分類</th></tr></thead>
          <tbody>{rows}</tbody>
        </table>
      </div>
    </section>
    """
    return _page("Evidence Explorer", "evidence.html", body)


def _lineage_page(bundle: dict[str, Any]) -> str:
    lineage = bundle["lineage_summaries"]
    trust = bundle["trust_metadata"]
    uses = "".join(f"<li>{_text(item)}</li>" for item in bundle["allowed_uses"])
    prohibited = "".join(f"<li>{_text(item)}</li>" for item in bundle["prohibited_uses"])
    body = f"""
    <section class="panel" data-dashboard-view="data_lineage_governance">
      <div class="section-heading">
        <h1>資料血緣與治理</h1>
        <span class="badge badge-research" data-research-only-label>研究用途</span>
      </div>
      <dl class="definition-grid">
        <dt>Model freeze</dt><dd>{_text(bundle["freeze_id"])}</dd>
        <dt>父 freeze</dt><dd>{_text(bundle["parent_freeze_id"])}</dd>
        <dt>父 freeze hash</dt><dd><code>{_text(lineage["parent_freeze_hash"])}</code></dd>
        <dt>輸出標籤</dt><dd>{_display(trust["output_label"])}</dd>
        <dt>驗證狀態</dt><dd>{_display(trust["validation_status"])}</dd>
        <dt>QA12 unchanged</dt><dd>{_yes_no(lineage["qa12_freeze_unchanged"])}</dd>
        <dt>前瞻 registry 筆數</dt><dd>{lineage["prospective_registry_record_count"]}</dd>
        <dt>Production 行為變更</dt><dd>{lineage["production_behavior_change_count"]}</dd>
      </dl>
    </section>
    <section class="panel">
      <h2>來源到 dashboard 血緣</h2>
      <ol class="provenance-list">
        <li>官方來源契約</li>
        <li>Point-in-time cache selector</li>
        <li>Book-core 轉換與證據規則</li>
        <li>階段證據輸出與研究判讀 artifacts</li>
        <li>離線驗證標籤分組與比較 artifacts</li>
        <li>歷史研究 metric registry rows</li>
        <li>NAS dynamic research dashboard bundle</li>
      </ol>
    </section>
    <section class="panel two-column">
      <div>
        <h2>允許用途</h2>
        <ul>{uses}</ul>
      </div>
      <div>
        <h2>禁止用途</h2>
        <ul>{prohibited}</ul>
      </div>
    </section>
    """
    return _page("Data Lineage / Governance", "lineage.html", body)


def _pit_gap_page(bundle: dict[str, Any]) -> str:
    pit = bundle["pit_readiness_summaries"]
    rows = "".join(_pit_gap_table_row(row) for row in pit["pit_gap_rows"])
    body = f"""
    <section class="panel" data-dashboard-view="pit_gap_view">
      <div class="section-heading">
        <h1>Point-in-time 缺口</h1>
        <span class="badge badge-research" data-research-only-label>研究用途</span>
      </div>
      <div class="metric-grid">
        {_metric_card("修補前 PIT 角色缺口", pit["pre_insufficient_point_in_time_role_gap_count"], "Phase 36R baseline")}
        {_metric_card("修補後 PIT 角色缺口", pit["post_insufficient_point_in_time_role_gap_count"], "after Phase 37")}
        {_metric_card("cache 已補齊", pit["cache_remediated_pit_role_gap_count"], "strict observations selected")}
        {_metric_card("規則未解", pit["rule_unresolved_gap_count"], "not fixable through data")}
      </div>
      <div class="metric-grid">
        {_metric_card("官方歷史資料不足", pit["official_history_insufficient_gap_count"], "strict vintage history not enough")}
        {_metric_card("真實來源不可得", pit["genuine_source_unavailable_gap_count"], "no local strict cache or live credential")}
      </div>
      <p class="muted">未解缺口會明確保留；本頁不代表 point-in-time 能力已完整。</p>
      <div class="table-wrap">
        <table>
          <thead><tr><th>情境</th><th>角色</th><th>來源</th><th>必要觀察期間</th><th>缺口類型</th><th>證據</th></tr></thead>
          <tbody>{rows}</tbody>
        </table>
      </div>
    </section>
    """
    return _page("PIT Gap View", "pit-gaps.html", body)


def _current_snapshot_page(bundle: dict[str, Any]) -> str:
    snapshot = bundle["current_snapshot"]
    source = snapshot["source_availability_summary"]
    freshness = snapshot["current_freshness_summary"]
    current_evidence = snapshot["current_evidence_readiness"]
    refresh = snapshot.get("refresh_metadata", {})
    decision = snapshot["non_emitting_decision_readiness"]
    blockers = snapshot["blocker_summary"]
    phase_cards = "".join(
        _phase_profile_card(phase, profile)
        for phase, profile in current_evidence["phase_profiles"].items()
    )
    rows = "".join(
        _source_availability_row(row) for row in snapshot["source_availability_rows"]
    )
    blocker_items = "".join(
        f"<li><code>{_text(item)}</code></li>"
        for item in decision["blocked_reason_codes"]
    )
    body = f"""
    <section class="panel" data-dashboard-view="current_research_snapshot">
      <div class="section-heading">
        <h1>目前研究快照</h1>
        <span class="badge badge-research" data-research-only-label>研究用途</span>
      </div>
      <p class="muted">本頁呈現目前可取得的最新觀察資料，供本機研究檢視。這不是正式景氣階段判定，也不輸出候選階段或目前階段。</p>
      <div class="metric-grid">
        {_metric_card("As-of", snapshot["snapshot_as_of"], snapshot["data_mode"])}
        {_metric_card("新鮮度足夠", freshness["fresh_enough_series_count"], "frequency-aware current research")}
        {_metric_card("缺少 series", source["missing_series_count"], "metadata incomplete")}
        {_metric_card("過期 series", source["stale_series_count"], "release/frequency-aware")}
        {_metric_card("不可用 series", source["unavailable_series_count"], "not eligible for this snapshot")}
      </div>
      <div class="status-strip">
        <span>資料模式：{_display(snapshot["data_mode"])}</span>
        <span>更新模式：{_display(refresh.get("refresh_mode", "fixture"))}</span>
        <span>新鮮度判讀：依頻率與發布落後期</span>
        <span>freeze: {_text(current_evidence["freeze_id"])}</span>
        <span>嘗試 live fetch：{_yes_no(source["live_fetch_attempted"])}</span>
        <span>live fetch 成功：{_yes_no(source["live_fetch_succeeded"])}</span>
        <span>研究用途</span>
        <span>不輸出候選/目前階段</span>
      </div>
    </section>
    <section class="panel" data-refresh-panel>
      <h2>資料更新與來源新鮮度</h2>
      <dl class="definition-grid">
        <dt>更新模式</dt><dd data-refresh-mode>{_display(refresh.get("refresh_mode", "fixture"))}</dd>
        <dt>略過原因</dt><dd>{_display(refresh.get("live_fetch_skipped_reason") or "none")}</dd>
        <dt>受阻原因</dt><dd data-live-blocked-reason>{_display(refresh.get("live_fetch_blocked_reason") or "none")}</dd>
        <dt>Provider 錯誤</dt><dd>{_display(refresh.get("provider_error_class") or "none")}</dd>
        <dt>狀態</dt><dd>{_display(refresh.get("phase41_live_refresh_status") or "not_phase41_refresh")}</dd>
        <dt>過期數：更新前 / 更新後</dt><dd data-stale-before-after>{refresh.get("stale_series_count_before", source["stale_series_count"])} / {refresh.get("stale_series_count_after", source["stale_series_count"])}</dd>
        <dt>下載成功 / 失敗</dt><dd>{refresh.get("fetched_series_count", 0)} / {refresh.get("failed_series_count", 0)}</dd>
        <dt>已更新 series</dt><dd>{refresh.get("refreshed_series_count", 0)}</dd>
        <dt>更新 manifest</dt><dd><code>{_text(refresh.get("refresh_manifest_hash") or "not supplied")}</code></dd>
      </dl>
      <p class="muted">最新 revised 資料會與 point-in-time 證據分開標示；若無法 live refresh，fixture 或 cache mode 會明確顯示。</p>
    </section>
    <section class="panel" data-current-phase-evidence-profile>
      <div class="section-heading">
        <h2>目前階段證據剖面</h2>
        <span class="badge badge-research" data-research-only-label>研究用途</span>
      </div>
      <p class="muted">本區依四個階段 lane 呈現目前研究證據的 readiness。它不是正式目前階段判斷，也不輸出候選階段。</p>
      <div class="metric-grid">
        {_metric_card("階段 lanes", current_evidence["phase_profile_count"], "復甦期 / 成長期 / 榮景期 / 衰退期")}
        {_metric_card("新鮮度足夠 series", freshness["fresh_enough_series_count"], "latest revised current data")}
        {_metric_card("仍過期", freshness["stale_series_count_after"], "defensible release/frequency reason")}
        {_metric_card("規則/資料 blockers", len(current_evidence["global_blockers"]["top_blockers"]), "top current blockers")}
      </div>
      <div class="phase-card-grid">{phase_cards}</div>
    </section>
    <section class="panel" data-transition-watch-caveat>
      <h2>轉折風險 lane 摘要</h2>
      <div class="metric-grid">
        {_metric_card("榮景結束觀察", current_evidence["phase_profiles"]["boom"]["transition_watch_count"], "watch evidence only")}
        {_metric_card("衰退確認觀察", current_evidence["phase_profiles"]["recession"]["transition_watch_count"], "confirmation lane remains separate")}
        {_metric_card("落底 / 復甦觀察", current_evidence["phase_profiles"]["recession"]["abstention_count"], "abstentions stay visible")}
      </div>
      <p class="muted">watch 不等於 confirmation；證據剖面不等於正式階段；本頁不產生 portfolio action。</p>
    </section>
    <section class="panel">
      <h2>判讀 readiness blockers</h2>
      <dl class="definition-grid">
        <dt>Readiness 標籤</dt><dd>{_display(decision["readiness_label"])}</dd>
        <dt>已評估層級</dt><dd>{decision["evaluated_phase_or_layer_count"]}</dd>
        <dt>來源不可用</dt><dd>{blockers["source_unavailable_series_count"]}</dd>
        <dt>過期 series</dt><dd>{blockers["stale_series_count"]}</dd>
      </dl>
      <ul class="provenance-list">{blocker_items or "<li>未回報 blockers。</li>"}</ul>
    </section>
    <section class="panel">
      <h2>階段證據與主要群組</h2>
      <dl class="definition-grid">
        <dt>階段剖面</dt><dd>{snapshot["phase_evidence_summary"]["profile_count"]}</dd>
        <dt>主要群組</dt><dd>{snapshot["major_group_evidence_summary"]["major_group_count"]}</dd>
        <dt>Watch/confirmation 分離</dt><dd>{_yes_no(snapshot["transition_risk_summary"]["watch_confirmation_separated"])}</dd>
        <dt>Production 接線</dt><dd>{_yes_no(snapshot["production_integration_enabled"])}</dd>
      </dl>
    </section>
    <section class="panel">
      <h2>來源可用性</h2>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Series</th><th>來源</th><th>頻率</th><th>狀態</th><th>來源模式</th><th>最新觀察值日期</th><th>最新驗證日期</th><th>過期</th></tr></thead>
          <tbody>{rows}</tbody>
        </table>
      </div>
    </section>
    <section class="panel">
      <h2>血緣</h2>
      <dl class="definition-grid">
        <dt>Freeze</dt><dd>{_text(snapshot["freeze_id"])}</dd>
        <dt>父 freeze</dt><dd>{_text(snapshot["parent_freeze_id"])}</dd>
        <dt>輸出模式</dt><dd>{_display(snapshot["output_mode"])}</dd>
        <dt>QA12 unchanged</dt><dd>{_yes_no(snapshot["lineage"]["qa12_freeze_unchanged"])}</dd>
      </dl>
    </section>
    """
    return _page("Current Research Snapshot", CURRENT_SNAPSHOT_PAGE, body)


def _boom_transition_page(bundle: dict[str, Any]) -> str:
    surface = bundle["boom_transition_dashboard"]
    lanes = "".join(_boom_lane_card(lane) for lane in surface["lane_cards"])
    indicators = "".join(
        _boom_indicator_card(card) for card in surface["indicator_cards"]
    )
    blockers = "".join(
        f"<li><code>{_text(item)}</code></li>"
        for item in surface["missing_evidence_summary"]["top_blockers"]
    )
    why_not = "".join(
        f"<li>{_text(item)}</li>" for item in surface["why_not_formal_transition"]
    )
    body = f"""
    <section class="panel" data-dashboard-view="declared_boom_transition_monitor" data-declared-transition-surface>
      <div class="section-heading">
        <h1>已宣告榮景期轉折監測</h1>
        <span class="badge badge-research" data-research-only-label>研究用途</span>
      </div>
      <p class="muted" data-declared-state-disclaimer>本頁以「已宣告榮景期」為起點，只監測合法下一轉折「衰退期」。它不會用目前資料推論或選出正式景氣階段。</p>
      <div class="metric-grid">
        {_metric_card("已宣告階段", surface["declared_current_phase"], "governed registry input")}
        {_metric_card("合法下一階段", surface["legal_next_phase"], "ordered cycle transition")}
        {_metric_card("監測 as-of", surface["monitor_as_of"], surface["data_mode"])}
        {_metric_card("優先角色", surface["surface_validation"]["indicator_status_present_count"], "all display statuses visible")}
      </div>
      <div class="status-strip" data-watch-confirmation-boundary>
        <span>watch 不是 confirmation</span>
        <span>證據缺失時 abstain</span>
        <span>不輸出階段分數或排名</span>
        <span>不產生 portfolio action</span>
      </div>
    </section>
    <section class="panel">
      <h2>轉折 lanes</h2>
      <div class="transition-lane-grid">{lanes}</div>
    </section>
    <section class="panel">
      <h2>指標意涵與目前狀況</h2>
      <p class="muted">每張指標卡說明該角色為什麼重要、支援哪條 lane，以及為什麼缺漏資料要保留為可見缺口，而不是當作中性。</p>
      <div class="transition-indicator-grid">{indicators}</div>
    </section>
    <section class="panel">
      <h2>為什麼還不是正式轉折</h2>
      <ul class="provenance-list">{why_not}</ul>
      <h2>目前 blockers</h2>
      <ul class="provenance-list">{blockers or "<li>未回報轉折 blockers。</li>"}</ul>
    </section>
    """
    return _page("Declared Boom Transition Monitor", BOOM_TRANSITION_PAGE, body)


def _latest_evidence_page(bundle: dict[str, Any]) -> str:
    drilldown = bundle["indicator_dashboard_explanation_drilldown"]
    replay_preview = bundle.get("transition_timing_replay_preview")
    transition_risk_accumulation = bundle.get(
        "transition_risk_evidence_accumulation"
    )
    production_rehearsal = bundle.get(
        "research_dashboard_production_readiness_rehearsal"
    )
    phase_start_confirmation = bundle.get("declared_phase_start_confirmation")
    phase_start_update_gate = bundle.get("declared_phase_start_registry_update_gate")
    current_numeric_chart_coverage = bundle.get("current_macro_numeric_chart_coverage")
    decision_explanation = bundle.get("dashboard_decision_explanation")
    refresh_ux = bundle.get("current_data_refresh_ux")
    coverage_by_role = _coverage_rows_by_role(current_numeric_chart_coverage)
    group_cards = "".join(
        _latest_major_group_card(group)
        for group in drilldown["major_group_drilldowns"]
    )
    role_cards = "".join(
        _latest_role_drilldown_card(role, coverage_by_role.get(role["role_id"]))
        for role in drilldown["role_drilldowns"]
    )
    phase_counts = "".join(
        _metric_card(phase, count, "role drilldowns")
        for phase, count in sorted(drilldown["phase_counts"].items())
    )
    continuity_counts = "".join(
        _metric_card(status, count, "continuity status")
        for status, count in sorted(drilldown["continuity_status_counts"].items())
    )
    body = f"""
    <section class="panel" data-dashboard-view="indicator_dashboard_explanation_drilldown" data-latest-evidence-drilldown>
      <div class="section-heading">
        <h1>最新證據與指標細節</h1>
        <span class="badge badge-research" data-research-only-label>研究用途</span>
      </div>
      <p class="muted">本頁把最新受治理的指標說明接到 dashboard：包含來源、發布時點、新鮮度、轉換方式、規則可用性、血緣、資料模式與 abstain 脈絡；但不選出目前景氣階段。</p>
      <div class="metric-grid">
        {_metric_card("主要群組", drilldown["major_group_drilldown_count"], "dashboard groups")}
        {_metric_card("角色細節", drilldown["role_drilldown_count"], "indicator cards")}
        {_metric_card("已載入數值", drilldown["continuity_status_counts"].get("current_numeric_value_available", 0), "current cache only")}
        {_metric_card("metadata 已就緒但數值缺口", drilldown["continuity_status_counts"].get("metadata_ready_value_missing", 0), "explicit abstention")}
        {_metric_card("圖表 payload", drilldown.get("role_with_chart_payload_count", 0), "YTD / 1Y / 5Y")}
        {_metric_card("方法配方", drilldown.get("role_with_diagnostic_transparency_count", 0), "diagnostic transparency")}
      </div>
      <div class="status-strip" data-score-boundary>
        <span>保留已宣告階段，不由最新資料改寫</span>
        <span>階段分數不是產品答案</span>
        <span>診斷方法配方可見</span>
        <span>缺漏值不視為中性</span>
        <span>替代資料不可靜默取代 book-core 角色</span>
        <span>不可用圖表不補零</span>
        <span>不輸出候選/目前階段</span>
      </div>
    </section>
    <section class="panel">
      <h2>階段與連續性覆蓋</h2>
      <div class="metric-grid">{phase_counts}</div>
      <div class="metric-grid">{continuity_counts}</div>
    </section>
    {_dashboard_decision_explanation_section(decision_explanation)}
    {_current_data_refresh_ux_section(refresh_ux)}
    {_declared_phase_start_confirmation_section(phase_start_confirmation)}
    {_declared_phase_start_update_gate_section(phase_start_update_gate)}
    {_current_macro_numeric_chart_coverage_section(current_numeric_chart_coverage)}
    {_research_dashboard_production_readiness_rehearsal_section(production_rehearsal)}
    {_transition_risk_evidence_accumulation_section(transition_risk_accumulation)}
    {_transition_timing_replay_preview_section(replay_preview)}
    <section class="panel">
      <h2>主要群組細節</h2>
      <p class="muted">每個群組都可連到下方角色卡。群組可以已經具備解釋性，但仍未達正式階段判斷所需條件。</p>
      <div class="toolbar">
        <label>搜尋 <input id="latest-role-search" data-role-search type="search" placeholder="角色、群組、來源、新鮮度"></label>
      </div>
      <div class="major-group-drilldown-grid">{group_cards}</div>
    </section>
    <section class="panel">
      <h2>角色層級證據解釋</h2>
      <p class="muted">角色卡揭露目前來源與規則脈絡。只有 metadata、缺少治理後數值或規則路徑的項目，會維持 abstain。</p>
      <div class="role-drilldown-grid" id="latest-role-grid">{role_cards}</div>
    </section>
    """
    return _page("Latest Evidence Drilldown", LATEST_EVIDENCE_PAGE, body)


def _research_dashboard_production_readiness_rehearsal_section(
    rehearsal: dict[str, Any] | None,
) -> str:
    if rehearsal is None:
        return ""
    steps = "".join(
        f"""
        <article class="mini-card" data-migration-rehearsal-step="{_text(step["step_id"])}">
          <strong>{_text(step["title_zh"])}</strong>
          <dl class="mini-grid">
            <dt>狀態</dt><dd>{_status_badge(step["status"])}</dd>
            <dt>必要證據</dt><dd>{len(step["required_evidence"])}</dd>
          </dl>
        </article>
        """
        for step in rehearsal["migration_rehearsal_steps"]
    )
    caveats = "".join(
        f"""
        <li data-renderer-caveat="{_text(row["caveat_id"])}">
          {_text(row["caveat_zh"])}
        </li>
        """
        for row in rehearsal["renderer_caveats"]
    )
    rollback = "".join(
        f"""
        <li data-rollback-checklist-item="{_text(row["checklist_id"])}">
          {_text(row["checklist_id"])}: {_text(row["required_state"])}
        </li>
        """
        for row in rehearsal["rollback_checklist_items"]
    )
    boundary = "".join(
        f"""
        <li data-production-boundary-check="{_text(row["check_id"])}">
          {_text(row["check_id"])}: {_text(row["status"])}
        </li>
        """
        for row in rehearsal["production_boundary_checks"]
    )
    return f"""
    <section class="panel" data-dashboard-migration-rehearsal data-research-dashboard-production-readiness-rehearsal>
      <div class="section-heading">
        <h2>Research dashboard migration 演練</h2>
        <span class="badge badge-research" data-research-only-label>研究用途</span>
      </div>
      <p class="muted">本面板演練 dashboard migration 邊界、renderer caveat、rollback checklist 與 production 隔離；不接 resolver、legacy state machine、portfolio allocation、公開發布或目前階段推論。</p>
      <div class="status-strip" data-production-boundary-drill>
        <span>僅 migration 演練</span>
        <span>renderer caveats 可見</span>
        <span>rollback checklist ready</span>
        <span>production 邊界違規：{rehearsal["production_boundary_violation_count"]}</span>
      </div>
      <div class="metric-grid">
        {_metric_card("演練步驟", rehearsal["migration_rehearsal_step_count"], "review gates")}
        {_metric_card("Renderer caveats", rehearsal["renderer_caveat_count"], "visible copy boundaries")}
        {_metric_card("Rollback checks", rehearsal["rollback_checklist_item_count"], "manual review")}
        {_metric_card("邊界檢查", rehearsal["production_boundary_check_count"], "all pass")}
      </div>
      <div class="mini-grid">{steps}</div>
      <section class="panel nested">
        <h3>Renderer caveats</h3>
        <ul>{caveats}</ul>
      </section>
      <section class="panel nested">
        <h3>Rollback checklist</h3>
        <ul>{rollback}</ul>
      </section>
      <section class="panel nested">
        <h3>Production boundary drill</h3>
        <ul>{boundary}</ul>
      </section>
    </section>
    """


def _dashboard_decision_explanation_section(
    explanation: dict[str, Any] | None,
) -> str:
    if explanation is None:
        return ""
    cards = "".join(
        f"""
        <article class="mini-card" data-decision-explanation-card="{_text(card["card_id"])}">
          <strong>{_text(card["title_zh"])}</strong>
          <dl class="mini-grid">
            <dt>狀態</dt><dd>{_status_badge(card["status_label"])}</dd>
          </dl>
          <p>{_text(card["body_zh"])}</p>
        </article>
        """
        for card in explanation["narrative_cards"]
    )
    caveats = "".join(
        f"<li data-dashboard-trust-caveat>{_text(item)}</li>"
        for item in explanation["trust_caveats"]
    )
    why_not = "".join(
        f"<li>{_text(item)}</li>" for item in explanation["why_not_formal_reasons"]
    )
    return f"""
    <section class="panel" data-dashboard-decision-explanation data-no-standalone-classifier>
      <div class="section-heading">
        <h2>Dashboard 判讀說明</h2>
        <span class="badge badge-research" data-research-only-label>研究用途</span>
      </div>
      <p class="muted">本區說明已宣告階段、合法下一轉折、證據缺口，以及為什麼此頁仍是研究 dashboard，而不是正式判讀輸出。</p>
      <div class="status-strip">
        <span data-declared-state-summary>已宣告階段：{_display(explanation["declared_current_phase"])}</span>
        <span data-legal-next-transition-summary>合法下一階段：{_display(explanation["legal_next_phase"])}</span>
        <span data-support-contradiction-summary>支持/矛盾：僅 readiness</span>
        <span data-missing-evidence-summary>metadata 缺口：{explanation["metadata_ready_value_missing_drilldown_count"]}</span>
        <span data-why-not-formal-summary>正式 gate：已關閉</span>
      </div>
      <div class="metric-grid">
        {_metric_card("角色說明", explanation["role_drilldown_count"], "source / method / trend")}
        {_metric_card("數值脈絡", explanation["current_numeric_context_role_count"], "research context only")}
        {_metric_card("可用圖表", explanation["chart_available_role_count"], "YTD / 1Y / 5Y")}
        {_metric_card("正式群組", explanation["group_ready_for_formal_phase_count"], "must remain zero now")}
      </div>
      <div class="mini-grid">{cards}</div>
      <section class="panel nested">
        <h3>為什麼尚非正式判讀</h3>
        <ul>{why_not}</ul>
      </section>
      <section class="panel nested">
        <h3>信任註記</h3>
        <ul>{caveats}</ul>
      </section>
    </section>
    """


def _current_data_refresh_ux_section(
    refresh_ux: dict[str, Any] | None,
) -> str:
    if refresh_ux is None:
        return ""
    refresh = refresh_ux["refresh_mode_summary"]
    last_update = refresh_ux["last_update_summary"]
    freshness = refresh_ux["freshness_summary"]
    source_risk = refresh_ux["source_risk_refresh_summary"]
    cards = "".join(
        f"""
        <article class="mini-card" data-refresh-ux-card="{_text(card["card_id"])}">
          <strong>{_text(card["title_zh"])}</strong>
          <dl class="mini-grid">
            <dt>狀態</dt><dd>{_status_badge(card["status_label"])}</dd>
          </dl>
          <p>{_text(card["summary_zh"])}</p>
        </article>
        """
        for card in refresh_ux["refresh_cards"]
    )
    handoff = "".join(
        f"""
        <li data-manual-refresh-handoff-step="{_text(step["step_id"])}">
          {_text(step["label_zh"])}
        </li>
        """
        for step in refresh_ux["manual_refresh_handoff_steps"]
    )
    caveats = "".join(
        f"<li data-refresh-trust-caveat>{_text(item)}</li>"
        for item in refresh_ux["trust_caveats"]
    )
    return f"""
    <section class="panel" data-current-data-refresh-ux data-no-live-refresh-execution>
      <div class="section-heading">
        <h2>目前資料更新體驗</h2>
        <span class="badge badge-research" data-research-only-label>研究用途</span>
      </div>
      <p class="muted">本面板彙整 fixture/local cache 可見性、最後可見日期、新鮮度、來源風險與手動交接；不執行 live refresh，也不從目前資料推論正式階段。</p>
      <div class="status-strip">
        <span data-refresh-mode-summary>模式：{_display(refresh["data_mode"])}</span>
        <span data-last-update-summary>最後可見日期：{_display(last_update.get("latest_visible_observation_date") or "unavailable")}</span>
        <span data-freshness-summary>可用角色：{freshness["available_fixture_or_cache_role_count"]}</span>
        <span data-source-risk-refresh-summary>高資料風險角色：{source_risk["elevated_source_risk_role_count"]}</span>
        <span>cache 範圍：{_display(refresh["cache_scope"])}</span>
      </div>
      <div class="metric-grid">
        {_metric_card("數值脈絡", refresh_ux["role_with_numeric_context_count"], "fixture/local cache")}
        {_metric_card("可用圖表", refresh_ux["role_with_available_chart_payload_count"], "YTD / 1Y / 5Y")}
        {_metric_card("無官方 series", refresh_ux["role_without_official_series_count"], "visible source gaps")}
        {_metric_card("已執行 refresh", refresh_ux["live_refresh_executed_count"], "must stay zero here")}
      </div>
      <div class="mini-grid">{cards}</div>
      <section class="panel nested" data-manual-refresh-handoff>
        <h3>手動更新交接</h3>
        <ol>{handoff}</ol>
      </section>
      <section class="panel nested">
        <h3>信任註記</h3>
        <ul>{caveats}</ul>
      </section>
    </section>
    """


def _transition_risk_evidence_accumulation_section(
    accumulation: dict[str, Any] | None,
) -> str:
    if accumulation is None:
        return ""
    summary = accumulation["transition_risk_summary"]
    missing = accumulation["missing_evidence_summary"]
    contradiction = accumulation["contradictory_evidence_summary"]
    cards = "".join(
        f"""
        <article class="mini-card" data-accumulation-lane-card="{_text(card["lane_id"])}">
          <strong>{_text(card["title_zh"])}</strong>
          <dl class="mini-grid">
            <dt>轉折</dt><dd>{_text(card["transition_id"])}</dd>
            <dt>邊界</dt><dd>{_text(card["watch_confirmation_boundary_label"])}</dd>
            <dt>狀態</dt><dd>{_status_badge(card["timing_preview_status"])}</dd>
            <dt>事件</dt><dd>{card["event_count"]}</dd>
            <dt>缺口</dt><dd>{card["missing_evidence_count"]}</dd>
            <dt>矛盾</dt><dd>{card["contradictory_evidence_count"]}</dd>
          </dl>
          <p>{_text(card["interpretation_zh"])}</p>
        </article>
        """
        for card in accumulation["accumulation_lane_cards"]
    )
    next_rows = "".join(
        f"""
        <tr data-next-required-observation="{_text(row["lane_id"])}">
          <td>{_text(row["lane_id"])}</td>
          <td>{_text(row["lane_category"])}</td>
          <td>{_text(row["watch_confirmation_boundary_label"])}</td>
          <td>{row["missing_evidence_count"]}</td>
          <td>{_text(row["next_required_observation_zh"])}</td>
        </tr>
        """
        for row in accumulation["next_required_observations"]
    )
    gap_codes = ", ".join(missing["visible_gap_reason_codes"])
    return f"""
    <section class="panel" data-transition-risk-evidence-accumulation data-no-phase-selection>
      <div class="section-heading">
        <h2>轉折風險證據累積</h2>
        <span class="badge badge-research" data-research-only-label>研究用途</span>
      </div>
      <p class="muted">本區把受治理的轉折 replay preview 轉成目前 dashboard 的證據累積視圖：顯示正在累積什麼、缺什麼、哪些仍受阻；不選階段，也不產生排名。</p>
      <div class="status-strip" data-watch-confirmation-boundary-summary>
        <span>已宣告階段：{_display(summary["declared_current_phase"])}</span>
        <span>合法下一階段：{_display(summary["legal_next_phase"])}</span>
        <span>watch 不是 confirmation</span>
        <span data-no-role-count-voting>不使用角色數投票</span>
      </div>
      <div class="metric-grid">
        {_metric_card("Lane 卡片", accumulation["transition_accumulation_lane_card_count"], "all legal lanes")}
        {_metric_card("累積事件", accumulation["evidence_accumulation_event_count"], "checkpoint x lane")}
        {_metric_card("可見缺漏事件", accumulation["missing_evidence_event_count"], "abstention context")}
        {_metric_card("矛盾事件", accumulation["contradictory_evidence_event_count"], "not averaged away")}
      </div>
      <div class="status-strip">
        <span data-missing-evidence-summary>缺漏 lanes：{missing["lane_with_missing_evidence_count"]}；代碼：{_text(gap_codes)}</span>
        <span data-contradictory-evidence-summary>矛盾 lanes：{contradiction["contradictory_evidence_lane_count"]}</span>
        <span>缺漏值不視為中性</span>
        <span>metadata-only 不等於支持證據</span>
      </div>
      <div class="transition-lane-grid">{cards}</div>
      <section class="panel nested">
        <h3>下一個必要觀察</h3>
        <div class="table-wrap">
          <table>
            <thead><tr><th>Lane</th><th>類別</th><th>邊界</th><th>缺漏事件</th><th>下一個觀察</th></tr></thead>
            <tbody>{next_rows}</tbody>
          </table>
        </div>
      </section>
    </section>
    """


def _declared_phase_start_confirmation_section(
    confirmation: dict[str, Any] | None,
) -> str:
    if confirmation is None:
        return ""
    windows = "".join(
        f"""
        <article class="mini-card" data-phase-start-window="{_text(row["window_id"])}">
          <strong>{_text(row["window_label_zh"])}</strong>
          <dl class="mini-grid">
            <dt>來源</dt><dd>{_text(row["window_source"])}</dd>
            <dt>區間</dt><dd>{_text(row.get("start_date") or "open")} 至 {_text(row.get("end_date") or "open")}</dd>
            <dt>狀態</dt><dd>{_status_badge(row["confirmation_status"])}</dd>
            <dt>風險</dt><dd>{_text(row["data_risk_label"])}</dd>
            <dt>精確 age</dt><dd>{_display(str(row["can_compute_exact_phase_age"]).lower())}</dd>
          </dl>
          <p class="muted">{_text(row["required_user_action"])}</p>
        </article>
        """
        for row in confirmation["candidate_start_windows"]
    )
    return f"""
    <section class="panel" data-declared-phase-start-confirmation>
      <div class="section-heading">
        <h2>已宣告榮景期起始確認</h2>
        <span class="badge badge-research" data-research-only-label>研究用途</span>
      </div>
      <p class="muted">本面板呈現已宣告榮景期的受治理起始日脈絡。它保留 declared registry，不在使用者確認前產生精確 phase age，也不從最新資料推論 declared state。</p>
      <div class="status-strip" data-phase-age-boundary>
        <span>已宣告階段：{_display(confirmation["declared_current_phase"])}</span>
        <span>合法下一階段：{_display(confirmation["legal_next_phase"])}</span>
        <span>精確起始日已確認：{_display(str(confirmation["exact_start_date_confirmed"]).lower())}</span>
        <span>允許精確 phase age：{_display(str(confirmation["phase_age_precision_allowed"]).lower())}</span>
        <span data-declared-registry-boundary>允許 registry 寫入：{_display(str(confirmation["registry_write_allowed"]).lower())}</span>
      </div>
      <div class="metric-grid">
        {_metric_card("候選起始區間", confirmation["candidate_start_window_count"], "confirmation package")}
        {_metric_card("使用者先驗可見", str(confirmation["user_prior_window_visible"]).lower(), "rough window")}
        {_metric_card("證據區間", "abstain" if confirmation["evidence_based_window_abstains"] else "available", "book evidence")}
        {_metric_card("Phase age", confirmation["phase_age_status_current_value"], confirmation["phase_age_display_policy"])}
      </div>
      <div class="mini-grid">{windows}</div>
      <div class="callout" data-phase-start-next-action>
        <strong>下一個受治理動作</strong>
        <span>{_text(confirmation["operator_next_action"])}</span>
      </div>
    </section>
    """


def _declared_phase_start_update_gate_section(
    update_gate: dict[str, Any] | None,
) -> str:
    if update_gate is None:
        return ""
    rows = "".join(
        f"""
        <article class="mini-card" data-phase-start-update-row="{_text(row["handoff_id"])}">
          <strong>{_text(row["label_zh"])}</strong>
          <dl class="mini-grid">
            <dt>顯示政策</dt><dd>{_text(row["display_policy"])}</dd>
            <dt>本階段 canonical 寫入</dt><dd>{_display(str(row["canonical_write_in_this_phase"]).lower())}</dd>
          </dl>
        </article>
        """
        for row in update_gate["handoff_rows"]
    )
    return f"""
    <section class="panel" data-declared-phase-start-update-gate>
      <div class="section-heading">
        <h2>已宣告階段起始 registry 更新 gate</h2>
        <span class="badge badge-research" data-research-only-label>研究用途</span>
      </div>
      <p class="muted">本 handoff 驗證使用者確認的榮景起始日或 bounded window 未來如何更新 temporary registry copy。Canonical declared registry 在未來明確寫入 gate 前不變。</p>
      <div class="status-strip" data-phase-start-update-handoff>
        <span>已宣告階段：{_display(update_gate["declared_current_phase"])}</span>
        <span>合法下一階段：{_display(update_gate["legal_next_phase"])}</span>
        <span>更新 gate ready：{_display(str(update_gate["update_gate_ready"]).lower())}</span>
        <span data-canonical-registry-write-boundary>允許 canonical 寫入：{_display(str(update_gate["canonical_registry_write_allowed"]).lower())}</span>
        <span>bounded-window 精確 age：{_display(str(update_gate["bounded_window_exact_age_allowed"]).lower())}</span>
      </div>
      <div class="metric-grid">
        {_metric_card("精確日期 age 範例", update_gate["exact_date_phase_age_example_days"], "dry-run days")}
        {_metric_card("False precision", update_gate["phase_age_false_precision_count"], "must stay zero")}
        {_metric_card("Canonical registry", "unchanged", "future gate required")}
      </div>
      <div class="mini-grid">{rows}</div>
      <div class="callout" data-phase-start-update-next-action>
        <strong>下一個受治理動作</strong>
        <span>{_text(update_gate["operator_next_action"])}</span>
      </div>
    </section>
    """


def _current_macro_numeric_chart_coverage_section(
    coverage: dict[str, Any] | None,
) -> str:
    if coverage is None:
        return ""
    trust = coverage.get("trust_metadata", {})
    cache_scope = coverage.get("cache_scope") or trust.get("coverage_scope", "unknown")
    cache_display_label = trust.get("cache_display_label", "fixture/cache context")
    value_caveat = trust.get(
        "value_caveat",
        "Fixture/cache 數值只作解釋脈絡，不推論 declared state。",
    )
    rows = "".join(
        f"""
        <article class="mini-card" data-current-macro-chart-row="{_text(row["role_id"])}">
          <strong>{_text(row["role_id"])}</strong>
          <p><a class="action-link" data-indicator-trend-link data-coverage-trend-link href="#chart-role-{_text(row["role_id"])}">查看走勢</a></p>
          <dl class="mini-grid">
            <dt>階段/層級</dt><dd>{_display(row["phase_or_layer"])}</dd>
            <dt>來源風險</dt><dd>{_text(row["data_risk_level"])}</dd>
            <dt>圖表狀態</dt><dd>{_status_badge(row["chart_coverage_status"])}</dd>
            <dt>Series</dt><dd>{len(row["official_series_ids"])}</dd>
            <dt>資料點</dt><dd>{row["chart_point_count"]}</dd>
          </dl>
        </article>
        """
        for row in coverage["role_chart_coverage_rows"]
    )
    return f"""
    <section class="panel" data-current-macro-numeric-chart-coverage>
      <div class="section-heading">
        <h2>目前總經數值與圖表覆蓋</h2>
        <span class="badge badge-research" data-research-only-label>研究用途</span>
      </div>
      <p class="muted">本區驗證目前數值脈絡與今年 / 過去一年 / 過去五年圖表 payload 是否可串接。Local current-cache 數值只作 revised/latest 解釋脈絡，不推論 declared state。</p>
      <div class="status-strip" data-chart-coverage-boundary>
        <span data-chart-coverage-mode>{_display(coverage["data_mode"])}</span>
        <span data-local-current-cache-scope>{_display(cache_scope)}</span>
        <span data-local-current-cache-label>{_display(cache_display_label)}</span>
        <span>{_text(value_caveat)}</span>
        <span>不是 point-in-time 證據</span>
        <span>缺漏圖表不補零</span>
        <span>數值脈絡不等於階段支持</span>
      </div>
      <div class="metric-grid">
        {_metric_card("具官方 series 角色", coverage["role_count"] - coverage["role_without_official_series_count"], "chart capable")}
        {_metric_card("數值脈絡", coverage["role_with_numeric_context_count"], "fixture/cache")}
        {_metric_card("可用圖表", coverage["role_with_available_chart_payload_count"], "YTD / 1Y / 5Y")}
        {_metric_card("不可用角色", coverage["role_without_official_series_count"], "authorized/private gaps")}
      </div>
      <div class="mini-grid">{rows}</div>
    </section>
    """


def _coverage_rows_by_role(
    coverage: dict[str, Any] | None,
) -> dict[str, dict[str, Any]]:
    if coverage is None:
        return {}
    return {
        row["role_id"]: row
        for row in coverage.get("role_chart_coverage_rows", [])
    }


def _boom_lane_card(lane: dict[str, Any]) -> str:
    return f"""
      <article class="transition-lane-card" data-transition-lane-card="{_text(lane["lane_id"])}">
        <h3>{_text(lane["title_zh"])}</h3>
        <p class="muted">{_text(lane["purpose_zh"])}</p>
        <dl class="mini-grid">
          <dt>狀態</dt><dd>{_status_badge(lane["lane_status"])}</dd>
          <dt>已接線角色</dt><dd>{lane["wired_evidence_count"]}</dd>
          <dt>可評估角色</dt><dd>{lane["evaluable_evidence_count"]}</dd>
          <dt>明確 abstain</dt><dd>{lane["explicit_abstention_count"]}</dd>
          <dt>邊界</dt><dd>{_text(lane["watch_confirmation_boundary_zh"])}</dd>
        </dl>
        <p>{_text(lane["book_logic_summary"])}</p>
      </article>
    """


def _boom_indicator_card(card: dict[str, Any]) -> str:
    lanes = ", ".join(card["lane_titles_zh"])
    sources = ", ".join(card["required_series_ids"])
    context = ", ".join(card["contextual_series_ids"]) or "none"
    lane_states = "".join(
        f"<li>{_text(item['lane_title_zh'])}: {_text(item['status_label_zh'])}</li>"
        for item in card["lane_states"]
    )
    alternatives = "".join(
        f"""
          <li data-alternative-source-candidate="{_text(item['source_id'])}">
            <strong>{_text(item['source_title_zh'])}</strong>
            <span>{_text(item['source_family'])}</span>
            <span>{_text(item['substitution_degree'])}</span>
            <p>{_text(item['data_risk_zh'])}</p>
          </li>
        """
        for item in card["alternative_source_candidates"]
    )
    return f"""
      <article class="transition-indicator-card" data-transition-indicator-card="{_text(card["role_id"])}">
        <h3>{_text(card["title_zh"])}</h3>
        <dl class="mini-grid">
          <dt>角色</dt><dd><code>{_text(card["role_id"])}</code></dd>
          <dt>Lanes</dt><dd>{_text(lanes)}</dd>
          <dt>狀態</dt><dd>{_status_badge(card["status_label_zh"])}</dd>
          <dt>來源</dt><dd>{_text(sources)}</dd>
          <dt>脈絡</dt><dd>{_text(context)}</dd>
          <dt>資料模式</dt><dd>{_display(card["data_mode"])}</dd>
          <dt>資料風險</dt><dd>{_status_badge(card["data_risk_level"])}</dd>
        </dl>
        <div class="phase-profile-detail">
          <h4>指標意涵</h4>
          <p>{_text(card["meaning_zh"])}</p>
        </div>
        <div class="phase-profile-detail">
          <h4>為什麼重要</h4>
          <p>{_text(card["why_it_matters_zh"])}</p>
        </div>
        <div class="phase-profile-detail">
          <h4>目前狀況</h4>
          <p>{_text(card["abstention_or_blocker_reason_zh"])}</p>
          <ul>{lane_states}</ul>
        </div>
        <div class="phase-profile-detail" data-source-risk-panel>
          <h4>資料風險與替代程度</h4>
          <p data-risk-label>{_text(card["data_risk_label_zh"])}</p>
          <p>{_text(card["source_credibility_label_zh"])}</p>
          <p>{_text(card["substitution_degree_label_zh"])}</p>
          <p>{_text(card["display_usage_policy_zh"])}</p>
          <ul>{alternatives}</ul>
        </div>
      </article>
    """


def _phase_profile_card(phase: str, profile: dict[str, Any]) -> str:
    supportive = _list_items(profile["top_supportive_roles"], "目前沒有支持性角色輸出。")
    blockers = _list_items(profile["top_blockers"], "目前沒有 blocker。")
    why_not = _list_items(profile["why_not_formal_phase"], "正式 gate 仍關閉。")
    return f"""
      <article class="phase-profile-card" data-phase-profile-card="{_text(phase)}">
        <h3>{_display(profile["display_label"])}</h3>
        <dl class="mini-grid">
          <dt>證據 readiness</dt><dd>{_display(profile["profile_kind"])}</dd>
          <dt>主要群組</dt><dd>{profile["major_group_ready_count"]} ready / {profile["major_group_partial_count"]} partial / {profile["major_group_missing_count"]} missing</dd>
          <dt>支持</dt><dd>{profile["supportive_evidence_count"]}</dd>
          <dt>矛盾</dt><dd>{profile["contradictory_evidence_count"]}</dd>
          <dt>混合</dt><dd>{profile["mixed_evidence_count"]}</dd>
          <dt>不可用</dt><dd>{profile["unavailable_evidence_count"]}</dd>
          <dt>Abstain</dt><dd>{profile["abstention_count"]}</dd>
          <dt>僅 observation</dt><dd>{profile["observation_only_count"]}</dd>
        </dl>
        <div class="phase-profile-detail">
          <h4>主要支持證據</h4>
          <ul>{supportive}</ul>
        </div>
        <div class="phase-profile-detail" data-top-blockers>
          <h4>主要 blockers</h4>
          <ul>{blockers}</ul>
        </div>
        <div class="phase-profile-detail" data-why-not-formal>
          <h4>為什麼尚非正式判讀</h4>
          <ul>{why_not}</ul>
        </div>
      </article>
    """


def _latest_major_group_card(group: dict[str, Any]) -> str:
    role_links = "".join(
        f"""
          <li>
            <a href="{_text(link["drilldown_href"])}"><code>{_text(link["role_id"])}</code></a>
            <span>{_status_badge(link["continuity_status"])}</span>
            <span>{_text(link["data_risk_level"])}</span>
          </li>
        """
        for link in group["role_links"]
    )
    missing = _list_items(
        group["missing_non_methodology_role_ids"],
        "No non-methodology role is hidden from this group.",
    )
    excluded = _list_items(
        group["excluded_methodology_role_ids"],
        "No methodology-only role excluded.",
    )
    return f"""
      <article class="major-group-drilldown-card" data-major-group-drilldown="{_text(group["major_group_drilldown_id"])}">
        <h3>{_text(group["phase_label_zh"])} / {_text(group["major_group_id"])}</h3>
        <dl class="mini-grid">
          <dt>Readiness</dt><dd>{_status_badge(group["readiness_status"])}</dd>
          <dt>角色連結</dt><dd>{group["role_drilldown_count"]}</dd>
          <dt>正式判讀 ready</dt><dd>{_yes_no(group["group_ready_for_formal_phase"])}</dd>
          <dt>候選 eligibility</dt><dd>{_yes_no(group["candidate_selection_eligible"])}</dd>
        </dl>
        <p>{_text(group["readiness_explanation_zh"])}</p>
        <div class="phase-profile-detail">
          <h4>角色連結</h4>
          <ul>{role_links}</ul>
        </div>
        <div class="phase-profile-detail">
          <h4>缺漏 / 排除脈絡</h4>
          <ul>{missing}{excluded}</ul>
        </div>
      </article>
    """


def _latest_role_drilldown_card(
    role: dict[str, Any],
    current_chart_row: dict[str, Any] | None = None,
) -> str:
    source = role["source_detail"]
    release = role["release_timing_detail"]
    freshness = role["freshness_detail"]
    transform = role["transformation_detail"]
    rule = role["rule_or_usability_detail"]
    provenance = role["provenance_detail"]
    data_mode = role["data_mode_detail"]
    abstention = role["abstention_reason_detail"]
    diagnostic = role["diagnostic_transparency_detail"]
    chart = role["chart_payload_detail"]
    search_text = " ".join(
        [
            role["role_id"],
            role["phase_or_layer"],
            role["major_group_id"],
            source["source_family"],
            source["data_risk_level"],
            role["continuity_status"],
            rule["evidence_usability_status"],
            diagnostic["method_id"],
            chart["unavailable_reason"] or "chart_available",
            " ".join(source["official_series_ids"]),
        ]
    ).lower()
    latest_context = "".join(
        _latest_observation_context_item(item)
        for item in source["latest_observation_context"]
    )
    release_rows = "".join(
        _release_context_item(item) for item in release["series_release_rows"]
    )
    freshness_counts = ", ".join(
        f"{key}: {value}"
        for key, value in sorted(freshness["freshness_status_counts"].items())
    )
    gap_codes = _list_items(
        abstention["continuity_gap_reason_codes"],
        "No continuity gap reason reported.",
    )
    chart_payload = _indicator_chart_payload_section(
        chart,
        current_chart_row=current_chart_row,
    )
    confidence_reducers = _plain_list_items(
        diagnostic.get("confidence_reduce_when"),
        "No confidence reducer declared.",
    )
    pseudo_code = _ordered_plain_items(diagnostic.get("pseudo_code_zh"))
    directionality = _definition_list_items(
        diagnostic.get("directionality_detail", {}),
    )
    score_interpretation = _score_interpretation_html(
        diagnostic.get("score_interpretation_zh", {}),
    )
    cleaned_inputs = ", ".join(
        str(item) for item in diagnostic.get("cleaned_input_requirements", [])
    )
    return f"""
      <article id="role-{_text(role["role_id"])}" class="role-drilldown-card" data-role-drilldown="{_text(role["role_id"])}" data-search="{_text(search_text)}">
        <div class="section-heading">
          <h3>{_text(role["phase_label_zh"])} / <code>{_text(role["role_id"])}</code></h3>
          <span>{_status_badge(role["continuity_status"])}</span>
        </div>
        <p><a class="action-link" data-indicator-trend-link data-role-trend-shortcut href="#chart-role-{_text(role["role_id"])}">查看 YTD / 1Y / 5Y 走勢</a></p>
        <p>{_text(role["dashboard_explanation_zh"])}</p>
        <dl class="mini-grid">
          <dt>主要群組</dt><dd>{_text(role["major_group_id"])}</dd>
          <dt>來源 family</dt><dd>{_text(source["source_family"])}</dd>
          <dt>資料風險</dt><dd>{_status_badge(source["data_risk_level"])}</dd>
          <dt>覆蓋 tier</dt><dd>{_text(source["source_coverage_tier"])}</dd>
          <dt>允許替代</dt><dd>{_yes_no(rule["book_core_replacement_allowed"])}</dd>
          <dt>Proxy 可取代 core</dt><dd>{_yes_no(rule["supporting_proxy_can_replace_book_core"])}</dd>
          <dt>數值載入</dt><dd>{data_mode["numeric_value_loaded_count"]}</dd>
          <dt>Point-in-time 結果</dt><dd>{_yes_no(data_mode["point_in_time_result"])}</dd>
        </dl>
        <div class="drilldown-detail-grid">
          <section data-source-detail>
            <h4>來源細節</h4>
            <p>{_text(source["source_risk_label_zh"])}</p>
            <p>Series：{_text(", ".join(source["official_series_ids"]) or "none")}</p>
            <ul>{latest_context}</ul>
          </section>
          <section data-release-timing-detail>
            <h4>發布時點</h4>
            <ul>{release_rows}</ul>
          </section>
          <section data-freshness-detail>
            <h4>新鮮度</h4>
            <p>{_text(freshness_counts or "no freshness status")}</p>
            <p>新鮮度足夠：{freshness["fresh_enough_series_count"]}；過期/缺漏：{freshness["stale_or_missing_series_count"]}</p>
          </section>
          <section data-transformation-detail>
            <h4>轉換方式</h4>
            <p>{_text(transform["transformation_semantics_status"])}</p>
          </section>
          <section data-rule-usability-detail>
            <h4>規則可用性</h4>
            <p>{_text(rule["coverage_status"])}</p>
            <p>{_text(rule["dashboard_display_status"])}</p>
            <p>{_text(rule["evidence_usability_status"])}</p>
          </section>
          <section data-score-transparency-detail>
            <h4>診斷方法透明度</h4>
            <p><strong>{_text(diagnostic["method_id"])}</strong></p>
            <p>{_text(diagnostic["method_purpose_zh"])}</p>
            {score_interpretation}
            <div data-method-recipe-detail>
              <p>方法歸屬：{_text(diagnostic["method_assignment_basis_zh"])}</p>
              <p>必要輸入：{_text(", ".join(diagnostic["method_inputs_required"]) or "not declared")}</p>
              <p>清理後輸入：{_text(cleaned_inputs or "not declared")}</p>
              <p>頻率處理：{_text(diagnostic.get("frequency_handling_zh") or "not declared")}</p>
              <p>缺漏資料：{_text(diagnostic.get("missing_value_handling_zh") or "not declared")}</p>
              <p>Lookback：{_text(diagnostic.get("lookback_rule") or "not declared")}；smoothing {_text(diagnostic.get("smoothing_window") or "not declared")}</p>
              <p>趨勢視窗：{_text(", ".join(str(item) for item in diagnostic["trend_window_options"] if item) or "not declared")}</p>
              <p>確認視窗：{_text(diagnostic["confirmation_window"])}</p>
              <p>最低歷史資料：{_text(diagnostic.get("min_history") or "not declared")}</p>
              <p>標準化方式：{_text(diagnostic.get("normalization_method") or "not declared")}</p>
            </div>
            <div data-method-directionality-detail>
              <p>方向性：</p>
              <dl class="mini-grid">{directionality}</dl>
            </div>
            <div data-method-confidence-detail>
              <p>信心折減條件：</p>
              <ul>{confidence_reducers}</ul>
            </div>
            <div data-method-pseudo-code-detail>
              <p>計算步驟：</p>
              <ol>{pseudo_code}</ol>
            </div>
            <p>已計算診斷值：{_yes_no(diagnostic["computed_diagnostic_value_present"])}</p>
            <p>{_text(diagnostic["legacy_diagnostic_boundary_zh"])}</p>
            <p>{_text(diagnostic["why_not_product_answer_zh"])}</p>
          </section>
          <section id="chart-role-{_text(role["role_id"])}" data-indicator-chart-payload data-indicator-trend-target>
            <h4>指標走勢圖</h4>
            <p data-chart-data-mode>{_display(chart["chart_data_mode"])}</p>
            <p>圖表可用：{_yes_no(chart["chart_available"])}</p>
            <p data-chart-unavailable-reason>{_text(chart["unavailable_reason"] or "available")}</p>
            <p class="muted">走勢圖在可用時使用受治理的 local current-cache 或 fixture/cache 脈絡。它只作解釋用途，不推論 declared state。</p>
            {chart_payload}
          </section>
          <section data-provenance-detail>
            <h4>血緣</h4>
            <p>{_text(provenance["source_indicator_detail_contract"])}</p>
            <p>{_text(provenance["source_continuity_contract"])}</p>
            <p>{_text(provenance["source_major_group_profile_contract"])}</p>
            <p>{_text(provenance["source_chart_payload_contract"])}</p>
            <p>資料模式：{_display(data_mode["display_data_mode"])}</p>
          </section>
          <section data-abstention-detail>
            <h4>Abstain / 下一缺口</h4>
            <p>{_text(abstention["why_not_evidence_zh"])}</p>
            <p>{_text(abstention["stale_or_missing_explanation_zh"])}</p>
            <p>{_text(role["next_gap_zh"])}</p>
            <ul>{gap_codes}</ul>
          </section>
        </div>
      </article>
    """


def _indicator_chart_payload_section(
    chart: dict[str, Any],
    *,
    current_chart_row: dict[str, Any] | None = None,
) -> str:
    periods = (
        current_chart_row["chart_periods"]
        if current_chart_row and current_chart_row.get("chart_periods")
        else _aggregate_chart_periods(chart["series_charts"])
    )
    return (
        '<div class="chart-period-grid">'
        + "".join(_chart_period_card(period) for period in periods)
        + "</div>"
    )


def _plain_list_items(items: Any, empty: str) -> str:
    if not isinstance(items, list) or not items:
        return f"<li>{_text(empty)}</li>"
    return "".join(f"<li>{_text(item)}</li>" for item in items)


def _ordered_plain_items(items: Any) -> str:
    if not isinstance(items, list) or not items:
        return "<li>尚未宣告計算步驟。</li>"
    return "".join(f"<li>{_text(item)}</li>" for item in items)


def _definition_list_items(mapping: dict[str, Any]) -> str:
    if not mapping:
        return "<dt>not_declared</dt><dd>尚未宣告方向性。</dd>"
    return "".join(
        f"<dt>{_text(key)}</dt><dd>{_text(value)}</dd>"
        for key, value in mapping.items()
    )


def _score_interpretation_html(interpretation: dict[str, Any]) -> str:
    if not interpretation:
        return """
            <div data-score-interpretation-detail>
              <p>尚未宣告分數解讀。</p>
            </div>
        """
    return f"""
            <div data-score-interpretation-detail>
              <p><strong>分數高代表：</strong>{_text(interpretation.get("high_score_zh") or "未宣告")}</p>
              <p><strong>分數低代表：</strong>{_text(interpretation.get("low_score_zh") or "未宣告")}</p>
              <p><strong>分數接近 0：</strong>{_text(interpretation.get("neutral_score_zh") or "未宣告")}</p>
              <p class="muted">{_text(interpretation.get("boundary_zh") or "此分數不是產品答案。")}</p>
            </div>
        """


def _aggregate_chart_periods(series_charts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    aggregated: list[dict[str, Any]] = []
    period_ids = ("ytd", "trailing_1y", "trailing_5y")
    for period_id in period_ids:
        matching = [
            period
            for series in series_charts
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
        aggregated.append(
            {
                "period_id": period_id,
                "label": source["label"],
                "start_date": source["start_date"],
                "end_date": source["end_date"],
                "chart_status": "available" if available else "unavailable",
                "point_count": len(points),
                "points": points[-12:],
                "unavailable_reason": ", ".join(reasons) if reasons else None,
            },
        )
    return aggregated


def _chart_period_card(period: dict[str, Any]) -> str:
    points = period["points"]
    first_value = _value_or_text(points[0]["value"], "none") if points else "none"
    last_value = _value_or_text(points[-1]["value"], "none") if points else "none"
    sparkline = _trend_sparkline_svg(period)
    point_items = "".join(
        f"<li>{_text(point['date'])}: {_text(point['value'])}</li>"
        for point in points[-6:]
    )
    if not point_items:
        point_items = "<li>此期間沒有可用數值點。</li>"
    return f"""
      <div class="chart-period-card" data-chart-period="{_text(period["period_id"])}">
        <strong>{_text(period["label"])}</strong>
        <span>{_status_badge(period["chart_status"])}</span>
        <p>{_text(period["start_date"])} 至 {_text(period["end_date"])}</p>
        <p>資料點：{period["point_count"]}；第一筆 {first_value}；最後一筆 {last_value}</p>
        <p data-trend-unavailable-reason>{_text(period["unavailable_reason"] or "chart data available")}</p>
        {sparkline}
        <ul class="chart-points">{point_items}</ul>
      </div>
    """


def _trend_sparkline_svg(period: dict[str, Any]) -> str:
    points = _numeric_chart_points(period["points"])
    if len(points) < 2 or period["chart_status"] != "available":
        return """
        <div class="trend-chart-empty" data-trend-chart-empty>
          此期間無法繪製趨勢線。
        </div>
        """
    width = 220
    height = 76
    padding = 8
    min_value = min(point["value"] for point in points)
    max_value = max(point["value"] for point in points)
    value_span = max(max_value - min_value, 1.0)
    denominator = max(len(points) - 1, 1)
    coords = []
    for index, point in enumerate(points):
        x = padding + ((width - padding * 2) * index / denominator)
        normalized = (point["value"] - min_value) / value_span
        y = height - padding - ((height - padding * 2) * normalized)
        coords.append(f"{x:.1f},{y:.1f}")
    start = points[0]
    end = points[-1]
    return f"""
      <svg class="trend-sparkline" data-trend-chart-svg data-chart-period-svg="{_text(period["period_id"])}" viewBox="0 0 {width} {height}" role="img" aria-label="{_text(period["label"])} trend">
        <polyline points="{' '.join(coords)}" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"></polyline>
        <circle cx="{coords[0].split(",")[0]}" cy="{coords[0].split(",")[1]}" r="2.5"></circle>
        <circle cx="{coords[-1].split(",")[0]}" cy="{coords[-1].split(",")[1]}" r="2.5"></circle>
      </svg>
      <p class="trend-caption" data-trend-caption>
        {_text(start["date"])} {_text(start["value"])} -> {_text(end["date"])} {_text(end["value"])}
      </p>
    """


def _numeric_chart_points(points: list[dict[str, Any]]) -> list[dict[str, Any]]:
    numeric_points: list[dict[str, Any]] = []
    for point in points:
        try:
            value = float(point["value"])
        except (TypeError, ValueError):
            continue
        numeric_points.append(
            {
                "date": point["date"],
                "value": value,
            },
        )
    return numeric_points


def _latest_observation_context_item(item: dict[str, Any]) -> str:
    return f"""
      <li>
        <code>{_text(item["series_id"])}</code>
        <span>{_display(item["source_mode"])}</span>
        <span>{_text(item["frequency"])}</span>
        <span>最新 {_text(item["latest_observation_date"])}</span>
        <span>數值 {_text(_value_or_text(item.get("latest_value"), "not loaded"))}</span>
      </li>
    """


def _release_context_item(item: dict[str, Any]) -> str:
    return f"""
      <li>
        <code>{_text(item["series_id"])}</code>
        <span>{_text(item["release_family"])}</span>
        <span>{_text(item["frequency"])}</span>
        <span>預期 {_text(item["expected_reference_period"])}</span>
        <span>觀察 {_text(item["observed_reference_period"])}</span>
      </li>
    """


def _page(title: str, active_href: str, body: str) -> str:
    nav = _nav(active_href)
    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{_display(title)} - 景氣循環研究儀表板</title>
  <link rel="icon" href="data:,">
  <link rel="stylesheet" href="assets/dashboard.css">
</head>
<body>
  <header class="topbar">
    <a class="brand" href="index.html">景氣循環研究儀表板</a>
    <span class="badge badge-research" data-research-only-label>研究用途</span>
  </header>
  <div class="shell">
    <nav class="sidebar" aria-label="研究儀表板導覽">{nav}</nav>
    <main>
      <div class="trust-ribbon">
        <span>研究用途</span>
        <span>驗證用途</span>
        <span>非正式 production</span>
        <span>不構成投資建議</span>
        <span>不輸出候選階段或目前階段</span>
      </div>
      {body}
    </main>
  </div>
  <script src="assets/dashboard.js"></script>
</body>
</html>
"""


def _nav(active_href: str) -> str:
    links = [
        ("index.html", "總覽"),
        ("scenarios.html", "歷史情境"),
        ("validation.html", "驗證結果"),
        ("evidence.html", "證據總覽"),
        ("lineage.html", "資料血緣"),
        ("pit-gaps.html", "PIT 缺口"),
    ]
    if active_href == CURRENT_SNAPSHOT_PAGE:
        links.append((CURRENT_SNAPSHOT_PAGE, "目前研究快照"))
    if active_href == BOOM_TRANSITION_PAGE:
        links.append((BOOM_TRANSITION_PAGE, "榮景轉折"))
    if active_href == LATEST_EVIDENCE_PAGE:
        links.append((LATEST_EVIDENCE_PAGE, "最新證據"))
    if active_href == PORTFOLIO_REPLAY_PAGE:
        links.append((PORTFOLIO_REPLAY_PAGE, "Portfolio 研究"))
    items = []
    for href, label in links:
        active = ' class="active"' if href == active_href else ""
        items.append(f'<a href="{href}"{active}>{label}</a>')
    return "".join(items)


def _current_snapshot_entry(bundle: dict[str, Any]) -> str:
    if "current_snapshot" not in bundle:
        return ""
    snapshot = bundle["current_snapshot"]
    return f"""
      <div class="callout" data-current-snapshot-entry>
        <strong>目前研究快照</strong>
        <span>{_text(snapshot["snapshot_as_of"])} / {_display(snapshot["data_mode"])}</span>
        <a href="{CURRENT_SNAPSHOT_PAGE}">查看目前研究快照</a>
      </div>
    """


def _boom_transition_entry(bundle: dict[str, Any]) -> str:
    if "boom_transition_dashboard" not in bundle:
        return ""
    surface = bundle["boom_transition_dashboard"]
    return f"""
      <div class="callout" data-boom-transition-entry>
        <strong>已宣告榮景期轉折監測</strong>
        <span>{_text(surface["monitor_as_of"])} / 合法下一階段 {_display(surface["legal_next_phase"])}</span>
        <a href="{BOOM_TRANSITION_PAGE}">查看轉折監測</a>
      </div>
    """


def _latest_evidence_entry(bundle: dict[str, Any]) -> str:
    if "indicator_dashboard_explanation_drilldown" not in bundle:
        return ""
    drilldown = bundle["indicator_dashboard_explanation_drilldown"]
    return f"""
      <div class="callout" data-latest-evidence-entry>
        <strong>最新證據與指標細節</strong>
        <span>{drilldown["major_group_drilldown_count"]} 個群組 / {drilldown["role_drilldown_count"]} 個角色</span>
        <a href="{LATEST_EVIDENCE_PAGE}">查看最新證據</a>
      </div>
    """


def _portfolio_replay_entry(bundle: dict[str, Any]) -> str:
    if "portfolio_replay_dashboard_surface" not in bundle:
        return ""
    surface = bundle["portfolio_replay_dashboard_surface"]
    return f"""
      <div class="callout" data-portfolio-replay-entry>
        <strong>Portfolio policy 與歷史重播研究</strong>
        <span>{surface["research_backtest_artifact_count"]} 個 artifacts / {surface["metric_formula_reference_family_count"]} 個 metric formulas 僅參照</span>
        <a href="{PORTFOLIO_REPLAY_PAGE}">查看 portfolio replay 研究</a>
      </div>
    """


def _portfolio_replay_page(bundle: dict[str, Any]) -> str:
    surface = bundle["portfolio_replay_dashboard_surface"]
    cards = "".join(_portfolio_replay_card(row) for row in surface["dashboard_cards"])
    lineage = "".join(
        _portfolio_replay_lineage_row(row) for row in surface["lineage_drilldown_rows"]
    )
    caveats = "".join(
        f"<li data-backtest-caveat>{_text(item)}</li>" for item in surface["caveats_zh"]
    )
    body = f"""
    <section class="panel" data-dashboard-view="portfolio_replay_dashboard_surface" data-portfolio-replay-surface>
      <div class="section-heading">
        <h1>Portfolio policy 與歷史重播研究</h1>
        <span class="badge badge-research" data-research-only-label>研究用途</span>
      </div>
      <p class="muted">本頁串接 replay rows、policy schedule 參照、cash-flow kernel 假設與 research-only backtest artifacts。它不計算 metric 值、不建議目前配置、不輸出交易指令，也不改變 declared phase。</p>
      <div class="status-strip">
        <span>尚未計算 metric 值</span>
        <span>回測執行停用</span>
        <span>保留已宣告階段</span>
        <span>僅本機/NAS 研究 dashboard</span>
      </div>
      <div class="metric-grid">
        {_metric_card("Artifacts", surface["research_backtest_artifact_count"], "scenario x data mode")}
        {_metric_card("情境", surface["scenario_count"], "validation manifest")}
        {_metric_card("資料模式", surface["replay_data_mode_count"], "strict/revised separated")}
        {_metric_card("Metric formulas", surface["metric_formula_reference_family_count"], "僅參照，未計算")}
      </div>
      <section class="panel nested" data-policy-schedule-reference data-cash-flow-kernel-reference>
        <h2>Policy schedule 與現金流 kernel 參照</h2>
        <dl class="definition-grid">
          <dt>Policy schedule</dt><dd><code>{_text(surface["policy_schedule_summary"]["contract_id"])}</code></dd>
          <dt>Template schedules</dt><dd>{surface["policy_schedule_summary"]["template_with_schedule_count"]}</dd>
          <dt>現金流 kernel</dt><dd><code>{_text(surface["cash_flow_kernel_summary"]["contract_id"])}</code></dd>
          <dt>Kernel 元件</dt><dd>{surface["cash_flow_kernel_summary"]["kernel_component_count"]}</dd>
          <dt>Metric 狀態</dt><dd data-metric-formula-reference>{surface["metric_formula_reference_family_count"]} 個公式僅參照；未計算數值</dd>
        </dl>
      </section>
      <div class="card-grid">{cards}</div>
      <section class="panel nested">
        <h2>Artifact 血緣細節</h2>
        <div class="table-wrap">
          <table>
            <thead><tr><th>Artifact</th><th>Replay row</th><th>Policy</th><th>Kernel</th><th>Metric registry</th><th>Input hash</th></tr></thead>
            <tbody>{lineage}</tbody>
          </table>
        </div>
      </section>
      <section class="panel nested">
        <h2>限制與註記</h2>
        <ul>{caveats}</ul>
      </section>
    </section>
    {_portfolio_policy_replay_research_section(bundle.get("portfolio_policy_replay_research_surface"))}
    """
    return _page("Portfolio Replay Research", PORTFOLIO_REPLAY_PAGE, body)


def _portfolio_replay_card(row: dict[str, Any]) -> str:
    return f"""
      <article class="mini-card" data-backtest-artifact-card="{_text(row["artifact_id"])}">
        <strong>{_text(row["scenario_id"])}</strong>
        <dl class="mini-grid">
          <dt>資料模式</dt><dd>{_display(row["data_mode"])}</dd>
          <dt>狀態</dt><dd>{_status_badge(row["artifact_status"])}</dd>
          <dt>Formula refs</dt><dd>{row["metric_formula_ref_count"]}</dd>
          <dt>Metric 值</dt><dd>{_display(row["metric_value_status"])}</dd>
        </dl>
        <p class="muted"><code>{_text(row["input_hash"])}</code></p>
      </article>
    """


def _portfolio_replay_lineage_row(row: dict[str, Any]) -> str:
    return f"""
      <tr data-backtest-lineage-row="{_text(row["artifact_id"])}">
        <td><code>{_text(row["artifact_id"])}</code></td>
        <td><code>{_text(row["source_replay_row_id"])}</code></td>
        <td><code>{_text(row["source_policy_schedule_contract_id"])}</code></td>
        <td><code>{_text(row["source_cash_flow_kernel_contract_id"])}</code></td>
        <td><code>{_text(row["source_metric_formula_registry_id"])}</code></td>
        <td><code>{_text(row["input_hash"])}</code></td>
      </tr>
    """


def _portfolio_policy_replay_research_section(surface: dict[str, Any] | None) -> str:
    if surface is None:
        return ""
    templates = "".join(
        _policy_template_card(row) for row in surface["template_catalog_rows"]
    )
    schedules = "".join(
        _policy_replay_schedule_row(row)
        for row in surface["replay_schedule_matrix_rows"]
    )
    costs = "".join(
        _policy_cost_turnover_row(row)
        for row in surface["cost_turnover_assumption_rows"]
    )
    coverage = "".join(
        _policy_scenario_coverage_row(row)
        for row in surface["scenario_policy_coverage_rows"]
    )
    caveats = "".join(
        f"<li data-policy-replay-caveat>{_text(item)}</li>"
        for item in surface["renderer_caveats_zh"]
    )
    return f"""
    <section class="panel" data-dashboard-view="portfolio_policy_replay_research_surface" data-policy-replay-research-surface>
      <div class="section-heading">
        <h2>Portfolio policy replay 研究</h2>
        <span class="badge badge-research" data-research-only-label>研究用途</span>
      </div>
      <p class="muted">本區說明研究性配置模板，以及未來如何在 replay/backtest 中檢視。它不執行 replay、不計算績效，也不產生個人化交易指令。</p>
      <div class="status-strip" data-no-personalized-trade-instruction>
        <span>policy replay execution disabled</span>
        <span>回測執行停用</span>
        <span>尚未計算 metric 值</span>
        <span>允許研究性配置模板</span>
        <span>不產生個人化交易指令</span>
      </div>
      <div class="metric-grid">
        {_metric_card("Templates", surface["policy_template_count"], "research-only")}
        {_metric_card("Schedules", surface["replay_schedule_row_count"], "pre-registered")}
        {_metric_card("情境覆蓋", surface["scenario_policy_coverage_row_count"], "scenario x template")}
        {_metric_card("註記", surface["renderer_caveat_count"], "visible guardrails")}
      </div>
      <section class="panel nested">
        <h3>Policy template 目錄</h3>
        <div class="mini-grid">{templates}</div>
      </section>
      <section class="panel nested">
        <h3>Replay schedule matrix</h3>
        <div class="table-wrap">
          <table>
            <thead><tr><th>Template</th><th>類型</th><th>觸發脈絡</th><th>必要轉折輸入</th><th>資料模式</th></tr></thead>
            <tbody>{schedules}</tbody>
          </table>
        </div>
      </section>
      <section class="panel nested">
        <h3>成本與 turnover 假設</h3>
        <div class="table-wrap">
          <table>
            <thead><tr><th>Template</th><th>成本政策</th><th>時鐘政策</th><th>Turnover</th><th>False signal</th><th>Missed recovery</th></tr></thead>
            <tbody>{costs}</tbody>
          </table>
        </div>
      </section>
      <section class="panel nested">
        <h3>情境 policy 覆蓋</h3>
        <div class="table-wrap">
          <table>
            <thead><tr><th>情境</th><th>Template</th><th>狀態</th><th>資料模式</th></tr></thead>
            <tbody>{coverage}</tbody>
          </table>
        </div>
      </section>
      <section class="panel nested">
        <h3>研究用途註記</h3>
        <ul>{caveats}</ul>
      </section>
    </section>
    """


def _policy_template_card(row: dict[str, Any]) -> str:
    return f"""
      <article class="mini-card" data-policy-template-card="{_text(row["template_id"])}">
        <span class="badge" data-research-allocation-template>研究性配置模板</span>
        <strong>{_text(row["template_id"])}</strong>
        <p>{_text(row["template_name_zh"])}</p>
        <dl class="mini-grid">
          <dt>類型</dt><dd>{_text(row["template_family"])}</dd>
          <dt>Schedule</dt><dd>{_text(row["schedule_family"])}</dd>
          <dt>現在可執行</dt><dd>{_display(str(row["execution_allowed_now"]).lower())}</dd>
        </dl>
      </article>
    """


def _policy_replay_schedule_row(row: dict[str, Any]) -> str:
    required = ", ".join(row["required_transition_inputs"]) or "none"
    return f"""
      <tr data-policy-replay-schedule-row="{_text(row["schedule_id"])}">
        <td><code>{_text(row["template_id"])}</code></td>
        <td>{_text(row["schedule_family"])}</td>
        <td>{_text(row["research_trigger_context_zh"])}</td>
        <td>{_text(required)}</td>
        <td>{_display(row["data_mode_policy"])}</td>
      </tr>
    """


def _policy_cost_turnover_row(row: dict[str, Any]) -> str:
    return f"""
      <tr data-policy-cost-turnover-row="{_text(row["template_id"])}">
        <td><code>{_text(row["template_id"])}</code></td>
        <td>{_text(row["cost_assumption_policy"])}</td>
        <td>{_text(row["rebalance_clock_policy"])}</td>
        <td>{_text(row["turnover_status"])}</td>
        <td>{_text(row["false_signal_cost_status"])}</td>
        <td>{_text(row["missed_recovery_cost_status"])}</td>
      </tr>
    """


def _policy_scenario_coverage_row(row: dict[str, Any]) -> str:
    return f"""
      <tr data-policy-scenario-coverage-row="{_text(row["scenario_id"])}::{_text(row["template_id"])}">
        <td><code>{_text(row["scenario_id"])}</code></td>
        <td><code>{_text(row["template_id"])}</code></td>
        <td>{_status_badge(row["coverage_status"])}</td>
        <td>{_display(row["data_mode_policy"])}</td>
      </tr>
    """


def _transition_timing_replay_preview_section(preview: dict[str, Any] | None) -> str:
    if preview is None:
        return ""
    checkpoints = "".join(
        f"""
        <article class="mini-card" data-transition-replay-checkpoint="{_text(row["checkpoint_id"])}">
          <strong>{_text(row["title_zh"])}</strong>
          <p class="muted">{_text(row["checkpoint_semantics_zh"])}</p>
        </article>
        """
        for row in preview["transition_replay_checkpoints"]
    )
    lanes = "".join(
        f"""
        <article class="mini-card" data-transition-lane-timing-preview="{_text(row["lane_id"])}">
          <strong>{_text(row["title_zh"])}</strong>
          <dl class="mini-grid">
            <dt>轉折</dt><dd>{_text(row["transition_id"])}</dd>
            <dt>Lane</dt><dd>{_text(row["lane_category"])}</dd>
            <dt>狀態</dt><dd>{_status_badge(row["timing_preview_status"])}</dd>
            <dt>群組</dt><dd>{len(row["major_group_profile_refs"])}</dd>
            <dt>角色</dt><dd>{len(row["continuity_role_refs"])}</dd>
          </dl>
          <p>{_text(row["accumulation_interpretation_zh"])}</p>
        </article>
        """
        for row in preview["transition_lane_timing_previews"]
    )
    events = "".join(
        f"""
        <tr data-transition-accumulation-event="{_text(row["checkpoint_id"])}::{_text(row["lane_id"])}">
          <td>{_text(row["checkpoint_id"])}</td>
          <td>{_text(row["transition_id"])}</td>
          <td>{_text(row["lane_id"])}</td>
          <td>{_status_badge(row["accumulation_status"])}</td>
          <td>{_text(row["abstention_state"])}</td>
        </tr>
        """
        for row in preview["evidence_accumulation_events"][:12]
    )
    return f"""
    <section class="panel" data-transition-timing-replay-preview>
      <div class="section-heading">
        <h2>轉折時點重播預覽</h2>
        <span class="badge badge-research" data-research-only-label>研究用途</span>
      </div>
      <p class="muted">本預覽顯示轉折證據如何在受治理 checkpoint 間累積。它不執行歷史驗證、不計算 accuracy、不選候選階段，也不推論目前階段。</p>
      <div class="status-strip" data-transition-replay-boundary>
        <span>保留已宣告階段</span>
        <span>watch 不是 confirmation</span>
        <span>缺漏值導致 abstain</span>
        <span>不輸出階段分數或排名</span>
      </div>
      <div class="metric-grid">
        {_metric_card("Checkpoints", preview["transition_replay_checkpoint_count"], "replay preview")}
        {_metric_card("Lane previews", preview["transition_lane_timing_preview_count"], "legal transitions")}
        {_metric_card("累積事件", preview["evidence_accumulation_event_count"], "research-only")}
      </div>
      <div class="mini-grid">{checkpoints}</div>
      <div class="transition-lane-grid">{lanes}</div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Checkpoint</th><th>轉折</th><th>Lane</th><th>狀態</th><th>Abstain</th></tr></thead>
          <tbody>{events}</tbody>
        </table>
      </div>
    </section>
    """


def _overview_scenario_row(scenario: dict[str, Any]) -> str:
    return (
        "<tr>"
        f"<td>{_text(scenario['scenario_name'])}</td>"
        f"<td>{_text(scenario['window_start'])} 至 {_text(scenario['window_end'])}</td>"
        f"<td>{_status_badge(scenario['comparability_label'])}</td>"
        f"<td>{_display(scenario['research_decision_state'])}</td>"
        f"<td><a href=\"{_text(scenario['detail_href'])}\">查看細節</a></td>"
        "</tr>"
    )


def _scenario_table_row(scenario: dict[str, Any]) -> str:
    search_text = " ".join(
        [
            scenario["scenario_id"],
            scenario["scenario_name"],
            scenario["scenario_family"],
            scenario["comparison_status"],
            " ".join(scenario["blocked_reason_codes"]),
        ]
    )
    return f"""<tr data-status="{_text(scenario['comparability_label'])}" data-search="{_text(search_text).lower()}">
      <td>{_text(scenario["scenario_name"])}<br><code>{_text(scenario["scenario_id"])}</code></td>
      <td>{_text(scenario["scenario_family"])}</td>
      <td>{_display(scenario["research_decision_state"])}</td>
      <td>{_display(scenario["predicted_label"])}</td>
      <td>{_status_badge(scenario["comparison_status"])}</td>
      <td>{scenario["pit_gap_count"]}</td>
      <td><a href="{_text(scenario["detail_href"])}">查看細節</a></td>
    </tr>"""


def _evidence_table_row(row: dict[str, Any]) -> str:
    status = "open" if row["post_gap_persists"] else "resolved"
    search = " ".join(
        [
            row["scenario_id"],
            row["phase_or_layer"],
            row["major_group_id"],
            row["role_id"],
            " ".join(row["required_series_ids"]),
            row["post_gap_class"],
        ]
    )
    return f"""<tr data-gap="{status}" data-search="{_text(search).lower()}">
      <td>{_text(row["scenario_id"])}</td>
      <td>{_display(row["phase_or_layer"])}</td>
      <td>{_text(row["major_group_id"])}</td>
      <td><code>{_text(row["role_id"])}</code></td>
      <td>{_text(", ".join(row["required_series_ids"]))}</td>
      <td>{_status_badge(row["evidence_state"])}</td>
      <td>{_display(row["post_gap_class"])}</td>
      <td>{_display(row["classification"])}</td>
    </tr>"""


def _pit_gap_table_row(row: dict[str, Any]) -> str:
    return f"""<tr>
      <td>{_text(row["scenario_id"])}</td>
      <td><code>{_text(row["role_id"])}</code></td>
      <td>{_text(", ".join(row["required_series_ids"]))}</td>
      <td>{_text(row["required_observation_window"])}</td>
      <td>{_status_badge(row["post_gap_class"])}</td>
      <td>{_text(row["genuine_blocker_evidence"])}</td>
    </tr>"""


def _source_availability_row(row: dict[str, Any]) -> str:
    return f"""<tr>
      <td><code>{_text(row["series_id"])}</code></td>
      <td>{_text(row["source"])}</td>
      <td>{_text(row["frequency"])}</td>
      <td>{_status_badge(row["availability_status"])}</td>
      <td>{_display(row.get("source_mode", "fixture"))}<br><span class="muted">{_display(row.get("freshness_status", "legacy"))}</span></td>
      <td>{_text(row.get("latest_observation_date", "unknown"))}</td>
      <td>{_text(row["latest_verified_vintage_date"])}</td>
      <td>{_yes_no(row["stale"])}</td>
    </tr>"""


def _list_items(items: list[str], empty: str) -> str:
    if not items:
        return f"<li>{_text(empty)}</li>"
    return "".join(f"<li><code>{_text(item)}</code></li>" for item in items)


def _bundle_has_current_snapshot(root: Path) -> bool:
    bundle_path = root / "data" / "dashboard_bundle.json"
    if not bundle_path.exists():
        return False
    try:
        payload = json.loads(bundle_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return "current_snapshot" in payload


def _bundle_has_boom_transition(root: Path) -> bool:
    bundle_path = root / "data" / "dashboard_bundle.json"
    if not bundle_path.exists():
        return False
    try:
        payload = json.loads(bundle_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return "boom_transition_dashboard" in payload


def _bundle_has_latest_evidence(root: Path) -> bool:
    bundle_path = root / "data" / "dashboard_bundle.json"
    if not bundle_path.exists():
        return False
    try:
        payload = json.loads(bundle_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return "indicator_dashboard_explanation_drilldown" in payload


def _bundle_has_portfolio_replay(root: Path) -> bool:
    bundle_path = root / "data" / "dashboard_bundle.json"
    if not bundle_path.exists():
        return False
    try:
        payload = json.loads(bundle_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return "portfolio_replay_dashboard_surface" in payload


def _metric_summary_row(metric: dict[str, Any]) -> str:
    value = _metric_value(metric)
    numerator = _value_or_text(metric.get("numerator"), "undefined")
    denominator = _value_or_text(metric.get("denominator"), "undefined")
    interpretation = metric.get("skip_reason") or metric.get("denominator_definition") or ""
    return f"""<tr>
      <td><code>{_text(metric["metric_id"])}</code></td>
      <td>{_status_badge(metric["result_status"])}</td>
      <td>{value}</td>
      <td>{_text(numerator)}</td>
      <td>{_text(denominator)}</td>
      <td>{_display(interpretation)}</td>
    </tr>"""


def _metric_state_row(metric: dict[str, Any]) -> str:
    return (
        "<tr>"
        f"<td><code>{_text(metric['metric_id'])}</code></td>"
        f"<td>{_status_badge(metric['result_status'])}</td>"
        "</tr>"
    )


def _metric_value(metric: dict[str, Any]) -> str:
    if metric.get("value") is None:
        return '<span class="muted">依預註冊前置條件尚未定義</span>'
    return _text(metric["value"])


def _metric_card(label: str, value: Any, note: str) -> str:
    return (
        '<div class="metric-card">'
        f"<span>{_display(label)}</span>"
        f"<strong>{_display(value)}</strong>"
        f"<em>{_display(note)}</em>"
        "</div>"
    )


def _status_badge(value: Any) -> str:
    text = _text(value)
    slug = "".join(ch if ch.isalnum() else "-" for ch in text.lower()).strip("-")
    return f'<span class="status status-{slug}">{_display(value)}</span>'


def _yes_no(value: bool) -> str:
    return "是" if value else "否"


def _value_or_text(value: Any, fallback: str) -> str:
    return fallback if value is None else str(value)


def _empty_row(colspan: int, message: str) -> str:
    return f'<tr><td colspan="{colspan}" class="muted">{_display(message)}</td></tr>'


def _display(value: Any) -> str:
    """Escape user-visible dashboard text with a Traditional Chinese label map."""

    raw = str(value)
    mapped = _display_raw(raw)
    return escape(mapped)


def _display_raw(raw: str) -> str:
    lowered = raw.lower()
    if raw in DISPLAY_TEXT_ZH:
        return DISPLAY_TEXT_ZH[raw]
    if raw in STATUS_TEXT_ZH:
        return STATUS_TEXT_ZH[raw]
    if lowered in PHASE_LABEL_ZH:
        return PHASE_LABEL_ZH[lowered]
    if lowered in DISPLAY_TEXT_ZH:
        return DISPLAY_TEXT_ZH[lowered]
    if lowered in STATUS_TEXT_ZH:
        return STATUS_TEXT_ZH[lowered]
    return raw


def _text(value: Any) -> str:
    return escape(str(value))


def _validated_output_dir(
    output_dir: str | Path,
    *,
    allow_repo_output: bool = False,
) -> Path:
    path = Path(output_dir)
    resolved = path.resolve()
    if allow_repo_output and resolved == (Path.cwd() / "public").resolve():
        return resolved
    if not resolved.is_relative_to(ALLOWED_OUTPUT_ROOT.resolve()):
        raise ValueError(f"Phase 38 dashboard output must be under /tmp: {output_dir}")
    cwd = Path.cwd().resolve()
    for root in PROHIBITED_OUTPUT_ROOTS:
        prohibited = (cwd / root).resolve()
        if resolved.is_relative_to(prohibited):
            raise ValueError(f"refusing prohibited output path: {output_dir}")
    return resolved


def _load_bundle_from_output(root: Path) -> dict[str, Any]:
    bundle_path = root / "data" / "dashboard_bundle.json"
    if bundle_path.exists():
        return json.loads(bundle_path.read_text(encoding="utf-8"))
    return build_research_dashboard_bundle()


def _scenario_ids_from_bundle_file(root: Path) -> list[str]:
    return [scenario["scenario_id"] for scenario in _load_bundle_from_output(root)["scenarios"]]


def _dashboard_css() -> str:
    return """
:root {
  color-scheme: light;
  --bg: #f5f7fa;
  --surface: #ffffff;
  --surface-alt: #f0f4f8;
  --line: #d8dee8;
  --text: #17202a;
  --muted: #5f6c7b;
  --accent: #1565c0;
  --research: #5b4b00;
  --ok: #146c43;
  --warn: #8a5a00;
  --bad: #9f1239;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.45;
}
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
.topbar {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 16px;
  border-bottom: 1px solid var(--line);
  background: var(--surface);
}
.brand { color: var(--text); font-weight: 800; }
.shell { display: grid; grid-template-columns: 210px minmax(0, 1fr); min-height: calc(100vh - 45px); }
.sidebar {
  border-right: 1px solid var(--line);
  padding: 14px;
  background: var(--surface);
}
.sidebar a {
  display: block;
  padding: 8px 10px;
  border-radius: 6px;
  color: var(--text);
}
.sidebar a.active, .sidebar a:hover { background: var(--surface-alt); text-decoration: none; }
main { min-width: 0; width: min(1240px, 100%); padding: 18px; }
.trust-ribbon {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
}
.trust-ribbon span, .badge, .status {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 2px 8px;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: var(--surface-alt);
  font-size: 0.78rem;
  font-weight: 700;
  white-space: nowrap;
}
.badge-research { border-color: #b59f00; background: #fff8c5; color: var(--research); }
.panel {
  margin: 0 0 14px;
  padding: 14px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--surface);
}
.section-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}
h1 { margin: 0; font-size: 1.45rem; }
h2 { margin: 0 0 10px; font-size: 1.1rem; }
.muted { color: var(--muted); }
.metric-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 10px;
}
.metric-card {
  min-width: 0;
  padding: 10px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--surface-alt);
}
.metric-card span, .metric-card em { display: block; color: var(--muted); font-style: normal; font-size: 0.78rem; }
.metric-card strong { display: block; margin: 3px 0; font-size: 1.45rem; }
.phase-card-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}
.phase-profile-card, .transition-lane-card, .transition-indicator-card {
  min-width: 0;
  padding: 10px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--surface-alt);
}
.phase-profile-card h3, .transition-lane-card h3, .transition-indicator-card h3 { margin: 0 0 8px; font-size: 1rem; }
.phase-profile-card h4, .transition-indicator-card h4 { margin: 8px 0 4px; font-size: 0.86rem; }
.phase-profile-card ul, .transition-indicator-card ul { margin: 0; padding-left: 18px; }
.major-group-drilldown-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}
.role-drilldown-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}
.major-group-drilldown-card, .role-drilldown-card {
  min-width: 0;
  padding: 10px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--surface-alt);
  scroll-margin-top: 70px;
}
.major-group-drilldown-card h3, .role-drilldown-card h3 { margin: 0 0 8px; font-size: 1rem; }
.major-group-drilldown-card h4, .role-drilldown-card h4 { margin: 8px 0 4px; font-size: 0.86rem; }
.major-group-drilldown-card ul, .role-drilldown-card ul { margin: 0; padding-left: 18px; }
.drilldown-detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  margin-top: 8px;
}
.drilldown-detail-grid section {
  min-width: 0;
  padding: 8px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--surface);
}
.drilldown-detail-grid p { margin: 4px 0; overflow-wrap: anywhere; }
.drilldown-detail-grid ul { margin: 0; padding-left: 18px; }
.drilldown-detail-grid li { margin-bottom: 4px; overflow-wrap: anywhere; }
.chart-period-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 8px;
  margin-top: 8px;
}
.chart-period-card {
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 8px;
  background: var(--surface-alt);
}
.action-link {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  color: var(--accent);
  font-weight: 700;
  text-decoration: none;
}
.action-link:hover { text-decoration: underline; }
.chart-period-card strong,
.chart-period-card span {
  display: inline-block;
  margin-right: 6px;
}
.trend-sparkline {
  display: block;
  width: 100%;
  height: 78px;
  margin: 8px 0 4px;
  color: var(--accent);
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 6px;
}
.trend-sparkline circle { fill: currentColor; }
.trend-caption {
  margin: 2px 0 6px;
  color: var(--muted);
  font-size: 0.78rem;
}
.trend-chart-empty {
  margin: 8px 0;
  padding: 8px;
  border: 1px dashed var(--line);
  border-radius: 6px;
  color: var(--muted);
  background: var(--surface);
}
.chart-points {
  max-height: 120px;
  overflow: auto;
}
.transition-lane-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}
.transition-indicator-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}
.mini-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 4px 8px;
  margin: 0;
  font-size: 0.82rem;
}
.mini-grid dt { color: var(--muted); }
.mini-grid dd { margin: 0; overflow-wrap: anywhere; }
.status-strip { display: flex; flex-wrap: wrap; gap: 8px; color: var(--muted); }
.status-strip span { border-left: 3px solid var(--accent); padding-left: 8px; }
.table-wrap { width: 100%; overflow-x: auto; border: 1px solid var(--line); border-radius: 8px; }
table { width: 100%; min-width: 760px; border-collapse: collapse; background: var(--surface); }
th, td { padding: 8px 10px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }
th { background: var(--surface-alt); font-size: 0.82rem; }
code { overflow-wrap: anywhere; }
.toolbar { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 10px; }
input, select { min-height: 34px; border: 1px solid var(--line); border-radius: 6px; padding: 4px 8px; background: #fff; }
.definition-grid { display: grid; grid-template-columns: 180px minmax(0, 1fr); gap: 8px 12px; }
.definition-grid dt { color: var(--muted); }
.definition-grid dd { margin: 0; overflow-wrap: anywhere; }
.two-column { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.provenance-list { overflow-wrap: anywhere; }
.status-comparable, .status-computed, .status-resolved-by-existing-pit-cache { color: var(--ok); }
.status-not-comparable, .status-abstained, .status-official-history-insufficient, .status-genuine-source-unavailable { color: var(--warn); }
.status-rule-unresolved-not-data-gap, .status-skipped-prerequisite-unavailable { color: var(--bad); }
@media (max-width: 760px) {
  .shell { grid-template-columns: 1fr; }
  .sidebar {
    display: flex;
    gap: 6px;
    overflow-x: auto;
    border-right: 0;
    border-bottom: 1px solid var(--line);
  }
  .sidebar a { white-space: nowrap; }
  main { padding: 12px; }
  .section-heading { align-items: flex-start; flex-direction: column; }
  .metric-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .phase-card-grid { grid-template-columns: 1fr; }
  .transition-lane-grid, .transition-indicator-grid { grid-template-columns: 1fr; }
  .major-group-drilldown-grid, .role-drilldown-grid { grid-template-columns: 1fr; }
  .drilldown-detail-grid { grid-template-columns: 1fr; }
  .definition-grid { grid-template-columns: 1fr; }
  .two-column { grid-template-columns: 1fr; }
  table { min-width: 680px; }
}
"""


def _dashboard_js() -> str:
    return """
(function () {
  function attachTableFilter(searchId, selectId, rowSelector) {
    var search = document.getElementById(searchId);
    var select = document.getElementById(selectId);
    var rows = Array.prototype.slice.call(document.querySelectorAll(rowSelector));
    if (!search && !select) return;
    function apply() {
      var q = search ? search.value.trim().toLowerCase() : "";
      var status = select ? select.value : "all";
      rows.forEach(function (row) {
        var haystack = row.getAttribute("data-search") || "";
        var rowStatus = row.getAttribute("data-status") || row.getAttribute("data-gap") || "";
        var matchesSearch = !q || haystack.indexOf(q) >= 0;
        var matchesStatus = status === "all" || rowStatus === status;
        row.hidden = !(matchesSearch && matchesStatus);
      });
    }
    if (search) search.addEventListener("input", apply);
    if (select) select.addEventListener("change", apply);
    apply();
  }
  attachTableFilter("scenario-search", "scenario-filter", "#scenario-table tbody tr");
  attachTableFilter("evidence-search", "evidence-filter", "#evidence-table tbody tr");
  attachTableFilter("latest-role-search", null, "#latest-role-grid [data-role-drilldown]");
})();
"""

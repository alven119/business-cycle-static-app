"""Private NAS service dashboard route/API/HTML rehearsal for Phase 95."""

from __future__ import annotations

from html import escape
from pathlib import Path
import hashlib
import json
from typing import Any

import yaml

from business_cycle.audits.product_capability_progress import (
    summarize_product_capability_progress,
)
from business_cycle.render.nas_cycle_command_center import (
    build_nas_cycle_command_center,
)
from business_cycle.render.nas_portfolio_replay_lab import (
    build_nas_portfolio_replay_lab,
)
from business_cycle.render.technology_manufacturing_cycle import (
    build_technology_manufacturing_cycle_view,
)
from business_cycle.storage.nas_indicator_snapshots import (
    build_nas_indicator_snapshot_manifest,
    summarize_nas_indicator_snapshot,
)
from business_cycle.transition_monitor.live_ordered_cycle_evidence import (
    build_live_ordered_cycle_evidence,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = ROOT / "specs/common/nas_service_dashboard_contract.yaml"
DEFAULT_ROLE_LABELS_PATH = (
    ROOT / "specs/common/book_core_role_display_labels_zh.yaml"
)
TMP_ROOT = Path("/tmp")
MAX_RENDERED_SVG_POINTS = 240

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


def load_nas_service_dashboard_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Load the governed Phase95 NAS service dashboard contract."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["nas_service_dashboard_contract"])


def build_nas_service_dashboard_bundle(
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
    snapshot_manifest: dict[str, Any] | None = None,
    runtime_live_mode: bool = False,
) -> dict[str, Any]:
    """Build route, API, and HTML view-models without starting a service."""

    contract = load_nas_service_dashboard_contract(contract_path)
    snapshot = snapshot_manifest or build_nas_indicator_snapshot_manifest()
    role_labels = load_book_core_role_display_labels_zh()
    _validate_role_label_coverage(snapshot=snapshot, role_labels=role_labels)
    declared_phase = str(
        snapshot.get("declared_cycle_state", {}).get(
            "declared_current_phase", "boom"
        )
    )
    live_transition_evidence = (
        build_live_ordered_cycle_evidence(snapshot)
        if runtime_live_mode and declared_phase == "boom"
        else None
    )
    command_center = build_nas_cycle_command_center(
        snapshot,
        live_transition_evidence=live_transition_evidence,
    )
    technology_cycle = None
    portfolio_replay_lab = None
    if runtime_live_mode:
        command_center["navigation"].insert(
            3,
            {
                "nav_id": "technology_cycle",
                "label_zh": "台美科技循環",
                "path": "/technology-cycle",
                "enabled": True,
            },
        )
        command_center["navigation"].append(
            {
                "nav_id": "prospective_monitoring",
                "label_zh": "前瞻驗證",
                "path": "/prospective-monitoring",
                "enabled": True,
                "planned_phase": 127,
            }
        )
        for nav in command_center["navigation"]:
            if nav["nav_id"] == "historical_replay":
                nav |= {"path": "/historical-replay", "enabled": True, "planned_phase": 124}
            elif nav["nav_id"] == "portfolio_research":
                nav |= {"path": "/portfolio-research", "enabled": True, "planned_phase": 124}
        technology_cycle = build_technology_manufacturing_cycle_view(snapshot)
        portfolio_replay_lab = build_nas_portfolio_replay_lab(
            snapshot,
            live_transition_evidence=live_transition_evidence,
        )
    routes = _route_manifest(contract)
    api_payloads = _api_payloads(
        snapshot=snapshot,
        contract=contract,
        routes=routes,
        role_labels=role_labels,
        command_center=command_center,
        runtime_live_mode=runtime_live_mode,
    )
    html_pages = _html_pages(
        snapshot=snapshot,
        contract=contract,
        routes=routes,
        role_labels=role_labels,
        command_center=command_center,
        runtime_live_mode=runtime_live_mode,
    )
    progress = summarize_product_capability_progress()
    bundle: dict[str, Any] = {
        "phase": "132" if runtime_live_mode else "95",
        "phase_id": 132 if runtime_live_mode else 95,
        "phase_label": contract["phase_label"],
        "artifact_id": (
            "phase132_phase_aware_dashboard_renderer"
            if runtime_live_mode
            else "phase95_nas_service_dashboard_renderer"
        ),
        "artifact_version": contract["version"],
        "output_mode": (
            "research_only_private_nas_live_postgres_dashboard"
            if runtime_live_mode
            else "research_only_private_nas_dashboard_rehearsal"
        ),
        "service_target": contract["service_scope"]["target_runtime"],
        "research_only": True,
        "snapshot_manifest_hash": snapshot["snapshot_manifest_hash"],
        "routes": routes,
        "api_payloads": api_payloads,
        "html_pages": html_pages,
        "command_center": command_center,
        "phase_context_hash": command_center["phase_context_hash"],
        "live_ordered_cycle_evidence": live_transition_evidence,
        "technology_manufacturing_cycle": technology_cycle,
        "portfolio_replay_lab": portfolio_replay_lab,
        "trust_metadata": _trust_metadata(contract=contract, snapshot=snapshot),
        "allowed_uses": contract["allowed_uses"],
        "prohibited_uses": contract["prohibited_uses"],
        "nas_service_dashboard_contract_ready": _contract_ready(contract),
        "nas_service_route_manifest_ready": _routes_ready(routes, contract),
        "nas_service_api_payload_ready": _api_payloads_ready(api_payloads, snapshot),
        "nas_service_html_renderer_ready": _html_pages_ready(html_pages, snapshot),
        "private_nas_service_target_ready": (
            contract["service_scope"]["target_runtime"]
            == "private_nas_dynamic_service"
        ),
        "phase94_snapshot_dependency_ready": _phase94_dependency_ready(),
        "product_capability_rebaseline_recorded": (
            _product_capability_rebaseline_recorded(progress, contract)
        ),
        "route_count": len(routes),
        "api_payload_count": len(api_payloads),
        "html_page_count": len(html_pages),
        "role_card_count": len(snapshot["role_snapshots"]),
        "indicator_snapshot_api_role_count": len(
            api_payloads["indicator_snapshot"]["roles"],
        ),
        "html_role_card_count": _html_marker_count(html_pages, "data-role-card="),
        "html_revised_snapshot_role_count": _html_marker_count(
            html_pages,
            'data-snapshot-status="revised_snapshot_ready"',
        ),
        "html_blocked_role_count": _html_marker_count(
            html_pages,
            'data-snapshot-status="blocked"',
        ),
        "traditional_chinese_role_label_count": len(role_labels),
        "mobile_trust_caveat_count": len(_mobile_trust_caveats()),
        "cycle_command_center_view_model_ready": command_center[
            "cycle_command_center_view_model_ready"
        ],
        "command_center_navigation_item_count": len(command_center["navigation"]),
        "command_center_transition_lane_count": len(
            command_center["transition_lanes"]
        ),
        "command_center_key_indicator_count": len(command_center["key_indicators"]),
        "live_transition_evaluator_connected": command_center[
            "live_transition_evaluator_connected"
        ],
        "frontend_database_access_allowed": False,
        "frontend_api_key_allowed": False,
        "live_server_start_attempt_count": 0,
        "live_db_connection_attempt_count": 1 if runtime_live_mode else 0,
        "postgres_write_attempt_count": 0,
        "live_fetch_attempt_count": 0,
        "repo_output_written_count": 0,
        "public_output_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "current_data_used_to_infer_declared_phase_count": 0,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "role_count_voting_added_count": 0,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "development_next_phase": (
            126
            if runtime_live_mode
            else int(contract["hard_gates"]["development_next_phase"])
        ),
    }
    bundle["prohibited_output_field_count"] = _contains_prohibited_field(bundle)
    bundle["bundle_hash"] = _hash_payload(
        {
            "snapshot_manifest_hash": bundle["snapshot_manifest_hash"],
            "routes": routes,
            "api_payloads": api_payloads,
            "portfolio_replay_lab": portfolio_replay_lab,
            "html_pages": [
                {"page_id": page["page_id"], "html_hash": _hash_payload(page["html"])}
                for page in html_pages
            ],
        },
    )
    bundle["nas_service_dashboard_ready"] = (
        _live_runtime_bundle_ready(bundle)
        if runtime_live_mode
        else _passes(bundle, contract["hard_gates"])
    )
    bundle["result"] = "passed" if bundle["nas_service_dashboard_ready"] else "blocked"
    return bundle


def render_technology_manufacturing_cycle_page(
    view: dict[str, Any],
    *,
    navigation: list[dict[str, Any]],
) -> str:
    """Render the governed Phase122 research extension inside the NAS shell."""

    cards = "".join(_technology_cycle_card(row) for row in view["series_cards"])
    return _html_document(
        title="台美科技製造循環",
        active_nav_id="technology_cycle",
        navigation=navigation,
        body=f"""
        <section class="hero">
          <div>
            <p class="eyebrow">modern supporting research / revised diagnostic</p>
            <h1>台美科技製造循環</h1>
            <p>以官方訂單年增率對照美國科技製造需求與台灣供應鏈接單動能。這一頁協助學習與研究，
            不取代書中 book-core 指標，也不單獨確認榮景結束或衰退。</p>
          </div>
          <p class="research-badge">研究擴充，不是階段結論</p>
        </section>
        <div class="trust-ribbon" aria-label="科技循環資料信任資訊">
          <span><b>資料模式</b> revised diagnostic</span>
          <span><b>主要判讀</b> 年增率</span>
          <span><b>原始資料</b> 名目百萬美元</span>
          <span><b>可用序列</b> {int(view['available_series_count'])}/{int(view['series_count'])}</span>
        </div>
        <section class="content-band">
          <h2>年增率怎麼看</h2>
          <dl class="learning-grid">
            <dt>走高</dt><dd>{escape(str(view['higher_meaning_zh']))}</dd>
            <dt>走低</dt><dd>{escape(str(view['lower_meaning_zh']))}</dd>
            <dt>零軸</dt><dd>{escape(str(view['zero_boundary_zh']))}</dd>
          </dl>
        </section>
        <section class="content-band">
          <div class="section-heading"><div><p class="section-kicker">Official source comparison</p>
          <h2>美國需求與台灣供應鏈</h2></div></div>
          <div class="role-grid">{cards}</div>
        </section>
        <p class="boundary-note">A34HNO 是「其他電子元件製造業」，不是半導體訂單；台灣外銷訂單是接單而非出口實績。
        所有序列均為名目金額，年增率受價格、匯率、基期與修訂影響。</p>
        """,
    )


def render_portfolio_research_page(
    view: dict[str, Any],
    *,
    navigation: list[dict[str, Any]],
) -> str:
    """Render declared-phase-linked research templates without advice wording."""

    cards = "".join(_portfolio_template_card(row) for row in view["template_cards"])
    cycle_rows = "".join(
        _full_cycle_policy_row(row) for row in view["full_cycle_policy_rows"]
    )
    lane_rows = "".join(
        f"<li><strong>{escape(str(lane_id))}</strong>"
        f"<span>{escape(str(row['lane_status']))}</span></li>"
        for lane_id, row in view["live_transition_lane_context"].items()
    )
    sensitivity_rows = "".join(
        _fixed_weight_sensitivity_row(row)
        for row in view["fixed_weight_sensitivity_rows"]
    )
    timeline = view["historical_policy_timeline_summary"]
    return _html_document(
        title="配置研究",
        active_nav_id="portfolio_research",
        navigation=navigation,
        body=f"""
        <section class="command-header">
          <div><p class="eyebrow">Book policy research / private NAS</p>
          <h1>景氣循環配置研究</h1>
          <p class="lede">以 declared {escape(str(view['declared_current_phase_label_zh']))} 與合法下一階段
          {escape(str(view['legal_next_phase_label_zh']))} 為研究脈絡，比較書籍模板與防守替代方案。
          這些比例是 backtest-only 參數，不是你的目前配置建議。</p></div>
          <p class="research-badge">研究模板，不是交易指令</p>
        </section>
        <div class="trust-ribbon" data-phase-context-hash="{escape(str(view['phase_context_hash']))}"><span><b>Declared state</b> {escape(str(view['declared_current_phase_label_zh']))}</span>
        <span><b>Legal next</b> {escape(str(view['legal_next_phase_label_zh']))}</span>
        <span><b>模板數</b> {len(view['template_cards'])}</span><span><b>研究結果</b> {int(view['research_backtest_result_count'])} 組</span></div>
        <section class="content-band"><div class="section-heading"><div><p class="section-kicker">Live transition context</p>
        <h2>目前 evidence 如何限制配置研究</h2></div></div>
        <ul class="lane-evidence-items">{lane_rows}</ul>
        <p class="boundary-note">Watch 不等於 confirmation；即使 confirmation evidence 到位，也不會自動觸發配置動作。</p></section>
        <section class="content-band"><div class="section-heading"><div><p class="section-kicker">Ordered-cycle policy timing</p>
        <h2>四階段轉折與配置研究時機</h2></div></div>
        <p>配置研究不能只看榮景轉衰退。衰退落底可能早於復甦確認，成長進入榮景則是書籍開始去風險研究的重要邊界。</p>
        <div class="role-grid">{cycle_rows}</div></section>
        <section class="content-band"><div class="section-heading"><div><p class="section-kicker">Eight governed templates</p>
        <h2>書籍基準與研究替代方案</h2></div></div><div class="role-grid">{cards}</div></section>
        <section class="content-band"><div class="section-heading"><div><p class="section-kicker">Historical policy research</p>
        <h2>歷史固定權重敏感度</h2></div></div>
        <p>沿用 Phase 125 的 cash-flow-aware strict PIT 結果，比較 100／70／50／30 股票與現金，以及 70／50 股票與長債代理。
        五個情境共有 {int(timeline['monthly_annotation_count'])} 個月度註解；目前 {int(timeline['strict_complete_scenario_count'])} 個情境可計算，
        {int(timeline['explicit_pit_blocked_scenario_count'])} 個因官方早期 PIT 缺口維持 abstain。</p>
        <div class="table-scroll"><table class="research-table"><thead><tr><th>情境</th><th>固定參數</th><th>防守資產</th><th>年化 TWR</th><th>最大回撤</th><th>回撤恢復</th><th>換手／成本</th><th>機會成本</th></tr></thead>
        <tbody>{sensitivity_rows}</tbody></table></div>
        <p class="boundary-note">表格依預註冊參數順序呈現，不排序、不挑選歷史最佳結果，也不回頭調整轉折規則。長債是 DGS10 duration model；所有結果均為 research-only、backtest-only。</p></section>
        <p class="boundary-note">目前已有 {int(view['research_backtest_result_count'])} 組 strict 固定參數 sensitivity，涵蓋 {int(view['quantitative_template_result_count'])} 個具數值參數模板；
        另有 {int(view['evidence_context_only_template_count'])} 個轉折時機模板因書中沒有額外精確權重而刻意不硬造數值。NASDAQ-100 偏重科技，長債為 DGS10 duration model，均不得稱為書籍正式 benchmark。
        research-only、backtest-only，不構成投資建議。</p>
        """,
    )


def render_historical_replay_page(
    view: dict[str, Any],
    *,
    navigation: list[dict[str, Any]],
) -> str:
    """Render an interactive scenario/mode/month input-readiness replay lab."""

    scenarios_json = json.dumps(view["scenario_rows"], ensure_ascii=False).replace("</", "<\\/")
    rows_json = json.dumps(view["monthly_playhead_rows"], ensure_ascii=False).replace("</", "<\\/")
    options = "".join(
        f'<option value="{escape(str(row["scenario_id"]))}">{escape(str(row["title_zh"]))}</option>'
        for row in view["scenario_rows"]
    )
    scenario_cards = "".join(_replay_scenario_card(row) for row in view["scenario_rows"])
    return _html_document(
        title="歷史重播",
        active_nav_id="historical_replay",
        navigation=navigation,
        body=f"""
        <section class="command-header"><div><p class="eyebrow">Historical replay lab / input readiness</p>
        <h1>景氣循環歷史重播</h1><p class="lede">選擇事件、資料模式與月份，檢查當時可得 inputs、缺漏與應觀察角色。
        Phase 125 僅在官方 PIT inputs 完整的月份執行 evidence replay，並以 unitized NAV／XIRR 顯示固定參數 sensitivity；缺資料月份維持 abstain。</p></div>
        <p class="research-badge">研究重播，不是歷史績效結論</p></section>
        <div class="trust-ribbon" data-phase-context-hash="{escape(str(view['phase_context_hash']))}">
        <span><b>Declared</b> {escape(str(view['declared_current_phase_label_zh']))}</span>
        <span><b>Legal next</b> {escape(str(view['legal_next_phase_label_zh']))}</span>
        <span><b>情境</b> {len(view['scenario_rows'])}</span>
        <span><b>月度節點</b> {len(view['monthly_playhead_rows'])}</span>
        <span><b>PIT 完整月</b> {int(view['strict_complete_month_count'])}</span>
        <span><b>PIT Abstain 月</b> {int(view['strict_abstention_month_count'])}</span>
        <span><b>Governed events</b> {int(view['governed_event_count'])}</span>
        <span><b>Backtest 結果</b> {int(view['research_backtest_result_count'])}</span></div>
        <section class="content-band"><div class="section-heading"><div><p class="section-kicker">Data mode boundary</p>
        <h2>Strict PIT 與 revised 比較不混用</h2></div></div>
        <p>「當時可得資料」只讀取可驗證的 release vintage；「修訂後診斷比較」只供研究對照，
        不會回填 PIT 缺口。網路泡沫、GFC 與歐債三個情境仍保留 uncertainty window，避免假完整。</p></section>
        <section class="content-band replay-console" aria-labelledby="replay-console-title">
          <div class="section-heading"><div><p class="section-kicker">Interactive playhead</p><h2 id="replay-console-title">事件月度檢視</h2></div></div>
          <div class="replay-controls">
            <label>歷史事件<select id="replay-scenario">{options}</select></label>
            <label>資料模式<select id="replay-mode"><option value="vintage_as_of">當時可得資料（PIT）</option><option value="revised_declared_comparison_only">修訂後診斷比較</option></select></label>
            <label>月份<input id="replay-playhead" type="range" min="0" max="0" value="0"><output id="replay-date"></output></label>
          </div>
          <article class="replay-readout"><h3 id="replay-title"></h3><p id="replay-focus"></p>
          <dl class="learning-grid"><dt>月份</dt><dd id="replay-asof"></dd><dt>資料狀態</dt><dd id="replay-state"></dd>
          <dt>可用／缺漏</dt><dd id="replay-counts"></dd><dt>Attribution</dt><dd id="replay-roles"></dd>
          <dt>Strict evidence</dt><dd id="replay-evidence"></dd><dt>研究回測</dt><dd id="replay-backtest"></dd>
          <dt>事後週期註解</dt><dd id="replay-reference-state"></dd><dt>書籍政策回放</dt><dd id="replay-policy"></dd>
          <dt>Watch／confirmation</dt><dd id="replay-transition-annotation"></dd><dt>Shock／不確定性</dt><dd id="replay-event-flags"></dd></dl>
          <p id="replay-caveat" class="boundary-note"></p></article>
        </section>
        <section class="content-band"><h2>預註冊歷史事件</h2><div class="role-grid">{scenario_cards}</div></section>
        <script type="application/json" id="replay-scenarios">{scenarios_json}</script>
        <script type="application/json" id="replay-rows">{rows_json}</script>
        <script>{_replay_interaction_script(view['default_scenario_id'], view['default_data_mode'])}</script>
        """,
    )


def _portfolio_template_card(row: dict[str, Any]) -> str:
    levels = row.get("research_parameter_levels_percent", [])
    level_html = "".join(f"<span>{int(value)}%</span>" for value in levels) or "<span>時機研究，不硬造權重</span>"
    relevance = {
        "declared_phase_primary_research": "Declared 階段主要研究",
        "declared_phase_related_research": "Declared 階段相關研究",
        "passive_comparator": "被動比較基準",
        "future_cycle_research": "後續循環研究",
    }.get(str(row["relevance_status"]), str(row["relevance_status"]))
    result_summary = row["research_result_summary"]
    result_html = _result_range_html(result_summary)
    return f"""
    <article class="role-card"><p class="eyebrow">{escape(relevance)}</p>
      <h3>{escape(str(row['description_zh']))}</h3><p class="technical-id">{escape(str(row['template_id']))}</p>
      <p>{escape(str(row['research_parameter_label_zh']))}</p><div class="parameter-levels">{level_html}</div>
      <dl><dt>資產範圍</dt><dd>{escape(' / '.join(row['asset_universe']))}</dd>
      <dt>分類</dt><dd>{escape(str(row['book_or_modern_classification']))}</dd>
      <dt>Strict PIT 研究結果</dt><dd>{result_html}</dd></dl>
      <p class="boundary-note">backtest-only；不是目前配置建議。</p></article>
    """


def _fixed_weight_sensitivity_row(row: dict[str, Any]) -> str:
    defensive = {
        "cash": "現金代理",
        "long_treasury_proxy": "長債代理",
    }.get(str(row["defensive_asset"]), str(row["defensive_asset"]))
    recovery = row["drawdown_recovery_months"]
    recovery_text = "期間內未恢復" if recovery is None else f"{int(recovery)} 個月"
    opportunity = row["missed_recovery_opportunity_cost_percent"]
    opportunity_label = "錯失復甦"
    if opportunity is None:
        opportunity = row["false_derisk_opportunity_cost_percent"]
        opportunity_label = "誤去風險"
    opportunity_text = (
        "不適用"
        if opportunity is None
        else f"{opportunity_label} {float(opportunity):.2f}%"
    )
    metrics = row
    return f"""
    <tr><td>{escape(_scenario_label_zh(str(row['scenario_id'])))}</td>
    <td>股票 {int(row['equity_parameter_percent'])}%／防守 {int(row['defensive_parameter_percent'])}%</td>
    <td>{escape(defensive)}</td>
    <td>{float(metrics['annualized_time_weighted_return']) * 100:.1f}%</td>
    <td>{float(metrics['max_drawdown_on_unitized_nav']) * 100:.1f}%</td>
    <td>{escape(recovery_text)}</td>
    <td>{float(metrics['turnover']):.3f}／{float(metrics['transaction_cost_total']):.0f}</td>
    <td>{escape(opportunity_text)}</td></tr>
    """


def _replay_scenario_card(row: dict[str, Any]) -> str:
    metrics = row["result_metric_range"]
    metric_html = (
        _ratio_range_zh(metrics["annualized_twr"], "年化 TWR")
        + "；"
        + _ratio_range_zh(metrics["max_drawdown"], "最大回撤")
        if metrics["annualized_twr"]
        else "PIT inputs 不完整，依法 abstain"
    )
    event_items = "".join(
        "<li><strong>"
        + escape(str(event["event_type"]))
        + "</strong><span>"
        + escape(str(event["display_label_zh"]))
        + "（"
        + escape(str(event["source_class"]))
        + "）</span></li>"
        for event in row["governed_events"]
    )
    gaps = "、".join(row["pit_gap_series_ids"]) or "無"
    return f"""
    <article class="role-card"><p class="eyebrow">{escape(str(row['scenario_family']))}</p>
    <h3>{escape(str(row['title_zh']))}</h3><p>{escape(str(row['focus_zh']))}</p>
    <dl><dt>期間</dt><dd>{escape(str(row['window_start']))} – {escape(str(row['window_end']))}</dd>
    <dt>月份</dt><dd>{int(row['month_count'])}</dd><dt>Strict replay</dt><dd>{'已執行' if row['strict_evidence_replay_executed'] else '未執行／abstain'}</dd>
    <dt>PIT 狀態</dt><dd>{escape(str(row['pit_status']))}</dd><dt>缺口 series</dt><dd>{escape(gaps)}</dd>
    <dt>固定參數結果</dt><dd>{int(row['research_backtest_result_count'])} 組；{metric_html}</dd></dl>
    <details><summary>事件與 provenance</summary><ul class="lane-evidence-items">{event_items}</ul></details></article>
    """


def _replay_interaction_script(default_scenario: str, default_mode: str) -> str:
    return f"""
    (() => {{
      const scenarios = JSON.parse(document.getElementById('replay-scenarios').textContent);
      const rows = JSON.parse(document.getElementById('replay-rows').textContent);
      const scenarioSelect = document.getElementById('replay-scenario');
      const modeSelect = document.getElementById('replay-mode');
      const playhead = document.getElementById('replay-playhead');
      scenarioSelect.value = {json.dumps(default_scenario)};
      modeSelect.value = {json.dumps(default_mode)};
      function render() {{
        const scenario = scenarios.find(row => row.scenario_id === scenarioSelect.value);
        const timeline = rows.filter(row => row.scenario_id === scenario.scenario_id);
        playhead.max = Math.max(0, timeline.length - 1);
        playhead.value = Math.min(Number(playhead.value), Number(playhead.max));
        const row = timeline[Number(playhead.value)] || timeline[0];
        const strict = modeSelect.value === 'vintage_as_of';
        document.getElementById('replay-title').textContent = scenario.title_zh;
        document.getElementById('replay-focus').textContent = scenario.focus_zh;
        document.getElementById('replay-date').textContent = row.as_of;
        document.getElementById('replay-asof').textContent = row.as_of;
        document.getElementById('replay-state').textContent = strict ? row.strict_input_state : row.revised_comparison_state;
        document.getElementById('replay-counts').textContent = strict ? `${{row.strict_available_series_count}} 可用 / ${{row.strict_missing_series_count}} 缺漏` : '修訂後資料比較介面；尚未執行模型';
        document.getElementById('replay-roles').textContent = row.attribution_role_ids.join('、');
        document.getElementById('replay-evidence').textContent = row.strict_evidence_replay_executed ? Object.entries(row.strict_lane_states).map(([key, value]) => `${{key}}: ${{value}}`).join('；') : '未執行';
        document.getElementById('replay-backtest').textContent = scenario.research_backtest_result_count ? `${{scenario.research_backtest_result_count}} 組固定參數 sensitivity` : '未執行';
        const referenceLabels = {{recession: 'NBER 事後衰退註解', nber_expansion_book_subphase_unclassified: 'NBER expansion；書籍子階段未分類', no_declared_us_recession_reference: '研究窗內無 NBER 美國衰退'}};
        document.getElementById('replay-reference-state').textContent = `${{referenceLabels[row.reference_cycle_state] || row.reference_cycle_state}}${{row.reference_phase_age_month ? `（第 ${{row.reference_phase_age_month}} 月）` : ''}}`;
        document.getElementById('replay-policy').textContent = row.book_policy_requirement_id ? `書籍衰退規則：股票 ${{row.book_policy_equity_parameter_percent}}%（歷史回放）` : '無可安全套用的書籍四階段權重';
        const watches = row.transition_watch_annotations.map(item => `${{item.lane_id}}: ${{item.evidence_state}}`);
        const confirmations = row.transition_confirmation_annotations.map(item => `${{item.lane_id}}: ${{item.evidence_state}}`);
        document.getElementById('replay-transition-annotation').textContent = [...watches, ...confirmations].join('；') || '當月無 strict evidence 註解';
        document.getElementById('replay-event-flags').textContent = [row.shock_annotation_present ? '外生衝擊' : '', row.uncertainty_annotation_present ? 'PIT 不確定窗' : ''].filter(Boolean).join('／') || '無';
        document.getElementById('replay-caveat').textContent = strict && row.strict_abstention_required ? '當月缺少官方 PIT inputs，strict replay 必須 abstain，不能回退 revised。' : (row.strict_evidence_replay_executed ? '已執行 strict evidence replay；不輸出歷史 current phase。回測為固定參數研究，不是動態換倉結果。' : '此模式目前不輸出歷史 phase。');
      }}
      scenarioSelect.addEventListener('change', () => {{ playhead.value = 0; render(); }});
      modeSelect.addEventListener('change', render);
      playhead.addEventListener('input', render);
      render();
    }})();
    """


def _scenario_label_zh(scenario_id: str) -> str:
    return {
        "dotcom_cycle_2000_2003": "網路泡沫",
        "global_financial_crisis_2007_2009": "全球金融危機",
        "covid_recession_2020": "COVID 衰退",
        "euro_debt_slowdown_2011_2012": "歐債壓力",
        "late_cycle_2018_2019": "2018–2019 晚期循環",
    }.get(scenario_id, scenario_id)


def _result_range_html(summary: dict[str, Any]) -> str:
    if not summary["result_count"]:
        return "轉折 evidence context 已接線；書中未另訂此模板的精確權重，故不產生虛構績效"
    return (
        f"{int(summary['result_count'])} 組；"
        + _ratio_range_zh(summary["annualized_twr_range"], "年化 TWR")
        + "；"
        + _ratio_range_zh(summary["max_drawdown_range"], "最大回撤")
    )


def _ratio_range_zh(value_range: dict[str, float] | None, label: str) -> str:
    if not value_range:
        return f"{label} 無"
    minimum = float(value_range["minimum"]) * 100.0
    maximum = float(value_range["maximum"]) * 100.0
    return f"{label} {minimum:.1f}%～{maximum:.1f}%"


def _full_cycle_policy_row(row: dict[str, Any]) -> str:
    priority = {
        "highest": "最高",
        "high": "高",
        "medium": "中",
    }.get(str(row["timing_priority"]), str(row["timing_priority"]))
    return f"""
    <article class="role-card"><p class="eyebrow">{escape(str(row['phase_label_zh']))} → {escape(str(row['legal_next_phase_label_zh']))}</p>
      <h3>{escape(str(row['early_attention_label_zh']))}／{escape(str(row['confirmation_label_zh']))}</h3>
      <p>{escape(str(row['book_policy_context_zh']))}</p>
      <dl><dt>投資時機重要度</dt><dd>{escape(priority)}</dd>
      <dt>早期觀察</dt><dd>{escape(str(row['early_attention_live_status']))}</dd>
      <dt>確認狀態</dt><dd>{escape(str(row['confirmation_live_status']))}</dd></dl>
      <p>{escape(str(row['timing_interpretation_zh']))}</p>
      <p class="boundary-note">只提供配置研究脈絡，不自動產生配置動作。</p></article>
    """


def _technology_cycle_card(row: dict[str, Any]) -> str:
    latest = row.get("latest_yoy_observation")
    latest_text = "尚無足夠同比資料"
    if latest:
        latest_text = f"{latest['value_numeric']}%（{latest['observation_date']}）"
    geography = "美國" if row["geography"] == "US" else "台灣"
    seasonal = "季調" if row["seasonal_adjustment"] == "seasonally_adjusted" else "未季調"
    return f"""
    <article class="role-card" data-technology-series="{escape(str(row['series_id']))}">
      <p class="eyebrow">{escape(geography)} / {escape(seasonal)}</p>
      <h3>{escape(str(row['title_zh']))}</h3>
      <p class="technical-id">{escape(str(row['series_id']))}</p>
      <p class="interpretation-value"><strong>最新年增率</strong><br>{escape(latest_text)}</p>
      <dl>
        <dt>官方來源</dt><dd>{escape(str(row['source_family']))}</dd>
        <dt>原始單位</dt><dd>名目百萬美元</dd>
        <dt>資料風險</dt><dd>{escape(str(row['definition_risk_zh']))}</dd>
      </dl>
      {_chart_details_html(row['chart_payload_detail'])}
    </article>
    """


def summarize_nas_service_dashboard(
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Return compact Phase95 NAS service dashboard readiness fields."""

    bundle = build_nas_service_dashboard_bundle(contract_path=contract_path)
    keys = (
        "phase",
        "phase_id",
        "nas_service_dashboard_contract_ready",
        "nas_service_route_manifest_ready",
        "nas_service_api_payload_ready",
        "nas_service_html_renderer_ready",
        "private_nas_service_target_ready",
        "phase94_snapshot_dependency_ready",
        "product_capability_rebaseline_recorded",
        "route_count",
        "api_payload_count",
        "html_page_count",
        "role_card_count",
        "indicator_snapshot_api_role_count",
        "html_role_card_count",
        "html_revised_snapshot_role_count",
        "html_blocked_role_count",
        "traditional_chinese_role_label_count",
        "mobile_trust_caveat_count",
        "cycle_command_center_view_model_ready",
        "command_center_navigation_item_count",
        "command_center_transition_lane_count",
        "command_center_key_indicator_count",
        "frontend_database_access_allowed",
        "frontend_api_key_allowed",
        "live_server_start_attempt_count",
        "live_db_connection_attempt_count",
        "postgres_write_attempt_count",
        "live_fetch_attempt_count",
        "repo_output_written_count",
        "public_output_count",
        "prohibited_output_field_count",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "current_data_used_to_infer_declared_phase_count",
        "standalone_classifier_added_count",
        "phase_rank_or_score_added_count",
        "role_count_voting_added_count",
        "production_behavior_change_count",
        "semantic_drift_count",
        "development_next_phase",
        "nas_service_dashboard_ready",
        "result",
    )
    return {key: bundle[key] for key in keys} | {
        "nas_service_dashboard_bundle": bundle,
    }


def write_nas_service_dashboard_dry_run(
    bundle: dict[str, Any],
    *,
    output_dir: str | Path,
) -> dict[str, Any]:
    """Write Phase95 route/API/HTML rehearsal artifacts only under /tmp."""

    root = _validated_tmp_output_dir(output_dir)
    api_dir = root / "api"
    indicators_dir = root / "indicators"
    api_dir.mkdir(parents=True, exist_ok=True)
    indicators_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    html_by_page = {page["page_id"]: page["html"] for page in bundle["html_pages"]}
    written.append(_write_text(root / "index.html", html_by_page["overview"]))
    written.append(
        _write_text(indicators_dir / "index.html", html_by_page["indicator_index"]),
    )
    written.append(
        _write_json(api_dir / "indicator-snapshot.json", bundle["api_payloads"]["indicator_snapshot"]),
    )
    written.append(
        _write_json(api_dir / "service-status.json", bundle["api_payloads"]["service_status"]),
    )
    written.append(
        _write_json(api_dir / "indicator-index.json", bundle["api_payloads"]["indicator_index"]),
    )
    return {
        "output_dir": str(root),
        "nas_service_dashboard_dry_run_written": True,
        "written_file_count": len(written),
        "written_files": [str(path) for path in written],
        "dry_run_output_under_tmp_only": True,
        "repo_output_written_count": 0,
        "public_output_count": 0,
    }


def _contract_ready(contract: dict[str, Any]) -> bool:
    scope = contract["service_scope"]
    renderer = contract["renderer_policy"]
    return (
        contract["status"] == "active_research_contract"
        and scope["target_runtime"] == "private_nas_dynamic_service"
        and scope["route_contract_allowed"] is True
        and scope["api_payload_allowed"] is True
        and scope["html_renderer_allowed"] is True
        and scope["live_server_start_allowed_now"] is False
        and scope["live_db_connection_allowed_now"] is False
        and scope["postgres_write_allowed_now"] is False
        and scope["live_fetch_allowed_now"] is False
        and scope["public_output_allowed_now"] is False
        and scope["frontend_database_access_allowed"] is False
        and scope["frontend_api_key_allowed"] is False
        and renderer["dry_run_output_under_tmp_only"] is True
        and renderer["research_only_label_required"] is True
        and renderer["revised_diagnostic_label_required"] is True
        and renderer["pit_accounting_label_required"] is True
    )


def _product_capability_rebaseline_recorded(
    progress: dict[str, Any],
    contract: dict[str, Any],
) -> bool:
    """Keep Phase95 replayable after later phases advance the progress table."""

    phase_id = int(progress["phase_id"])
    if phase_id == 95:
        return (
            progress["phase_label"] == contract["phase_label"]
            and progress["progress_decrease_count"] > 0
            and progress["progress_decrease_without_reason_count"] == 0
        )
    return (
        phase_id > 95
        and progress["product_capability_progress_ready"] is True
        and progress["progress_decrease_without_reason_count"] == 0
    )


def _phase94_dependency_ready() -> bool:
    summary = summarize_nas_indicator_snapshot()
    return (
        summary["result"] == "passed"
        and summary["nas_indicator_snapshot_materialization_ready"] is True
        and summary["role_snapshot_count"] == 39
        and summary["service_view_model_ready"] is True
    )


def _route_manifest(contract: dict[str, Any]) -> list[dict[str, Any]]:
    routes = []
    for row in contract["route_policy"]["routes"]:
        routes.append(
            {
                "route_id": row["route_id"],
                "path": row["path"],
                "method": row["method"],
                "output_kind": row["output_kind"],
                "title_zh": row["title_zh"],
                "private_nas_only": True,
                "requires_server_side_snapshot": True,
                "frontend_database_access_allowed": False,
                "frontend_api_key_allowed": False,
            },
        )
    return routes


def _api_payloads(
    *,
    snapshot: dict[str, Any],
    contract: dict[str, Any],
    routes: list[dict[str, Any]],
    role_labels: dict[str, str],
    command_center: dict[str, Any],
    runtime_live_mode: bool,
) -> dict[str, Any]:
    roles = [
        _role_api_row(row, display_name_zh=role_labels[row["role_id"]])
        for row in snapshot["role_snapshots"]
    ]
    return {
        "indicator_snapshot": {
            "payload_id": "nas_indicator_snapshot_api_v1",
            "path": "/api/indicator-snapshot.json",
            "output_mode": "research_only_private_nas_api",
            "snapshot_manifest_hash": snapshot["snapshot_manifest_hash"],
            "data_mode": (
                "live_postgres_revised_diagnostic"
                if runtime_live_mode
                else "revised_diagnostic_with_pit_availability_accounting"
            ),
            "role_count": len(roles),
            "roles": roles,
            "allowed_uses": contract["allowed_uses"],
            "prohibited_uses": contract["prohibited_uses"],
            "trust_metadata": snapshot["trust_metadata"],
        },
        "service_status": {
            "payload_id": "nas_service_status_api_v1",
            "path": "/api/service-status.json",
            "service_target": contract["service_scope"]["target_runtime"],
            "route_count": len(routes),
            "live_db_connection_attempted": runtime_live_mode,
            "live_db_connected": runtime_live_mode,
            "dashboard_data_source": (
                "live_postgres_read_only"
                if runtime_live_mode
                else "bundled_rehearsal_snapshot"
            ),
            "snapshot_as_of": snapshot.get("snapshot_as_of"),
            "database_latest_observation_date": snapshot.get(
                "database_latest_observation_date",
            ),
            "refresh_status": snapshot.get("refresh_status", {}),
            "source_refresh_health_status": snapshot.get(
                "source_refresh_health_status",
                "not_configured",
            ),
            "declared_cycle_state": snapshot.get("declared_cycle_state", {}),
            "phase_context_hash": command_center["phase_context_hash"],
            "active_evaluator_mode": command_center["active_evaluator_mode"],
            "live_transition_evaluator_connected": command_center[
                "live_transition_evaluator_connected"
            ],
            "transition_lane_count": len(command_center["transition_lanes"]),
            "watch_confirmation_separated": command_center["trust_metadata"][
                "watch_confirmation_separated"
            ],
            "postgres_write_attempted": False,
            "live_fetch_attempted": False,
            "frontend_database_access_allowed": False,
            "frontend_api_key_allowed": False,
            "research_only": True,
            "strict_point_in_time_result": False,
            "candidate_phase_selection_enabled": False,
            "current_phase_inference_enabled": False,
        },
        "indicator_index": {
            "payload_id": "nas_indicator_index_api_v1",
            "path": "/api/indicator-index.json",
            "role_count": len(roles),
            "roles": [
                {
                    "role_id": row["role_id"],
                    "display_name_zh": row["display_name_zh"],
                    "phase_or_layer": row["phase_or_layer"],
                    "major_group_id": row["major_group_id"],
                    "snapshot_status": row["snapshot_status"],
                    "pit_backfill_status": row["pit_backfill_status"],
                    "freshness_status": row.get("freshness_status", "unavailable"),
                    "chart_available": row.get("chart_payload_detail", {}).get(
                        "chart_available",
                        False,
                    ),
                    "detail_anchor": f"#role-{row['role_id']}",
                }
                for row in roles
            ],
        },
    }


def _role_api_row(
    row: dict[str, Any],
    *,
    display_name_zh: str,
) -> dict[str, Any]:
    latest = row["latest_revised_observations"]
    latest_display = latest[0] if latest else {}
    latest_value = latest_display.get("value_numeric")
    if latest_value is None:
        latest_value = latest_display.get("value_text")
    return {
        "role_id": row["role_id"],
        "display_name_zh": display_name_zh,
        "phase_or_layer": row["phase_or_layer"],
        "major_group_id": row["major_group_id"],
        "official_series_ids": row["official_series_ids"],
        "snapshot_status": row["snapshot_status"],
        "data_mode": row["data_mode"],
        "latest_revised_observation_count": len(latest),
        "latest_observation_date": latest_display.get("observation_date"),
        "latest_value": latest_value,
        "latest_value_text": latest_display.get("value_text"),
        "latest_unit": latest_display.get("unit"),
        "freshness_status": row.get("freshness_status", "unavailable"),
        "source_mode": row.get("source_mode", "bundled_rehearsal_snapshot"),
        "source_lineage": row.get("source_lineage", []),
        "learning_semantics": row.get("learning_semantics", {}),
        "latest_interpretation_observations": row.get(
            "latest_interpretation_observations",
            [],
        ),
        "chart_payload_detail": row.get("chart_payload_detail", {}),
        "pit_backfill_status": row["pit_backfill_status"],
        "blocked_reason_codes": row["blocked_reason_codes"],
        "strict_point_in_time_result": False,
        "candidate_selection_eligible": False,
        "formal_current_output_allowed": False,
    }


def _html_pages(
    *,
    snapshot: dict[str, Any],
    contract: dict[str, Any],
    routes: list[dict[str, Any]],
    role_labels: dict[str, str],
    command_center: dict[str, Any],
    runtime_live_mode: bool,
) -> list[dict[str, Any]]:
    return [
        {
            "page_id": "overview",
            "path": "/",
            "title_zh": "NAS 私有研究儀表板",
            "html": _overview_html(
                snapshot=snapshot,
                contract=contract,
                routes=routes,
                role_labels=role_labels,
                command_center=command_center,
                runtime_live_mode=runtime_live_mode,
            ),
        },
        {
            "page_id": "indicator_index",
            "path": "/indicators",
            "title_zh": "指標總覽",
            "html": _indicator_index_html(
                snapshot=snapshot,
                contract=contract,
                role_labels=role_labels,
                command_center=command_center,
                runtime_live_mode=runtime_live_mode,
            ),
        },
    ]


def _overview_html(
    *,
    snapshot: dict[str, Any],
    contract: dict[str, Any],
    routes: list[dict[str, Any]],
    role_labels: dict[str, str],
    command_center: dict[str, Any],
    runtime_live_mode: bool,
) -> str:
    del routes, role_labels
    return _html_document(
        title="景氣循環指揮中心",
        active_nav_id="overview",
        navigation=command_center["navigation"],
        body=f"""
        <section class="command-header">
          <div>
            <p class="eyebrow">{escape(_dashboard_eyebrow(runtime_live_mode))}</p>
            <h1>景氣循環指揮中心</h1>
            <p class="lede">{escape(_dashboard_intro(runtime_live_mode))}</p>
          </div>
          <p class="research-badge">Declared {escape(str(command_center['declared_state']['declared_current_phase_label_zh']))} / revised diagnostic</p>
        </section>
        {_command_center_trust_ribbon(command_center)}
        <section class="cycle-command" aria-labelledby="cycle-command-heading">
          <div class="section-heading">
            <div>
              <p class="section-kicker">Ordered cycle state</p>
              <h2 id="cycle-command-heading">目前研究位置</h2>
            </div>
            <a class="text-link" href="/cycle-state">檢視階段治理</a>
          </div>
          {_declared_cycle_command_html(command_center)}
          {_cycle_order_html(command_center)}
        </section>
        <section id="transition-monitor" class="content-band" aria-labelledby="transition-heading">
          <div class="section-heading">
            <div>
              <p class="section-kicker">{escape(str(command_center['declared_state']['declared_current_phase_label_zh']))} → {escape(str(command_center['declared_state']['legal_next_phase_label_zh']))}</p>
              <h2 id="transition-heading">轉折風險雷達</h2>
            </div>
            <span class="status-note">{escape(str(command_center['active_evaluator_mode']))}；研究判讀，不是 declared state 改判</span>
          </div>
          <p class="section-intro">{escape(str(command_center['transition_heading_zh']))}。{escape(str(command_center['learning_intro_zh']))} Watch 不會自動升級成 confirmation，任何 evidence 也不會改寫 declared state。</p>
          {_transition_lane_html(command_center)}
        </section>
        <section class="content-band" aria-labelledby="indicator-heading">
          <div class="section-heading">
            <div>
              <p class="section-kicker">Transition-critical indicators</p>
              <h2 id="indicator-heading">本期優先觀察</h2>
            </div>
            <a class="text-link" href="/indicators">查看 39 個指標</a>
          </div>
          {_key_indicator_html(command_center)}
        </section>
        <section class="content-band" aria-labelledby="health-heading">
          <div class="section-heading">
            <div>
              <p class="section-kicker">Data trust</p>
              <h2 id="health-heading">資料健康度</h2>
            </div>
            <a class="text-link" href="/source-operations">查看來源維運</a>
          </div>
          {_command_center_health_html(command_center)}
        </section>
        <section class="roadmap-band" aria-labelledby="roadmap-heading">
          <p class="section-kicker">Next product surfaces</p>
          <h2 id="roadmap-heading">接下來會接進這個工作台</h2>
          <div class="roadmap-grid">
            <article id="portfolio-research-roadmap"><strong>配置研究</strong><span>Phase 124：declared phase 對應書籍研究模板</span></article>
            <article id="historical-replay-roadmap"><strong>歷史重播</strong><span>Phase 124：事件選擇器與月度 playhead</span></article>
            <article><strong>指標學習</strong><span>Phase 121：圖表、書中意涵與資料血緣</span></article>
          </div>
        </section>
        """,
    )


def _indicator_index_html(
    *,
    snapshot: dict[str, Any],
    contract: dict[str, Any],
    role_labels: dict[str, str],
    command_center: dict[str, Any],
    runtime_live_mode: bool,
) -> str:
    priority_ids = list(command_center["phase_context"]["priority_role_ids"])
    priority_order = {role_id: index for index, role_id in enumerate(priority_ids)}
    declared_phase = command_center["declared_state"]["declared_current_phase"]
    ordered_rows = sorted(
        snapshot["role_snapshots"],
        key=lambda row: (
            0 if row["role_id"] in priority_order else 1,
            priority_order.get(row["role_id"], 999),
            0 if row["phase_or_layer"] == declared_phase else 1,
            str(row["role_id"]),
        ),
    )
    cards = "\n".join(
        _role_card(
            row,
            display_name_zh=role_labels[row["role_id"]],
            is_priority=row["role_id"] in priority_order,
        )
        for row in ordered_rows
    )
    caveats = "\n".join(
        f"<li>{escape(item)}</li>" for item in _mobile_trust_caveats()
    )
    return _html_document(
        title="指標總覽",
        active_nav_id="indicators",
        navigation=command_center["navigation"],
        body=f"""
        <section class="hero">
          <p class="eyebrow">research-only / {escape(_dashboard_data_source_label(runtime_live_mode))}</p>
          <h1>總經指標快照</h1>
          <p>每個卡片分開顯示官方原始值與書籍導向的主要判讀值，並說明數值升降在
          declared {escape(str(command_center['declared_state']['declared_current_phase_label_zh']))} 與
          {escape(str(command_center['declared_state']['legal_next_phase_label_zh']))}轉折觀察中的意義。
          {escape(str(command_center['learning_intro_zh']))} 可展開查看今年以來、過去 1 年與過去 5 年走勢；
          blocked 不會被當作 neutral，也不會被補零。</p>
        </section>
        {_command_center_trust_ribbon(command_center)}
        <section>
          <h2>資料邊界</h2>
          <ul>{caveats}</ul>
        </section>
        <section class="role-grid">{cards}</section>
        """,
    )


def _command_center_trust_ribbon(command_center: dict[str, Any]) -> str:
    health = command_center["data_health"]
    return f"""
    <div class="trust-ribbon" aria-label="資料信任資訊"
      data-phase-context-hash="{escape(str(command_center['phase_context_hash']))}">
      <span><b>Declared</b> {escape(str(command_center['declared_state']['declared_current_phase_label_zh']))}</span>
      <span><b>Legal next</b> {escape(str(command_center['declared_state']['legal_next_phase_label_zh']))}</span>
      <span><b>資料模式</b> revised diagnostic</span>
      <span><b>資料截至</b> {escape(str(health.get('database_latest_observation_date') or '尚無'))}</span>
      <span><b>可用角色</b> {int(health['available_role_count'])}/{int(health['role_count'])}</span>
      <span><b>轉折判讀</b> {"live evaluator 已接線" if command_center['live_transition_evaluator_connected'] else "尚未接通即時 evaluator"}</span>
    </div>
    """


def _declared_cycle_command_html(command_center: dict[str, Any]) -> str:
    state = command_center["declared_state"]
    age = state.get("declared_phase_age_days")
    age_range = state.get("declared_phase_age_range_days")
    if age is not None:
        age_display = f"約 {int(age)} 天"
    elif age_range:
        age_display = (
            f"約 {int(age_range['minimum_days'])} 至 "
            f"{int(age_range['maximum_days'])} 天"
        )
    else:
        age_display = "尚待使用者確認起始日"
    return f"""
    <div class="phase-command-grid">
      <article class="phase-primary">
        <span class="phase-label">Declared current cycle state</span>
        <strong>{escape(str(state['declared_current_phase_label_zh']))}</strong>
        <p>由使用者／治理 registry 宣告，並非最新資料分類結果。</p>
      </article>
      <article class="transition-primary">
        <span class="phase-label">Legal next transition</span>
        <strong>{escape(str(state['declared_current_phase_label_zh']))} → {escape(str(state['legal_next_phase_label_zh']))}</strong>
        <p>系統只監測合法下一階段，不在四個階段間重新投票。</p>
      </article>
      <article class="phase-context">
        <span class="phase-label">Declared phase age</span>
        <strong>{escape(age_display)}</strong>
        <p>缺少確認日期時不製造精確階段年齡。</p>
      </article>
    </div>
    """


def _cycle_order_html(command_center: dict[str, Any]) -> str:
    items = []
    for row in command_center["cycle_order"]:
        classes = ["cycle-step"]
        state = "循環階段"
        if row["is_declared"]:
            classes.append("is-declared")
            state = "目前宣告"
        elif row["is_legal_next"]:
            classes.append("is-next")
            state = "合法下一階段"
        items.append(
            f'<li class="{" ".join(classes)}"><strong>{escape(row["label_zh"])}</strong>'
            f"<span>{escape(state)}</span></li>"
        )
    return f'<ol class="cycle-order" aria-label="合法景氣循環順序">{"".join(items)}</ol>'


def _transition_lane_html(command_center: dict[str, Any]) -> str:
    cards = []
    for lane in command_center["transition_lanes"]:
        status_class = _lane_status_class(lane)
        role_links = "".join(
            f'<a href="/indicators#role-{escape(role_id)}">{escape(role_id)}</a>'
            for role_id in lane["required_role_ids"]
        )
        lane_label = {
            "continuation_context": "延續脈絡",
            "transition_watch": "風險觀察",
            "transition_confirmation": "轉折確認",
        }.get(lane["lane_type"], lane["lane_type"])
        evidence_html = _lane_evidence_items_html(lane)
        why_html = "".join(
            f"<li>{escape(str(reason))}</li>"
            for reason in lane.get("why_not_confirmation", [])
        )
        counts_html = ""
        if command_center["live_transition_evaluator_connected"]:
            counts_html = (
                '<dl class="lane-evidence-counts">'
                f"<dt>支持</dt><dd>{int(lane.get('supportive_evidence_count', 0))}</dd>"
                f"<dt>反對</dt><dd>{int(lane.get('contradictory_evidence_count', 0))}</dd>"
                f"<dt>Mixed</dt><dd>{int(lane.get('mixed_evidence_count', 0))}</dd>"
                f"<dt>Abstain</dt><dd>{int(lane.get('abstained_evidence_count', 0))}</dd>"
                "</dl>"
            )
        cards.append(
            f"""
            <article class="lane-card" data-transition-lane="{escape(lane['lane_id'])}">
              <div class="lane-card-head">
                <span class="lane-type">{escape(lane_label)}</span>
                <span class="lane-input-count">{int(lane['available_input_count'])}/{int(lane['required_role_count'])} 輸入</span>
              </div>
              <h3>{escape(lane['title_zh'])}</h3>
              <p>{escape(lane['purpose_zh'])}</p>
              <p class="lane-status {status_class}">{escape(lane['display_status_zh'])}</p>
              {counts_html}
              {evidence_html}
              {f'<details class="why-not"><summary>為何尚未確認／不能改判</summary><ul>{why_html}</ul></details>' if why_html else ''}
              <div class="lane-role-links">{role_links}</div>
            </article>
            """
        )
    return f'<div class="lane-grid">{"".join(cards)}</div>'


def _lane_status_class(lane: dict[str, Any]) -> str:
    status = str(lane.get("evidence_evaluation_status", ""))
    if "supportive" in status:
        return "status-supportive"
    if "contradictory" in status or "mixed" in status:
        return "status-warning"
    if lane["missing_input_count"] or "abstention" in status or "incomplete" in status:
        return "status-missing"
    return "status-pending"


def _lane_evidence_items_html(lane: dict[str, Any]) -> str:
    items = []
    state_labels = {
        "supportive": "支持",
        "contradictory": "反對",
        "mixed": "Mixed",
        "abstained": "Abstain",
        "neutral": "中性",
    }
    for item in lane.get("evidence_items", []):
        state = str(item["lane_evidence_state"])
        dates = ", ".join(
            sorted(set(item.get("latest_transformed_observation_dates", {}).values()))
        ) or "尚無"
        reason = item.get("abstention_reason")
        reason_html = (
            f'<span class="evidence-reason">{escape(str(reason))}</span>'
            if reason
            else ""
        )
        items.append(
            f'<li data-evidence-state="{escape(state)}">'
            f'<strong>{escape(str(item.get("display_name_zh", item["role_id"])))}</strong>'
            f'<span class="evidence-state">{escape(state_labels.get(state, state))}</span>'
            f'<span>{escape(dates)}</span>{reason_html}</li>'
        )
    return f'<ul class="lane-evidence-items">{"".join(items)}</ul>' if items else ""


def _key_indicator_html(command_center: dict[str, Any]) -> str:
    rows = []
    for indicator in command_center["key_indicators"]:
        value = indicator.get("latest_value")
        value_display = "尚無資料" if value is None else str(value)
        if value is not None and indicator.get("latest_unit"):
            value_display = f"{value_display} {indicator['latest_unit']}"
        rows.append(
            f"""
            <a class="priority-indicator" href="{escape(indicator['detail_path'])}">
              <span class="indicator-name">{escape(indicator['display_name_zh'])}</span>
              <strong>{escape(value_display)}</strong>
              <span>{escape(str(indicator.get('latest_observation_date') or '尚無日期'))}</span>
              <span>{escape(_freshness_label_zh(indicator['freshness_status']))}</span>
            </a>
            """
        )
    return f'<div class="priority-indicator-list">{"".join(rows)}</div>'


def _command_center_health_html(command_center: dict[str, Any]) -> str:
    health = command_center["data_health"]
    health_label = {
        "healthy": "來源更新正常",
        "degraded": "來源更新降級",
        "baseline_loaded_waiting_for_scheduled_refresh": "已有基準，等待排程",
        "unavailable": "來源資料不可用",
    }.get(health["source_refresh_health_status"], health["source_refresh_health_status"])
    return f"""
    <div class="health-grid">
      <article><span>來源狀態</span><strong>{escape(health_label)}</strong></article>
      <article><span>新鮮角色</span><strong>{int(health['fresh_role_count'])}</strong></article>
      <article><span>過期角色</span><strong>{int(health['stale_role_count'])}</strong></article>
      <article><span>可用圖表</span><strong>{int(health['chart_available_role_count'])}/{int(health['role_count'])}</strong></article>
      <article><span>最近同步</span><strong>{escape(str(health.get('last_completed_at_utc') or '尚無'))}</strong></article>
      <article><span>下次排程</span><strong>{escape(str(health.get('next_scheduled_at_utc') or '尚未排程'))}</strong></article>
    </div>
    <p class="boundary-note">目前首頁顯示 revised research data。資料健康不等於景氣證據，raw value 也不會自動升級成 watch 或 confirmation。</p>
    """


def _role_card(
    row: dict[str, Any], *, display_name_zh: str, is_priority: bool = False
) -> str:
    status = row["snapshot_status"]
    latest = row["latest_revised_observations"]
    latest_display = latest[0] if latest else {}
    observation_date = latest_display.get("observation_date") or "尚無數值"
    value_text = latest_display.get("value_numeric")
    if value_text is None:
        value_text = latest_display.get("value_text") or "unavailable"
    unit = latest_display.get("unit") or "未提供"
    blocked = ", ".join(row["blocked_reason_codes"]) or "none"
    freshness = _freshness_label_zh(row.get("freshness_status", "unavailable"))
    chart_html = _chart_details_html(row.get("chart_payload_detail", {}))
    learning = row.get("learning_semantics", {})
    interpreted = list(row.get("latest_interpretation_observations", []))
    interpretation_html = _latest_interpretation_html(interpreted, learning)
    learning_html = _learning_semantics_html(learning)
    return f"""
    <article id="role-{escape(row['role_id'])}" class="role-card"
      data-role-card="true" data-snapshot-status="{escape(status)}"
      data-phase-priority="{str(is_priority).lower()}">
      {"<p class='eyebrow'>本階段優先觀察</p>" if is_priority else ""}
      <h3>{escape(display_name_zh)}</h3>
      <p class="technical-id">技術識別：<code>{escape(row['role_id'])}</code></p>
      <p class="meta">{escape(row['phase_or_layer'])} / {escape(row['major_group_id'])}</p>
      <dl>
        <dt>快照狀態</dt><dd>{escape(status)}</dd>
        <dt>最新 revised 日期</dt><dd>{escape(str(observation_date))}</dd>
        <dt>官方原始值</dt><dd>{escape(str(value_text))}</dd>
        <dt>官方原始單位</dt><dd>{escape(str(unit))}</dd>
        <dt>主要判讀方式</dt><dd>{escape(str(learning.get('transform_label_zh') or '尚未定義'))}</dd>
        <dt>資料新鮮度</dt><dd>{escape(freshness)}</dd>
        <dt>PIT 補齊</dt><dd>{escape(row['pit_backfill_status'])}</dd>
        <dt>缺口</dt><dd>{escape(blocked)}</dd>
      </dl>
      {interpretation_html}
      {learning_html}
      {chart_html}
    </article>
    """


def _role_sample(row: dict[str, Any], *, display_name_zh: str) -> str:
    return (
        f"<li><a href=\"/indicators#role-{escape(row['role_id'])}\">"
        f"{escape(display_name_zh)}</a> - {escape(row['snapshot_status'])}</li>"
    )


def _dashboard_eyebrow(runtime_live_mode: bool) -> str:
    if runtime_live_mode:
        return "私人 NAS / PostgreSQL revised research data"
    return "Phase95 / private NAS dynamic service rehearsal"


def _dashboard_heading(runtime_live_mode: bool) -> str:
    if runtime_live_mode:
        return "景氣循環私人研究儀表板"
    return "NAS 私有研究儀表板資料路由"


def _dashboard_intro(runtime_live_mode: bool) -> str:
    if runtime_live_mode:
        return (
            "此頁由 NAS PostgreSQL 以唯讀模式提供最新 revised 歷史資料。"
            "它是研究用 diagnostic surface，不是正式目前景氣判斷，也不是投資建議。"
        )
    return (
        "此頁使用 Phase94 指標快照建立 server-side HTML 與 JSON API rehearsal。"
        "它是研究用 revised diagnostic surface，不是正式目前景氣判斷，也不是投資建議。"
    )


def _dashboard_data_source_label(runtime_live_mode: bool) -> str:
    return "PostgreSQL revised diagnostic" if runtime_live_mode else "revised diagnostic"


def _refresh_status_html(snapshot: dict[str, Any]) -> str:
    status = snapshot.get("refresh_status", {})
    release = snapshot.get("source_release_diagnostics", {})
    state_labels = {
        "not_started": "尚未開始定期更新",
        "scheduled": "已排程",
        "running": "更新執行中",
        "succeeded": "最近更新成功",
        "failed": "最近更新失敗",
    }
    health_labels = {
        "healthy": "正常",
        "degraded": "最近更新失敗，沿用既有資料",
        "baseline_loaded_waiting_for_scheduled_refresh": "已有基準資料，等待排程更新",
        "unavailable": "無可用來源資料",
    }
    state = str(status.get("refresh_state", "not_started"))
    health = str(snapshot.get("source_refresh_health_status", "unknown"))
    return f"""
    <section aria-labelledby="refresh-status-heading">
      <h2 id="refresh-status-heading">官方資料更新狀態</h2>
      <div class="summary-grid" data-source-refresh-status="{escape(state)}">
        <article><strong>{escape(state_labels.get(state, state))}</strong><span>排程狀態</span></article>
        <article><strong>{escape(str(status.get('last_completed_at_utc') or '尚無'))}</strong><span>上次完成</span></article>
        <article><strong>{escape(str(status.get('next_scheduled_at_utc') or '尚未排程'))}</strong><span>下次預定</span></article>
        <article><strong>{int(status.get('completed_series_count', 0))}/{int(status.get('requested_series_count', 0))}</strong><span>完成來源</span></article>
      </div>
      <p class="meta">來源健康：{escape(health_labels.get(health, health))}；此更新只代表 revised 資料同步，不代表景氣階段確認。</p>
      <p class="meta">官方發布家族：{int(release.get('release_family_count', 0))}；
      待更新或需查核：{int(release.get('family_due_or_missing_refresh_count', 0))}；
      有失敗原因的序列：{int(release.get('series_with_failure_reason_count', 0))}。</p>
      <p><a href="/source-operations">查看官方發布日曆與更新失敗明細</a></p>
    </section>
    """


def _declared_cycle_state_html(snapshot: dict[str, Any]) -> str:
    state = snapshot.get("declared_cycle_state", {})
    phase = str(state.get("declared_current_phase_label_zh", "榮景"))
    next_phase = str(state.get("legal_next_phase_label_zh", "衰退"))
    start = str(state.get("declared_phase_start_display_zh", "尚待使用者確認"))
    age = state.get("declared_phase_age_days")
    age_range = state.get("declared_phase_age_range_days")
    if age is not None:
        age_display = f"約 {age} 天"
    elif age_range:
        age_display = (
            f"約 {age_range['minimum_days']} 至 {age_range['maximum_days']} 天"
        )
    else:
        age_display = "未知，需使用者確認"
    return f"""
    <section aria-labelledby="declared-cycle-state-heading"
      data-declared-cycle-state="true">
      <h2 id="declared-cycle-state-heading">目前宣告景氣狀態</h2>
      <div class="summary-grid">
        <article><strong>{escape(phase)}</strong><span>宣告階段</span></article>
        <article><strong>{escape(next_phase)}</strong><span>合法下一階段</span></article>
        <article><strong>{escape(start)}</strong><span>榮景起始</span></article>
        <article><strong>{escape(age_display)}</strong><span>階段年齡</span></article>
      </div>
      <p class="meta">這是使用者／治理登錄的研究背景，不是由最新資料推論的目前階段。</p>
      <p><a href="/cycle-state">檢視或確認榮景起始資訊</a></p>
    </section>
    """


def _freshness_label_zh(status: str) -> str:
    return {
        "fresh": "在新鮮度期限內",
        "stale": "已超過新鮮度期限",
        "mixed": "部分序列已過期或頻率不同",
        "unknown_frequency": "頻率未識別，無法判定",
        "unavailable": "無可用資料",
    }.get(status, status)


def _chart_details_html(chart: dict[str, Any]) -> str:
    series_charts = list(chart.get("series_charts", []))
    if not chart.get("chart_available") or not series_charts:
        return "<p class=\"chart-meta\">目前沒有可繪製的 revised 歷史數值。</p>"
    panels = "".join(
        _chart_period_panel(series, period)
        for series in series_charts
        for period in series.get("periods", [])
    )
    return (
        "<details><summary>查看今年／過去 1 年／過去 5 年走勢（主要判讀值）</summary>"
        f"<div class=\"chart-grid\">{panels}</div></details>"
    )


def _chart_period_panel(series: dict[str, Any], period: dict[str, Any]) -> str:
    title = (
        f"{series.get('interpretation_name_zh', series.get('series_id', 'series'))}"
        f" · {series.get('series_id', 'series')} · {period.get('label', '')}"
    )
    unit = str(series.get("interpretation_unit_zh") or series.get("unit") or "")
    points = list(period.get("points", []))
    if period.get("chart_status") != "available" or not points:
        return (
            "<section class=\"chart-panel\">"
            f"<h4>{escape(title)}</h4>"
            "<p class=\"chart-meta\">此期間沒有可用數值。</p>"
            "</section>"
        )
    svg, rendered_count = _sparkline_svg(points)
    first = points[0]
    last = points[-1]
    return (
        "<section class=\"chart-panel\">"
        f"<h4>{escape(title)}</h4>"
        '<div class="chart-interactive-wrap">'
        f"{svg}"
        '<output class="chart-tooltip" aria-live="polite" hidden></output>'
        "</div>"
        '<p class="chart-hint">移動游標或觸碰走勢線，可查看日期與數值；鍵盤可用左右方向鍵。</p>'
        f'<p class="chart-meta">判讀方式：{escape(str(series.get("display_transform_label_zh") or ""))}；'
        f'顯示單位：{escape(unit)}；原始單位：{escape(str(series.get("source_unit") or "未提供"))}</p>'
        f"<p class=\"chart-meta\">{escape(str(first['date']))}："
        f"{escape(str(first['value']))} → {escape(str(last['date']))}："
        f"{escape(str(last['value']))}；資料點 {len(points)}，繪圖點 {rendered_count}</p>"
        "</section>"
    )


def _latest_interpretation_html(
    rows: list[dict[str, Any]],
    learning: dict[str, Any],
) -> str:
    if not rows:
        return (
            '<p class="interpretation-value is-unavailable">主要判讀值：'
            f'{escape(str(learning.get("interpretation_name_zh") or "尚無"))}目前不可用；不填零。</p>'
        )
    items = "".join(
        "<li>"
        f"{escape(', '.join(str(item) for item in row.get('source_series_ids', [])))}："
        f"{escape(str(row.get('value_numeric')))} {escape(str(row.get('unit') or ''))}"
        f"（{escape(str(row.get('observation_date')))}）"
        "</li>"
        for row in rows
    )
    return (
        '<div class="interpretation-value"><strong>最新主要判讀值</strong>'
        f"<ul>{items}</ul></div>"
    )


def _learning_semantics_html(learning: dict[str, Any]) -> str:
    if not learning:
        return ""
    return f"""
    <div class="learning-panel" data-indicator-learning-semantics="true">
      <h4>如何判讀這個指標</h4>
      <dl class="learning-grid">
        <dt>升高／走強</dt><dd>{escape(str(learning['high_or_rising_meaning_zh']))}</dd>
        <dt>降低／走弱</dt><dd>{escape(str(learning['low_or_falling_meaning_zh']))}</dd>
        <dt>當下榮景脈絡</dt><dd>{escape(str(learning['declared_boom_context_zh']))}</dd>
        <dt>判讀限制</dt><dd>{escape(str(learning['caveat_zh']))}</dd>
      </dl>
    </div>
    """


def _sparkline_svg(points: list[dict[str, Any]]) -> tuple[str, int]:
    rendered = _downsample_points(points, MAX_RENDERED_SVG_POINTS)
    values = [float(point["value"]) for point in rendered]
    minimum = min(values)
    maximum = max(values)
    span = maximum - minimum
    width = 300.0
    height = 80.0
    padding = 5.0
    coordinates: list[str] = []
    interactive_points: list[dict[str, Any]] = []
    for index, value in enumerate(values):
        x = (
            padding
            if len(values) == 1
            else padding + (width - 2 * padding) * index / (len(values) - 1)
        )
        normalized = 0.5 if span == 0 else (value - minimum) / span
        y = height - padding - (height - 2 * padding) * normalized
        coordinates.append(f"{x:.2f},{y:.2f}")
        interactive_points.append(
            {
                "date": rendered[index]["date"],
                "value": value,
                "x": round(x, 2),
                "y": round(y, 2),
            },
        )
    encoded_points = escape(
        json.dumps(
            interactive_points,
            ensure_ascii=False,
            separators=(",", ":"),
        ),
        quote=True,
    )
    svg = (
        '<svg class="interactive-chart" viewBox="0 0 300 80" role="img" '
        'aria-label="指標歷史走勢；可查看日期與數值" tabindex="0" '
        f'data-chart-points="{encoded_points}">'
        '<line class="chart-axis" x1="5" y1="75" x2="295" y2="75"></line>'
        f'<polyline class="chart-line" points="{" ".join(coordinates)}"></polyline>'
        '<line class="chart-crosshair" x1="0" y1="5" x2="0" y2="75" '
        'visibility="hidden"></line>'
        '<circle class="chart-marker" cx="0" cy="0" r="3.5" '
        'visibility="hidden"></circle>'
        "</svg>"
    )
    return svg, len(rendered)


def _downsample_points(
    points: list[dict[str, Any]],
    limit: int,
) -> list[dict[str, Any]]:
    if len(points) <= limit:
        return points
    indexes = {
        round(index * (len(points) - 1) / (limit - 1))
        for index in range(limit)
    }
    return [points[index] for index in sorted(indexes)]


def _html_document(
    *,
    title: str,
    body: str,
    active_nav_id: str,
    navigation: list[dict[str, Any]],
) -> str:
    desktop_navigation = _navigation_html(navigation, active_nav_id=active_nav_id)
    mobile_navigation = _mobile_navigation_html(
        navigation,
        active_nav_id=active_nav_id,
    )
    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
    :root {{ color-scheme: light; --ink: #17211b; --muted: #627068; --line: #d9dfda; --paper: #fff; --wash: #f4f7f4; --green: #176b4d; --green-soft: #e3f2eb; --red: #a43c35; --red-soft: #fae9e6; --amber: #9a6518; --amber-soft: #fff2d7; --blue: #245f86; }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Noto Sans TC", sans-serif; background: var(--wash); color: var(--ink); line-height: 1.55; }}
    .app-shell {{ min-height: 100vh; }}
    .sidebar {{ display: none; background: #10251d; color: #f5faf7; padding: 24px 18px; }}
    .brand {{ display: block; margin-bottom: 28px; }}
    .brand strong {{ display: block; font-size: 1.05rem; }}
    .brand span {{ color: #a9c4b7; font-size: .75rem; }}
    .nav-list {{ display: grid; gap: 4px; }}
    .nav-item {{ display: flex; align-items: center; justify-content: space-between; min-height: 42px; padding: 9px 10px; border-left: 3px solid transparent; color: #d7e5de; text-decoration: none; }}
    .nav-item:hover, .nav-item.is-active {{ background: #19372b; border-left-color: #73c69e; color: #fff; }}
    .nav-item.is-disabled {{ color: #799488; cursor: default; }}
    .nav-item small {{ font-size: .65rem; }}
    .sidebar-footer {{ margin-top: 30px; border-top: 1px solid #315044; padding-top: 16px; color: #a9c4b7; font-size: .72rem; }}
    main {{ width: min(1180px, calc(100% - 28px)); margin: 0 auto; padding: 22px 0 92px; }}
    .command-header, .hero {{ display: flex; align-items: flex-start; justify-content: space-between; gap: 18px; padding: 14px 0 22px; border-bottom: 1px solid var(--line); }}
    .eyebrow, .section-kicker {{ margin: 0 0 5px; font-size: .72rem; text-transform: uppercase; color: var(--muted); letter-spacing: 0; }}
    h1 {{ margin: 0 0 8px; font-size: 2rem; line-height: 1.18; }}
    h2 {{ margin: 0; font-size: 1.25rem; }}
    h3 {{ font-size: 1rem; }}
    .lede, .section-intro {{ max-width: 760px; margin: 0; color: var(--muted); }}
    .research-badge {{ flex: none; margin: 0; border: 1px solid #b8c9bf; background: var(--paper); color: var(--green); padding: 6px 9px; font-size: .72rem; font-weight: 700; }}
    .trust-ribbon {{ display: flex; gap: 18px; overflow-x: auto; margin: 0 -14px; padding: 11px 14px; background: #edf2ee; border-bottom: 1px solid var(--line); font-size: .76rem; white-space: nowrap; }}
    .trust-ribbon b {{ color: var(--green); margin-right: 4px; }}
    .cycle-command, .content-band, .roadmap-band {{ padding: 26px 0; border-bottom: 1px solid var(--line); }}
    .section-heading {{ display: flex; justify-content: space-between; align-items: end; gap: 16px; margin-bottom: 14px; }}
    .text-link {{ color: var(--blue); font-size: .85rem; font-weight: 650; }}
    .status-note {{ color: var(--amber); font-size: .75rem; font-weight: 700; }}
    .phase-command-grid {{ display: grid; gap: 10px; grid-template-columns: 1fr; }}
    .phase-primary, .transition-primary, .phase-context {{ min-height: 142px; padding: 16px; border: 1px solid var(--line); border-top: 4px solid var(--green); background: var(--paper); }}
    .transition-primary {{ border-top-color: var(--red); }}
    .phase-context {{ border-top-color: var(--blue); }}
    .phase-label {{ display: block; color: var(--muted); font-size: .72rem; text-transform: uppercase; }}
    .phase-command-grid strong {{ display: block; margin: 10px 0 6px; font-size: 1.65rem; }}
    .phase-command-grid p {{ margin: 0; color: var(--muted); font-size: .82rem; }}
    .cycle-order {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 2px; list-style: none; margin: 12px 0 0; padding: 0; }}
    .cycle-step {{ min-width: 0; padding: 9px 7px; border-bottom: 3px solid #bdc7c0; background: #e9eeea; text-align: center; }}
    .cycle-step strong, .cycle-step span {{ display: block; }}
    .cycle-step span {{ overflow-wrap: anywhere; color: var(--muted); font-size: .65rem; }}
    .cycle-step.is-declared {{ border-color: var(--green); background: var(--green-soft); color: var(--green); }}
    .cycle-step.is-next {{ border-color: var(--red); background: var(--red-soft); color: var(--red); }}
    .lane-grid {{ display: grid; gap: 10px; margin-top: 16px; }}
    .lane-card {{ min-height: 220px; padding: 15px; border: 1px solid var(--line); background: var(--paper); }}
    .lane-card-head {{ display: flex; justify-content: space-between; gap: 8px; }}
    .lane-type, .lane-input-count {{ color: var(--muted); font-size: .7rem; }}
    .lane-card h3 {{ margin: 14px 0 7px; }}
    .lane-card > p {{ color: var(--muted); font-size: .82rem; }}
    .lane-status {{ padding-left: 9px; border-left: 3px solid var(--amber); color: var(--amber) !important; font-weight: 650; }}
    .lane-status.status-missing {{ border-color: var(--red); color: var(--red) !important; }}
    .lane-status.status-supportive {{ border-color: var(--green); color: var(--green) !important; }}
    .lane-status.status-warning {{ border-color: var(--amber); color: var(--amber) !important; }}
    .lane-evidence-counts {{ display: grid; grid-template-columns: repeat(4, auto); gap: 3px 8px; margin: 12px 0; font-size: .72rem; }}
    .lane-evidence-counts dt {{ color: var(--muted); }}
    .lane-evidence-counts dd {{ margin: 0; font-weight: 700; }}
    .lane-evidence-items {{ display: grid; gap: 6px; padding: 0; list-style: none; }}
    .lane-evidence-items li {{ display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 3px 8px; padding: 7px; border: 1px solid var(--line); font-size: .68rem; }}
    .lane-evidence-items li > span:nth-of-type(2), .evidence-reason {{ grid-column: 1 / -1; color: var(--muted); }}
    .evidence-state {{ font-weight: 750; }}
    .why-not {{ margin: 10px 0; font-size: .72rem; }}
    .why-not summary {{ cursor: pointer; color: var(--blue); font-weight: 700; }}
    .parameter-levels {{ display: flex; flex-wrap: wrap; gap: 6px; margin: 12px 0; }}
    .parameter-levels span {{ padding: 5px 8px; border: 1px solid var(--blue); color: var(--blue); font-weight: 750; }}
    .replay-console {{ border-top: 3px solid var(--blue); }}
    .replay-controls {{ display: grid; grid-template-columns: 1fr; gap: 12px; margin: 16px 0; }}
    .replay-controls label {{ display: grid; gap: 6px; color: var(--muted); font-size: .78rem; font-weight: 700; }}
    .replay-controls select {{ min-height: 40px; border: 1px solid var(--line); background: var(--paper); color: var(--ink); padding: 7px; }}
    .replay-controls input {{ width: 100%; }}
    .replay-readout {{ padding: 16px; border: 1px solid var(--line); background: var(--paper); }}
    .lane-role-links {{ display: flex; flex-wrap: wrap; gap: 5px; }}
    .lane-role-links a {{ border: 1px solid var(--line); padding: 3px 5px; color: var(--blue); font-size: .65rem; overflow-wrap: anywhere; }}
    .priority-indicator-list {{ display: grid; border-top: 1px solid var(--line); }}
    .priority-indicator {{ display: grid; grid-template-columns: minmax(0, 1.8fr) minmax(90px, 1fr); gap: 4px 12px; padding: 12px 6px; border-bottom: 1px solid var(--line); color: var(--ink); text-decoration: none; }}
    .priority-indicator:hover {{ background: #edf4f0; }}
    .priority-indicator span {{ color: var(--muted); font-size: .74rem; }}
    .indicator-name {{ color: var(--ink) !important; font-size: .88rem !important; font-weight: 650; }}
    .health-grid, .summary-grid, .role-grid, .roadmap-grid {{ display: grid; gap: 10px; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); }}
    .table-scroll {{ overflow-x: auto; margin-top: 12px; border: 1px solid var(--line); border-radius: 6px; }}
    .research-table {{ width: 100%; min-width: 900px; border-collapse: collapse; font-size: .8rem; background: #fff; }}
    .research-table th, .research-table td {{ padding: 9px 10px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
    .research-table th {{ background: #edf2ee; color: var(--muted); font-weight: 700; }}
    .research-table tbody tr:last-child td {{ border-bottom: 0; }}
    .health-grid article {{ min-height: 92px; padding: 13px 0; border-top: 2px solid var(--line); }}
    .health-grid span, .health-grid strong {{ display: block; }}
    .health-grid span {{ color: var(--muted); font-size: .72rem; }}
    .health-grid strong {{ margin-top: 7px; font-size: 1rem; overflow-wrap: anywhere; }}
    .boundary-note {{ margin: 12px 0 0; padding: 10px 12px; background: var(--amber-soft); color: #76531e; font-size: .78rem; }}
    .roadmap-grid article {{ min-height: 90px; padding: 13px; border: 1px dashed #aab8af; background: transparent; }}
    .roadmap-grid strong, .roadmap-grid span {{ display: block; }}
    .roadmap-grid span {{ margin-top: 5px; color: var(--muted); font-size: .75rem; }}
    .summary-grid article, .role-card {{ background: var(--paper); border: 1px solid var(--line); border-radius: 6px; padding: 14px; }}
    .summary-grid strong {{ display: block; font-size: 1.8rem; }}
    .summary-grid span, .meta, .technical-id, dt {{ color: var(--muted); }}
    .technical-id {{ margin: -2px 0 8px; font-size: .82rem; }}
    details {{ margin-top: 12px; border-top: 1px solid var(--line); padding-top: 10px; }}
    summary {{ color: var(--blue); cursor: pointer; font-weight: 650; }}
    .chart-grid {{ display: grid; gap: 10px; margin-top: 10px; }}
    .chart-panel {{ border: 1px solid var(--line); border-radius: 5px; padding: 8px; }}
    .chart-panel h4 {{ margin: 0 0 6px; font-size: .88rem; }}
    .chart-interactive-wrap {{ position: relative; }}
    .chart-panel svg {{ display: block; width: 100%; height: 92px; touch-action: pan-y; outline: none; }}
    .chart-panel svg:focus-visible {{ outline: 2px solid var(--blue); outline-offset: 2px; }}
    .chart-axis {{ stroke: #c6cdd5; stroke-width: 1; }}
    .chart-line {{ fill: none; stroke: var(--blue); stroke-width: 2; vector-effect: non-scaling-stroke; }}
    .chart-crosshair {{ stroke: #59697c; stroke-width: 1; stroke-dasharray: 3 2; vector-effect: non-scaling-stroke; }}
    .chart-marker {{ fill: #fff; stroke: var(--blue); stroke-width: 2; vector-effect: non-scaling-stroke; }}
    .chart-tooltip {{ position: absolute; top: 2px; z-index: 2; transform: translateX(-50%); background: #1c2430; color: #fff; border-radius: 4px; padding: 5px 7px; font-size: .75rem; white-space: nowrap; pointer-events: none; }}
    .chart-hint, .chart-meta {{ color: var(--muted); font-size: .75rem; margin: 4px 0 0; }}
    .interpretation-value, .learning-panel {{ margin: 12px 0; padding: 11px; border-left: 3px solid var(--blue); background: #f1f6f9; }}
    .interpretation-value.is-unavailable {{ border-left-color: var(--amber); background: var(--amber-soft); }}
    .interpretation-value ul {{ margin: 6px 0 0; padding-left: 18px; }}
    .learning-panel h4 {{ margin: 0 0 8px; font-size: .88rem; }}
    .learning-grid {{ display: grid; grid-template-columns: minmax(88px, .3fr) minmax(0, 1fr); gap: 6px 10px; margin: 0; font-size: .78rem; }}
    .learning-grid dt {{ color: var(--muted); font-weight: 700; }}
    .learning-grid dd {{ margin: 0; }}
    dl {{ display: grid; grid-template-columns: minmax(92px, auto) 1fr; gap: 6px 10px; margin: 0; }}
    dd {{ margin: 0; overflow-wrap: anywhere; }}
    code {{ background: #e9edf2; border-radius: 4px; padding: 2px 4px; }}
    a {{ color: var(--blue); }}
    .mobile-nav {{ position: fixed; z-index: 10; right: 0; bottom: 0; left: 0; display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); border-top: 1px solid var(--line); background: rgba(255,255,255,.97); }}
    .mobile-nav a {{ min-width: 0; padding: 9px 2px 8px; color: var(--muted); text-align: center; text-decoration: none; font-size: .66rem; }}
    .mobile-nav a.is-active {{ color: var(--green); font-weight: 750; }}
    @media (max-width: 640px) {{
      .command-header, .hero, .section-heading {{ display: block; }}
      .research-badge, .status-note, .text-link {{ display: inline-block; margin-top: 9px; }}
      h1 {{ font-size: 1.65rem; }}
      .cycle-order {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
    @media (min-width: 720px) {{
      .phase-command-grid {{ grid-template-columns: 1.1fr 1.1fr .8fr; }}
      .lane-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .priority-indicator {{ grid-template-columns: minmax(220px, 2fr) minmax(120px, 1fr) minmax(100px, .8fr) minmax(130px, .8fr); align-items: center; }}
      .chart-grid {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
      .replay-controls {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
    }}
    @media (min-width: 980px) {{
      .app-shell {{ display: grid; grid-template-columns: 220px minmax(0, 1fr); }}
      .sidebar {{ position: sticky; top: 0; display: flex; flex-direction: column; height: 100vh; }}
      main {{ padding: 22px 0 48px; }}
      .mobile-nav {{ display: none; }}
      .lane-grid {{ grid-template-columns: repeat(4, minmax(0, 1fr)); }}
    }}
  </style>
</head>
<body>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand"><strong>景氣循環研究台</strong><span>Private NAS research service</span></div>
      {desktop_navigation}
      <p class="sidebar-footer">Declared state + ordered transition monitor<br>研究用途，不是投資建議</p>
    </aside>
    <main>{body}</main>
  </div>
  {mobile_navigation}
  {_chart_interaction_script()}
</body>
</html>
"""


def _navigation_html(
    navigation: list[dict[str, Any]],
    *,
    active_nav_id: str,
) -> str:
    rows = []
    for item in navigation:
        classes = ["nav-item"]
        if item["nav_id"] == active_nav_id:
            classes.append("is-active")
        if not item["enabled"]:
            classes.append("is-disabled")
            rows.append(
                f'<span class="{" ".join(classes)}">{escape(item["label_zh"])}'
                f'<small>Phase {int(item["planned_phase"])}</small></span>'
            )
            continue
        rows.append(
            f'<a class="{" ".join(classes)}" href="{escape(item["path"])}">'
            f'{escape(item["label_zh"])}</a>'
        )
    return f'<nav class="nav-list" aria-label="主要導覽">{"".join(rows)}</nav>'


def _mobile_navigation_html(
    navigation: list[dict[str, Any]],
    *,
    active_nav_id: str,
) -> str:
    rows = []
    for item in navigation:
        if not item["enabled"]:
            continue
        active = "is-active" if item["nav_id"] == active_nav_id else ""
        rows.append(
            f'<a class="{active}" href="{escape(item["path"])}">'
            f'{escape(item["label_zh"])}</a>'
        )
    return f'<nav class="mobile-nav" aria-label="行動版主要導覽">{"".join(rows)}</nav>'


def _chart_interaction_script() -> str:
    return """<script>
(() => {
  const formatter = new Intl.NumberFormat("zh-TW", { maximumFractionDigits: 4 });
  document.querySelectorAll("svg.interactive-chart").forEach((svg) => {
    const points = JSON.parse(svg.dataset.chartPoints || "[]");
    const wrap = svg.closest(".chart-interactive-wrap");
    const tooltip = wrap?.querySelector(".chart-tooltip");
    const crosshair = svg.querySelector(".chart-crosshair");
    const marker = svg.querySelector(".chart-marker");
    if (!points.length || !tooltip || !crosshair || !marker) return;
    let activeIndex = points.length - 1;
    const showPoint = (index) => {
      activeIndex = Math.max(0, Math.min(points.length - 1, index));
      const point = points[activeIndex];
      crosshair.setAttribute("x1", point.x);
      crosshair.setAttribute("x2", point.x);
      crosshair.setAttribute("visibility", "visible");
      marker.setAttribute("cx", point.x);
      marker.setAttribute("cy", point.y);
      marker.setAttribute("visibility", "visible");
      tooltip.textContent = `${point.date}｜數值 ${formatter.format(point.value)}`;
      tooltip.style.left = `${Math.max(8, Math.min(92, point.x / 3))}%`;
      tooltip.hidden = false;
    };
    const hidePoint = () => {
      crosshair.setAttribute("visibility", "hidden");
      marker.setAttribute("visibility", "hidden");
      tooltip.hidden = true;
    };
    const showFromPointer = (event) => {
      const bounds = svg.getBoundingClientRect();
      const ratio = Math.max(0, Math.min(1, (event.clientX - bounds.left) / bounds.width));
      showPoint(Math.round(ratio * (points.length - 1)));
    };
    svg.addEventListener("pointermove", showFromPointer);
    svg.addEventListener("pointerdown", showFromPointer);
    svg.addEventListener("pointerleave", (event) => {
      if (event.pointerType === "mouse") hidePoint();
    });
    svg.addEventListener("focus", () => showPoint(activeIndex));
    svg.addEventListener("blur", hidePoint);
    svg.addEventListener("keydown", (event) => {
      if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
      event.preventDefault();
      showPoint(activeIndex + (event.key === "ArrowRight" ? 1 : -1));
    });
  });
})();
</script>"""


def _routes_ready(routes: list[dict[str, Any]], contract: dict[str, Any]) -> bool:
    return (
        len(routes) == int(contract["route_policy"]["route_count"])
        and all(route["private_nas_only"] is True for route in routes)
        and all(route["frontend_database_access_allowed"] is False for route in routes)
        and all(route["frontend_api_key_allowed"] is False for route in routes)
    )


def load_book_core_role_display_labels_zh(
    path: str | Path = DEFAULT_ROLE_LABELS_PATH,
) -> dict[str, str]:
    """Load the governed Traditional Chinese display name for every role."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    contract = payload["book_core_role_display_labels_zh"]
    if contract["language"] != "zh-Hant-TW":
        raise ValueError("book-core role labels must use zh-Hant-TW")
    return {str(key): str(value) for key, value in contract["roles"].items()}


def _validate_role_label_coverage(
    *,
    snapshot: dict[str, Any],
    role_labels: dict[str, str],
) -> None:
    role_ids = {str(row["role_id"]) for row in snapshot["role_snapshots"]}
    label_ids = set(role_labels)
    if role_ids != label_ids:
        missing = sorted(role_ids - label_ids)
        unexpected = sorted(label_ids - role_ids)
        raise ValueError(
            "book-core role label coverage mismatch: "
            f"missing={missing}, unexpected={unexpected}",
        )
    if any(not label.strip() for label in role_labels.values()):
        raise ValueError("book-core Traditional Chinese role labels must be non-empty")


def _api_payloads_ready(api_payloads: dict[str, Any], snapshot: dict[str, Any]) -> bool:
    expected_live_db = bool(snapshot["trust_metadata"].get("live_db_connected"))
    return (
        len(api_payloads) == 3
        and api_payloads["indicator_snapshot"]["role_count"]
        == snapshot["role_snapshot_count"]
        and api_payloads["service_status"]["live_db_connection_attempted"]
        is expected_live_db
        and api_payloads["service_status"]["postgres_write_attempted"] is False
        and api_payloads["service_status"]["live_fetch_attempted"] is False
        and api_payloads["service_status"]["frontend_database_access_allowed"] is False
        and api_payloads["service_status"]["frontend_api_key_allowed"] is False
    )


def _html_pages_ready(html_pages: list[dict[str, Any]], snapshot: dict[str, Any]) -> bool:
    html = "\n".join(page["html"] for page in html_pages)
    return (
        len(html_pages) == 2
        and "景氣循環指揮中心" in html
        and html.count('data-transition-lane="') >= 3
        and 'aria-label="主要導覽"' in html
        and "research-only" in html
        and "revised diagnostic" in html
        and 'data-role-card="true"' in html
        and _html_marker_count(html_pages, "data-role-card=")
        == snapshot["role_snapshot_count"]
    )


def _trust_metadata(contract: dict[str, Any], snapshot: dict[str, Any]) -> dict[str, Any]:
    live_db_connected = bool(snapshot["trust_metadata"].get("live_db_connected"))
    return {
        "service_target": contract["service_scope"]["target_runtime"],
        "nas_migration_surface": (
            "live_postgres_route_api_html_renderer"
            if live_db_connected
            else "route_api_html_renderer_rehearsal"
        ),
        "source_snapshot_artifact_id": snapshot["artifact_id"],
        "source_snapshot_hash": snapshot["snapshot_manifest_hash"],
        "research_only": True,
        "revised_diagnostic_only": True,
        "pit_availability_accounting_included": True,
        "strict_point_in_time_result": False,
        "frontend_database_access_allowed": False,
        "frontend_api_key_allowed": False,
        "live_db_connection_attempted": live_db_connected,
        "live_db_connected": live_db_connected,
        "refresh_state": snapshot.get("refresh_status", {}).get(
            "refresh_state",
            "not_configured",
        ),
        "source_refresh_health_status": snapshot.get(
            "source_refresh_health_status",
            "not_configured",
        ),
        "declared_state_source": snapshot.get("declared_cycle_state", {}).get(
            "active_registry_source",
            "canonical_default",
        ),
        "postgres_write_attempted": False,
        "live_fetch_attempted": False,
        "candidate_phase_selection_enabled": False,
        "current_phase_inference_enabled": False,
    }


def _live_runtime_bundle_ready(bundle: dict[str, Any]) -> bool:
    return (
        bundle["nas_service_dashboard_contract_ready"] is True
        and bundle["nas_service_route_manifest_ready"] is True
        and bundle["nas_service_api_payload_ready"] is True
        and bundle["nas_service_html_renderer_ready"] is True
        and bundle["role_card_count"] == 39
        and bundle["traditional_chinese_role_label_count"] == 39
        and bundle["live_db_connection_attempt_count"] == 1
        and bundle["postgres_write_attempt_count"] == 0
        and bundle["candidate_phase_emitted"] is False
        and bundle["current_phase_emitted"] is False
        and bundle["prohibited_output_field_count"] == 0
    )


def _mobile_trust_caveats() -> list[str]:
    return [
        "研究用，不是正式景氣階段判斷。",
        "目前數值使用 revised diagnostic snapshot。",
        "PIT 欄位只表示補齊可行性，不是 point-in-time 結果。",
        "前端不持有資料庫帳密或 API key。",
        "不輸出買賣、配置或個人化交易指令。",
        "blocked/missing 不會被當作 neutral 或補零。",
    ]


def _validated_tmp_output_dir(output_dir: str | Path) -> Path:
    path = Path(output_dir)
    resolved = path.resolve()
    tmp_resolved = TMP_ROOT.resolve()
    if resolved == tmp_resolved or tmp_resolved in resolved.parents:
        return path
    raise ValueError("Phase95 dry-run output must be under /tmp")


def _write_text(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _write_json(path: Path, payload: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _html_marker_count(html_pages: list[dict[str, Any]], marker: str) -> int:
    return sum(page["html"].count(marker) for page in html_pages)


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def _hash_payload(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _contains_prohibited_field(value: Any) -> int:
    if isinstance(value, dict):
        return sum(
            (1 if key in PROHIBITED_FIELDS else 0) + _contains_prohibited_field(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return sum(_contains_prohibited_field(item) for item in value)
    return 0

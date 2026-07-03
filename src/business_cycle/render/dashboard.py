"""Render a minimal static dashboard from a cycle snapshot."""

from __future__ import annotations

import json
import shutil
from html import escape
from pathlib import Path
from typing import Any

import yaml

from business_cycle.render.explanations import (
    get_indicator_explanation,
    get_phase_score_explanation,
    load_indicator_explanations,
    load_phase_score_explanations,
)
from business_cycle.render.labels import label_for, load_display_labels

PHASE_ORDER = ("recovery", "growth", "boom", "recession")
DISCLAIMER_ZH = "本頁僅為總經資料整理與景氣循環判讀輔助，不構成投資建議。"
DEFAULT_LABELS_PATH = Path("specs/common/display_labels_zh.yaml")
DEFAULT_PHASE_EXPLANATIONS_PATH = Path("specs/common/phase_score_explanations_zh.yaml")
DEFAULT_INDICATOR_EXPLANATIONS_PATH = Path("specs/common/indicator_explanations_zh.yaml")
DEFAULT_SCORING_METHODS_PATH = Path("specs/common/scoring_methods.yaml")
INDICATOR_GROUPS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("employment", ("initial_jobless_claims", "short_term_unemployment", "unemployment_rate")),
    ("consumption", ("real_retail_sales", "real_pce_durable_goods")),
    ("investment", ("durable_goods_orders", "real_private_fixed_investment")),
    ("trade", ("imports_goods_services", "exports_goods_services")),
    (
        "rates_financial_conditions",
        ("federal_funds_rate", "ten_year_treasury_yield", "thirty_year_mortgage_rate"),
    ),
    ("commodities", ("wti_oil_price",)),
)


def build_dashboard(
    snapshot: dict[str, Any],
    phase_explanations: dict[str, dict[str, Any]] | None = None,
    indicator_explanations: dict[str, dict[str, Any]] | None = None,
    scoring_methods: dict[str, dict[str, Any]] | None = None,
) -> str:
    """Build a complete mobile-first HTML document from cycle_snapshot.json data."""

    _reject_secret_keys(snapshot)
    decision = _mapping(snapshot.get("current_phase_decision"))
    decision_details = _mapping(decision.get("details"))
    cycle_context = _mapping(decision_details.get("cycle_context"))
    summary = _mapping(snapshot.get("summary"))
    labels = _load_default_labels()
    phase_explanations = phase_explanations if phase_explanations is not None else _load_default_phase_explanations()
    indicator_explanations = (
        indicator_explanations
        if indicator_explanations is not None
        else _load_default_indicator_explanations()
    )
    scoring_methods = (
        scoring_methods if scoring_methods is not None else _load_default_scoring_methods()
    )
    phase_scores = sorted(
        _list_of_mappings(snapshot.get("phase_scores")),
        key=lambda phase: (_phase_sort_index(str(phase.get("phase_id", ""))), str(phase.get("phase_id", ""))),
    )
    indicator_scores = _list_of_mappings(snapshot.get("indicator_scores"))
    warnings = [str(item) for item in snapshot.get("warnings", []) or []]
    failures = _mapping(snapshot.get("failures"))
    indicator_failures = _list_of_mappings(failures.get("indicator_failures"))
    phase_failures = _list_of_mappings(failures.get("phase_failures"))
    current_phase_id = _optional_text(decision.get("current_phase_id"))
    candidate_phase_id = _optional_text(decision.get("candidate_phase_id") or decision.get("allowed_next_phase_id"))
    current_phase_score = _phase_by_id(phase_scores, current_phase_id)
    highest_phase = _highest_phase_id(phase_scores)

    return f"""<!doctype html>
<html lang="zh-Hant-TW">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>景氣循環儀表板</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f6f7f9;
      --panel: #ffffff;
      --text: #17202a;
      --muted: #5c6773;
      --line: #d9dee5;
      --accent: #1f6feb;
      --warn: #9a6700;
      --ok-bg: #eef6ff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
    }}
    main {{ width: min(1120px, 100%); margin: 0 auto; padding: 16px; }}
    header {{ padding: 20px 0 10px; }}
    h1 {{ margin: 0 0 8px; font-size: 1.8rem; }}
    h2 {{ margin: 28px 0 12px; font-size: 1.2rem; }}
    h3 {{ margin: 0 0 8px; font-size: 1rem; }}
    .muted {{ color: var(--muted); }}
    .technical {{ color: var(--muted); font-size: 0.82rem; overflow-wrap: anywhere; }}
    .hero {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
      margin-top: 12px;
    }}
    .hero-title {{ margin: 0 0 14px; }}
    .grid {{ display: grid; grid-template-columns: 1fr; gap: 12px; }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
    }}
    .current {{ border-left: 4px solid var(--accent); background: var(--ok-bg); }}
    .badge {{
      display: inline-block;
      border: 1px solid var(--accent);
      border-radius: 999px;
      color: var(--accent);
      font-size: 0.78rem;
      font-weight: 700;
      padding: 2px 8px;
      margin-left: 6px;
      vertical-align: middle;
    }}
    .metric {{ display: flex; justify-content: space-between; gap: 12px; padding: 4px 0; }}
    .metric span:first-child {{ color: var(--muted); }}
    .score {{ font-size: 1.7rem; font-weight: 700; }}
    .warning {{ color: var(--warn); }}
    ul {{ margin: 8px 0 0; padding-left: 20px; }}
    .table-list {{ display: grid; gap: 10px; }}
    .section-note {{ margin: 8px 0 0; color: var(--muted); }}
    .group {{ margin-bottom: 18px; }}
    .group h3 {{ margin-bottom: 10px; }}
    footer {{ margin: 28px 0 10px; padding-top: 16px; border-top: 1px solid var(--line); }}
    @media (min-width: 720px) {{
      main {{ padding: 24px; }}
      .phase-grid {{ grid-template-columns: repeat(4, 1fr); }}
      .hero-grid {{ grid-template-columns: repeat(2, 1fr); }}
      .indicator-grid {{ grid-template-columns: repeat(2, 1fr); }}
    }}
  </style>
</head>
<body>
<main>
  <header>
    <div class="hero">
      <h1 class="hero-title">景氣循環儀表板</h1>
      <div class="grid hero-grid">
        <div>
          {_metric("目前景氣位階", _cycle_position_label(labels, current_phase_id, current_phase_score, cycle_context))}
          {_metric("週期位階分數", _cycle_score_text(current_phase_score))}
          {_metric("轉折風險", _turning_risk_label(decision))}
          {_metric("資料信心", _confidence_label(decision.get("confidence")))}
        </div>
        <div>
          {_metric("本期重點", _headline_focus(labels, decision))}
          {_metric("基準情境", _baseline_stage(cycle_context))}
          {_metric("判讀狀態", _status_label(labels, decision.get("decision_status")))}
          {_metric("generated_at", snapshot.get("generated_at"))}
          {_metric("as_of", snapshot.get("as_of"))}
          <div class="technical">current technical id: {_text(decision.get("current_phase_id"))}</div>
        </div>
      </div>
      <p class="section-note">週期位階分數代表目前資料對該階段的證據強度，不是景氣好壞分數。</p>
      <p class="section-note">本頁依總經資料、四階段分數與景氣循環順序進行判讀；基準情境來自外部週期脈絡，模型再檢查是否維持或轉換。本頁僅供總經研究與景氣循環判讀，不構成投資建議。</p>
    </div>
  </header>

  <section>
    <h2>下一階段觀察</h2>
    <div class="card">
      <h3>{_phase_label(labels, decision.get("allowed_next_phase_id"))}</h3>
      {_metric("轉換候選階段", _phase_label(labels, decision.get("candidate_phase_id")))}
      {_metric("候選階段分數", _format_number(decision.get("candidate_score")))}
      {_metric("候選階段信心", _format_percent(decision.get("candidate_confidence")))}
      {_metric("非相鄰阻擋階段", _blocked_phase_text(labels, decision.get("blocked_phase_ids")))}
      <p>{_text(decision.get("reason_zh"))}</p>
      <p class="section-note">依循景氣循環順序，系統只會檢查目前階段與允許的下一階段；非相鄰階段即使分數較高，也不會直接跳轉。</p>
    </div>
  </section>

  <section>
    <h2>四階段證據分數</h2>
    <p class="section-note">四階段證據分數表示目前資料有多像該景氣階段，不是景氣好壞分數；例如衰退期分數高代表衰退證據較強，榮景期分數高代表景氣後期循環證據較強。</p>
    <div class="grid phase-grid">
      {_phase_cards(phase_scores, labels, current_phase_id, phase_explanations)}
    </div>
    <p class="muted">四階段分數是各階段證據強度，最終階段仍需依循景氣循環順序與轉換規則判讀。</p>
    {_highest_score_note(current_phase_id, highest_phase)}
  </section>

  {_boom_context_html(current_phase_id)}

  <section>
    <h2>核心指標</h2>
    {_indicator_groups_html(indicator_scores, labels, indicator_explanations, scoring_methods, current_phase_id, candidate_phase_id)}
  </section>

  <section>
    <h2>資料警示與失敗項目</h2>
    {_warnings_html(warnings)}
    {_failures_html(indicator_failures, phase_failures)}
  </section>

  <footer class="muted">
    <p>{DISCLAIMER_ZH}</p>
    <p>分數與階段判讀依賴資料品質、資料修正與模型假設。</p>
    <p>summary technical id: current_phase_id={_text(summary.get("current_phase_id"))}, decision_status={_text(summary.get("decision_status"))}</p>
  </footer>
</main>
</body>
</html>
"""


def build_static_site(snapshot_path: str | Path, output_dir: str | Path) -> dict[str, Path]:
    """Build public/index.html and public/data/cycle_snapshot.json."""

    source_path = Path(snapshot_path)
    if not source_path.exists():
        raise FileNotFoundError(f"Cycle snapshot JSON does not exist: {source_path}")

    snapshot = json.loads(source_path.read_text(encoding="utf-8"))
    if not isinstance(snapshot, dict):
        raise ValueError("Cycle snapshot JSON must be a mapping")
    _reject_secret_keys(snapshot)

    output_root = Path(output_dir)
    data_dir = output_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    output_root.mkdir(parents=True, exist_ok=True)

    index_path = output_root / "index.html"
    copied_snapshot_path = data_dir / "cycle_snapshot.json"
    index_path.write_text(build_dashboard(snapshot), encoding="utf-8")
    shutil.copyfile(source_path, copied_snapshot_path)
    return {"index_path": index_path, "snapshot_path": copied_snapshot_path}


def _phase_cards(
    phase_scores: list[dict[str, Any]],
    labels: dict[str, dict[str, str]],
    current_phase_id: str | None,
    phase_explanations: dict[str, dict[str, Any]],
) -> str:
    return "\n".join(
        _phase_card(phase, labels, current_phase_id, phase_explanations)
        for phase in phase_scores
    )


def _phase_card(
    phase: dict[str, Any],
    labels: dict[str, dict[str, str]],
    current_phase_id: str | None,
    phase_explanations: dict[str, dict[str, Any]],
) -> str:
    phase_id = _optional_text(phase.get("phase_id"))
    explanation = get_phase_score_explanation(phase_explanations, phase_id)
    return f"""<article class="card">
  <h3>{_phase_label(labels, phase_id, phase.get("phase_name_zh"))}{_current_badge(phase_id, current_phase_id)}</h3>
  <div class="technical">technical id: {_text(phase_id)}</div>
  <div class="score">{_text(_format_number(phase.get("score")))}</div>
  {_metric("資料信心", _format_percent(phase.get("confidence")))}
  {_metric("可用權重", _format_number(phase.get("available_weight")))}
  {_metric("階段位置", _stage_label(labels, phase.get("stage_hint")))}
  {_metric("缺漏指標數", len(phase.get("missing_indicators") or []))}
  <p><strong>分數代表什麼：</strong>{_text(explanation.get("score_meaning_zh") or "尚未建立此階段分數說明。")}</p>
  <p><strong>高分常見意義：</strong>{_text(explanation.get("high_score_zh") or "尚未建立高分解釋。")}</p>
  <p class="muted">{_text(explanation.get("interpretation_warning_zh") or "此分數代表階段證據強度，不代表景氣好壞分數。")}</p>
</article>"""


def _indicator_groups_html(
    indicator_scores: list[dict[str, Any]],
    labels: dict[str, dict[str, str]],
    indicator_explanations: dict[str, dict[str, Any]],
    scoring_methods: dict[str, dict[str, Any]],
    current_phase_id: str | None,
    candidate_phase_id: str | None,
) -> str:
    scores_by_id = {
        str(indicator.get("indicator_id")): indicator
        for indicator in indicator_scores
        if indicator.get("indicator_id") is not None
    }
    sections: list[str] = []
    rendered: set[str] = set()
    for group_id, indicator_ids in INDICATOR_GROUPS:
        group_items = [scores_by_id[indicator_id] for indicator_id in indicator_ids if indicator_id in scores_by_id]
        rendered.update(str(item.get("indicator_id")) for item in group_items)
        sections.append(
            f"""<section class="group">
  <h3>{_text(label_for(labels, "indicator_groups", group_id, group_id))}</h3>
  <div class="table-list indicator-grid">
    {_indicator_cards(group_items, labels, indicator_explanations, scoring_methods, current_phase_id, candidate_phase_id)}
  </div>
</section>"""
        )

    ungrouped = [
        indicator
        for indicator in sorted(indicator_scores, key=lambda item: str(item.get("indicator_id", "")))
        if str(indicator.get("indicator_id")) not in rendered
    ]
    if ungrouped:
        sections.append(
            f"""<section class="group">
  <h3>其他</h3>
  <div class="table-list indicator-grid">
    {_indicator_cards(ungrouped, labels, indicator_explanations, scoring_methods, current_phase_id, candidate_phase_id)}
  </div>
</section>"""
        )
    return "\n".join(sections)


def _indicator_cards(
    indicator_scores: list[dict[str, Any]],
    labels: dict[str, dict[str, str]],
    indicator_explanations: dict[str, dict[str, Any]],
    scoring_methods: dict[str, dict[str, Any]],
    current_phase_id: str | None,
    candidate_phase_id: str | None,
) -> str:
    cards: list[str] = []
    for indicator in indicator_scores:
        details = _mapping(indicator.get("details"))
        indicator_id = _optional_text(indicator.get("indicator_id"))
        explanation = get_indicator_explanation(indicator_explanations, indicator_id)
        current_impact = _phase_impact_text(explanation, current_phase_id)
        next_impact = _phase_impact_text(explanation, candidate_phase_id)
        method_id = _optional_text(indicator.get("method"))
        method = scoring_methods.get(method_id or "")
        score_interpretation = _score_interpretation_html(method)
        cards.append(
            f"""<article class="card">
  <h3>{_text(label_for(labels, "indicators", indicator_id))}</h3>
  <div class="technical">technical id: {_text(indicator_id)}; selected_series_id: {_text(details.get("selected_series_id"))}</div>
  {_metric("分數", _format_number(indicator.get("score")))}
  {score_interpretation}
  {_metric("資料信心", _format_percent(indicator.get("confidence")))}
  {_metric("診斷配方", label_for(labels, "methods", method_id))}
  {_metric("資料日期", indicator.get("as_of"))}
  <p>{_text(indicator.get("reason_zh") or indicator.get("reason"))}</p>
  <p><strong>景氣意義：</strong>{_text(explanation.get("cycle_meaning_zh") or "尚未建立此指標說明。")}</p>
  <p><strong>為什麼重要：</strong>{_text(explanation.get("why_it_matters_zh") or "尚未建立此指標的重要性說明。")}</p>
  {_metric("指標屬性", _leading_lagging_label(explanation.get("leading_lagging")))}
  <p><strong>對目前階段的影響：</strong>{_text(current_impact)}</p>
  <p><strong>對下一階段的影響：</strong>{_text(next_impact)}</p>
  {_indicator_method_detail_html(method_id, method)}
</article>"""
        )
    return "\n".join(cards)


def _indicator_method_detail_html(
    method_id: str | None,
    method: dict[str, Any] | None,
) -> str:
    if not method:
        return """
  <details class="method-detail" data-indicator-method-explanation>
    <summary>診斷配方：未找到治理定義</summary>
    <p class="muted">此指標缺少 scoring_methods.yaml 對應定義，因此只能顯示既有分數，不能說明計算配方。</p>
  </details>
"""
    inputs = _mapping(method.get("inputs"))
    parameters = _mapping(method.get("parameters"))
    confidence = _mapping(method.get("confidence_behavior"))
    required_fields = _list_text(inputs.get("required_fields"))
    cleaned = _list_text(inputs.get("cleaned_input"))
    directionality = _definition_items(_mapping(parameters.get("directionality")))
    confidence_reducers = _list_items_plain(
        confidence.get("reduce_when"),
        "未宣告信心下調條件。",
    )
    pseudo_code = _ordered_items(method.get("pseudo_code_zh"))
    score_interpretation = _score_interpretation_html(method)
    windows = _method_window_text(parameters)
    return f"""
  <details class="method-detail" data-indicator-method-explanation data-method-id="{_text(method_id)}">
    <summary>診斷配方：{_text(method.get("purpose_zh"))}</summary>
    <div data-method-recipe>
      <p><strong>資料需求：</strong>{_text(required_fields or "未宣告")}</p>
      <p><strong>清理後輸入：</strong>{_text(cleaned or "未宣告")}</p>
      <p><strong>頻率處理：</strong>{_text(inputs.get("frequency_handling") or "未宣告")}</p>
      <p><strong>缺值處理：</strong>{_text(inputs.get("missing_value_handling") or "未宣告")}</p>
      <p><strong>視窗設定：</strong>{_text(windows)}</p>
      <p><strong>正反方向：</strong></p>
      <dl class="technical">{directionality}</dl>
      {score_interpretation}
      <p><strong>標準化：</strong>{_text(parameters.get("normalization_method") or "未宣告")}</p>
      <p><strong>不足歷史：</strong>{_text(method.get("insufficient_history_behavior") or "abstain_or_low_confidence_diagnostic")}</p>
      <div data-method-confidence>
        <p><strong>信心下調條件：</strong></p>
        <ul>{confidence_reducers}</ul>
      </div>
      <div data-method-pseudo-code>
        <p><strong>計算步驟摘要：</strong></p>
        <ol>{pseudo_code}</ol>
      </div>
      <p data-method-boundary class="muted">此區只解釋 legacy 診斷分數的配方；它不是 declared current phase、不是 legal transition confirmation，也不會產生交易或配置建議。</p>
    </div>
  </details>
"""


def _score_interpretation_html(method: dict[str, Any] | None) -> str:
    interpretation = _mapping(method.get("score_interpretation_zh")) if method else {}
    if not interpretation:
        return '<p class="muted" data-score-interpretation>分數高低解讀尚未宣告。</p>'
    return f"""
  <div class="technical" data-score-interpretation>
    <p><strong>分數高代表：</strong>{_text(interpretation.get("high_score_zh"))}</p>
    <p><strong>分數低代表：</strong>{_text(interpretation.get("low_score_zh"))}</p>
    <p><strong>分數接近 0：</strong>{_text(interpretation.get("neutral_score_zh"))}</p>
    <p>{_text(interpretation.get("boundary_zh"))}</p>
  </div>
"""


def _method_window_text(parameters: dict[str, Any]) -> str:
    parts = [
        ("percentile lookback", parameters.get("percentile_lookback")),
        ("lookback", parameters.get("lookback_window")),
        ("trend", parameters.get("trend_window") or parameters.get("trend_window_options")),
        ("moving average", parameters.get("moving_average_window")),
        ("smoothing", parameters.get("smoothing_window")),
        ("slope", parameters.get("slope_window")),
        ("momentum", parameters.get("momentum_window")),
        ("confirmation", parameters.get("confirmation_window")),
        ("min history", parameters.get("min_history")),
    ]
    visible = [
        f"{label}: {_compact_value(value)}"
        for label, value in parts
        if value not in (None, [], {})
    ]
    return "; ".join(visible) if visible else "未宣告"


def _compact_value(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    if isinstance(value, dict):
        return ", ".join(f"{key}={item}" for key, item in value.items())
    return str(value)


def _definition_items(mapping: dict[str, Any]) -> str:
    if not mapping:
        return "<dt>未宣告</dt><dd>未宣告方向判讀。</dd>"
    return "".join(
        f"<dt>{_text(key)}</dt><dd>{_text(value)}</dd>"
        for key, value in mapping.items()
    )


def _list_text(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    if value is None:
        return ""
    return str(value)


def _list_items_plain(value: Any, empty_text: str) -> str:
    if not isinstance(value, list) or not value:
        return f"<li>{_text(empty_text)}</li>"
    return "".join(f"<li>{_text(item)}</li>" for item in value)


def _ordered_items(value: Any) -> str:
    if not isinstance(value, list) or not value:
        return "<li>未宣告計算步驟。</li>"
    return "".join(f"<li>{_text(item)}</li>" for item in value)


def _warnings_html(warnings: list[str]) -> str:
    if not warnings:
        return '<p class="muted">目前沒有 snapshot warning。</p>'
    items = "\n".join(f'<li class="warning">{_text(warning)}</li>' for warning in warnings)
    low_confidence_note = ""
    if any("confidence is low" in warning for warning in warnings):
        low_confidence_note = (
            '<p class="muted">部分判讀信心偏低，可能與資料更新、指標缺漏或模型假設有關。</p>'
        )
    return f"<ul>{items}</ul>{low_confidence_note}"


def _failures_html(indicator_failures: list[dict[str, Any]], phase_failures: list[dict[str, Any]]) -> str:
    if not indicator_failures and not phase_failures:
        return '<p class="muted">目前沒有 pipeline failure。</p>'
    sections: list[str] = []
    if indicator_failures:
        sections.append("<h3>指標失敗項目</h3>" + _failure_list(indicator_failures))
    if phase_failures:
        sections.append("<h3>階段失敗項目</h3>" + _failure_list(phase_failures))
    return "\n".join(sections)


def _failure_list(failures: list[dict[str, Any]]) -> str:
    items = "\n".join(
        f"<li>{_text(failure.get('indicator_id') or failure.get('phase_id'))}: "
        f"{_text(failure.get('error_type'))} - {_text(failure.get('message'))}</li>"
        for failure in failures
    )
    return f"<ul>{items}</ul>"


def _metric(label: str, value: Any) -> str:
    return f'<div class="metric"><span>{escape(label)}</span><strong>{_text(value)}</strong></div>'


def _baseline_context_html(cycle_context: dict[str, Any]) -> str:
    if not cycle_context:
        return ""
    return f"""<div class="baseline">
  <h3>外部基準情境</h3>
  {_metric("基準階段", cycle_context.get("baseline_phase_name_zh"))}
  {_metric("基準位置", cycle_context.get("baseline_stage_note_zh"))}
  <p>{_text(cycle_context.get("source_note_zh"))}</p>
  <p class="muted">此 baseline/context 是 resolver 的 previous phase 脈絡，不是純模型自動算出的結論，也不是投資建議。</p>
</div>"""


def _boom_context_html(current_phase_id: str | None) -> str:
    if current_phase_id != "boom":
        return ""
    return """<section>
    <h2>榮景期觀察重點</h2>
    <div class="card">
      <p>榮景期屬於景氣後期循環，重點不只是確認經濟仍熱絡，而是觀察升息、通膨、利率、原物料、估值與就業/消費是否開始出現轉弱訊號。本系統目前以榮景期作為外部基準情境，再由資料模型檢查是否維持榮景期或進入下一階段觀察。</p>
    </div>
  </section>"""


def _baseline_stage(cycle_context: dict[str, Any]) -> str:
    return str(cycle_context.get("baseline_stage_note_zh") or "-")


def _load_default_labels() -> dict[str, dict[str, str]]:
    try:
        return load_display_labels(DEFAULT_LABELS_PATH)
    except FileNotFoundError:
        return {}


def _load_default_phase_explanations() -> dict[str, dict[str, Any]]:
    try:
        return load_phase_score_explanations(DEFAULT_PHASE_EXPLANATIONS_PATH)
    except (FileNotFoundError, ValueError):
        return {}


def _load_default_indicator_explanations() -> dict[str, dict[str, Any]]:
    try:
        return load_indicator_explanations(DEFAULT_INDICATOR_EXPLANATIONS_PATH)
    except (FileNotFoundError, ValueError):
        return {}


def _load_default_scoring_methods() -> dict[str, dict[str, Any]]:
    try:
        payload = yaml.safe_load(DEFAULT_SCORING_METHODS_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    methods = payload.get("methods", []) if isinstance(payload, dict) else []
    return {
        str(method["method_id"]): method
        for method in methods
        if isinstance(method, dict) and method.get("method_id")
    }


def _phase_label(
    labels: dict[str, dict[str, str]],
    phase_id: Any,
    fallback: Any = None,
) -> str:
    key = _optional_text(phase_id)
    fallback_text = _optional_text(fallback)
    return label_for(labels, "phases", key, fallback_text or key or "-")


def _status_label(labels: dict[str, dict[str, str]], status: Any) -> str:
    key = _optional_text(status)
    return label_for(labels, "decision_statuses", key, key or "-")


def _stage_label(labels: dict[str, dict[str, str]], stage_hint: Any) -> str:
    key = _optional_text(stage_hint)
    return label_for(labels, "stage_hints", key, key or "未判定")


def _blocked_phase_text(labels: dict[str, dict[str, str]], value: Any) -> str:
    if not isinstance(value, list) or not value:
        return "無非相鄰階段被阻擋"
    return "、".join(_phase_label(labels, item) for item in value)


def _current_badge(phase_id: Any, current_phase_id: str | None) -> str:
    if _optional_text(phase_id) != current_phase_id:
        return ""
    return '<span class="badge">目前階段</span>'


def _highest_score_note(current_phase_id: str | None, highest_phase_id: str | None) -> str:
    if current_phase_id is None or highest_phase_id is None or current_phase_id == highest_phase_id:
        return ""
    return '<p class="muted">分數最高不等於目前階段，仍需依循景氣循環順序與轉換規則。</p>'


def _phase_by_id(phase_scores: list[dict[str, Any]], phase_id: str | None) -> dict[str, Any]:
    if phase_id is None:
        return {}
    for phase in phase_scores:
        if phase.get("phase_id") == phase_id:
            return phase
    return {}


def _cycle_position_label(
    labels: dict[str, dict[str, str]],
    current_phase_id: str | None,
    phase_score: dict[str, Any],
    cycle_context: dict[str, Any] | None = None,
) -> str:
    phase_name = _phase_label(labels, current_phase_id, phase_score.get("phase_name_zh"))
    stage = _optional_text(phase_score.get("stage_hint"))
    stage_labels = {"early": "前段", "mid": "中段", "late": "後段"}
    if stage in stage_labels:
        return f"{phase_name}{stage_labels[stage]}"
    derived_stage = _derived_stage_from_cycle_context(current_phase_id, cycle_context)
    if derived_stage is not None:
        return f"{phase_name}{derived_stage}"
    return f"{phase_name}，階段未判定"


def _derived_stage_from_cycle_context(
    current_phase_id: str | None,
    cycle_context: dict[str, Any] | None,
) -> str | None:
    if current_phase_id is None or not isinstance(cycle_context, dict):
        return None
    if _optional_text(cycle_context.get("baseline_phase_id")) != current_phase_id:
        return None
    note = _optional_text(cycle_context.get("baseline_stage_note_zh")) or ""
    if "第一年" in note or "剛結束" in note:
        return "前段"
    return None


def _cycle_score_text(phase_score: dict[str, Any]) -> str:
    score = phase_score.get("score")
    if isinstance(score, (int, float)):
        return f"{float(score):.0f} / 100"
    return "尚未取得"


def _turning_risk_label(decision: dict[str, Any]) -> str:
    status = decision.get("decision_status")
    candidate_score = float(decision.get("candidate_score") or 0.0)
    if status == "confirmed":
        return "高"
    if status == "transition_watch":
        return "偏高"
    if status == "hold_current" and candidate_score >= 60.0:
        return "中"
    if status == "hold_current" and candidate_score >= 45.0:
        return "觀察中"
    return "偏低"


def _confidence_label(value: Any) -> str:
    if not isinstance(value, (int, float)):
        return "偏低"
    confidence = float(value)
    if confidence >= 0.75:
        return "高"
    if confidence >= 0.60:
        return "中高"
    if confidence >= 0.45:
        return "中"
    return "偏低"


def _headline_focus(labels: dict[str, dict[str, str]], decision: dict[str, Any]) -> str:
    current_phase = _phase_label(labels, decision.get("current_phase_id"))
    candidate_phase = _phase_label(labels, decision.get("candidate_phase_id") or decision.get("allowed_next_phase_id"))
    status = decision.get("decision_status")
    if status == "confirmed":
        return f"{candidate_phase}已達確認條件；仍需持續觀察資料信心與指標廣度。"
    if status == "transition_watch":
        return f"{candidate_phase}進入轉換觀察；就業、消費、投資與利率條件仍需合併判讀。"
    return f"目前維持{current_phase}；{candidate_phase}證據尚未足以推動階段轉換。"


def _phase_impact_text(explanation: dict[str, Any], phase_id: str | None) -> str:
    impacts = explanation.get("phase_impacts")
    if not isinstance(impacts, dict) or phase_id is None:
        return "尚未建立此階段影響說明。"
    impact = impacts.get(phase_id)
    if not isinstance(impact, dict):
        return "尚未建立此階段影響說明。"
    return str(impact.get("explanation_zh") or "尚未建立此階段影響說明。")


def _leading_lagging_label(value: Any) -> str:
    labels = {
        "leading": "領先",
        "coincident": "同步",
        "lagging": "落後",
        "policy": "政策/金融條件",
    }
    key = _optional_text(value)
    if key is None:
        return "未分類"
    return labels.get(key, key)


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list_of_mappings(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _phase_sort_index(phase_id: str) -> int:
    try:
        return PHASE_ORDER.index(phase_id)
    except ValueError:
        return len(PHASE_ORDER)


def _format_number(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{float(value):.2f}"
    return "" if value is None else str(value)


def _format_percent(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{float(value) * 100:.0f}%"
    return "" if value is None else str(value)


def _highest_phase_id(phase_scores: list[dict[str, Any]]) -> str | None:
    if not phase_scores:
        return None
    highest = max(phase_scores, key=lambda phase: float(phase.get("score") or 0.0))
    return _optional_text(highest.get("phase_id"))


def _optional_text(value: Any) -> str | None:
    return None if value is None else str(value)


def _text(value: Any) -> str:
    if value is None:
        return "-"
    return escape(str(value))


def _reject_secret_keys(value: Any) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if "FRED_API_KEY" in str(key):
                raise ValueError("Snapshot contains forbidden secret key name: FRED_API_KEY")
            _reject_secret_keys(item)
    elif isinstance(value, list):
        for item in value:
            _reject_secret_keys(item)

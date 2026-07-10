"""Traditional-Chinese private NAS source-operations renderer."""

from __future__ import annotations

from html import escape
import json
from typing import Any


def render_nas_source_operations_page(diagnostics: dict[str, Any]) -> str:
    families = "".join(_family_card(row) for row in diagnostics["release_families"])
    series_rows = "".join(
        _series_row(row) for row in diagnostics["series_refresh_diagnostics"]
    )
    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>官方資料來源維運</title>
  <style>
    body {{ margin: 0; background: #f5f7f8; color: #17202a; font-family: -apple-system, BlinkMacSystemFont, "Noto Sans TC", sans-serif; }}
    main {{ width: min(1120px, calc(100% - 28px)); margin: auto; padding: 24px 0 48px; }}
    h1 {{ font-size: clamp(1.65rem, 5vw, 2.5rem); margin: 4px 0 10px; }}
    h2 {{ margin-top: 28px; font-size: 1.2rem; }}
    .eyebrow, .meta, dt {{ color: #5d6874; }}
    .summary, .families {{ display: grid; gap: 12px; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); }}
    .summary article, .family {{ background: white; border: 1px solid #d8dee5; border-radius: 8px; padding: 14px; }}
    .summary strong {{ display: block; font-size: 1.65rem; }}
    .family h3 {{ margin: 0 0 4px; font-size: 1rem; }}
    dl {{ display: grid; grid-template-columns: minmax(105px, auto) 1fr; gap: 5px 10px; margin: 12px 0; }}
    dd {{ margin: 0; overflow-wrap: anywhere; }}
    .status {{ font-weight: 700; color: #174f7a; }}
    .warning {{ color: #8b3f18; }}
    details {{ background: white; border: 1px solid #d8dee5; border-radius: 8px; padding: 12px; }}
    summary {{ cursor: pointer; color: #0b5cab; font-weight: 700; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 12px; font-size: .84rem; }}
    th, td {{ border-bottom: 1px solid #e2e6eb; padding: 8px 6px; text-align: left; vertical-align: top; }}
    a {{ color: #0b5cab; }} code {{ background: #edf0f3; padding: 2px 4px; border-radius: 4px; }}
    @media (max-width: 700px) {{ table, thead, tbody, tr, th, td {{ display: block; }} thead {{ display: none; }} tr {{ padding: 8px 0; border-bottom: 1px solid #d8dee5; }} td {{ border: 0; padding: 3px 0; }} }}
  </style>
</head>
<body><main>
  <p class="eyebrow">private NAS / research-only / revised diagnostic</p>
  <h1>官方資料發布與更新維運</h1>
  <p>這裡分開顯示「官方何時預定發布」與「本機 refresh 是否成功」。
  只有官方日曆有精確日期時才判斷 due；頻率或參考頁不足時不會冒充官方延遲。</p>
  <section class="summary">
    <article><strong>{int(diagnostics['release_family_count'])}</strong><span>官方發布家族</span></article>
    <article><strong>{int(diagnostics['series_diagnostic_count'])}</strong><span>監看序列</span></article>
    <article><strong>{int(diagnostics['family_due_or_missing_refresh_count'])}</strong><span>待更新／需查核</span></article>
    <article><strong>{int(diagnostics['series_with_failure_reason_count'])}</strong><span>有失敗原因序列</span></article>
  </section>
  <p><a href="/">返回總覽</a> · <a href="/api/source-operations.json">查看 JSON</a></p>
  <h2>每個官方發布來源</h2>
  <section class="families">{families}</section>
  <h2>逐序列 refresh drilldown</h2>
  <details><summary>展開 {int(diagnostics['series_diagnostic_count'])} 個序列</summary>
    <table><thead><tr><th>序列</th><th>發布家族</th><th>最新觀察</th><th>新鮮度</th><th>最近 refresh</th><th>原因</th></tr></thead>
    <tbody>{series_rows}</tbody></table>
  </details>
  <p class="meta">此頁不執行 refresh、不提供交易或配置指示，也不會由發布狀態推論目前景氣階段。</p>
</main></body></html>"""


def build_nas_source_operations_api(diagnostics: dict[str, Any]) -> str:
    return json.dumps(diagnostics, ensure_ascii=False, sort_keys=True)


def _family_card(row: dict[str, Any]) -> str:
    last_release = _release_display(row.get("last_official_release"), "尚無已登錄日期")
    next_release = _release_display(row.get("next_official_release"), "日曆尚未提供")
    reasons = "、".join(row.get("blocked_reason_codes", [])) or "無"
    precision = {
        "exact_schedule": "精確官方日期",
        "cadence_only": "僅發布頻率",
        "reference_only": "僅官方參考頁",
    }.get(str(row["calendar_precision"]), str(row["calendar_precision"]))
    warning = " warning" if row.get("blocked_reason_codes") else ""
    return f"""
    <article class="family" data-release-family="{escape(str(row['release_family_id']))}">
      <h3>{escape(str(row['title_zh']))}</h3>
      <p class="meta">{escape(str(row['agency_zh']))} · {escape(precision)}</p>
      <p class="status{warning}">{escape(str(row['release_monitor_status_zh']))}</p>
      <dl>
        <dt>序列</dt><dd>{escape(', '.join(row['series_ids']))}</dd>
        <dt>上次發布</dt><dd>{escape(last_release)}</dd>
        <dt>下次發布</dt><dd>{escape(next_release)}</dd>
        <dt>原因碼</dt><dd>{escape(reasons)}</dd>
        <dt>下一步</dt><dd>{escape(str(row['operator_next_action_zh']))}</dd>
      </dl>
      <a href="{escape(str(row['official_calendar_url']), quote=True)}" rel="noreferrer">官方發布頁</a>
    </article>"""


def _series_row(row: dict[str, Any]) -> str:
    reasons = ", ".join(row.get("failure_reason_codes", [])) or "無"
    return (
        "<tr>"
        f"<td><code>{escape(str(row['series_id']))}</code></td>"
        f"<td>{escape(str(row['release_family_id']))}</td>"
        f"<td>{escape(str(row.get('latest_observation_date') or '無'))}</td>"
        f"<td>{escape(str(row['freshness_status']))}</td>"
        f"<td>{escape(str(row['last_refresh_result']))}</td>"
        f"<td>{escape(reasons)}</td>"
        "</tr>"
    )


def _release_display(value: Any, fallback: str) -> str:
    if not isinstance(value, dict):
        return fallback
    return (
        f"{value['release_date']} {value.get('release_time', '')} "
        f"ET（參考期 {value.get('reference_period', '未標示')}）"
    ).strip()

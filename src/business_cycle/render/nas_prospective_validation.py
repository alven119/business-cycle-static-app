"""Traditional Chinese prospective validation wait-state page."""

from __future__ import annotations

from html import escape
from typing import Any


def render_nas_prospective_validation_page(
    state: dict[str, Any], *, navigation: list[dict[str, Any]]
) -> str:
    nav = "".join(
        f'<a href="{escape(str(row["path"]))}">{escape(str(row["label_zh"]))}</a>'
        for row in navigation
        if row.get("enabled")
    )
    blockers = "".join(
        f"<li>{escape(text)}</li>"
        for text in _blockers_zh(state)
    )
    return f"""<!doctype html>
<html lang="zh-Hant-TW"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>前瞻驗證進度｜景氣循環研究</title>
<style>{_styles()}</style></head><body>
<header><strong>景氣循環研究</strong><nav>{nav}</nav></header>
<main>
  <section class="hero"><p class="eyebrow">Prospective validation / calendar gate</p>
  <h1>前瞻驗證進度</h1><p>這裡只顯示日曆門檻、資料完整度與 registry metadata；不會偷看結果、
  自動啟動 protocol、輸出 candidate phase 或改寫 declared 榮景。</p></section>
  <section class="ribbon">
    <span><b>目前狀態</b> {_wait_label(state['current_wait_state'])}</span>
    <span><b>第一期</b> {escape(str(state['observation_period']))}</span>
    <span><b>Canonical as-of</b> {escape(str(state['canonical_as_of']))}</span>
    <span><b>最早人工 append</b> {escape(str(state['earliest_possible_manual_append_at']))}</span>
  </section>
  <section class="grid">
    <article><h2>評估月份</h2><p class="metric">{int(state['evaluation_month_count'])} / {int(state['minimum_evaluation_months'])}</p>
    <p>必須在 protocol 正式啟動後累積完整月份，現在不可回填。</p></article>
    <article><h2>Complete strict dates</h2><p class="metric">{int(state['complete_strict_date_count'])} / {int(state['minimum_complete_strict_dates'])}</p>
    <p>缺任何必要 point-in-time 輸入就 abstain，不會用 revised fallback。</p></article>
    <article><h2>Append-only registry</h2><p class="metric">{int(state['prospective_registry_record_count'])} 筆</p>
    <p>本頁寫入嘗試：{int(state['real_registry_write_attempt_count'])}。只能由明確人工命令啟動。</p></article>
  </section>
  <section class="panel"><h2>為什麼現在還不能 seal</h2><ul>{blockers}</ul></section>
  <section class="panel"><h2>模型變更規則</h2><p>若 evaluator、decision rule 或資料範圍改版，未來評估窗必須重置；
  既有 append-only records 保留，不能刪除或覆寫。</p></section>
  <p class="boundary">下一步：{escape(str(state['recommended_next_action']))}。本頁是 private NAS research-only 狀態，
  不代表經濟驗證完成，也不構成投資建議。</p>
</main></body></html>"""


def _blockers_zh(state: dict[str, Any]) -> list[str]:
    blockers = []
    if not state["canonical_as_of_reached"]:
        blockers.append("尚未到 2026-08-31 canonical as-of。")
    if not state["earliest_manual_append_reached"]:
        blockers.append("季度角色尚需等待至最早 2026-10-31 才可能完整。")
    if not state["protocol_started"]:
        blockers.append("前瞻 protocol 尚未由明確人工命令啟動。")
    if state["evaluation_month_count"] < state["minimum_evaluation_months"]:
        blockers.append("尚未累積 12 個完整前瞻評估月份。")
    if state["complete_strict_date_count"] < state["minimum_complete_strict_dates"]:
        blockers.append("尚未累積 12 個 complete strict dates。")
    if state["unseen_transition_event_count"] < 1:
        blockers.append("尚未觀察到一個未見的合法景氣轉折事件。")
    if state["unseen_non_recession_stress_event_count"] < 1:
        blockers.append("尚未觀察到一個未見的非衰退壓力事件。")
    return blockers


def _wait_label(value: str) -> str:
    return {
        "pre_period": "第一期尚未開始",
        "awaiting_canonical_as_of": "等待 canonical as-of",
        "awaiting_late_releases": "等待較晚發布資料",
    }.get(value, value)


def _styles() -> str:
    return """
body{margin:0;background:#f4f6f7;color:#182126;font:16px/1.6 system-ui,sans-serif}header{display:flex;gap:24px;align-items:center;padding:14px 5%;background:#18323a;color:white}nav{display:flex;gap:14px;flex-wrap:wrap}nav a{color:#d8eef0;text-decoration:none}main{max-width:1120px;margin:auto;padding:34px 5%}.hero h1{font-size:clamp(2rem,5vw,3.4rem);margin:.2rem 0}.eyebrow{color:#087f8c;font-weight:700}.ribbon,.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px;margin:24px 0}.ribbon span,article,.panel{background:white;border:1px solid #d7dfe2;padding:18px;border-radius:6px}.metric{font-size:2rem;font-weight:750;color:#8b3e2f;margin:.2rem 0}.panel{margin:14px 0}.boundary{border-left:4px solid #087f8c;padding:12px 16px;background:#e8f4f4}@media(max-width:640px){header{align-items:flex-start;flex-direction:column}.hero h1{font-size:2.2rem}}
"""

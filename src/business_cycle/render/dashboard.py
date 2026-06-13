"""Render a minimal static dashboard from a cycle snapshot."""

from __future__ import annotations

import json
import shutil
from html import escape
from pathlib import Path
from typing import Any

PHASE_ORDER = ("recession", "recovery", "growth", "boom")
DISCLAIMER_ZH = "本頁僅為總經資料整理與景氣循環判讀輔助，不構成投資建議。"


def build_dashboard(snapshot: dict[str, Any]) -> str:
    """Build a complete mobile-first HTML document from cycle_snapshot.json data."""

    _reject_secret_keys(snapshot)
    decision = _mapping(snapshot.get("current_phase_decision"))
    summary = _mapping(snapshot.get("summary"))
    phase_scores = sorted(
        _list_of_mappings(snapshot.get("phase_scores")),
        key=lambda phase: (_phase_sort_index(str(phase.get("phase_id", ""))), str(phase.get("phase_id", ""))),
    )
    indicator_scores = sorted(
        _list_of_mappings(snapshot.get("indicator_scores")),
        key=lambda indicator: str(indicator.get("indicator_id", "")),
    )
    warnings = [str(item) for item in snapshot.get("warnings", []) or []]
    failures = _mapping(snapshot.get("failures"))
    indicator_failures = _list_of_mappings(failures.get("indicator_failures"))
    phase_failures = _list_of_mappings(failures.get("phase_failures"))

    return f"""<!doctype html>
<html lang="zh-Hant">
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
    .grid {{ display: grid; grid-template-columns: 1fr; gap: 12px; }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
    }}
    .current {{ border-left: 4px solid var(--accent); }}
    .metric {{ display: flex; justify-content: space-between; gap: 12px; padding: 4px 0; }}
    .metric span:first-child {{ color: var(--muted); }}
    .score {{ font-size: 1.7rem; font-weight: 700; }}
    .warning {{ color: var(--warn); }}
    ul {{ margin: 8px 0 0; padding-left: 20px; }}
    .table-list {{ display: grid; gap: 10px; }}
    footer {{ margin: 28px 0 10px; padding-top: 16px; border-top: 1px solid var(--line); }}
    @media (min-width: 720px) {{
      main {{ padding: 24px; }}
      .phase-grid {{ grid-template-columns: repeat(4, 1fr); }}
      .indicator-grid {{ grid-template-columns: repeat(2, 1fr); }}
    }}
  </style>
</head>
<body>
<main>
  <header>
    <h1>景氣循環儀表板</h1>
    <div class="muted">generated_at: {_text(snapshot.get("generated_at"))}</div>
    <div class="muted">as_of: {_text(snapshot.get("as_of"))}</div>
    <p>{DISCLAIMER_ZH}</p>
  </header>

  <section>
    <h2>Current Phase</h2>
    <div class="card current">
      <h3>{_text(decision.get("current_phase_name_zh"))} ({_text(decision.get("current_phase_id"))})</h3>
      {_metric("decision_status", decision.get("decision_status"))}
      {_metric("confidence", _format_number(decision.get("confidence")))}
      {_metric("previous_phase_id", decision.get("previous_phase_id"))}
      {_metric("candidate_phase_id", decision.get("candidate_phase_id"))}
      {_metric("allowed_next_phase_id", decision.get("allowed_next_phase_id"))}
      <p>{_text(decision.get("reason_zh"))}</p>
    </div>
  </section>

  <section>
    <h2>Phase Scores</h2>
    <div class="grid phase-grid">
      {_phase_cards(phase_scores)}
    </div>
    <p class="muted">Phase score 不會直接取最高分當作 current phase；state machine 會考慮前一階段、相鄰轉換與信心。</p>
  </section>

  <section>
    <h2>Indicator Scores</h2>
    <div class="table-list indicator-grid">
      {_indicator_cards(indicator_scores)}
    </div>
  </section>

  <section>
    <h2>Warnings / Failures</h2>
    {_warnings_html(warnings)}
    {_failures_html(indicator_failures, phase_failures)}
  </section>

  <footer class="muted">
    <p>{DISCLAIMER_ZH}</p>
    <p>分數與階段判讀依賴資料品質、資料修正與模型假設。</p>
    <p>summary: current_phase_id={_text(summary.get("current_phase_id"))}, decision_status={_text(summary.get("decision_status"))}</p>
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


def _phase_cards(phase_scores: list[dict[str, Any]]) -> str:
    return "\n".join(
        f"""<article class="card">
  <h3>{_text(phase.get("phase_name_zh"))}</h3>
  <div class="muted">{_text(phase.get("phase_id"))}</div>
  <div class="score">{_text(_format_number(phase.get("score")))}</div>
  {_metric("confidence", _format_number(phase.get("confidence")))}
  {_metric("available_weight", _format_number(phase.get("available_weight")))}
  {_metric("stage_hint", phase.get("stage_hint"))}
  {_metric("missing_indicators", len(phase.get("missing_indicators") or []))}
</article>"""
        for phase in phase_scores
    )


def _indicator_cards(indicator_scores: list[dict[str, Any]]) -> str:
    cards: list[str] = []
    for indicator in indicator_scores:
        details = _mapping(indicator.get("details"))
        cards.append(
            f"""<article class="card">
  <h3>{_text(indicator.get("indicator_id"))}</h3>
  {_metric("score", _format_number(indicator.get("score")))}
  {_metric("confidence", _format_number(indicator.get("confidence")))}
  {_metric("method", indicator.get("method"))}
  {_metric("as_of", indicator.get("as_of"))}
  {_metric("selected_series_id", details.get("selected_series_id"))}
  <p>{_text(indicator.get("reason_zh"))}</p>
</article>"""
        )
    return "\n".join(cards)


def _warnings_html(warnings: list[str]) -> str:
    if not warnings:
        return '<p class="muted">目前沒有 snapshot warning。</p>'
    items = "\n".join(f'<li class="warning">{_text(warning)}</li>' for warning in warnings)
    return f"<ul>{items}</ul>"


def _failures_html(indicator_failures: list[dict[str, Any]], phase_failures: list[dict[str, Any]]) -> str:
    if not indicator_failures and not phase_failures:
        return '<p class="muted">目前沒有 pipeline failure。</p>'
    sections: list[str] = []
    if indicator_failures:
        sections.append("<h3>Indicator failures</h3>" + _failure_list(indicator_failures))
    if phase_failures:
        sections.append("<h3>Phase failures</h3>" + _failure_list(phase_failures))
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

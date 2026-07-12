"""Traditional Chinese private-NAS view for declared boom start governance."""

from __future__ import annotations

from html import escape
from typing import Any

from business_cycle.cycle_state.nas_declared_phase_start_registry import (
    APPLY_CONFIRMATION,
    ROLLBACK_CONFIRMATION,
)
from business_cycle.cycle_state.nas_governed_cycle_transition import (
    APPLY_TRANSITION_CONFIRMATION,
    ROLLBACK_TRANSITION_CONFIRMATION,
)


def render_nas_declared_phase_start_page(
    *,
    status: dict[str, Any],
    preview: dict[str, Any] | None = None,
    transition_preview: dict[str, Any] | None = None,
    confirmation_note: str = "",
    message_zh: str | None = None,
    error_zh: str | None = None,
) -> str:
    """Render the authenticated declared-start review and confirmation page."""

    age = _age_display(status)
    message = (
        f'<p class="notice success">{escape(message_zh)}</p>' if message_zh else ""
    )
    error = f'<p class="notice error">{escape(error_zh)}</p>' if error_zh else ""
    preview_html = _preview_html(preview, confirmation_note) if preview else ""
    rollback_html = _rollback_html(status)
    transition_html = _transition_html(
        status,
        transition_preview=transition_preview,
        confirmation_note=confirmation_note,
    )
    history_html = _transition_history_html(status)
    return f"""<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>景氣狀態設定</title>
<style>
body{{margin:0;background:#f4f6f8;color:#17212b;font-family:system-ui,sans-serif;line-height:1.55}}
main{{max-width:780px;margin:auto;padding:20px}}section{{background:#fff;border:1px solid #d9e0e6;padding:18px;margin:14px 0}}
h1,h2{{letter-spacing:0}}label{{display:block;font-weight:650;margin-top:12px}}input{{box-sizing:border-box;width:100%;padding:10px;border:1px solid #9aa8b4}}
button{{margin-top:14px;padding:10px 16px;border:0;background:#176b5b;color:#fff;font-weight:700;cursor:pointer}}
.danger button{{background:#9b2c2c}}.meta{{color:#52616d}}.notice{{padding:10px;border-left:4px solid}}
.success{{background:#e8f5ef;border-color:#176b5b}}.error{{background:#fff0f0;border-color:#9b2c2c}}
.check{{display:flex;gap:8px;align-items:flex-start;font-weight:500}}.check input{{width:auto;margin-top:5px}}
code{{overflow-wrap:anywhere}}a{{color:#075ea8}}
.table-wrap{{overflow-x:auto}}table{{width:100%;border-collapse:collapse}}th,td{{padding:8px;border-bottom:1px solid #d9e0e6;text-align:left}}
.compare-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;margin:12px 0}}.compare-grid article{{display:grid;gap:4px;padding:10px;background:#f4f6f8}}
</style></head><body><main>
<p><a href="/">返回總覽</a></p>
<h1>景氣狀態設定</h1>
<p class="meta">這裡管理的是你明確宣告的景氣狀態起始資訊，不是系統由最新資料推論的景氣階段。</p>
{message}{error}
<section>
  <h2>目前受治理狀態</h2>
  <p><strong>宣告階段：</strong>{escape(status['declared_current_phase_label_zh'])}</p>
  <p><strong>合法下一階段：</strong>{escape(status['legal_next_phase_label_zh'])}</p>
  <p><strong>目前階段起始：</strong>{escape(status['declared_phase_start_display_zh'])}</p>
  <p><strong>階段年齡：</strong>{escape(age)}</p>
  <p><strong>登錄來源：</strong>{escape(_registry_source_label(status))}</p>
</section>
<section>
  <h2>預覽起始日或起始區間</h2>
  <p>精確日期與區間只能擇一。區間只會顯示年齡範圍，不會產生假精度。</p>
  <form method="post" action="/cycle-state/preview">
    <label for="exact_start_date">精確起始日</label>
    <input id="exact_start_date" name="exact_start_date" type="date">
    <label for="window_start_date">或：起始區間開始</label>
    <input id="window_start_date" name="window_start_date" type="date">
    <label for="window_end_date">起始區間結束</label>
    <input id="window_end_date" name="window_end_date" type="date">
    <label for="confirmation_note">確認理由</label>
    <input id="confirmation_note" name="confirmation_note" required maxlength="500"
      placeholder="例如：依個人研究判斷，將此區間作為 declared boom 起始背景">
    <button type="submit">先預覽，不寫入</button>
  </form>
</section>
{preview_html}{rollback_html}{transition_html}{history_html}
<section><h2>安全邊界</h2><ul>
<li>只寫入 NAS 私有 cycle-state volume，不修改 repository canonical registry。</li>
<li>不使用目前總經資料猜起始日；只有明確確認的合法 transition 才能更改 declared phase。</li>
<li>不產生候選階段、正式目前階段、分數、排名或交易行動。</li>
<li>每次套用前保留備份，可由下方 rollback 恢復。</li>
</ul></section>
</main></body></html>"""


def _transition_html(
    status: dict[str, Any],
    *,
    transition_preview: dict[str, Any] | None,
    confirmation_note: str,
) -> str:
    if "transition_preview_allowed" not in status:
        return ""
    review = status["evidence_review"]
    lane_rows = "".join(
        "<tr>"
        f"<td>{escape(str(row['lane_id']))}</td>"
        f"<td>{escape(_lane_type_zh(str(row['lane_type'])))}</td>"
        f"<td>{escape(_lane_status_zh(str(row['lane_status'])))}</td>"
        f"<td>{int(row['supportive_evidence_count'])}</td>"
        f"<td>{int(row['contradictory_evidence_count'])}</td>"
        f"<td>{int(row['abstained_evidence_count'])}</td>"
        "</tr>"
        for row in review["lane_rows"]
    ) or '<tr><td colspan="6">目前沒有可用 evidence snapshot；不得據此自動切換。</td></tr>'
    if not status["transition_preview_allowed"]:
        form = (
            '<p class="notice error">請先在上方確認目前階段的起始日或起始區間，'
            "才可預覽下一個合法轉折。</p>"
        )
    else:
        form = f"""
  <form method="post" action="/cycle-state/transition/preview">
    <input type="hidden" name="requested_next_phase" value="{escape(status['legal_next_phase'])}">
    <label for="transition_exact_date">下一階段精確生效日</label>
    <input id="transition_exact_date" name="exact_effective_date" type="date">
    <label for="transition_window_start">或：生效區間開始</label>
    <input id="transition_window_start" name="window_start_date" type="date">
    <label for="transition_window_end">生效區間結束</label>
    <input id="transition_window_end" name="window_end_date" type="date">
    <label for="transition_note">轉折確認理由</label>
    <input id="transition_note" name="confirmation_note" required maxlength="500"
      placeholder="記錄你為何確認已進入下一個合法階段">
    <button type="submit">預覽階段切換，不寫入</button>
  </form>"""
    preview_html = (
        _transition_preview_html(transition_preview, confirmation_note)
        if transition_preview
        else ""
    )
    return f"""
<section>
  <h2>下一個合法階段確認</h2>
  <p><strong>{escape(status['declared_current_phase_label_zh'])}</strong> 只能依序進入
  <strong>{escape(status['legal_next_phase_label_zh'])}</strong>。以下 evidence 供你檢閱，
  不會自動替你確認轉折。</p>
  <div class="table-wrap"><table><thead><tr><th>Lane</th><th>類型</th><th>狀態</th>
  <th>支持</th><th>反對</th><th>Abstain</th></tr></thead><tbody>{lane_rows}</tbody></table></div>
  <p class="meta">Evidence as-of：{escape(str(review.get('snapshot_as_of') or '無'))}；
  data mode：{escape(str(review.get('data_mode') or 'unavailable'))}。</p>
  {form}{preview_html}
</section>"""


def _transition_preview_html(
    preview: dict[str, Any], confirmation_note: str
) -> str:
    if not preview["preview_valid"]:
        errors = "、".join(preview["input_validation_error_codes"])
        return f'<p class="notice error">轉折預覽未通過：{escape(errors)}</p>'
    before = preview["before_after_context"]["before"]
    after = preview["before_after_context"]["after"]
    fields = {
        "preview_token": preview["preview_token"],
        "requested_next_phase": preview["to_phase"],
        "exact_effective_date": preview["proposed_exact_effective_date"] or "",
        "window_start_date": preview["proposed_window_start_date"] or "",
        "window_end_date": preview["proposed_window_end_date"] or "",
        "confirmation_note": confirmation_note,
        "as_of": preview["as_of"],
    }
    hidden = "".join(
        f'<input type="hidden" name="{escape(key)}" value="{escape(str(value))}">'
        for key, value in fields.items()
    )
    context = f"""
  <div class="compare-grid">
    <article><b>切換前</b><span>{escape(before['declared_phase_label_zh'])} → {escape(before['legal_next_phase_label_zh'])}</span></article>
    <article><b>切換後</b><span>{escape(after['declared_phase_label_zh'])} → {escape(str(after['legal_next_phase_label_zh']))}</span></article>
    <article><b>新階段起始</b><span>{escape(after['start_display_zh'])}</span></article>
  </div>"""
    if not preview["live_transition_activation_enabled"]:
        return context + (
            '<p class="notice error">核心 preview／receipt／correction 已完成；為避免其他頁面仍使用舊階段內容，'
            "NAS 寫入會等 Phase 132 全頁原子 context routing 完成後才開啟。</p>"
        )
    return context + f"""
  <form method="post" action="/cycle-state/transition/apply">
    {hidden}
    <label class="check"><input type="checkbox" required name="evidence_review_acknowledged"
      value="true">我已檢閱支持、反對、缺失與 confirmation 邊界。</label>
    <label class="check"><input type="checkbox" required name="transition_confirmation"
      value="{escape(APPLY_TRANSITION_CONFIRMATION)}">我確認這是使用者宣告的合法景氣轉折。</label>
    <button type="submit">確認轉折並寫入 receipt</button>
  </form>"""


def _transition_history_html(status: dict[str, Any]) -> str:
    history = list(status.get("transition_history", []))
    if not history:
        return ""
    rows = "".join(
        "<li>"
        f"<code>{escape(str(row['receipt_id']))}</code> · "
        f"{escape(str(row['event_type']))} · "
        f"{escape(str(row['from_phase']))} → {escape(str(row['to_phase']))} · "
        f"{escape(str(row['timestamp_utc']))}</li>"
        for row in history
    )
    latest = status.get("latest_transition_event") or {}
    correction = ""
    if latest and status.get("live_transition_activation_enabled"):
        correction = f"""
  <form method="post" action="/cycle-state/transition/rollback" class="danger">
    <input type="hidden" name="receipt_id" value="{escape(str(latest['receipt_id']))}">
    <input type="hidden" name="expected_active_hash" value="{escape(status['active_registry_hash'])}">
    <label for="correction_note">Correction 理由</label>
    <input id="correction_note" name="correction_note" required maxlength="500">
    <label class="check"><input type="checkbox" required name="correction_confirmation"
      value="{escape(ROLLBACK_TRANSITION_CONFIRMATION)}">我確認新增 correction receipt；原事件不得刪除。</label>
    <button type="submit">建立 correction 並回復前一狀態</button>
  </form>"""
    return f"""
<section><h2>轉折 Receipt 歷史</h2><ol>{rows}</ol>
<p class="meta">Ledger hash chain：{'有效' if status.get('transition_hash_chain_valid') else '異常'}；
rollback 只新增 correction，不刪除原始 transition。</p>{correction}</section>"""


def _lane_type_zh(value: str) -> str:
    return {
        "continuation_context": "階段延續",
        "transition_watch": "轉折觀察",
        "transition_confirmation": "轉折確認",
    }.get(value, value)


def _lane_status_zh(value: str) -> str:
    return {
        "supportive_evidence_present": "已有支持證據",
        "contradictory_evidence_present": "反對證據存在",
        "mixed_evidence": "證據混合",
        "incomplete_evidence": "證據不完整",
        "explicit_abstention": "明確 abstain",
        "neutral_evidence": "中性",
    }.get(value, value)


def _preview_html(preview: dict[str, Any], confirmation_note: str) -> str:
    if not preview["preview_valid"]:
        errors = "、".join(preview["input_validation_error_codes"])
        return (
            '<section><h2>預覽未通過</h2><p class="notice error">'
            f"{escape(errors)}</p></section>"
        )
    proposed = preview["proposed_exact_start_date"] or (
        f"{preview['proposed_window_start_date']} 至 "
        f"{preview['proposed_window_end_date']}"
    )
    fields = {
        "preview_token": preview["preview_token"],
        "exact_start_date": preview["proposed_exact_start_date"] or "",
        "window_start_date": preview["proposed_window_start_date"] or "",
        "window_end_date": preview["proposed_window_end_date"] or "",
        "confirmation_note": confirmation_note,
        "as_of": preview.get("as_of", ""),
    }
    hidden = "".join(
        f'<input type="hidden" name="{escape(key)}" value="{escape(str(value))}">'
        for key, value in fields.items()
    )
    return f"""
<section>
  <h2>寫入前預覽</h2>
  <p><strong>擬套用：</strong>{escape(str(proposed))}</p>
  <p><strong>精度：</strong>{escape(preview['input_precision'])}</p>
  <p><strong>顯示規則：</strong>{escape(preview['phase_age_display_policy'])}</p>
  <p class="meta">來源 registry hash：<code>{escape(preview['source_registry_hash'])}</code></p>
  <form method="post" action="/cycle-state/apply">
    {hidden}
    <label class="check"><input type="checkbox" required name="apply_confirmation"
      value="{escape(APPLY_CONFIRMATION)}">我確認這是使用者宣告的研究背景，並同意寫入 NAS 私有 registry。</label>
    <button type="submit">確認並套用</button>
  </form>
</section>"""


def _rollback_html(status: dict[str, Any]) -> str:
    if not status["active_registry_override_present"]:
        return ""
    return f"""
<section class="danger">
  <h2>回復上一版</h2>
  <p>Rollback 會恢復最近一次套用前的 registry 備份。</p>
  <form method="post" action="/cycle-state/rollback">
    <input type="hidden" name="expected_active_hash"
      value="{escape(status['active_registry_hash'])}">
    <label class="check"><input type="checkbox" required name="rollback_confirmation"
      value="{escape(ROLLBACK_CONFIRMATION)}">我確認要回復上一版 declared start context。</label>
    <button type="submit">回復上一版</button>
  </form>
</section>"""


def _age_display(status: dict[str, Any]) -> str:
    if status["declared_phase_age_days"] is not None:
        return f"約 {status['declared_phase_age_days']} 天"
    age_range = status["declared_phase_age_range_days"]
    if age_range:
        return f"約 {age_range['minimum_days']} 至 {age_range['maximum_days']} 天"
    return "未知，需使用者確認"


def _registry_source_label(status: dict[str, Any]) -> str:
    if status["active_registry_source"] == "private_nas_override":
        return "NAS 私有受治理登錄"
    return "Repository 預設值（尚未確認起始資訊）"

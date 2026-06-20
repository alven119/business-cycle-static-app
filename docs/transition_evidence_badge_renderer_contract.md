# Transition Evidence Badge Renderer Contract

## 背景

Phase 7G1 定義 transition evidence badge schema，Phase 7G2 建立 valid / invalid fixtures 與 static validator。Phase 7G3 進一步定義未來 dashboard renderer 顯示這些 badge 時必須遵守的 contract，但本階段不修改 dashboard templates、不產生 `public/` output，也不接 live dashboard。

## 為什麼需要 Renderer Contract

Badge schema 能驗證輸入資料結構；renderer contract 則定義顯示層如何安全呈現。它防止 renderer 把 diagnostics badge 轉成正式 phase confirmation、買賣訊號、配置建議或 phase override。

## 與 Badge Schema / Fixtures 的關係

Renderer contract 必須建立在既有 schema 與 fixtures 之上：

- render 前必須先通過 `validate_transition_evidence_badge_object`。
- dashboard integration 前必須通過 fixture validation。
- renderer 只能輸出 safe display model，不得複製 prohibited fields。

## Input Contract

Renderer 未來只接受 validated badge object list。未驗證 badge 必須被拒絕。來源 schema 是 `specs/common/transition_evidence_badge_schema.yaml`，來源 fixtures 是 `specs/common/transition_evidence_badge_fixtures.yaml`。

## Safe Display Model

Safe display model 可包含 family、level、display name、summary、confidence、evidence date、diagnostics-only flag、formal decision impact、caveats、score、top contributors、warning flags 與 explanation。

Renderer 可額外產生：

- `badge_css_class`
- `badge_level_label_zh`
- `badge_family_label_zh`
- `display_caveat_summary_zh`

## Level Display Mapping

Level display mapping 將每個 family / level 轉成中文 label 與 severity。高 severity level 必須附加 suffix，例如「仍非正式階段切換」、「不是衰退確認或賣出訊號」、「不是正式復甦確認或買進訊號」。

## Required Caveats

所有 safe display model 必須保留或摘要顯示：

- experimental diagnostics，不代表正式階段切換。
- watch 不是買賣訊號。
- 不構成投資建議。

## Prohibited Fields

Renderer 不得輸出：

- `action`
- `buy_signal`
- `sell_signal`
- `reduce_signal`
- `add_signal`
- `allocation`
- `target_weight`
- `confirmed_phase_override`
- `current_phase_override`
- `decision_status_override`

## Prohibited Text Patterns

Renderer 顯示文字不得包含肯定式買賣、配置或正式階段確認語句，例如買進、賣出、加碼、減碼、調整配置、建議配置、confirmed phase、investment advice。否定式 caveat，例如「不是買進訊號」，是必要安全說明，不能被解讀為行動建議。

## Dashboard Integration Preconditions

未來若要接 dashboard，至少必須完成：

- schema validator passed
- fixture validator passed
- renderer contract validator passed
- generated site validation updated
- no formal decision impact tested
- no trade signal text tested
- caveats display tested

## Display Model Fixture Validation

Phase 7G4 新增 `specs/common/transition_evidence_badge_display_fixtures.yaml`，用 valid / invalid display model fixtures 檢查 renderer contract 是否能守住輸出邊界。

```bash
python scripts/validate_transition_evidence_badge_display_fixtures.py
```

CLI 會輸出 valid / invalid display fixture counts、通過數、拒絕數、unexpected pass / failure、expected error mismatch 與 `result=passed|failed`。這個 validator 不接 dashboard templates，也不產生 `public/` output。

## Valid Display Model Examples

Valid fixtures 覆蓋三類 display model：

- recession confirmation watch display
- boom ending strong warning display
- recovery strong watch display

它們都必須是 `diagnostics_only=true`、`formal_decision_impact=none`，並在 `display_caveat_summary_zh` 保留 experimental diagnostics、watch 不是買賣訊號與不構成投資建議。

## Invalid Display Model Examples

Invalid fixtures 故意加入：

- `buy_signal`
- `sell_signal`
- `allocation`
- `current_phase_override`
- `decision_status_override`
- prohibited text，例如「建議買進」或「建議賣出」
- `diagnostics_only=false`
- `formal_decision_impact` 非 `none`
- 缺少 global caveat

每個 invalid display model 都必須被 validator 拒絕。

## 為什麼 Display Model Fixtures 必須擋 Prohibited Text

即使欄位安全，顯示文字仍可能把 diagnostics 誤寫成行動建議或正式階段確認。Prohibited text fixtures 用來確認 renderer-level validator 能擋住「買進」、「賣出」、「加碼」、「減碼」、「調整配置」、「確認轉入復甦」等語句。

## 為什麼 Display Model Fixtures 必須擋 Phase Override / Action / Allocation

Display model 是 renderer 中間格式，不是 decision payload。任何 `action`、`allocation`、`target_weight`、`current_phase_override` 或 `decision_status_override` 都代表 schema boundary 被破壞，必須在 dashboard rendering 前失敗。

## 如何避免 Future Dashboard Renderer 誤用 Diagnostics Badge

未來接 dashboard 前，必須先跑 badge fixture validator、renderer contract summary 與 display fixture validator。Dashboard 只可讀 safe display fields，不可讀或推導 action / allocation / phase override；若 validator 發現 prohibited field 或 prohibited text，render phase 必須失敗。

## Allowed / Disallowed Future Dashboard Sections

允許的 future sections 僅限 diagnostics summary、phase detail evidence section、experimental evidence note。

禁止接到 portfolio action panel、buy/sell recommendation、allocation target panel、formal phase override banner。

## 為什麼本階段不接 Dashboard Renderer

Phase 7G3 是 contract planning。若現在直接接 renderer，會把 schema design 與 UI output 變更混在一起，難以驗證 no formal decision impact 與 no trade signal boundary。Dashboard integration 必須另開 phase，並更新 generated site validation。

## Recommended Next Phase

下一步是 Phase 7G4：transition evidence badge renderer fixture contract validator。該階段可建立 renderer display model fixtures，繼續驗證 output model 不包含 prohibited fields 或 prohibited text。

## Caveats

- 此為 renderer contract，不代表 dashboard 已接入。
- Evidence badge 僅供 diagnostics display。
- Evidence badge 不會改變 current_phase_id 或 decision_status。
- Watch 類訊號不是買賣訊號。
- 不構成投資建議。

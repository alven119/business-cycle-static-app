# Transition Evidence Badge Schema

## 背景

Phase 7G 已將 recession confirmation、boom ending watch、recovery watch 三類 experimental evidence 收斂成統一架構。Phase 7G1 進一步定義未來 dashboard diagnostics 可使用的 badge schema，但本階段不接 dashboard renderer、不產生 `public/` output，也不改正式模型。

## 為什麼需要 Evidence Badge Schema

Evidence badge 是 diagnostics display layer 的資料契約。它讓未來 dashboard 能一致顯示「衰退確認證據」、「榮景後期風險觀察」、「復甦證據形成中」，同時保證 badge 不會被誤用為正式 phase decision、resolver override 或 portfolio action。

## 三類 Badge Family

### 衰退確認證據

此 family 顯示 recession confirmation candidate evidence。允許 level 為 `none`、`weak`、`watch`、`confirmed_candidate`。即使出現 `confirmed_candidate`，在本 schema 中仍只代表 experimental diagnostics，不得單獨 confirmed recession。

### 榮景後期風險觀察

此 family 顯示 boom ending / late-cycle evidence。允許 level 為 `none`、`weak`、`watch`、`strong_late_cycle_warning`。Boom ending watch 不等於 confirmed recession，也不是減碼或賣出訊號。

### 衰退落底 / 復甦觀察

此 family 顯示 recovery / recession trough evidence。允許 level 為 `none`、`weak`、`recovery_watch`、`strong_recovery_watch`。Recovery watch 不等於正式復甦確認，也不是買進或加碼訊號。

## Badge Object Schema

每個 badge 至少需要：

- `family_id`
- `level`
- `display_name_zh`
- `summary_zh`
- `confidence`
- `evidence_date`
- `diagnostics_only`
- `formal_decision_impact`
- `caveats_zh`

`diagnostics_only` 必須是 `true`，`formal_decision_impact` 必須是 `none`。`confidence` 必須落在 `0.0` 到 `1.0`。

## Allowed And Prohibited Fields

允許欄位只描述 diagnostics evidence，例如 score、top contributors、warning flags、source artifacts 與中文說明。

禁止欄位包括 `action`、`buy_signal`、`sell_signal`、`allocation`、`target_weight`、`confirmed_phase_override`、`current_phase_override`。這些欄位會讓 diagnostics badge 變成決策或交易訊號，因此必須被 validator 拒絕。

## 為什麼 Badge 不得改變 Current Phase

Phase 7G1 只定義 display schema。正式 `current_phase_id` 與 `decision_status` 仍由既有 deterministic model / resolver 管理。Evidence badge 若能改 phase，會繞過正式 scoring、resolver guardrails 與 historical validation。

## 為什麼 Badge 不能包含買賣訊號

Watch 類 evidence 可能提前、延後或過度密集。沒有 portfolio backtest、turnover analysis 與 false-signal cost analysis 前，badge 不得包含買進、賣出、減碼、加碼或 allocation 欄位。

## Dashboard Contract

本階段 `allowed_dashboard_contract.allowed_now=false`。若未來接 dashboard，必須另開 phase，只能以 diagnostics badge / explanation 顯示，且必須明確顯示：

- experimental diagnostics，不代表正式階段切換。
- watch 不是買賣訊號。
- 不構成投資建議。

## Validation Rules

Validator 必須檢查：

- family 必須是 schema 定義的三類之一。
- level 必須屬於該 family 的 allowed levels。
- `diagnostics_only=true`。
- `formal_decision_impact=none`。
- 不得包含 prohibited fields。
- caveats 必須包含不構成投資建議。

## Recommended Next Phase

下一步是 Phase 7G2：transition evidence badge static validator。該階段可加入 sample badge fixtures 與 static validation，確認未來 dashboard diagnostics badge 不包含正式決策或投資行動欄位。

## Caveats

- 使用修訂後歷史資料，不等同當時投資人可見資料。
- 此為 experimental diagnostics schema，不代表正式模型已更新。
- Evidence badge 不會改變正式景氣階段。
- Watch 類訊號不是買賣訊號。
- 不構成投資建議。

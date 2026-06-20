# Cycle Transition Evidence Architecture

## 背景

Phase 7F 系列完成三類 experimental evidence：recession confirmation、boom ending watch、recovery watch。每一類都有自己的 diagnostics、rule、overlay 與 integration guardrails。

Phase 7G 的目的不是把它們接入正式模型，而是統一 evidence architecture，明確定義哪些 evidence 可作 diagnostics，哪些只能作 future research input，以及哪些用途被禁止。

## 為什麼要整合 Evidence Architecture

如果不先定義共同邊界，watch 類訊號容易被誤用成 phase confirmation 或 portfolio action。統一架構可以讓後續 dashboard badge、transition risk research、Phase 8 / Phase 9 portfolio policy planning 共享同一套語意。

## Evidence Family

### Recession Confirmation

用途是確認 recession 是否成立，降低 false confirmed recession。它可作為 dashboard diagnostics 與 future transition risk research input，但不得在正式整合驗證前直接覆寫 `current_phase_id`。

### Boom Ending Watch

用途是提示榮景後期與衰退前風險。Boom ending watch 不等於 confirmed recession，也不是直接減碼或賣出訊號。它可作為 future transition risk 或 portfolio policy research input，但必須先完成 persistence、cooldown、density threshold 與 portfolio backtest。

### Recovery Watch

用途是提示衰退落底與復甦證據形成。Recovery watch 不等於正式復甦確認，也不是買進訊號。Policy easing 與 financial easing 不得單獨確認 recovery；recession context gate 必須保留。

## 禁止用途

Watch 類訊號不得直接：

- 改變正式 `current_phase_id`。
- confirmed recession 或 confirmed recovery。
- 觸發買進、賣出、加碼或減碼。
- 對外呈現為投資建議。

## 為什麼 Watch 不能等於 Phase Confirmation

Watch 是 evidence layer，不是 resolver。正式 phase confirmation 仍需要正式 phase scoring、state machine persistence、confidence、coverage、hysteresis 與 full-horizon acceptance。Watch 可以提示風險或證據形成，但不能替代決策器。

## 為什麼 Watch 不能等於買賣訊號

Phase 7F overlay 顯示 watch 可能有很長 lead time 或較高 density。例如 recovery watch 可早於原始 recovery phase 多個月，boom ending watch 也可能長期存在。直接把 watch 當買賣訊號會造成過早或過度交易，必須等 portfolio backtest。

## Dashboard Diagnostics Contract

目前 dashboard integration 不允許。未來若接入，只能用 diagnostics badge / explanation 呈現，例如：

- 衰退確認證據
- 榮景後期風險觀察
- 復甦證據形成中

Dashboard 必須顯示 caveats：experimental evidence 不代表正式階段切換，watch 不是買賣訊號，不構成投資建議。

## Future Transition Risk Contract

Transition risk 可作 future research input，但不得直接覆寫 state machine。啟用前必須定義 persistence、cooldown、density threshold、false-positive backtest 與 no direct phase override。

## Future Portfolio Policy Contract

Portfolio policy 必須等 Phase 8 / Phase 9 才能研究。啟用前至少需要 portfolio backtest、drawdown analysis、turnover analysis、false-signal cost analysis 與 revised/vintage data limitation documentation。

## Phase 8 / Phase 9 關係

Phase 7G 只整理 evidence architecture。Phase 8 / Phase 9 可以使用 evidence 作為 research input，但不得直接從 Phase 7G 產生 allocation、買賣建議或 live portfolio action。

## Recommended Next Phase

建議下一步是 Phase 7G1：design transition evidence badge schema。7G1 可設計 dashboard diagnostics 用的 badge schema，但仍不接入正式 dashboard output。另一條路是開始 Phase 8 portfolio policy research planning。

## Caveats

- 使用修訂後歷史資料，不等同當時投資人可見資料。
- 此為 experimental evidence architecture，不代表正式模型已更新。
- Watch 類訊號不是買賣訊號。
- 不構成投資建議。

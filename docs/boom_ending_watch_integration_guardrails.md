# Boom Ending Watch Integration Guardrails

## 背景

Phase 7F2 建立了 boom ending candidate indicators、refined scoring、watch rule 與 full-horizon overlay。這些結果顯示 boom ending watch 對 dotcom 與 GFC 具備 historical early-warning value，但仍是 experimental diagnostics，不是正式模型輸出。

## Phase 7F2.5 Overlay 結論

Phase 7F2.5 overlay 顯示：

- dotcom 與 GFC 在 confirmed recession 前已出現 boom ending watch。
- euro debt slowdown 沒有 excessive watch。
- late cycle 2018 有 watch，但未達 excessive watch。
- global watch density 約 0.4563，代表 watch 有辨識力，但密度仍偏高。
- strong warning density 約 0.004，代表 strong layer 很保守。
- COVID 需要外生衝擊 caveat，因為 boom ending 指標可能是同步壓力反映，不代表事前預測。

## 為什麼 Watch 有價值

Boom ending watch 可比 confirmed recession 更早提示 late-cycle risk。它適合先作為 dashboard diagnostics 或 backtest diagnostics，協助使用者理解榮景後段壓力是否累積。

## 為什麼 Watch 不能直接等於減碼

Watch density 偏高，若直接轉成配置行動，可能造成過早減碼或過度交易。任何 portfolio policy 使用前，都必須先建立 persistence、cooldown、confirmation 與 portfolio backtest。

## 為什麼 Watch 不能 Confirmed Recession

Boom ending watch 表示 late-cycle risk，不是衰退確認。Confirmed recession 仍需要 recession confirmation evidence、phase score、transition logic 與多期確認。Boom ending watch 不得直接改 current phase，也不得作為 recession confirmation gate。

## 未來可行整合模式

- Diagnostic badge only：可先顯示榮景後期風險 badge，不影響正式判斷。
- Transition risk boost：未來可在 watch 具備 persistence 且與 recession watch 同向時，提高 transition risk 顯示，但不改 current phase。
- Portfolio policy input：未來可作為 Phase 8 / Phase 9 配置策略研究 input，但不是買賣訊號。
- Recession confirmation gate：目前不允許。

## Live Integration 前必須通過的 Guardrails

- Watch density 必須有上限。
- Watch persistence 必須定義。
- Watch 解除與再觸發必須有 cooldown。
- Boom ending watch 不得直接 confirmed recession。
- 外生衝擊案例需顯示 caveat。
- 任何配置行動前必須完成 portfolio backtest。

## 與 Phase 8 / Phase 9 Portfolio Policy 的關係

Boom ending watch 可作為未來 70/50/30 policy 或其他配置策略的 early-warning research input，但必須先經 portfolio backtest。Phase 7F2.6 不接 portfolio allocation，也不產生交易建議。

## 為什麼下一步轉向 Recession Trough / Recovery Indicators

目前已完成 recession confirmation 與 boom ending early-warning 的 experimental guardrails。若要形成完整減碼與再加碼流程，還需要補齊衰退落底與復甦起點指標，因此下一步應進 Phase 7F3。

## Caveats

- 使用修訂後歷史資料，不等同當時投資人可見資料。
- 此為 experimental overlay / integration guardrails，不代表正式模型已更新。
- Boom ending watch 不等於 confirmed recession。
- Boom ending watch 不是買賣訊號。
- 不構成投資建議。

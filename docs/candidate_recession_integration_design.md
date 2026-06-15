# Candidate Recession Integration Design

## Background

Phase 7F1 建立了一批 experimental recession confirmation candidate indicators，並完成 diagnostics、rule report 與 full-horizon overlay。這些結果顯示 candidate rule 對降低 false confirmed recession 有幫助，但目前仍不能直接接入正式模型。

本文件定義未來整合 candidate recession rule 的 guardrails。它不會修改正式 phase scoring、不會修改 resolver，也不會讓 live dashboard 使用 candidate indicators。

## What Phase 7F1.2 Diagnostics Showed

Phase 7F1.2 將 candidate scores 放入固定 diagnostic points。結果顯示：

- COVID 2019-02-28 為 `partial`，比較適合視為 watch，而不是 confirmed recession。
- COVID 2020-03-31 與 GFC 2008-10-31 具有較強 confirmed support。
- euro debt 2011 與 late cycle 2018 主要為 weak 或 partial，不適合直接 confirmed recession。
- 續領失業救濟金、投保失業率、金融壓力、信用利差、實質個人消費支出、工業生產等指標有辨識力。

這代表 candidate indicators 有助於區分局部放緩與較廣泛的衰退壓力。

## What Phase 7F1.3 Rule Showed

Phase 7F1.3 的 experimental rule 不只看 weighted score，也檢查 group breadth、high-confidence signal count 與 high-signal count。固定 diagnostic points 的結果為：

- `confirmed`：COVID 2020-03-31、GFC 2008-10-31。
- `watch`：COVID 2019-02-28、COVID 2020-04-30、GFC 2007-12-31、dotcom 2001-01-31。
- `weak`：euro debt 2011-12-31、late cycle 2018-12-31。

這組結果符合既定 diagnostic expectations，但它仍只是 experiment，不是正式模型結論。

## What Phase 7F1.4 Full-Horizon Overlay Showed

Phase 7F1.4 將 candidate rule 疊加到 full-horizon scenario timeline：

- COVID 2019 early false confirmed recession 可被降級。
- GFC 2008 confirmed recession 得到 candidate confirmed support。
- COVID 2020 在 diagnostic level 保留 confirmed support。
- euro debt / late cycle 2018 沒有新增 false confirmed recession。
- dotcom 原始 confirmed recession 被降為 watch，沒有 overlay confirmed recession。

因此 candidate rule 有診斷價值，但不能直接作為硬性 confirmed recession gate。

## Why Hard Gate Is Not Safe Yet

若規定 candidate status 必須為 `confirmed`，正式模型才可以 confirmed recession，dotcom_bubble 可能被漏掉。這代表 hard gate 會降低 false positive，但也可能造成 false negative。

目前較安全的方向是 soft filter：candidate `confirmed` 可以支持 confirmed recession；candidate `watch` 則應維持 transition_watch 或 delayed confirmation，並搭配 persistence、原始 recession score、phase score margin 與 scenario acceptance。

## Recommended Future Integration Modes

1. `diagnostic_only`：僅在 backtest / dashboard diagnostics 顯示 candidate recession context，不影響正式 decision。風險最低。
2. `soft_confirmation_filter`：candidate `confirmed` 支持 confirmed recession；candidate `watch` 不直接擋掉歷史衰退，而是要求 persistence 或其他 evidence path。風險中等。
3. `hard_confirmation_gate`：candidate 必須 confirmed 才能 confirmed recession。現在不允許，因為 dotcom 風險尚未解決。

## Acceptance Guardrails Before Live Integration

正式整合前至少要通過：

- 擋掉 COVID 2019 early false confirmed recession。
- 保留 GFC 2008 confirmed recession。
- 保留 COVID 2020 confirmed support。
- dotcom 不可完全失去 recession confirmation；若 candidate 只給 watch，必須有 watch persistence 或其他 evidence path。
- euro debt slowdown 不新增 confirmed recession。
- late cycle 2018 不新增 confirmed recession。

任何 live integration 都應先在 full-horizon calibration、acceptance review 與 out-of-sample cases 上比較 baseline vs experiment。

## Why Next Phase Should Be Boom Ending Indicators

Recession confirmation 通常偏晚。若目標是改善景氣循環判讀與配置節奏，下一步應補強榮景期結束與衰退前風險指標，例如 yield curve、credit spread、financial stress、policy reversal、production/orders momentum 與就業市場從過熱轉弱的訊號。

因此 Phase 7F2 應優先實作 boom ending candidate indicators，而不是把 current candidate recession rule 直接接進正式模型。

## Caveats

- 使用修訂後歷史資料，不等同當時投資人可見資料。
- 本文件只描述 experimental diagnostics 與 integration guardrails，不代表正式模型已更新。
- 本內容僅供總經研究與模型校準，不構成投資建議。

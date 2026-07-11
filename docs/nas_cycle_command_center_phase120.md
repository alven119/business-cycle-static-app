# Phase 120：景氣循環指揮中心與專業導覽

Phase 120 將 NAS 首頁從資料快照與維運資訊的順序堆疊，改為以使用者研究流程為中心的景氣循環指揮中心。

## 首頁先回答的問題

1. 目前治理登錄的景氣階段是什麼？
2. 合法下一階段是什麼？
3. 榮景延續、榮景結束觀察、衰退觀察與衰退確認各自需要哪些資料？
4. 哪些關鍵指標已有 revised 數值，哪些資料缺漏或過期？
5. 目前畫面顯示的是 raw observation、input readiness，還是真正的 transition evidence？

## 畫面結構

- 桌面版使用固定側欄，手機版使用五項底部導覽。
- 主區第一層顯示 declared 榮景、合法 `榮景 -> 衰退` 轉折與 phase age。
- 四條 transition lane 明確區分 continuation、watch 與 confirmation。
- 五個 transition-critical 指標提供最新 revised 值、日期、新鮮度與指標詳情連結。
- trust ribbon 固定揭露 revised data mode、資料截至日、可用角色數與 evaluator 接線狀態。
- 資料健康區顯示 refresh、fresh/stale、chart coverage 與排程狀態。

## 語意邊界

本 Phase 沒有將 live transition evaluator 接進首頁。`input_ready_evaluation_pending` 只表示需要的資料已存在，不表示支持或反對轉折。raw value、資料新鮮度與 chart availability 都不能自行形成 watch 或 confirmation。

首頁仍不輸出 standalone current phase classifier、candidate phase、phase score、phase rank、phase winner、個人化配置或交易行動。

## 後續產品路徑

- Phase 121：指標學習詳情、書中觀察方法、互動圖與 recession shading。
- Phase 122：將 live evidence evaluator 接入四條 transition lane。
- Phase 123：declared-phase-linked 書籍配置研究模板。
- Phase 124：歷史事件選擇器、月度 playhead 與 strict/revised replay。
- Phase 125：可理解的 cash-flow-aware backtest UX。

Phase 120 的專業導覽保留上述入口，但未完成的功能一律標示規劃階段，不建立假路由或空白可操作頁面。

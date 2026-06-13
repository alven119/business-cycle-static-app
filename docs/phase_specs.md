# Phase Specs

Phase 3A 建立 phase-level spec loader 與 schema。這一步只定義 phase scoring 需要的資料結構，不計算 phase score，也不輸出 `current_phase`。

## Phase Spec 的角色

Phase spec 描述一個景氣階段需要觀察哪些 indicators、各自權重、角色與最低資料覆蓋要求。它是後續 phase scoring 的設定來源。

`specs/phases` 目前包含四個 MVP phase specs：

- `recovery.yaml`：復甦期，聚焦勞動市場壓力下降、消費回溫與訂單改善。
- `growth.yaml`：成長期，聚焦消費、投資、貿易與就業的廣泛改善。
- `boom.yaml`：榮景期，聚焦活動強勁、勞動市場緊俏，以及利率與能源等晚週期壓力 proxy。
- `recession.yaml`：衰退期，聚焦就業、消費、投資與貿易活動惡化。

這些都是 MVP specs，不宣稱已完全涵蓋書中所有指標，也不是最終景氣階段判斷。

## Indicator Score 與 Phase Score 的差別

Indicator score 是單一指標的 0-100 分數與 confidence。

Phase score 則需要整合多個 indicator score、權重、資料可用性、confidence、missing data 與 stale data。Phase 3A 只建立 phase score 的 schema，不實作 aggregation。

## Weight / Role / Available Weight

`weight` 表示 indicator 在該 phase spec 中的相對重要性。Loader 會保留 `raw_total_weight`，並把 indicator weights normalize，方便後續 aggregation。

`role` 描述 indicator 的用途：

- `core`：核心證據
- `confirmation`：確認訊號
- `warning`：警示或反向風險
- `optional`：輔助訊號

`available_weight` 是後續 scoring 時實際有可用資料的權重總和。若核心指標缺漏，phase score 的 confidence 應下降。

## signal_transform

`signal_transform` 定義 indicator score 如何轉成該 phase 的支持訊號：

- `as_is`：直接使用 indicator score。
- `inverted`：使用 `100 - indicator score`。

預設是 `as_is`。Recovery 目前四個 MVP indicators 都使用 `as_is`，因為這些 indicator 的改善分數對 recovery 是正向支持。Recession 則對多數活動與就業健康指標使用 `inverted`，避免把「經濟改善」誤當成衰退支持訊號。

`signal_note_zh` 可補充為什麼該 phase 要這樣解讀 indicator score。

## minimum_available_weight

`minimum_available_weight` 定義一個 phase score 至少需要多少資料覆蓋。若低於門檻，後續 phase scoring 不應產生高信心結果。

## early / mid / late Thresholds

`early_mid_late_thresholds` 只提供 phase 內位階提示，例如復甦早期、中期、晚期。它不是 `current_phase` 判斷，也不是 state machine transition。

## 為什麼 Phase 3A 還不做 current_phase

`current_phase` 需要比較多個 phase scores、transition policy、persistence、confidence 與 state machine。Phase 3A 只定義單一 phase spec 的 schema 與 loader，避免太早把設定與決策邏輯混在一起。

即使四個 MVP phase specs 都能被 scoring，也不能直接取最高 phase score 當成 `current_phase`。四階段判斷需要 state machine 與 transition rules 確認順序、持續性、資料覆蓋與信心。

## 不應用單一指標直接判斷景氣階段

單一指標可能落後、修正、缺值或受短期噪音影響。例如失業率偏落後，初領失業救濟金較高頻但波動較大。Phase spec 必須把多個 indicator 的 evidence 結合起來，不能把任一單一最新值直接當成景氣階段判斷。

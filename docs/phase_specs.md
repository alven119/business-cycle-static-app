# Phase Specs

Phase 3A 建立 phase-level spec loader 與 schema。這一步只定義 phase scoring 需要的資料結構，不計算 phase score，也不輸出 `current_phase`。

## Phase Spec 的角色

Phase spec 描述一個景氣階段需要觀察哪些 indicators、各自權重、角色與最低資料覆蓋要求。它是後續 phase scoring 的設定來源。

`specs/phases/recovery.yaml` 目前是 MVP spec，聚焦復甦期的四個核心觀察：

- 初領失業救濟金
- 實質零售銷售
- 耐久財新訂單
- 失業率

這不宣稱已完全涵蓋書中所有指標。

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

## minimum_available_weight

`minimum_available_weight` 定義一個 phase score 至少需要多少資料覆蓋。若低於門檻，後續 phase scoring 不應產生高信心結果。

## early / mid / late Thresholds

`early_mid_late_thresholds` 只提供 phase 內位階提示，例如復甦早期、中期、晚期。它不是 `current_phase` 判斷，也不是 state machine transition。

## 為什麼 Phase 3A 還不做 current_phase

`current_phase` 需要比較多個 phase scores、transition policy、persistence、confidence 與 state machine。Phase 3A 只定義單一 phase spec 的 schema 與 loader，避免太早把設定與決策邏輯混在一起。

## 不應用單一指標直接判斷景氣階段

單一指標可能落後、修正、缺值或受短期噪音影響。例如失業率偏落後，初領失業救濟金較高頻但波動較大。Phase spec 必須把多個 indicator 的 evidence 結合起來，不能把任一單一最新值直接當成景氣階段判斷。


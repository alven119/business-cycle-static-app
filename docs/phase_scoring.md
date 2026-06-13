# Phase Scoring

Phase 3B 建立單一 phase 的 score aggregation。它把多個 indicator-level scores 依照 phase spec 的權重整合成 `PhaseScoreResult`，但不選出 `current_phase`。

## 角色

Phase score aggregation 的輸入是：

- `PhaseScoringSpec`
- 多個 `IndicatorScoreResult`

輸出是單一 phase 的：

- score
- confidence
- available_weight
- missing_indicators
- contributing_indicators
- stage_hint
- reason_zh

## Indicator Score 與 Phase Score 的差別

Indicator score 只描述單一指標，例如失業率、初領失業救濟金或零售銷售。

Phase signal score 是 indicator score 經過 phase-specific `signal_transform` 後的分數。Phase score 則是把 phase spec 內列出的 phase signal scores 依權重整合。它仍然不是最終景氣階段判斷，因為最終判斷需要比較多個 phases、transition policy、persistence 與 state machine。

## Signal Transform

`signal_transform` 定義 indicator score 如何轉成特定 phase 的支持度：

- `as_is`：`phase_signal_score = indicator_score`
- `inverted`：`phase_signal_score = 100 - indicator_score`

例如失業率改善對 recovery 是正向，因此 recovery 可以使用 `as_is`。但如果未來建立 recession spec，同一個「失業率改善高分」對 recession 可能應該是反向訊號，因此需要 `inverted`。

不能直接把單一 indicator score 當成所有 phases 的支持度，因為同一個經濟訊號對不同階段可能有不同意義。

## Weighted Contribution

每個 contributing indicator 會輸出：

- `indicator_id`
- `original_score`
- `phase_signal_score`
- `confidence`
- `weight`
- `weighted_contribution`
- `role`
- `signal_transform`

計算方式：

```text
phase_signal_score = indicator_score 或 100 - indicator_score
weighted_contribution = phase_signal_score * normalized_weight
phase_score = sum(weighted_contribution) / available_weight
```

只使用 phase spec 中列出的 indicators。未列出的 indicator score 會被忽略。

## Available Weight

`available_weight` 是有可用 indicator score 的 normalized weight 總和。

若 `available_weight` 低於 `minimum_available_weight`，仍可輸出 phase score，但 confidence 必須下調，並在 `reason_zh` 說明資料覆蓋不足。

## Confidence

Phase confidence 會受到以下因素影響：

- available_weight
- contributing indicator confidence
- confidence_policy 中的 missing role penalty

例如 missing core indicator 的 penalty 應大於 missing optional indicator。單一高分 indicator 即使 score 很高，只要 available_weight 不足，也不能產生高 confidence。

## early / mid / late

`stage_hint` 依 `early_mid_late_thresholds` 判斷：

- `early`
- `mid`
- `late`

這只是 phase 內位階提示，不是 `current_phase`，也不是四階段最終判斷。

## 為什麼 Phase 3B 還不做 current_phase

`current_phase` 需要多個 phase scores、transition radar、persistence、confidence、available_weight 與 state machine 一起判斷。Phase 3B 只計算單一 phase 分數，避免把 aggregation 與狀態轉換混在一起。

Phase 3E 新增 growth、boom、recession 三個 MVP specs 後，系統可以對四個 phase 都產生 score。這仍然不是 `current_phase` 判斷，因為景氣循環有順序與持續性限制，不能只把分數最高的 phase 當成目前階段。

## 不靠單一高分指標判斷景氣階段

單一 indicator 可能有短期噪音、修正、缺值或落後性。Phase scoring 必須看多個 indicators 的 weighted evidence 與 available_weight，不能因為一個指標高分就直接判斷景氣階段。

同理，也不能只因某個 phase score 最高就直接宣告景氣階段。後續仍需要 state machine、transition policy、persistence、confidence 與 missing data impact 共同決定。

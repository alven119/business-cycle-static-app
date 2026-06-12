# Indicator Scoring Dispatcher

Phase 2C 建立 indicator scoring dispatcher。這一層負責把 indicator spec 連到正確的 single-indicator scoring method，輸出 `IndicatorScoreResult`。

## 為什麼需要 Dispatcher

Indicator catalog 只應描述指標如何被評分，例如 `score_method`、方向、觀察窗、確認窗與 stale 規則。Dispatcher 讓後續流程可以依照 spec 呼叫一致的 scoring API，而不需要在每個使用端手寫 method selection。

## Spec 如何對應 Scoring Method

`IndicatorScoringSpec` 包含：

- `indicator_id`
- `score_method`
- `direction`
- `date_column`
- `value_column`
- `parameters`
- `stale_after_days`
- `public_explanation_zh`

Dispatcher 目前支援：

- `level_percentile_score`
- `moving_average_slope_score`
- `yoy_momentum_score`
- `peak_trough_reversal_score`

若 `score_method` 不支援，或必要參數缺漏，dispatcher 會丟出明確錯誤。

## as_of 如何避免偷看未來

`score_indicator(..., as_of=...)` 會把 observations 限制在 `date <= as_of`。這可以避免 scoring method 在回測或歷史 snapshot 中偷看到未來資料。

Dispatcher 的 output details 會記錄：

- method
- parameters
- as_of
- available_observations
- stale_after_days

## stale_after_days 如何影響 Confidence

Dispatcher 會把 `stale_after_days` 傳給 scoring method。若最新可用資料距離 `as_of` 太久，score 可以保留，但 confidence 會下降。這避免 stale data 產生高信心訊號。

## 這一層不是 Phase Scoring

Dispatcher 只處理單一 indicator。它不計算 phase score、不輸出 `current_phase`、不做 transition radar，也不產生投資建議。Phase scoring 需要等每個 indicator 都有 score/confidence 後，才在後續階段處理 coverage、權重、persistence 與 state machine。


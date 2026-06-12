# Batch Indicator Scoring

Phase 2F 建立 indicator layer 的批次 scoring pipeline。它會從 catalog 載入 indicator scoring specs，讀取本機 raw CSV observations，逐一呼叫 dispatcher，最後輸出 indicator-level JSON。

## 角色

Batch indicator scoring 負責把多個單一指標評分結果集中到同一份 output。它仍然只處理 indicator，不計算 phase score，也不輸出 `current_phase`。

## 串接流程

1. `specs/indicator_catalog.yaml` 提供 indicator 設定。
2. `load_indicator_scoring_specs()` 建立 `IndicatorScoringSpec`。
3. `scripts/score_indicators.py` 從 `data/raw/fred/{SERIES_ID}.csv` 讀 observations。
4. `score_indicator_batch()` 對每個 indicator 呼叫 `score_indicator()`。
5. `write_indicator_scores_json()` 寫出 `data/derived/indicator_scores.json`。

## 為什麼 failure 不中斷整批

總經資料常有發布落差、缺檔、stale 或單一 series 失敗。若一個 indicator 失敗就中斷整批，後續流程無法看到其他可用指標。因此 batch scoring 會把失敗記錄在 `failures`，讓成功的 indicators 仍然輸出。

## as_of 如何避免偷看未來

CLI 的 `--as-of YYYY-MM-DD` 會傳給 dispatcher。Dispatcher 和 scoring method 只使用 `date <= as_of` 的 observations，避免歷史評分或回測時偷看未來資料。

## Output JSON

預設 output：

```text
data/derived/indicator_scores.json
```

格式包含：

- `summary.total_indicators`
- `summary.scored_indicators`
- `summary.failed_indicators`
- `results`
- `failures`

`data/derived/` 已被 `.gitignore` 排除，不應 commit。

## 仍然不是 Phase Scoring

Batch indicator scoring 只產生 indicator-level `score` 與 `confidence`。它不做 phase aggregation、不輸出 `current_phase`、不做 dashboard，也不產生投資建議。


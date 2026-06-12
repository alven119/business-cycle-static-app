# Indicator Catalog

`specs/indicator_catalog.yaml` 是 indicator layer 的設定來源。它描述每個總經指標的資料來源候選、頻率、分類、scoring method、方向、參數、stale 規則與公開說明。

## candidate_series vs verified_series

`candidate_series` 表示目前只是候選資料序列，例如 FRED 的 `UNRATE` 或 `ICSA`。候選序列可以用於 spec 設計與後續驗證流程，但不代表已完成 live download、歷史長度、缺值、stale、修正資料與頻率相容性檢查。

若未來完成資料驗證，可以新增 `verified_series` 或類似欄位。Phase 2D 不假裝任何候選序列已被正式驗證。

## score_method 如何對應 Dispatcher

Catalog entry 會透過 `build_scoring_spec()` 轉成 `IndicatorScoringSpec`。接著 `score_indicator()` 依照 `score_method` 呼叫對應的 single-indicator scoring method。

目前支援：

- `level_percentile_score`
- `moving_average_slope_score`
- `yoy_momentum_score`
- `peak_trough_reversal_score`

`parameters` 欄位會傳給 scoring method，例如 `periods`、`momentum_window`、`moving_average_window`、`slope_window`、`confirmation_window`、`mode`。

## 為什麼放 YAML

總經指標規格會持續調整。把設定放在 YAML，可以讓資料來源、指標方向、觀察窗、stale 規則與公開解釋被審查與版本控管，而不是散落在 Python 程式碼中。

Python 只負責 deterministic loading、validation、dispatch 與 scoring。這讓 spec 與 implementation 邊界清楚，也比較容易測試。

## 這一層不是 Phase Scoring

Catalog loader 只把 indicator spec 載入並轉成 single-indicator scoring spec。它不計算 phase score、不輸出 `current_phase`、不做 dashboard，也不產生投資建議。Phase scoring 需要等後續階段整合多個 indicator 的 score、confidence、coverage、權重與 persistence。


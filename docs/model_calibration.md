# Model Calibration Plan

Phase 7A 建立模型校準計畫，但不修改 scoring、phase resolver decision logic 或 FRED provider。

Machine-readable spec 位於：

```text
specs/backtests/calibration_plan.yaml
```

這份計畫的目的，是把 Phase 6A 到 6F 的 backtest diagnostics 轉成可追蹤的後續校準方向。它不是模型設定檔，目前不會被 production pipeline、resolver 或 dashboard 用來改變判讀結果。

## 為什麼現在不能直接改 scoring

Phase 6F 找到的是模型診斷問題，不是書本結論錯誤，也不是單一指標足以推翻整套循環邏輯的證據。直接調整 scoring、phase resolver 或指標權重，容易把模型過度貼合少數歷史片段，造成 out-of-sample 案例惡化。

因此 Phase 7A 只把問題轉成校準假設與驗收標準。後續任何模型更新都必須先經過 baseline backtest diagnostics 比較，確認沒有只針對單一 scenario overfit，也沒有讓非衰退案例變得過度敏感。

## 診斷基準

Phase 6F attribution smoke summary 顯示：

- scenario_count = 5
- scenario_with_failures_count = 0
- scenario_with_attribution_count = 3
- total_diagnostic_count = 7
- attribution_quality_counts = `{"full": 5, "limited": 2}`

常見 indicator delta 包含：

- `initial_jobless_claims`
- `real_retail_sales`
- `ten_year_treasury_yield`
- `short_term_unemployment`

這些結果顯示模型目前可以揭露 whipsaw、短期 phase segment、直接 confirmed transition 等診斷訊號，但不代表模型已完成歷史驗證。

這些診斷結果是 Phase 7A calibration plan 的輸入。它們描述模型行為需要檢查之處，不代表《景氣循環投資》的方法論錯誤。

## 主要校準問題

`calibration_plan.yaml` 目前列出五類問題：

- `direct_confirmed_without_watch`：未經 transition watch 即直接 confirmed transition。
- `short_phase_segment`：phase segment 僅持續 1 至 2 期。
- `rapid_round_trip`：短期間出現 boom -> recession -> recovery 類型 whipsaw。
- `concentrated_indicator_delta`：少數指標變動過度集中於 transition 附近。
- `incomplete_book_indicator_coverage`：目前仍是 MVP 指標集合，尚未完整覆蓋書籍方法論。
- `revised_data_limitation`：目前使用修訂後歷史資料，不能等同當時投資人實際可見資料。

## Candidate Controls

7A 只定義候選控制項，不啟用任何行為：

- `confirmation_period`
- `transition_watch_required`
- `hysteresis_margin`
- `cooldown_period`
- `breadth_confirmation`
- `indicator_smoothing`
- `outlier_guard`
- `book_aligned_indicator_coverage_expansion`

後續 Phase 7B 若要實作，應先放在 feature flags 或 experimental config 後面，並以 baseline backtest diagnostics 比較，不應直接改 production resolver 行為。

## Phase 7B Experimental Transition Controls

Phase 7B 實作 feature-gated transition confirmation controls。設定檔位於：

```text
specs/backtests/transition_controls_experiment.yaml
```

此設定預設 `enabled: false`，因此不影響正式 dashboard、不影響 GitHub Pages workflow，也不改變沒有傳入 controls 時的 resolver 行為。只有在 backtest 或 calibration experiment 明確傳入 `--transition-controls`，且設定本身啟用時，才會套用實驗控制。

目前支援的 controls：

- `transition_watch_required`：confirmed transition 前需先經過 transition_watch。
- `confirmation_period`：候選階段需連續 N 期滿足轉換條件。
- `hysteresis_margin`：candidate phase score 需高於 current phase score 指定 margin。
- `cooldown_period`：confirmed transition 後 N 期內阻止再次 confirmed transition。
- `breadth_confirmation`：Phase 7B 先載入與驗證；若資料不足，僅輸出 warning，不會 crash。

Phase 7B 的目的，是提供後續實驗工具，用來檢查是否能降低 direct confirmed transition、short segment 與 rapid round trip。Phase 7B 不評估校準效果；Phase 7C 才會比較 baseline 與 experimental controls 的 backtest diagnostics。

這些 controls 只用於模型診斷與校準實驗，不構成投資建議。

## Phase 7C Calibration Experiments

Phase 7C 新增 calibration experiment runner，用來比較 baseline resolver 與 transition controls enabled 後的 backtest diagnostics。

執行方式：

```bash
python scripts/run_calibration_experiment.py --experiment-id transition_controls_v1 --max-periods 12
```

預設 controls config：

```text
specs/backtests/transition_controls_enabled_experiment.yaml
```

預設輸出：

```text
data/backtests/calibration/<experiment_id>/calibration_summary.json
```

Runner 會針對每個 scenario 產生兩組結果：

- `baseline/`：不傳 transition controls。
- `experiment/`：傳入 enabled transition controls config。

每組都會產生 timeline、report 與 transition attribution，最後比較：

- plausibility warning count
- transition event count
- phase segment count
- first recession current date

Acceptance checks 目前包含：

- direct confirmed without watch、short segment、rapid round trip 是否可望下降。
- experiment 是否沒有新增 failure。
- out-of-sample scenario 是否沒有新增 false recession。

Phase 7C 的結果不會直接進 live dashboard，也不會改 production resolver 預設。下一步才會根據 diagnostics 決定是否把 controls 轉成正式設定或繼續調整實驗參數。

## Phase 7C.1 Calibration Acceptance Review

Phase 7C 顯示 transition controls enabled 後 plausibility warning count 明顯下降，但 warning count 下降不等於模型可正式啟用。Phase 7C.1 新增 acceptance window review，用每個 scenario 的歷史窗口檢查 calibration experiment 是否合理。

執行方式：

```bash
python scripts/review_calibration_experiment.py --experiment-id transition_controls_v1
```

預設輸出：

```text
data/backtests/calibration/<experiment_id>/calibration_acceptance_review.json
```

Acceptance windows 定義於：

```text
specs/backtests/calibration_acceptance_windows.yaml
```

Review 會檢查：

- experiment 是否在 `early_false_recession_before` 之前過早確認衰退。
- `should_avoid_confirmed_recession` scenario 是否維持未確認衰退。
- `expected_recession_window` 中的 first recession current date 是否過早、過晚、落在窗口內或尚未偵測。
- dotcom 與金融海嘯這類前 12 期 smoke run 尚未偵測衰退時，是否應標記為 `needs_longer_horizon` 而非直接視為失敗。
- COVID 2019 若過早 confirmed recession，應被標記為 early false recession risk。

Phase 7C.1 仍只產生 review/report，不修改 scoring、resolver、live dashboard 或 GitHub Pages workflow。Acceptance windows 是模型診斷輔助，不代表唯一正確答案，也不構成投資建議。

## Scenario Split

計畫採用簡單的 in-sample / out-of-sample 分組，避免只針對單一歷史案例 overfit：

- in-sample：`dotcom_bubble`、`global_financial_crisis`、`covid_recession`
- out-of-sample：`euro_debt_slowdown`、`late_cycle_2018`

校準後應確認 out-of-sample cases 不因過度敏感而新增誤判衰退。

## Acceptance Criteria

初版驗收方向包括：

- confirmed transition 前應先出現 transition_watch，除非有明確外生衝擊例外。
- recession/recovery 不應頻繁只維持 1 至 2 期。
- 降低短期 whipsaw。
- 保留非衰退案例的穩定性。
- 所有回測與校準報告都必須保留 revised data caveat。

## Caveats

所有校準計畫都必須保留：

- 使用修訂後歷史資料，不等同當時投資人可見資料。
- 回測結果用於模型診斷，不構成投資建議。
- 校準不得只針對單一歷史案例最佳化。

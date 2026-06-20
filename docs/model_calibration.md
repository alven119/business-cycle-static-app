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

## Phase 7C.2 Full-Horizon Review and COVID False-Positive Attribution

Phase 7C.1 使用 `max_periods=12` 的 calibration experiment，因此 dotcom 與金融海嘯只能標記為 `needs_longer_horizon`，不能判斷完整歷史窗口下 transition controls 是否合理。Phase 7C.2 新增 full-horizon calibration orchestration，對每個 scenario 使用完整 `window_start` 到 `window_end` 執行 baseline、experiment、report、transition attribution 與 acceptance review。

執行方式：

```bash
python scripts/run_full_horizon_calibration.py --experiment-id transition_controls_v1_full
python scripts/review_calibration_experiment.py --experiment-id transition_controls_v1_full
```

預設輸出：

```text
data/backtests/calibration/<experiment_id>/calibration_summary.json
data/backtests/calibration/<experiment_id>/calibration_acceptance_review.json
```

COVID scenario 在 7C.1 被標記為 2019-02-28 early false recession，因此 Phase 7C.2 也新增 attribution diagnostic：

```bash
python scripts/diagnose_covid_false_positive.py --experiment-id transition_controls_v1_full
```

預設輸出：

```text
data/backtests/calibration/<experiment_id>/covid_false_positive_diagnostic.json
```

此 diagnostic 會整理 false transition 附近的 phase score changes、top indicator score changes、candidate phase evidence，以及 transition controls applied/blocked/warnings。它的用途是檢查：

- 是否由少數指標推動。
- 是否需要 `breadth_confirmation`。
- 是否需要更嚴格的 recession-specific confirmation。
- 是否需要 COVID / exogenous shock handling。
- 是否需要先補齊書中衰退確認指標。

Phase 7C.2 不會正式啟用 transition controls，也不修改 live dashboard、scoring、resolver 或 FRED provider。它只提供下一步校準決策依據，避免只看 plausibility warning count 下降就誤判模型已可上線。

## Phase 7D Book-Aligned Indicator Gap Analysis

Phase 7D 是 Phase 7C.2 後的 gap analysis。它不改模型，而是整理目前 MVP 指標與《景氣循環投資》方法論在三個面向上的缺口：

- 榮景期結束：過熱、升息、信用壓力、金融條件與領先訂單/房市訊號。
- 衰退確認：就業、消費、投資、金融壓力與利率循環是否形成 breadth confirmation。
- 衰退落底反轉：初領失業救濟金、短期失業、消費、訂單、進出口與貨幣寬鬆是否出現高峰或低點反轉。

Machine-readable spec：

```text
specs/backtests/book_indicator_gap_analysis.yaml
```

中文說明：

```text
docs/book_indicator_gap_analysis.md
```

查看摘要：

```bash
python scripts/show_book_indicator_gap.py
```

7D 的結果會用來決定下一步應先做 recession-specific breadth confirmation，還是先補齊書中衰退/復甦指標。這仍是 calibration planning，不會正式啟用 transition controls，也不構成投資建議。

## Phase 7E Recession-Specific Breadth Confirmation

Phase 7E 實作 recession-specific breadth confirmation，目的是避免少數高敏感指標造成 premature confirmed recession。這是 feature-gated experiment control，預設不會被 live dashboard、GitHub Pages workflow 或 production resolver 使用。

實驗設定檔：

```text
specs/backtests/transition_controls_recession_breadth_experiment.yaml
```

核心規則：

- 只在原 resolver 已準備 confirmed transition 時檢查。
- 只針對 `target_phases: [recession]` 生效。
- confirmed recession 需達到多個 indicator group 同步支持。
- 初版要求至少 3 個 group、至少 2 個 core group、至少 4 個支持指標。
- 支持指標需達到最低 phase signal score 與 confidence。
- 若 evidence 不足，保守降級為 `transition_watch`，不使用 `manual_review_required`。

執行 calibration experiment：

```bash
python scripts/run_calibration_experiment.py --experiment-id transition_controls_v2_breadth --controls specs/backtests/transition_controls_recession_breadth_experiment.yaml
```

執行 full-horizon review：

```bash
python scripts/run_full_horizon_calibration.py --experiment-id transition_controls_v2_breadth_full --controls specs/backtests/transition_controls_recession_breadth_experiment.yaml
python scripts/review_calibration_experiment.py --experiment-id transition_controls_v2_breadth_full
```

Phase 7E 後應比較是否改善 COVID false positive，同時保留 dotcom 與金融海嘯的 recession detection window。此實驗仍不構成投資建議。

## Phase 7E.1 Breadth Rule Sensitivity Experiment

Phase 7E 的 breadth gate 已能運作，但 v2 breadth 規則沒有擋掉 COVID 2019-02-28 early false recession。Phase 7E.1 新增 breadth sensitivity matrix，用多組 recession breadth 規則比較：COVID false positive 是否能被擋下、dotcom 與 GFC 是否仍在 expected window、euro debt 與 late cycle 2018 是否仍避免 confirmed recession。

Matrix spec：

```text
specs/backtests/breadth_sensitivity_matrix.yaml
```

執行方式：

```bash
python scripts/run_breadth_sensitivity.py --experiment-id breadth_sensitivity_v1
```

也可只跑單一 variant：

```bash
python scripts/run_breadth_sensitivity.py --experiment-id breadth_sensitivity_v1 --variant-id v4_core_plus_financial
```

預設輸出：

```text
data/backtests/calibration/breadth_sensitivity/<experiment_id>/breadth_sensitivity_summary.json
```

若沒有任何 variant 同時擋掉 COVID false positive 並保留 dotcom/GFC recession detection，應優先進 Phase 7F 補齊書籍衰退確認指標，而不是繼續硬調 breadth rule。Phase 7E.1 仍不會正式啟用 transition controls，也不構成投資建議。

## Phase 7E.2 Runtime Reuse

Phase 7E.2 新增 `--reuse-existing` / `--force`，目的只是降低重複運算時間。它不改模型判斷、不改 scoring、不改 resolver，也不代表 transition controls 正式啟用。

使用方式：

```bash
python scripts/run_full_horizon_calibration.py --experiment-id transition_controls_v2_breadth_full --controls specs/backtests/transition_controls_recession_breadth_experiment.yaml --reuse-existing
python scripts/run_breadth_sensitivity.py --experiment-id breadth_sensitivity_v1 --reuse-existing
python scripts/run_breadth_sensitivity.py --experiment-id breadth_sensitivity_v1 --force
```

`--reuse-existing` 只有在 required JSON outputs 全部存在且可 parse 時才會跳過重算；`--force` 會強制重跑。這只影響 calibration/backtest runtime，不影響 live dashboard。

## Phase 7F Book-Aligned Indicator Implementation Plan

Phase 7E.1 的結論是：沒有任何 breadth variant 同時擋掉 COVID 2019 early false recession、保留 dotcom/GFC recession detection，並維持 euro debt / late cycle 2018 不新增 false recession。因此 Phase 7F 不再繼續硬調 breadth rule，而是轉向補齊書籍方法論指標。

Implementation plan：

```text
specs/backtests/book_aligned_indicator_implementation_plan.yaml
docs/book_aligned_indicator_implementation_plan.md
```

查看摘要：

```bash
python scripts/show_book_indicator_plan.py
```

7F 規劃三批候選實作：

- 7F1：衰退確認指標，補強就業廣度、廣義消費、金融壓力與信用條件。
- 7F2：榮景期結束指標，補強 yield curve、信用利差、金融壓力、工業生產與政策反轉。
- 7F3：衰退落底與復甦反轉指標，補強 claims peak reversal、短期失業高峰反轉與寬鬆已到位訊號。

Phase 7F 仍不改模型輸出、不啟用 transition controls、不修改 dashboard。後續真正新增 scoring 前，需先用既有 calibration review 驗證 COVID false positive 是否降低，同時保留 dotcom/GFC 的合理 recession window。本計畫不構成投資建議。

## Phase 7F1 Recession Confirmation Candidate Indicators

Phase 7F1 先實作 recession confirmation candidate indicators，但不接入正式 phase scoring、resolver 或 live dashboard。這些 candidate outputs 只供後續 calibration/backtest diagnostics 使用。

Candidate spec：

```text
specs/backtests/recession_confirmation_candidate_indicators.yaml
specs/common/experimental_indicator_groups.yaml
```

Coverage check：

```bash
python scripts/check_recession_confirmation_candidate_coverage.py
```

Experimental scoring：

```bash
python scripts/score_recession_confirmation_candidates.py --as-of 2019-02-28
```

輸出寫入 ignored `data/backtests/candidate_indicators/`。若本機 raw cache 缺少 candidate series，CLI 會列出 failures/warnings，但不會呼叫 FRED API。Phase 7F1 不構成投資建議，也不代表模型結論已更新。

## Phase 7F1.1 Candidate Series Cache

Phase 7F1.1 只補齊 experimental candidate FRED cache。它不把 candidate indicators 加進正式 `indicator_catalog.yaml`，也不改 phase scoring、resolver 或 live dashboard。

```bash
python scripts/update_recession_confirmation_candidate_data.py --dry-run
python scripts/update_recession_confirmation_candidate_data.py --no-api
python scripts/update_recession_confirmation_candidate_data.py
```

`--dry-run` 與 `--no-api` 不需要 API key。真實下載沿用既有 `FRED_API_KEY` 環境變數或 `.env` 設定，但不會印出或寫入 key。下載後的 raw cache 位於 ignored `data/raw/fred/`，不得 commit。

下一步 Phase 7F1.2 才會把 candidate scores 納入 calibration diagnostics，比較這批指標是否降低 COVID early false recession 並保留 dotcom/GFC recession detection。本階段不構成投資建議。

## Phase 7F1.2 Candidate Recession Diagnostics

Phase 7F1.2 只判斷 candidate indicators 是否有辨識力，不把它們接入正式 phase scoring。它會比較：

- COVID 2019 early false recession。
- COVID 2020 true recession / exogenous shock。
- dotcom 與 GFC recession window。
- euro debt 與 late cycle 2018 non-recession cases。

```bash
python scripts/run_candidate_recession_diagnostics.py
```

輸出位於 ignored：

```text
data/backtests/candidate_indicators/recession_confirmation_diagnostics/candidate_recession_diagnostics.json
```

若 candidate indicators 能有效區分 false positive 與真實 recession window，下一步才評估是否把部分指標接入 experimental phase scoring 或 calibration controls。Phase 7F1.2 不改 live dashboard，也不構成投資建議。

## Phase 7F1.3 Experimental Candidate Rule

Phase 7F1.3 新增 experimental candidate recession confirmation rule，用來診斷 candidate indicators 是否能降低 false confirmed recession。Rule 不只看單一 weighted score，而是同時檢查 group breadth、high-confidence signals、high-signal count 與 weighted confirmation score。

```bash
python scripts/run_candidate_recession_diagnostics.py
python scripts/run_candidate_recession_rule.py
```

輸出位於 ignored：

```text
data/backtests/candidate_indicators/recession_confirmation_rule/candidate_recession_rule_report.json
```

此 rule 只用於 diagnostics，不代表正式模型已更新，不改 resolver、不改 live dashboard，也不構成投資建議。

## Phase 7F1.4 Full-Horizon Candidate Overlay

Phase 7F1.4 用 full-horizon overlay 比較原始 timeline 與 candidate-filtered recession confirmation。Overlay 僅新增 diagnostics，不覆寫 backtest timeline，也不會讓 live dashboard 使用 candidate indicators。

```bash
python scripts/run_candidate_recession_overlay.py --experiment-id candidate_recession_overlay_v1
```

輸出位於 ignored：

```text
data/backtests/candidate_indicators/recession_confirmation_overlay/candidate_recession_overlay_report.json
```

此步驟檢查 COVID 2019 false confirmed recession 是否可被降級、COVID 2020 / GFC 是否仍有 candidate confirmed support，以及 euro debt / 2018 是否沒有新增 false confirmed recession。下一步若結果合理，才進 Phase 7F1.5 experimental phase scoring / transition control integration design。本階段不構成投資建議。

## Phase 7F1.5 Candidate Recession Integration Design

Phase 7F1.5 將 Phase 7F1.2～7F1.4 的結果整理成 integration design 與 acceptance guardrails：

```text
specs/backtests/candidate_recession_integration_design.yaml
docs/candidate_recession_integration_design.md
```

結論是：candidate recession rule 有助於擋掉 COVID 2019 early false confirmed recession，並保留 GFC / COVID 2020 的 confirmed support，但 dotcom 在 full-horizon overlay 中被降級為 watch。因此它目前不適合成為 hard confirmation gate。

未來較合理的整合路徑是先維持 diagnostic-only，或設計 soft confirmation filter：candidate confirmed 支持 confirmed recession，candidate watch 則要求 persistence、原始 recession score、phase score margin 或其他 evidence path。這仍不會改 live dashboard，也不代表正式模型已更新。

下一步應進 Phase 7F2 補強榮景期結束與衰退前風險指標，因為 recession confirmation 通常偏晚。Phase 7F1.5 不構成投資建議。

## Phase 7F2 Boom Ending Candidate Indicators

Phase 7F2 開始補強榮景期結束與衰退前風險指標。這些 candidate indicators 只供 experimental diagnostics 使用，不加入正式 `indicator_catalog.yaml`、不改 phase scoring、不改 resolver，也不會讓 live dashboard 使用。

Candidate spec：

```text
specs/backtests/boom_ending_candidate_indicators.yaml
```

本階段包含：

- 10Y-3M / 10Y-2Y yield curve inversion pressure。
- Fed policy restrictive pressure。
- BAA-10Y credit spread widening。
- Financial conditions tightening。
- Oil price pressure。
- Unemployment rate cycle-low weakening pressure。
- Industrial production momentum loss。

執行方式：

```bash
python scripts/check_boom_ending_candidate_coverage.py
python scripts/update_boom_ending_candidate_data.py --dry-run
python scripts/update_boom_ending_candidate_data.py --no-api
python scripts/score_boom_ending_candidates.py --as-of 2019-02-28
```

下一步 Phase 7F2.1 才會把這些 candidate scores 放進 boom ending diagnostics / overlay，檢查它們是否能提前辨識榮景期後段風險。Phase 7F2 不構成投資建議。

## Phase 7F2.1 Boom Ending Diagnostics

Phase 7F2.1 將 boom ending candidate scores 放入固定 historical diagnostic points，檢查這批指標是否能早於 recession confirmation 提示 late-cycle risk。

```bash
python scripts/run_boom_ending_diagnostics.py
```

輸出：

```text
data/backtests/candidate_indicators/boom_ending_diagnostics/boom_ending_diagnostics.json
```

Diagnostic status 使用 `strong`、`watch`、`weak`、`none`，並依 group breadth、high-confidence signal count 與 weighted boom-ending score 判斷。這些門檻只供 diagnostics，不是正式 phase scoring rule。

Phase 7F2.1 不改 live model。下一步才可能建立 experimental boom ending rule 或 overlay，用來比較 dotcom / GFC / 2018 / euro debt 的 early-warning 行為。本內容不構成投資建議。

## Phase 7F2.2 Boom Ending Attribution And Refinement Plan

Phase 7F2.2 針對 7F2.1 diagnostics 產生 attribution，回答哪些指標支持 watch、哪些重要指標偏弱，以及為什麼 GFC 2006 / 2007 只有 weak。

```bash
python scripts/run_boom_ending_diagnostics.py
python scripts/run_boom_ending_attribution.py
python scripts/show_boom_ending_refinement_plan.py
```

目前 refinement plan 的重點是：

- yield curve 需要 lead-time pressure scoring，而不只看當期倒掛。
- `credit_spread_baa_10y` 需要與 BAA - AAA、spread velocity、percentile proxy 比較。
- financial conditions 需要加入 delta / deterioration speed。
- Fed policy pressure 需要區分升息、高利率維持、升息接近尾聲與政策轉向前後。
- boom ending watch rule 應被定義為 early-warning diagnostics，不是 confirmed recession。

Phase 7F2.2 不直接修改 experimental scoring method，也不改正式模型或 live dashboard。後續 Phase 7F2.3 才能依據 plan 實作 scoring refinements。本內容不構成投資建議。

## Phase 7F2.3 Boom Ending Scoring Refinement Experiment

Phase 7F2.3 依據 refinement plan 實作 experimental scoring refinements，並產生 baseline vs refined comparison：

```bash
python scripts/run_boom_ending_diagnostics.py
python scripts/run_boom_ending_refinement_experiment.py
```

Refined scoring 包含：

- yield curve lead-time pressure：檢查持續倒掛後 3～18 個月的 late-cycle pressure。
- credit spread velocity：比較 BAA - AAA 與 BAA - DGS10 的分位數與擴大速度。
- financial conditions delta：加入金融條件的惡化速度，不只看 level。
- Fed policy peak/pause：檢查高利率水準、近期升息與高檔停留。

輸出位於：

```text
data/backtests/candidate_indicators/boom_ending_refinement/boom_ending_refinement_experiment.json
```

此階段只比較 experimental diagnostics，不改正式 phase scoring、不改 resolver、不影響 live dashboard，也不構成投資建議。

## Phase 7F2.4 Boom Ending Watch Rule

Phase 7F2.4 使用 refined boom ending diagnostics 建立 experimental watch rule，將 diagnostic points 分為：

- `strong_late_cycle_warning`
- `watch`
- `weak`
- `none`

這個 rule 只用於 future strategy / overlay design，不接正式 phase scoring、不改 resolver，也不進 live dashboard。`watch` 代表 late-cycle risk 正在累積，可作為減碼風險提示研究，但不等於 confirmed recession。

COVID 這類外生衝擊案例需特別標註：boom ending 指標在衝擊發生時可能是同步壓力反映，不代表事前預測。後續若 rule 結果穩定，下一步才會做 full-horizon boom ending watch overlay。本內容不構成投資建議。

## Phase 7F2.5 Boom Ending Watch Overlay

Phase 7F2.5 將 experimental boom ending watch rule 套到完整 scenario timeline，檢查 watch 是否早於 confirmed recession、是否在 dotcom / GFC 這類 late-cycle 案例提供提前提示，以及 euro debt / late cycle 2018 是否出現過度警報。

```bash
python scripts/run_boom_ending_watch_overlay.py
```

輸出位於：

```text
data/backtests/candidate_indicators/boom_ending_watch_overlay/boom_ending_watch_overlay_report.json
```

Overlay 不覆寫原始 backtest timeline、不改 current phase、不確認 recession，也不進 live dashboard。它的用途是判斷 boom ending watch 是否適合作為未來 portfolio policy 或 transition diagnostics 的 early-warning input。COVID 等外生衝擊案例仍需標記 caveat：watch 可能是同步壓力反映，不代表事前預測。本內容不構成投資建議。

## Phase 7F2.6 Boom Ending Watch Integration Guardrails

Phase 7F2.6 將 7F2.5 overlay 結果整理成 integration guardrails。結論是：boom ending watch 有 early-warning value，但 watch density 偏高，因此不能直接作為 confirmed recession，也不能直接作為 portfolio action。

```bash
python scripts/show_boom_ending_watch_integration_guardrails.py
```

Guardrails 明確允許 diagnostic-only 顯示，也允許未來研究 transition risk boost；但禁止 direct recession confirmation 與 direct portfolio action。任何配置策略使用前，都必須先定義 persistence、cooldown、watch density 上限，並完成 portfolio backtest。

下一步轉向 Phase 7F3，補齊 recession trough / recovery candidate indicators。Phase 7F2.6 不改 live dashboard，也不構成投資建議。

## Phase 7F3 Recovery Candidate Indicators

Phase 7F3 補齊 recession trough / recovery candidate indicators，用於判斷衰退落底、復甦起點與未來再加碼前的資料證據。這些 candidate indicators 仍只供 experimental diagnostics 使用，不加入正式 `indicator_catalog.yaml`，不改 phase scoring、不改 resolver，也不進 live dashboard。

```bash
python scripts/check_recovery_candidate_coverage.py
python scripts/update_recovery_candidate_data.py --dry-run
python scripts/update_recovery_candidate_data.py --no-api
python scripts/score_recovery_candidates.py --as-of 2009-03-31
```

本階段支援的候選方向包含 claims / unemployment peak reversal、消費與生產落底回升、信用與金融壓力緩解，以及 Fed easing support。這些訊號不構成投資建議，也不會直接觸發 portfolio allocation。下一步 Phase 7F3.1 才會建立 recovery diagnostics / overlay。

## Phase 7F3.1 Recovery Diagnostics

Phase 7F3.1 建立 recovery / recession trough diagnostics，將 candidate scores 放入 dotcom、GFC、COVID、euro debt 與 late cycle 2018 的固定 as-of points，檢查它們是否能區分衰退中段、落底附近、復甦初期與非衰退 slowdown。

```bash
python scripts/run_recovery_diagnostics.py
```

輸出位於：

```text
data/backtests/candidate_indicators/recovery_diagnostics/recovery_diagnostics.json
```

此 diagnostics 使用 `strong/watch/weak/none`，但 `recovery watch` 不等於正式復甦確認。Policy easing 只能是 support signal，不能單獨確認 recovery。COVID 外生衝擊後的快速反彈需保留 caveat，不應直接等同一般景氣循環復甦。本階段不改 live dashboard，也不構成投資建議。

## Phase 7F3.2 Recovery Attribution And Refinement Plan

Phase 7F3.2 將 7F3.1 recovery diagnostics 的 mismatch 拆解為 indicator / group attribution，並建立 refinement plan。

```bash
python scripts/run_recovery_diagnostics.py
python scripts/run_recovery_attribution.py
python scripts/show_recovery_refinement_plan.py
```

Attribution 用來回答 euro debt / 2018 false positive、dotcom / COVID missed recovery watch，以及 GFC 有效訊號來自哪些群組。Refinement plan 明確要求下一步補 `recession_context_gate`，並限制 policy / financial easing 不能單獨推升到 recovery watch/strong。

Phase 7F3.2 仍只做 diagnostics 與 plan，不改 scoring、不改 resolver、不改 FRED provider、不進 live dashboard，也不構成投資建議。

## Phase 7F3.3 Recovery Scoring Refinement Experiment

Phase 7F3.3 實作 experimental recovery scoring refinements，加入 recession-context gate、policy/financial support cap、labor reversal tuning 與 real activity bottoming tuning。

```bash
python scripts/run_recovery_diagnostics.py
python scripts/run_recovery_refinement_experiment.py
```

此 comparison 的重點是：non-recession slowdown 不應被誤判為 recovery strong/watch，policy easing 與 financial easing 不能單獨確認 recovery，而 GFC / dotcom / COVID trough 附近的 recovery evidence 仍需保留。`recovery watch` 仍不等於正式復甦確認，COVID 類外生衝擊仍需 caveat。

Phase 7F3.3 不改正式 phase scoring、不改 resolver、不改 FRED provider、不進 live dashboard，也不構成投資建議。

## Phase 7F3.4 Recovery Watch Rule

Phase 7F3.4 將 refined recovery diagnostics 轉成 experimental recovery watch rule，分類為 `strong_recovery_watch`、`recovery_watch`、`weak`、`none`。

```bash
python scripts/run_recovery_diagnostics.py
python scripts/run_recovery_refinement_experiment.py
python scripts/run_recovery_watch_rule.py
```

此 rule 只用於 future recovery overlay / portfolio research。它保留 recession-context gate，並限制 policy easing / financial easing 不得單獨推升到 recovery watch 或 strong。`recovery watch` 不等於正式復甦確認；COVID 外生衝擊案例需保留 caveat。

如果結果合理，下一步才做 full-horizon recovery watch overlay。Phase 7F3.4 不改正式模型、不進 live dashboard，也不構成投資建議。

## Phase 7F3.5 Recovery Watch Overlay

Phase 7F3.5 將 experimental recovery watch rule 套用到 full-horizon scenario timeline，評估 watch timing、watch density、strong watch density、policy-only block、context gate block 與 COVID caveat。

```bash
python scripts/run_recovery_watch_overlay.py
```

此 overlay 用於判斷 recovery watch 是否可成為 future portfolio policy research input；它不會改 current phase、不會 confirmed recovery，也不會產生買進訊號。若結果合理，下一步才做 recovery integration guardrails。

Phase 7F3.5 不改正式 phase scoring、不改 resolver、不改 FRED provider、不進 live dashboard，也不構成投資建議。

## Phase 7F3.6 Recovery Watch Integration Guardrails

Phase 7F3.6 根據 full-horizon recovery watch overlay 建立 integration guardrails。Recovery watch 有 trough / recovery evidence value，但不能直接 confirmed recovery，也不能直接成為買進或加碼訊號。

```bash
python scripts/show_recovery_watch_integration_guardrails.py
```

Guardrails 禁止 `direct_recovery_confirmation` 與 `direct_portfolio_action`，並要求保留 recession context gate、policy / financial support cap、persistence、cooldown、COVID exogenous shock caveat 與 portfolio backtest。

下一步轉向 Phase 7G：cycle transition evidence architecture，整合 recession confirmation、boom ending watch、recovery watch 三類 experimental evidence。Phase 7F3.6 不改正式模型、不進 live dashboard，也不構成投資建議。

## Phase 7G Cycle Transition Evidence Architecture

Phase 7G 整合三類 experimental evidence：recession confirmation、boom ending watch、recovery watch。此階段統一定義 usage boundary：哪些 evidence 可作 dashboard diagnostics research，哪些只能作 future transition risk research，哪些可供 Phase 8 / Phase 9 portfolio policy research planning。

```bash
python scripts/show_cycle_transition_evidence_architecture.py
```

核心規則是：watch 不等於正式 phase confirmation，watch 也不是買賣訊號。Portfolio policy 必須等 Phase 8 / Phase 9 回測後才可研究，不能由 evidence architecture 直接產生 allocation。

下一步可做 Phase 7G1 evidence badge schema，或轉向 Phase 8 portfolio policy research planning。Phase 7G 不改正式模型、不進 dashboard，也不構成投資建議。

## Phase 7G1 Transition Evidence Badge Schema

Phase 7G1 定義 future dashboard diagnostics 的 transition evidence badge schema。此 schema 只描述 display layer contract：badge 可以呈現 recession confirmation、boom ending watch、recovery watch 三類 experimental evidence，但不得影響 `current_phase_id`、不得改 `decision_status`，也不得包含買賣或配置欄位。

```bash
python scripts/show_transition_evidence_badge_schema.py
```

Badge schema 是 diagnostics display layer 的前置設計，不接正式 dashboard output。下一步可做 Phase 7G2 static validator / sample badge fixtures，檢查未來 badge 不包含正式決策或投資行動欄位。此階段不改正式模型，也不構成投資建議。

## Phase 7G2 Transition Evidence Badge Fixtures

Phase 7G2 建立 transition evidence badge 的 valid / invalid fixtures，並提供 batch validator。

```bash
python scripts/validate_transition_evidence_badge_fixtures.py
```

Valid fixtures 必須是 diagnostics-only、`formal_decision_impact=none` 且含不構成投資建議 caveat。Invalid fixtures 則刻意包含 `buy_signal`、`sell_signal`、`allocation`、`current_phase_override`、`diagnostics_only=false` 或 formal decision impact，用來確保未來 dashboard diagnostics 不會誤接正式決策、交易訊號或配置欄位。

Phase 7G2 只做 static validation，不接 dashboard renderer、不產生 `public/` output、不改正式模型，也不構成投資建議。

## Phase 7G3 Transition Evidence Badge Renderer Contract

Phase 7G3 定義 future dashboard diagnostics 的 renderer contract，規範 badge input、safe display model、level display mapping、required caveats、forbidden fields 與 prohibited text patterns。

```bash
python scripts/show_transition_evidence_badge_renderer_contract.py
```

此 contract 是 dashboard diagnostics 前置安全規格。Renderer 必須先接受已通過 schema validation 的 badge，輸出 safe display model，並阻擋買賣、配置、phase override 與正式階段確認文字。本階段不接 dashboard renderer、不產生 `public/` output，也不構成投資建議。

## Phase 7G4 Transition Evidence Badge Display Fixtures

Phase 7G4 建立 renderer display model fixtures 與 batch validator。

```bash
python scripts/validate_transition_evidence_badge_display_fixtures.py
```

Display fixtures 是 future dashboard diagnostics 的 renderer-level guard。Validator 確認 safe display model 不包含 formal decision impact、buy/sell signal、allocation、target weight、phase override 或 prohibited text pattern，並要求保留 global caveats。

Phase 7G4 只做 display model contract validation，不接 dashboard templates、不產生 `public/` output，也不構成投資建議。

## Phase 7G5 Dashboard Evidence Integration Readiness

Phase 7G5 建立 dashboard evidence integration readiness checklist，彙整 Phase 7G 到 7G4 的 schema、fixtures、renderer contract、display model fixtures 與 validator 狀態。

```bash
python scripts/show_dashboard_evidence_integration_readiness.py
```

此 checklist 明確指出 dashboard wiring 仍 blocked：尚未定義 data adapter schema、尚未更新 generated site validation、尚未加入 HTML text-safety tests，也不得影響 `current_phase_id` 或 `decision_status`。Phase 7G 可收斂為 fully specified but not wired。下一步轉 Phase 8A portfolio policy research planning。

## Phase 8A Portfolio Policy Research Planning

Phase 8A 開始進入 portfolio policy research，但目前只做 planning。

```bash
python scripts/show_portfolio_policy_research_plan.py
```

此階段將榮景期逐步防守、衰退期防守、復甦再加碼規格化為 future backtest-only templates。70/50/30 只能作為 backtest-only parameter，不是目前配置建議。Transition evidence watch 不能直接觸發交易，任何 portfolio action 前必須完成 backtest、風險分析、交易成本與 false signal cost 分析。本階段不構成投資建議。

## Phase 8B Portfolio Policy Template Schema

Phase 8B 建立 portfolio policy template schema、valid / invalid fixtures 與 static validator。

```bash
python scripts/show_portfolio_policy_template_schema.py
python scripts/validate_portfolio_policy_template_fixtures.py
```

Validator 確保三個 policy templates 只能是 research-only / backtest-only，並阻擋 live allocation、trade signal、target weight、current market recommendation 與 prohibited text。70/50/30 只能作為 `stock_weight_levels_for_backtest_only`，不是目前配置建議。本階段不產生 allocation、不接 dashboard，也不構成投資建議。

## Phase 8C Portfolio Backtest Input Contract

Phase 8C 定義 future portfolio backtest 的 input contract 與 scenario mapping。

```bash
python scripts/show_portfolio_backtest_input_contract.py
```

Contract 定義 monthly as-of alignment、phase / evidence inputs、rebalance frequency、transaction cost / slippage assumptions、risk metrics 與 output safety boundaries。Scenario mapping 覆蓋 dotcom、GFC、COVID、euro debt slowdown、late-cycle 2018，並將每個 scenario 對應到 future research policy questions。

本階段不跑正式 backtest、不產生 `data/backtests`、不產生 allocation、不接 dashboard，也不構成投資建議。

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

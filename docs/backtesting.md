# Backtesting

Phase 6A 只建立 historical backtest scenario specs 與 loader，不執行完整 backtest runner。

未來 backtest 的目標，是沿著歷史月份重跑 current pipeline，觀察模型在重大歷史轉折前後的反應。重點包括 state machine 是否避免任意跳階段、phase scores 是否能反映資料轉弱或改善、以及不同指標群組的領先/落後關係。

## QA0 methodology caveat

QA0 之後，所有既有 historical diagnostics 仍應視為 revised-data model diagnostics。它們不是 point-in-time backtest，不重現書中 1994-2018 benchmark，也不能證明策略歷史績效。Phase 9B 僅是 controlled synthetic in-memory calculation harness；QA0 審核完成前暫停 9B1。

## QA1 temporal modes

QA1 新增 point-in-time observation model、ALFRED/FRED vintage provider、ignored local cache 與 coverage audit，但 production live default 仍是 `revised`。

四種 data mode 的邊界：

- `revised` 使用目前最新修訂值。
- `release_lag_adjusted_revised_proxy` 使用修訂值加發布延遲，只能作 sensitivity diagnostic，不能稱為 point-in-time。
- `initial_release_only` 使用首次發布值，不能冒充 as-of 當時最新可見修訂值。
- `vintage_as_of` 使用 ALFRED date-level real-time interval，as-of policy 是 end-of-day；缺任一 required series 或 metadata 時 fail closed。

Inventory complete 不等於 point-in-time ready。`data/raw/fred_vintages/` cache 被 git ignore；pytest 使用 tmp cache，不呼叫真實 API。

Phase 9B 仍是 synthetic harness。9B1、book benchmark execution、dashboard portfolio integration 與 real backtest progression 仍 blocked。

## Phase 6B Runner Skeleton

Phase 6B 新增 historical backtest runner skeleton。它可以針對單一 scenario 依每月月底 as-of 日期跑出 timeline JSON，但尚未新增 dashboard 歷史頁、圖表或前端互動。

Smoke test：

```bash
python scripts/run_backtest.py --scenario-id global_financial_crisis --max-periods 3
```

完整 scenario：

```bash
python scripts/run_backtest.py --scenario-id global_financial_crisis
```

預設輸出：

```text
data/backtests/<scenario_id>/timeline.json
```

第一期的 `previous_phase_id` 來自 scenario 的 `baseline_phase_id`。後續每一期的 `previous_phase_id` 來自前一期 resolver 的 `current_phase_id`。這讓 backtest 沿用同一套 state machine 順序，而不是每期直接取最高分 phase。

Runner 不會呼叫 FRED API，也不會下載資料。它只讀本機 `data/raw/fred` CSV cache；若 raw CSV 缺漏，timeline 會記錄 period failure 或 indicator failure。正式執行前請先用 live data refresh 建好 raw cache。

## Phase 6C Timeline Report

Phase 6C 新增 diagnostics report layer。先產生 timeline，再產生 report：

```bash
python scripts/run_backtest.py --scenario-id global_financial_crisis --max-periods 12
python scripts/summarize_backtest.py --scenario-id global_financial_crisis
```

Report 預設輸出：

```text
data/backtests/<scenario_id>/report.json
```

`report.json` 包含：

- `phase_segments`：current phase 的連續分段。
- `transition_events`：current phase 實際改變的日期與轉換資訊。
- `decision_status_counts`：各種 resolver status 的出現次數。
- `phase_score_extrema`：各 phase 分數的最高、最低、最新值與日期。
- `first_transition_watch_as_of`。
- `first_recession_watch_as_of`。
- `first_recession_current_as_of`。

Report 用途是檢查模型是否太早或太晚出現轉折訊號，並觀察四階段分數在歷史事件中的演變。它仍然使用 timeline 的 revised data caveat，不代表當時投資人可見資料，也不是投資建議。

## Phase 6C.1 Plausibility Diagnostics

Phase 6C.1 在 `report.json` 增加 `plausibility_warnings` 與 `plausibility_warning_count`。這些 warning 只用來檢查模型在歷史案例中的可疑跳轉，不會改變模型結果。

常見 warning：

- `short_phase_segment`：某個 phase segment 持續期數過短。
- `direct_confirmed_transition_without_watch`：階段直接 confirmed transition，前一期沒有先進入 transition watch。
- `rapid_round_trip`：短時間內出現 A -> B -> C，且中間 phase 過短，可能代表 whipsaw。
- `early_scenario_transition`：第一個 transition 發生在 scenario window 前段。
- `recession_without_watch`：衰退期在同一期直接被確認，缺少觀察期。

看到 warning 後，下一步通常是檢查：

- phase thresholds
- phase scoring weights
- indicator scoring sensitivity
- required confirmation periods
- book-aligned indicator coverage

這些 warning 是模型診斷資訊，不是投資建議。

## Phase 6D Full Smoke Summary

Phase 6D 新增多 scenario 的 limited smoke runner。它會依 `specs/backtests/scenarios.yaml` 對每個 scenario 執行有限期數的 backtest，再產生 timeline report，最後彙整成整體診斷摘要。

```bash
python scripts/run_backtest_smoke.py --max-periods 24
```

預設輸出：

```text
data/backtests/smoke_summary.json
```

也可以只跑單一 scenario：

```bash
python scripts/run_backtest_smoke.py --max-periods 12 --scenario-id global_financial_crisis
```

Smoke summary 用途是快速比較多個歷史案例是否出現 whipsaw、過早轉換、沒有 `transition_watch`、短期 phase segment，並判斷後續是否需要檢查 phase thresholds、confirmation periods、indicator scoring sensitivity 或 book-aligned indicator coverage。

Smoke summary 不代表模型已驗證完成。它仍使用 revised data，不等同當時投資人可見資料，也不構成投資建議。

## Phase 6E Transition Attribution

Phase 6E 新增 transition attribution diagnostics。它只讀取既有 backtest outputs 與 intermediate outputs，不重新計分、不修改 resolver，也不新增 dashboard 歷史頁或圖表。

典型流程：

```bash
python scripts/run_backtest.py --scenario-id global_financial_crisis --max-periods 12
python scripts/summarize_backtest.py --scenario-id global_financial_crisis
python scripts/diagnose_backtest_transitions.py --scenario-id global_financial_crisis
```

預設輸出：

```text
data/backtests/<scenario_id>/transition_attribution.json
```

`transition_attribution.json` 用來解釋 transition event 或 plausibility warning 發生時：

- 各 phase score 相對前一期如何變化。
- candidate/current phase 是否有 per-indicator contribution evidence。
- indicator score 是否有明顯變化。
- warning 是否和同一期 transition event 連在一起。

Attribution quality 分為：

- `full`：可取得 phase score changes、indicator score changes 與 phase contribution evidence。
- `partial`：至少可取得 phase score changes 或 indicator score changes。
- `limited`：只能建立基本 transition/warning 資訊。
- `failed`：必要 timeline/report 缺失時不會產生正常 output，CLI 會回傳錯誤。

這些 attribution 可協助判斷 whipsaw 或過早轉換較可能來自 threshold、score sensitivity、缺少 confirmation period，或缺少書中觀察指標。它只解釋回測結果，不會修改模型判斷。輸出仍使用 revised data，不等同當時投資人可見資料，也不構成投資建議。

## Phase 6F Attribution Smoke Summary

Phase 6F 新增多 scenario 的 attribution smoke summary。它會彙整各 scenario 的 `transition_attribution.json`，比較不同歷史案例中哪些 phase score 或 indicator score 最常出現在 transition / plausibility warning 附近。

建議先跑 limited backtest smoke，再重用既有 outputs 做 attribution aggregation：

```bash
python scripts/run_backtest_smoke.py --max-periods 12
python scripts/run_attribution_smoke.py --max-periods 12 --reuse-existing
```

預設輸出：

```text
data/backtests/attribution_summary.json
```

用途：

- 比較多個歷史案例中，哪些指標最常導致 transition 或 whipsaw 診斷。
- 檢查 attribution quality 是否多數為 `full` / `partial` / `limited`。
- 判斷下一步應檢查 confirmation periods、thresholds、indicator sensitivity，或補齊書中觀察指標。

Attribution summary 仍是 diagnostics aggregation，不代表模型已驗證完成。它使用 revised data，不等同當時投資人可見資料，也不構成投資建議。

Phase 6F 的 attribution summary 是 Phase 7A calibration plan 的主要輸入之一，用來把常見 whipsaw、transition warning 與 indicator delta 集中現象整理成後續校準假設。

## Phase 7A Calibration Plan

Phase 7A 將 Phase 6A 到 6F 的 diagnostics 整理成模型校準計畫，但不修改 scoring、resolver 或 FRED provider。

Machine-readable spec：

```text
specs/backtests/calibration_plan.yaml
```

中文說明文件：

```text
docs/model_calibration.md
```

校準計畫目前只定義 diagnosed issues、candidate controls、in-sample/out-of-sample scenario split 與 acceptance criteria。候選 controls 包含 confirmation period、transition watch requirement、hysteresis margin、cooldown period、breadth confirmation 與 indicator smoothing。這些 controls 尚未啟用，也不會改變 production dashboard 或 current phase resolver 結果。

所有校準設計都保留 revised data caveat，且不得只針對單一 scenario overfit。回測與校準結果仍是模型診斷，不構成投資建議。

## Phase 7B Transition Controls Experiments

`run_backtest.py` 可用 `--transition-controls` 明確指定實驗性 transition controls：

```bash
python scripts/run_backtest.py --scenario-id global_financial_crisis --max-periods 12 --transition-controls specs/backtests/transition_controls_experiment.yaml
```

若不加 `--transition-controls`，backtest 維持 baseline resolver 行為。`specs/backtests/transition_controls_experiment.yaml` 本身預設 `enabled: false`，因此即使傳入此檔，也不會改變正式 dashboard 或 live pipeline 的 current phase 判斷。

當未來 Phase 7C 建立 enabled experiment config 時，timeline period 會記錄 `transition_controls_enabled`、`transition_controls_applied`、`transition_controls_blocked` 與 `transition_controls_warnings`，方便比較 baseline 與 controls enabled 的 diagnostics。

## Phase 7C Calibration Experiment Runner

Calibration experiment runner 會同時跑 baseline 與 enabled transition controls，並輸出比較報告：

```bash
python scripts/run_calibration_experiment.py --experiment-id transition_controls_v1 --max-periods 12
```

預設輸出：

```text
data/backtests/calibration/transition_controls_v1/calibration_summary.json
```

Baseline 不傳 transition controls；experiment 使用 `specs/backtests/transition_controls_enabled_experiment.yaml`。此流程只產生 diagnostics comparison，不會修改 live dashboard、GitHub Pages workflow 或 production resolver 預設。

## Phase 7C.1 Calibration Acceptance Review

Calibration acceptance review 會讀取 calibration summary 與 scenario acceptance windows，檢查 warning count 下降後是否仍有過早衰退、應避免衰退卻 confirmed recession，或需要更長 horizon 才能判斷的情況。

```bash
python scripts/review_calibration_experiment.py --experiment-id transition_controls_v1
```

預設輸出：

```text
data/backtests/calibration/transition_controls_v1/calibration_acceptance_review.json
```

Acceptance windows 位於：

```text
specs/backtests/calibration_acceptance_windows.yaml
```

此 review 仍是模型診斷，不會啟用 transition controls，也不會改 live dashboard。它使用 revised data，不等同當時投資人可見資料，也不構成投資建議。

## Phase 7C.2 Full-Horizon Calibration and COVID Diagnostic

Full-horizon calibration 會使用每個 scenario 的完整 window，不套用 `max_periods` smoke 限制：

```bash
python scripts/run_full_horizon_calibration.py --experiment-id transition_controls_v1_full
```

預設輸出：

```text
data/backtests/calibration/transition_controls_v1_full/calibration_summary.json
data/backtests/calibration/transition_controls_v1_full/calibration_acceptance_review.json
```

若只想跑單一 scenario：

```bash
python scripts/run_full_horizon_calibration.py --experiment-id transition_controls_v1_full --scenario-id covid_recession
```

COVID early false-positive diagnostic 可針對 `covid_recession` 的 experiment output 產生歸因報告：

```bash
python scripts/diagnose_covid_false_positive.py --experiment-id transition_controls_v1_full
```

預設輸出：

```text
data/backtests/calibration/transition_controls_v1_full/covid_false_positive_diagnostic.json
```

這些 output 都在 ignored `data/backtests/calibration/` 之下，只用於 diagnostics。它們不會修改正式 dashboard、不會啟用 transition controls，也不構成投資建議。

## Phase 7D Book Indicator Gap Analysis

Phase 7D 讀取 machine-readable gap spec，整理目前 MVP 指標與書籍方法論之間的缺口：

```bash
python scripts/show_book_indicator_gap.py
```

Spec 與說明文件：

```text
specs/backtests/book_indicator_gap_analysis.yaml
docs/book_indicator_gap_analysis.md
```

此步驟不執行 backtest、不產生 `data/backtests/` output，也不修改 scoring 或 resolver。它用來規劃後續 recession-specific breadth confirmation 與 book-aligned indicator expansion。

## Phase 7E Recession Breadth Confirmation Experiment

Phase 7E 可用新的 transition controls config 進行 recession-specific breadth confirmation 實驗：

```bash
python scripts/run_calibration_experiment.py --experiment-id transition_controls_v2_breadth --controls specs/backtests/transition_controls_recession_breadth_experiment.yaml
```

Full-horizon calibration 與 review：

```bash
python scripts/run_full_horizon_calibration.py --experiment-id transition_controls_v2_breadth_full --controls specs/backtests/transition_controls_recession_breadth_experiment.yaml
python scripts/review_calibration_experiment.py --experiment-id transition_controls_v2_breadth_full
python scripts/diagnose_covid_false_positive.py --experiment-id transition_controls_v2_breadth_full
```

此 config 只供 calibration experiment 使用。若不明確傳入 `--controls`，backtest 仍維持 baseline 或原本指定的 controls。Live dashboard 與 GitHub Pages workflow 不會使用此設定。

## Phase 7E.1 Breadth Sensitivity Matrix

Phase 7E.1 比較多組 recession breadth 規則：

```bash
python scripts/run_breadth_sensitivity.py --experiment-id breadth_sensitivity_v1
```

只跑單一 variant：

```bash
python scripts/run_breadth_sensitivity.py --experiment-id breadth_sensitivity_v1 --variant-id v4_core_plus_financial
```

預設輸出：

```text
data/backtests/calibration/breadth_sensitivity/breadth_sensitivity_v1/breadth_sensitivity_summary.json
```

Matrix spec：

```text
specs/backtests/breadth_sensitivity_matrix.yaml
```

此流程只產生 diagnostics aggregation，不會修改 scoring、resolver、dashboard 或 GitHub Pages workflow。

## Phase 7E.2 Reuse Existing Calibration Outputs

Full-horizon calibration 與 breadth sensitivity 可能耗時很久。若只是重看既有結果，可使用 `--reuse-existing`：

```bash
python scripts/run_full_horizon_calibration.py --experiment-id transition_controls_v2_breadth_full --controls specs/backtests/transition_controls_recession_breadth_experiment.yaml --reuse-existing
python scripts/run_breadth_sensitivity.py --experiment-id breadth_sensitivity_v1 --reuse-existing
```

若 config、程式或資料已改，需要強制重算：

```bash
python scripts/run_breadth_sensitivity.py --experiment-id breadth_sensitivity_v1 --force
```

Reuse 機制會保守檢查 required JSON outputs 是否存在且可 parse；缺檔或壞檔不會被默默使用。Generated output 仍在 ignored `data/backtests/` 之下，不應 commit。

## Phase 7F Book-Aligned Indicator Plan

Phase 7F 建立下一批書籍方法論指標的實作計畫，不執行 backtest、不產生 `data/backtests/` output，也不修改 scoring 或 resolver。

```bash
python scripts/show_book_indicator_plan.py
```

Spec 與說明文件：

```text
specs/backtests/book_aligned_indicator_implementation_plan.yaml
docs/book_aligned_indicator_implementation_plan.md
```

此計畫使用 Phase 7E.1 的 breadth sensitivity 結論作為輸入：若 breadth rule alone 無法同時滿足所有 acceptance targets，下一步應補齊 recession confirmation、boom ending、recession trough/recovery 指標，再重新跑 calibration diagnostics。

## Data Mode

第一版 scenario 的 `data_mode` 都是 `revised`，代表使用目前可下載的修訂後歷史資料。

這有明確限制：revised data 不等於當時投資人實際能看到的資料，因此不能用來宣稱即時判斷能力。未來可擴充 `realtime_vintage` 或 ALFRED 類資料，以降低 look-ahead bias。

## 初始案例

- 網路泡沫
- 金融海嘯
- COVID 衰退
- 歐債危機與二次衰退疑慮
- 2018 升息與貿易戰壓力

Scenario spec 位於：

```text
specs/backtests/scenarios.yaml
```

列出所有 scenario：

```bash
python scripts/list_backtest_scenarios.py
```

列出單一 scenario 詳細內容：

```bash
python scripts/list_backtest_scenarios.py --scenario-id global_financial_crisis
```

## 不是投資建議

Backtest scenario 與 timeline JSON 用於研究模型在歷史總經資料中的行為，不提供資產配置、不提供交易訊號，也不構成投資建議。使用 revised data 的結果尤其不能直接視為當時可交易的即時訊號。

## Phase QA0.1 Inventory Reconciliation

QA0 是 initial audit baseline。QA0.1 建立 canonical book requirement manifest 與 repository inventory reconciliation，確認 indicator、series、traceability、release lag registry、book indicator coverage 與 anti-hardcoding checks 會一起防止 audit drift。

QA0.1 通過不代表模型已驗證、書籍方法已完整對齊或 point-in-time backtest ready。現況仍是：

- `book_alignment_claim_allowed=false`
- `point_in_time_backtest_ready=false`
- `real_backtest_progression_allowed=false`
- Phase 9B1 blocked

下一步是 QA1 temporal integrity remediation。

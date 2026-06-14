# Backtesting

Phase 6A 只建立 historical backtest scenario specs 與 loader，不執行完整 backtest runner。

未來 backtest 的目標，是沿著歷史月份重跑 current pipeline，觀察模型在重大歷史轉折前後的反應。重點包括 state machine 是否避免任意跳階段、phase scores 是否能反映資料轉弱或改善、以及不同指標群組的領先/落後關係。

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

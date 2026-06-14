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

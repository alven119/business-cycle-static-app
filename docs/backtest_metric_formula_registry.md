# Backtest Metric Formula Registry

## 背景

Phase 9A 已定義 future real backtest engine contract，Phase 9A1 已定義 future backtest result output contract。Phase 9A2 接續定義 metric formula registry，讓後續 backtest prototype 有清楚的績效、風險、交易行為與錯誤訊號成本指標規格。

## Phase 9A1 Result Output Contract 與 Phase 9A2 的關係

Result output contract 只允許列出 future metric 欄位名稱，且明確標記 `metric_values_allowed_now=false`。Metric formula registry 則進一步定義這些欄位未來要用的公式、必要輸入、單位與方向性，但仍不計算任何實際數值。

## 為什麼 Formula Registry 仍不是 Metric Calculation

本階段只做公式與欄位設計。它不載入歷史資料、不建立 portfolio value series、不執行 rebalance、不計算 total return、max drawdown、turnover 或任何 false signal cost，也不產生 backtest result。

## Registry Scope

允許：

- 定義 metric formulas。
- 定義 required inputs。
- 定義 output fields 與 units。
- 定義 higher-is-better / lower-is-better。
- 定義 future acceptance gates。

禁止：

- compute metric values。
- execute backtest。
- produce backtest results。
- write `data/backtests` 或 `public`。
- produce allocation 或 trade signal。
- dashboard / resolver integration。

## Required Series Inputs

Registry 定義 future backtest 可能需要的 series：portfolio value、benchmark value、contribution / cash flow、backtest-only weight series、policy / evidence state series。這些都是 future engine 的輸入規格，不代表 live allocation 或 trade signal。

## Metric Definitions

本階段定義 11 個 metric：

- `total_return`
- `annualized_return`
- `volatility`
- `max_drawdown`
- `turnover`
- `whipsaw_count`
- `false_de_risk_cost`
- `false_re_risk_cost`
- `missed_recovery_cost`
- `late_exit_cost`
- `late_reentry_cost`

## Performance Metrics

Performance metrics 包含 `total_return` 與 `annualized_return`。公式只描述 future calculation method，不產生任何績效值。

QA0 補充 cash-flow guard：`ending_value / beginning_value - 1` 只可用於沒有 external cash flows 的 no-cashflow harness。若有年度追加投入、提領或其他外部 cash flow，必須改用 terminal wealth、total contributions、net investment gain、time-weighted return、money-weighted return / XIRR、unitized NAV 與 unitized NAV drawdown。Terminal wealth 不可稱為 total return，含投入的 account balance 也不可直接拿來計算 max drawdown。

## Risk Metrics

Risk metrics 包含 `volatility` 與 `max_drawdown`。本階段只定義需要 monthly returns 或 portfolio value series。

## Trading Behavior Metrics

Trading behavior metrics 包含 `turnover` 與 `whipsaw_count`。`weight_series` 只能是 future backtest-only weights，不可解讀為 live allocation。

## False Signal Cost Metrics

False signal cost metrics 包含 `false_de_risk_cost` 與 `false_re_risk_cost`，用於 future backtest 研究錯誤防守或錯誤再承擔風險的成本。

## Opportunity Cost Metrics

Opportunity cost metrics 包含 `missed_recovery_cost`、`late_exit_cost` 與 `late_reentry_cost`，用於 future backtest 研究過晚退出、錯過復甦或過晚再進入的成本。

## 為什麼 Compute Allowed Now 等於 False

Phase 9A2 尚未完成 output location policy、result safety validator、result caveat policy，也沒有 real backtest engine runtime。因此每個 metric 都必須維持 `compute_allowed_now=false`。

## Prohibited Result Fields

Registry 明確禁止 live allocation、target weight、buy/sell signal、current market recommendation、phase override、decision override 與 public dashboard output。

## Required Caveats

所有 future metric 使用前必須保留 caveats：

- metric formula registry，不是回測結果。
- 本階段不計算任何實際績效值。
- 回測結果不代表未來績效。
- 不構成投資建議。

## Required Acceptance Before Metric Computation

未來若要計算 metric values，必須先完成並驗證 metric formula registry、result output contract、result safety validator、output location policy，且明確阻擋 live allocation、trade signal 與 public auto-output。

## 為什麼下一步先做 Output Location Policy

公式 registry 完成後，下一個風險點是結果能寫到哪裡。Phase 9A3 應先定義 backtest output location policy，確保 future result 只能寫入受控 research path，不會自動進入 `public` 或 dashboard。

## Caveats

- formula-only。
- no metric values。
- no result output。
- no allocation。
- not investment advice。

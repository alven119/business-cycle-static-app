# Backtest Result Output Contract

## 背景

Phase 9A1 定義 future real portfolio backtest result 的 output schema。這是結果輸出前的安全規格，不是回測結果，也不會產生任何績效數值或檔案。

## Phase 9A Engine Contract 與 Phase 9A1 的關係

Phase 9A 定義 future engine 的 stages 與 dependency。Phase 9A1 補上其中 `build_result_output` 所依賴的 result output contract，讓未來 result 的欄位、caveats 與禁止輸出先被規格化。

## 為什麼 Result Output Contract 仍不是 Backtest Result

本階段只描述 result object 可以長什麼樣子。它不執行 engine、不計算 metric values、不寫 result file，也不輸出 `data/backtests` 或 `public`。

## Output Contract Scope

允許定義 result schema、future metric fields、required caveats、prohibited fields、output location dependency、result safety dependency 與 future acceptance gates。

禁止產生 backtest results、計算 metric values、寫 result files、寫 `data/backtests`、寫 public output、產生 allocation、產生 trade signal、接 dashboard 或接 resolver。

## Result Object Schema

result object schema 定義 `result_id`、scenario / policy / parameter id、`data_mode`、`backtest_only`、`result_type`、`metric_summary`、`risk_summary`、`caveats_zh` 與 validation status 等必要欄位。

## Allowed Future Metric Fields

schema 可列出 future metric fields，例如 total return、annualized return、volatility、max drawdown、turnover、whipsaw 與 false signal cost。這些只是 future result schema 欄位，不代表本階段可產生數值。

## Metric Values 為什麼本階段仍不允許

metric values 必須等 Phase 9A2 metric formula registry 定義公式後，並且 result safety validator 與 output policy 都完成後，才能在後續 prototype 中計算。本階段 `metric_values_allowed_now=false`。

## Result Type Policy

允許的 future result types 包含 backtest summary、scenario metric table、sensitivity result table、policy parameter result 與 caveat report。live allocation、current market recommendation、trade signal 與 dashboard portfolio action 都被禁止。

## Prohibited Result Fields

禁止欄位包含 live allocation、target weight、portfolio action、buy/sell/add/reduce signal、current market recommendation、public dashboard output、phase override 與 decision status override。

## Prohibited Text Patterns

結果文字不得包含目前建議、建議買進、建議賣出、買進訊號、賣出訊號、target weight、live allocation 或 investment advice 等語句。

## Required Result Caveats

所有 future result 都必須保留：backtest-only 不是目前配置建議、回測結果不代表未來績效、不構成投資建議。

## Output Location Dependency

result output 必須依賴 future output location policy。本階段 `auto_write_allowed_now=false`，且禁止自動寫入 public、dashboard、github_pages 與 data/backtests。

## Result Safety Dependency

result output 必須依賴 future result safety validator，檢查 no live allocation、no current recommendation、no trade signal、no public auto-output、caveats required 與 output location policy enforced。

## Result Caveat Dependency

result output 必須依賴 future result caveat policy，確保所有結果都帶有 backtest-only、不代表未來績效與不構成投資建議 caveat。

## Required Acceptance Before Result Generation

result generation 前必須先通過 result output contract、output location policy、result safety validator、result caveat policy 與 metric formula registry 的 validation。

## 為什麼下一步先做 Metric Formula Registry

result schema 已定義後，下一步才適合定義各項 metric 的公式。公式 registry 完成前，不能計算任何實際績效數值。

## Caveats

- contract-only
- no performance values
- no allocation
- no public output
- not investment advice

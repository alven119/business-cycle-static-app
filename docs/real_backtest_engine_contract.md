# Real Backtest Engine Contract

## 背景

Phase 9A 進入 real backtest 的 contract design 階段，但仍不是 real backtest engine。此階段只定義 future engine 的輸入、流程、依賴與安全邊界。

## Phase 8I Readiness Gate 與 Phase 9A 的關係

Phase 8I 已確認目前只允許進入 contract design。Phase 9A 承接這個 gate，將第一個必要 contract，也就是 real backtest engine contract，具體化。

## 為什麼 9A 仍不能執行 Real Backtest

真正回測必須依賴 metric formula registry、result output contract、result safety validator、output location policy 與 result caveat policy。這些 dependency 尚未定義前，執行回測會讓績效數字、結果欄位、輸出位置與投資建議風險失去約束。

## Engine Scope

Phase 9A 允許定義 engine contract、engine stages、required dependencies、safety requirements 與 future acceptance gates。它禁止實作 runtime、執行 backtest、計算績效、產生 result、寫入 `data/backtests` 或 `public`、產生 allocation、產生 trade signal、接 dashboard 或接 resolver。

## Required Input Contracts

future engine 必須使用既有 backtest input contract、scenario mapping、input fixtures、policy template schema 與 policy template fixtures。

## Required Future Dependency Contracts

執行前必須先有：

- metric formula registry
- backtest result output contract
- backtest result safety validator
- output location policy
- result caveat policy

## Engine Stage Contract

stage contract 分成 load contracts、validate inputs、build time-series panel、apply policy template、compute metrics、build result output、validate result safety、write research output。前兩者目前僅 design-only；其餘涉及資料建構、績效或輸出者都維持 future-only 或 blocked。

## Prohibited Outputs

engine contract 禁止 live allocation、target weight、portfolio action、buy/sell/add/reduce signal、current market recommendation、public dashboard output 與 live recommendation。

## Prohibited Auto-Write Locations

engine contract 禁止自動寫入 `public`、`docs`、`site`、`dashboard`、`github_pages` 與 `data/backtests`。

## Required Safety Guards Before Execution

真正執行前，metric formula registry、result output contract、result safety validator、output location policy 與 result caveat policy 都必須通過 validator。結果不得自動輸出到 public/dashboard，也不得包含 live allocation 或 trade signal。

## 為什麼下一步先做 Result Output Contract

在計算任何績效前，必須先定義 result schema、允許欄位、禁止欄位、caveats 與輸出位置。否則 engine 即使計算正確，也無法保證結果安全呈現。

## Caveats

- contract-only
- no performance metrics
- no allocation
- no public output
- not investment advice

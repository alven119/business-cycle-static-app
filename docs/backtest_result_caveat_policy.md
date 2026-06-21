# Backtest Result Caveat Policy

## 背景

Phase 9A 到 9A3 已定義 real backtest engine contract、result output contract、metric formula registry 與 output location policy。這些 contract 仍不允許執行 real backtest 或產生結果。Phase 9A4 補上 result caveat policy，確保 future result 必須有清楚 caveat 與禁止語意。

## Phase 9A3 Output Location Policy 與 Phase 9A4 的關係

Output location policy 定義 future result 寫入位置與前置條件，但還沒有定義 result 內容必須如何提示風險。Caveat policy 定義 future result 必須顯示的 caveat、禁止文字與 validation rules。

## 為什麼 Caveat Policy 不是 Backtest Result

本階段只設計 caveat requirements。它不計算績效、不產生 result file、不建立 output directory、不寫入 `data/backtests` 或 `public`，也不提供 allocation 或交易訊號。

## Caveat Policy Scope

允許：

- 定義 required caveats。
- 定義 display requirements。
- 定義 prohibited text patterns。
- 定義 future result validation rules。
- 定義 future acceptance gates。

禁止：

- produce backtest results。
- compute metric values。
- write result files。
- write `data/backtests` 或 `public`。
- create output directories。
- produce allocation 或 trade signal。
- dashboard / resolver integration。

## Required Global Caveats

Future result 必須包含：

- backtest-only，不是目前配置建議。
- 回測結果不代表未來績效。
- 本結果僅供研究與模型驗證。
- 不構成投資建議。

## Required Contextual Caveats

Future result 必須依情境包含：

- revised data caveat。
- transaction cost caveat。
- false signal cost / whipsaw caveat。
- scenario-specific caveat。
- COVID exogenous shock caveat。

## Display Requirements

Caveat 必須靠近 result summary 與 metric table，必須包含在 export metadata 與 caveat report，語言必須是中文。Caveat 必須在任何 metric value 前可見，且不得只放在可折疊區塊中。

## Prohibited Text Patterns

禁止文字包含目前建議、建議買進、建議賣出、立即買進、立即賣出、目標配置、買進訊號、賣出訊號、加碼、減碼、保證、穩賺，以及 current recommendation、buy signal、sell signal、target weight、live allocation、rebalance now、guaranteed return、investment advice。

## Prohibited Interpretations

不得將回測結果解讀為目前配置建議，不得將 policy template 或 transition evidence watch 解讀為交易訊號，不得宣稱回測結果保證未來績效，也不得以單一 scenario 推論完整策略有效。

## Future Result Validation Rules

Future result validator 必須檢查 global caveats、prohibited text、caveats visible before metrics、metadata caveats、scenario-specific caveats 與 not investment advice caveat。

## Required Acceptance Before Result Generation

任何 future result generation 前必須先通過 caveat policy、result output contract、output location policy，並具備 result safety validator、prohibited text validator、no public auto-output guard 與 no live allocation / trade signal guard。

## Prohibited Result Fields

Future result 不得包含 live allocation、current allocation、target weight、target weights、portfolio action、buy/sell/add/reduce signal、rebalance now、current market recommendation、public dashboard output、dashboard portfolio action、live recommendation、phase override 或 decision override。

## 為什麼下一步做 Result Safety Validator Contract

Caveat policy 定義了文字與語意要求；下一步 Phase 9A5 應定義 result safety validator contract，讓 future result 能被系統性驗證為 no live allocation、no trade signal、no public auto-output。

## Caveats

- policy-only。
- no result file。
- no metric values。
- no allocation。
- no public output。
- not investment advice。

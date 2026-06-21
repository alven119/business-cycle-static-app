# Backtest Result Safety Validator Contract

## 背景

Phase 9A 到 9A4 已定義 real backtest engine contract、result output contract、metric formula registry、output location policy 與 result caveat policy。Phase 9A5 接續定義 future backtest result safety validator contract，讓後續 fixtures 與 runtime 有明確安全檢查範圍。

## Phase 9A4 Caveat Policy 與 Phase 9A5 的關係

Caveat policy 定義 future result 必須附帶哪些 caveats 與禁止文字。Safety validator contract 則定義 future validator 必須如何檢查 caveat presence、prohibited fields、prohibited text、output location、metadata caveats、scenario-specific caveats 與 no-live-decision status。

## 為什麼 Safety Validator Contract 不是 Validator Runtime

本階段只定義 contract。它不實作 validator runtime、不驗證任何真實 result、不計算績效、不產生 result file、不建立 output directory、不寫入 `data/backtests` 或 `public`。

## Validator Contract Scope

允許：

- 定義 safety validator contract。
- 定義 check groups。
- 定義 required caveat checks。
- 定義 prohibited field / text checks。
- 定義 output location checks。
- 定義 future acceptance gates。

禁止：

- run validator on real results。
- produce backtest results。
- compute metric values。
- write result files。
- write `data/backtests` 或 `public`。
- create output directories。
- produce allocation 或 trade signal。
- dashboard / resolver integration。

## Safety Check Groups

Required check groups 包含 prohibited field checks、prohibited text checks、required caveat checks、caveat visibility checks、output location checks、metadata caveat checks、scenario-specific caveat checks 與 no-live-decision checks。

## Prohibited Result Fields

Future validator 必須阻擋 live allocation、current allocation、target weight、target weights、portfolio action、buy/sell/add/reduce signal、rebalance now、current market recommendation、public dashboard output、dashboard portfolio action、live recommendation、phase override 與 decision override。

## Prohibited Text Patterns

Future validator 必須阻擋目前建議、建議買進、建議賣出、立即買進、立即賣出、目標配置、買進訊號、賣出訊號、加碼、減碼、保證、穩賺，以及 current recommendation、buy signal、sell signal、target weight、live allocation、rebalance now、guaranteed return、investment advice。

## Required Caveat Checks

Future validator 必須確認 backtest-only、不是目前配置建議、回測結果不代表未來績效、本結果僅供研究與模型驗證、不構成投資建議等 global caveats 存在，也必須檢查 revised data、transaction cost、false signal cost、scenario-specific 與 COVID exogenous shock caveats。

## Output Location Enforcement

Future validator 必須強制 public、GitHub Pages、dashboard、docs、site auto-output 都為 false。本階段仍禁止 `data/backtests` write 與 output directory creation。Future controlled research path 必須等 explicit writer 與 explicit user command。

## Validator Result Contract

Future validator 可以回傳 `passed` 或 `failed`，並包含 validation status、failed check ids、warning check ids、blocked reason、caveat presence status、prohibited field status、prohibited text status、output location status 與 no-live-decision status。本階段 `validator_runtime_allowed_now=false`、`real_result_validation_allowed_now=false`。

## Required Acceptance Before Validator Runtime

Runtime 前必須先通過 safety validator contract、result output contract、output location policy、result caveat policy，並定義 safety validator fixtures，驗證 prohibited text、live allocation / target weight 與 public auto-output fixture rejection。

## 為什麼下一步做 Safety Validator Fixtures

Contract 只定義應檢查什麼。Phase 9A6 應建立合法與非法 result fixtures，用 fixture 驗證 future safety validator 能阻擋 live allocation、trade signal、public auto-output、prohibited text 與 caveat 缺失。

## Caveats

- contract-only。
- no validator runtime。
- no real result validation。
- no result file。
- no metric values。
- no allocation。
- no public output。
- not investment advice。

# Real Backtest Prototype Readiness Gate

## 背景

Phase 8A 到 Phase 8H 已把 portfolio policy research 推進到 research-only / structural dry-run-only 的安全閉環。接近真正回測前，需要先定義 readiness gate，避免從 dry-run 直接跳到績效計算與結果輸出。

## Phase 8A-8H 已完成什麼

已完成 portfolio research planning、policy template schema、template fixtures、backtest input contract、scenario mapping、input fixtures、dry-run contract、dry-run fixtures、structural dry-run runner，以及 portfolio research safety closure checklist。

## 為什麼不能直接進 Real Backtest Prototype

真正回測會引入績效公式、結果 schema、輸出位置、結果 caveat 與誤用風險。若沒有獨立 contract 與 validator，回測結果可能被誤解為 live allocation、current market recommendation 或投資建議。

## Readiness Gate 的目的

Phase 8I 只定義進入 real backtest prototype 前的前置條件。它不計算績效、不產生結果、不寫 `data/backtests` 或 `public`，也不接 dashboard。

## Current Phase 8 Closure Checks

readiness gate 要求 Phase 8 safety closure 仍維持 research-only / structural dry-run-only。formal backtest、performance metrics、allocation、trade signal、`data/backtests` output、public output 與 live recommendation 都必須維持 false。

## Readiness Scope

本階段允許定義 real backtest engine contract、result output contract、metric formula registry、result safety validator、output location policy 與 next phase acceptance gates。

本階段禁止實作 real backtest engine、計算 performance metrics、產生 backtest results、寫入 `data/backtests`、寫入 `public`、產生 allocation、產生 trade signal 或接 dashboard。

## Required Contracts Before Real Backtest

真正 backtest prototype 前必須先定義：

- real backtest engine contract
- backtest result output contract
- metric formula registry
- backtest result safety validator
- output location policy
- result caveat policy

## Prototype Blockers

目前 blocker 仍 active，因為上述 contracts 尚未定義，且 public auto-output 與 live allocation 必須持續禁止。

## Allowed Future Phases

Phase 9A 可定義 real backtest engine contract，但仍不執行回測。Phase 9A1 可定義 result output contract。Phase 9A2 可定義 metric formula registry。Phase 9B 仍被阻擋，直到 result safety validator 與 output policy 完成。

## Required Acceptance Before Phase 9A

進入 Phase 9A 前，readiness gate 必須通過 validator，Phase 8 safety closure 必須仍有效，real backtest execution 必須仍 blocked，且 output location policy、metric registry、result safety validator 與 not investment advice caveat requirements 必須已定義。

## 為什麼 Phase 9A 仍只能做 Contract Design

Phase 9A 的任務是定義 engine contract，而不是執行回測。真正績效計算必須等 result output contract、metric registry、safety validator 與 output policy 都完成後才可進入 prototype。

## Caveats

- not real backtest
- no performance metrics
- no allocation
- no public output
- not investment advice

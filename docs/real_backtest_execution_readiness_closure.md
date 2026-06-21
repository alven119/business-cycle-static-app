# Real Backtest Execution Readiness Closure

## 背景

Phase 8A 到 8H 完成 portfolio research-only / structural dry-run-only 安全閉環。Phase 8I 定義進入 real backtest prototype 前的 readiness gate。Phase 9A 到 9A7 接續完成 engine、result output、metric registry、output location、caveat、safety validator、fixtures 與 writer contracts。

## Phase 9A–9A7 完成了什麼

- Phase 9A：real backtest engine contract。
- Phase 9A1：backtest result output contract。
- Phase 9A2：backtest metric formula registry。
- Phase 9A3：backtest output location policy。
- Phase 9A4：backtest result caveat policy。
- Phase 9A5：backtest result safety validator contract。
- Phase 9A6：backtest result safety validator fixtures。
- Phase 9A7：backtest result writer contract。

## 為什麼 9A8 仍不是 Real Backtest Execution

9A8 只做 readiness closure。它不實作 engine runtime、不實作 writer runtime、不實作 real result validator runtime、不執行回測、不計算 metric values、不產生 result file、不建立 output directory、不寫入 `data/backtests` 或 `public`。

## Source Artifacts

Closure 彙整 10 個 required artifacts：portfolio research safety closure、real backtest prototype readiness gate、real backtest engine contract、result output contract、metric formula registry、output location policy、result caveat policy、safety validator contract、safety validator fixtures 與 writer contract。

## Required Validator Commands

Required validator commands 包含 9A 到 9A7 的 show / validate commands，例如 engine contract、result output contract、metric registry、output location policy、caveat policy、safety validator contract、safety validator fixtures 與 writer contract。

## Readiness Scope

允許：

- validate contract stack readiness。
- summarize source artifacts。
- summarize safety boundaries。
- declare 9B entry readiness。
- define 9B entry conditions。
- define future 9B hard gates。

禁止：

- execute backtest。
- implement engine / writer / result validator runtime。
- compute metric values。
- produce result。
- write files or create directories。
- write `data/backtests` 或 `public`。
- produce allocation 或 trade signal。
- dashboard / resolver integration。

## Source Artifact Readiness

Closure 要求 `required_artifact_count=10`、all required artifacts present、all required artifacts validated，且 `phase_9a_contract_stack_complete=true`。

## Safety Boundary Summary

9A8 仍要求 research-only、backtest-only、not investment advice。Real backtest execution、engine runtime、writer runtime、result validator runtime、metric computation、result generation、file write、directory creation、`data/backtests` write、public write、allocation output、trade signal 與 live recommendation 目前全部不允許。

## Phase 9B Entry Conditions

9A8 可以宣告進入 Phase 9B controlled synthetic harness 的 readiness，但 9B 初始條件必須是 research-only / backtest-only。Default output write、public output、allocation output、trade signal 與 live recommendation 都必須 false。

## Remaining Blockers For Output Writing

Output writing 仍被 blocker 擋住：writer runtime 尚未實作、real result safety validator runtime 尚未實作、本階段沒有 explicit user command 寫入結果，且 public / dashboard / GitHub Pages auto-output 仍禁止。

## 為什麼下一步可以進 Controlled 9B Prototype

9A contract stack 已完成必要前置規格，因此可以進入 9B controlled synthetic in-memory calculation harness。但 9B 初始實作應先保持 synthetic fixture-only、不自動寫 output、不接 dashboard、不產生 live allocation、trade signal 或 current recommendation。

## 9B 初始 Scope 建議

- controlled synthetic in-memory calculation harness。
- no output write by default。
- no dashboard integration。
- no allocation / trade signal / current recommendation。
- required not investment advice caveat。

## Caveats

- readiness-only。
- no execution。
- no metric values。
- no result file。
- no output directory。
- no allocation。
- no public output。
- not investment advice。

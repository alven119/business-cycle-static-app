# Portfolio Research Safety Closure

## 背景

Phase 8A 到 Phase 8G 將 portfolio policy research 從研究想法推進到 schema、fixtures、contract、validator 與 stdout-only structural dry-run runner。這些 artifact 的目的，是讓未來真正 portfolio backtest 有明確輸入與安全邊界。

## Phase 8A-8G 已完成什麼

已完成 portfolio policy research plan、policy template schema、template fixtures、backtest input contract、scenario mapping、backtest input fixtures、dry-run engine contract、dry-run output fixtures，以及 structural dry-run runner。runner 只驗證 contract 與 valid fixtures，並產生 in-memory structural summary。

## 為什麼需要 Safety Closure

Phase 8A-8G 已經有完整研究前置規格，但仍不是正式回測。Safety closure 用來明確標記目前狀態是 research-only / structural dry-run-only，避免把 schema、fixtures 或 dry-run summary 誤解成績效結論、配置建議或交易訊號。

## Artifact Readiness

closure checklist 要求下列 artifact 都存在且維持 draft 狀態：

- portfolio policy research plan
- portfolio policy template schema
- portfolio policy template fixtures
- portfolio backtest input contract
- portfolio backtest scenario mapping
- portfolio backtest input fixtures
- portfolio backtest dry-run contract
- portfolio backtest dry-run fixtures

## Validator Readiness

closure checklist 彙整既有 summary / validation command，包括 policy plan summary、template schema summary、template fixture validation、backtest input contract summary、input fixture validation、dry-run contract summary、dry-run fixture validation，以及 structural dry-run runner。

## Safety Boundaries

目前邊界固定為 research-only 與 structural dry-run-only。formal backtest 沒有執行，performance metrics 沒有計算，allocation / target weight / trade signal 沒有產生，`data/backtests` 與 `public` 不由本階段寫入。

## Active Blockers Before Real Backtest

真正回測前仍需定義 real metric engine contract、result output contract、metric formula registry、result caveat validator、public output policy，以及 result 層級禁止 live allocation / current recommendation 的 guardrails。

## Required Before Real Backtest Prototype

進入 real backtest prototype 前，必須先完成真正 backtest engine contract、結果輸出 schema、績效公式 registry、no-live-allocation result validator、回測結果 caveat，以及 output location policy。

## Allowed Future Work

下一步可做 Phase 8I：real backtest prototype readiness gate。Phase 9A / 9B 仍被阻擋，直到 8I 與後續 result safety contract 完成。

## 為什麼 Phase 8A-8G 可收斂

Phase 8A-8G 已完成 research policy、template、input、dry-run output 與 structural runner 的安全閉環。這足以把目前狀態收斂成 fully specified research-only foundation。

## 為什麼下一步不是直接跑正式回測

正式回測會引入績效計算、結果檔案、資料輸出位置與結果解讀風險。這些都需要獨立 contract、validator 與 caveat policy，不能由 structural dry-run 直接跳過。

## Recommended Next Phase

Recommended next phase 是 Phase 8I：real backtest prototype readiness gate。

## Caveats

- research-only
- structural dry-run only
- no performance conclusion
- no allocation
- not investment advice

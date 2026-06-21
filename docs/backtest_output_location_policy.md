# Backtest Output Location Policy

## 背景

Phase 9A 到 9A2 已完成 real backtest engine contract、backtest result output contract 與 metric formula registry。這些 contract 仍不允許執行回測或產生結果。Phase 9A3 補上 output location policy，先定義 future result 可以在什麼前置條件下寫到哪裡。

## Phase 9A2 Metric Registry 與 Phase 9A3 的關係

Metric registry 定義 future backtest 公式，但不計算 metric values。Output location policy 則定義若未來有 result writer，結果只能在通過 safety validation 與 caveat validation 後寫入受控 research path。

## 為什麼 Output Location Policy 不是 Output Writer

本 policy 只描述位置規則與安全依賴。它不建立資料夾、不寫 JSON / CSV / Markdown、不同步 public、不觸發 dashboard，也不代表 `data/backtests` 現在可以被寫入。

## Location Policy Scope

允許：

- 定義 output location policy。
- 定義 future controlled research paths。
- 定義 prohibited auto-write locations。
- 定義 write preconditions。
- 定義 safety dependencies。
- 定義 future acceptance gates。

禁止：

- write result files。
- write `data/backtests` 或 `public`。
- create output directories。
- execute backtest。
- compute metric values。
- produce backtest results。
- produce allocation 或 trade signal。
- dashboard / GitHub Pages integration。

## Future Controlled Research Path

Policy 定義 `data/backtests/research` 可作為 future controlled local research path，但只能在未來 explicit output writer phase 後使用。該 path 不允許 auto publication，不允許 git tracking，且必須通過 result safety validation、caveat validation 與 explicit user command。

## 為什麼本階段仍不得建立 Data Backtests Research

建立資料夾本身會讓 policy phase 變成 writer preparation。Phase 9A3 的目的只是定義規則，因此 `create_output_directories_allowed=false`，也不得建立 `data/backtests/research`。

## Prohibited Auto-Write Locations

禁止自動寫入：

- `public`
- `docs`
- `site`
- `dashboard`
- `github_pages`
- `data/backtests`
- `data/raw`
- `specs`
- `src`
- `tests`

## Prohibited Auto-Publication

Policy 禁止 public dashboard output、GitHub Pages output、docs output、site output 與 dashboard renderer output。回測結果不得自動進入任何公開或展示層。

## Write Preconditions Before Any Result File

未來任何 result file 寫入前，必須先通過 result output contract、metric formula registry、result safety validator、result caveat policy、output location policy，且必須另有 explicit output writer phase 與 explicit user command。

## Output File Policy

Future-only 副檔名可包含 `.json`、`.csv`、`.md`。本階段 `default_write_allowed_now=false`、`overwrite_allowed_now=false`、`append_allowed_now=false`、`directory_creation_allowed_now=false`、`public_sync_allowed_now=false`、`git_track_result_files_allowed_now=false`。

## Required Safety Dependencies

未來寫入結果前必須先完成：

- backtest result safety validator。
- backtest result caveat policy。
- explicit output writer contract。

## Prohibited Result Fields For Written Output

任何 future written output 都不得包含 live allocation、target weight、buy/sell signal、current recommendation、public dashboard output、phase override 或 decision override。

## 為什麼下一步先做 Result Caveat Policy

在定義 writer 前，必須先確保 result caveats 是可驗證的。Phase 9A4 應定義 backtest result caveat policy，強制 future result 標記 backtest-only、不代表未來績效、不構成投資建議。

## Caveats

- policy-only。
- no output writer。
- no result file。
- no public output。
- not investment advice。

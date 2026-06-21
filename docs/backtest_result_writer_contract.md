# Backtest Result Writer Contract

## 背景

Phase 9A 到 9A6 已完成 real backtest engine contract、result output contract、metric formula registry、output location policy、result caveat policy、safety validator contract 與 safety validator fixtures。Phase 9A7 接續定義 future backtest result writer contract，讓未來 writer runtime 有明確的輸出位置、觸發條件與 pre-write safety requirements。

## Phase 9A6 Fixtures 與 Phase 9A7 的關係

Phase 9A6 fixtures 驗證 future safety validator contract 能阻擋 live allocation、target weight、trade signal、current recommendation、public auto-output、prohibited text 與 caveat 缺失。Writer contract 要求 future writer 在任何寫檔前必須依賴 safety validator runtime 與 safety validation pass。

## 為什麼 Writer Contract 不是 Writer Runtime

本階段只定義 contract。它不實作 writer runtime、不建立 output directory、不寫 result file、不執行 backtest、不計算 metric values、不產生 allocation、不寫入 `data/backtests` 或 `public`。

## Writer Contract Scope

允許：

- 定義 writer contract。
- 定義 pre-write validations。
- 定義 allowed future output path。
- 定義 prohibited write locations。
- 定義 writer status fields。
- 定義 future acceptance gates。

禁止：

- implement writer runtime。
- write result files。
- create output directories。
- write `data/backtests`、`public`、docs、dashboard 或 GitHub Pages。
- execute backtest。
- compute metric values。
- produce allocation 或 trade signal。
- dashboard / resolver integration。

## Future Writer Trigger Policy

Future writer 必須由 explicit user command 觸發。Automatic write、scheduled write、dashboard-triggered write、GitHub Pages-triggered write 與 CI auto write 都必須維持 false。Future writer 預設必須 dry-run，且 overwrite / append 預設不得開啟。

## Allowed Future Output Paths

唯一 future controlled research path 是 `data/backtests/research`。此 path 只是一個 contract definition，本階段不得建立資料夾或寫入任何檔案。未來使用前必須有 writer runtime phase、explicit user command、safety validator pass、caveat policy pass 與 output location policy pass。

## Prohibited Write Locations

Writer contract 禁止自動寫入 public、docs、site、dashboard、github_pages、data/backtests、data/raw、specs、src 與 tests。

## Required Pre-Write Validations

Future writer 寫檔前必須先驗證 result output contract、metric formula registry、output location policy、result caveat policy、result safety validator contract 與 safety validator fixtures。真正寫檔前也必須有 safety validator runtime、result safety validation passed、explicit user command、no public auto-output 與 no live allocation / trade signal。

## Writer Status Contract

本階段 `writer_runtime_allowed_now=false`、`result_file_write_allowed_now=false`、`output_directory_creation_allowed_now=false`、`data_backtests_write_allowed_now=false`、`public_write_allowed_now=false`。Future writer status 可包含 dry_run_passed、write_blocked、write_completed 與 validation_failed。

## Prohibited Result Fields For Writer

Future writer 必須拒絕 live allocation、current allocation、target weight、portfolio action、buy/sell/add/reduce signal、rebalance now、current market recommendation、public dashboard output、dashboard portfolio action、live recommendation、phase override 與 decision override。

## Required Writer Caveats

Future written result 必須包含 backtest-only、不是目前配置建議、回測結果不代表未來績效、本結果僅供研究與模型驗證、不構成投資建議。

## 為什麼下一步做 Real Backtest Execution Readiness Closure

9A7 完成後，9A 到 9A7 已形成 execution 前的 contract stack。下一步應彙整 engine、result、metric、location、caveat、safety validator、fixtures 與 writer contracts，確認是否具備進入 9B real backtest prototype 的前置條件。

## Caveats

- contract-only。
- no writer runtime。
- no output directory。
- no result file。
- no metric values。
- no allocation。
- no public output。
- not investment advice。

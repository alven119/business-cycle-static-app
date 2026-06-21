# Controlled synthetic in-memory calculation harness

## 背景

Phase 9B 是 portfolio research pipeline 的 controlled synthetic in-memory calculation harness。它建立在 Phase 9A8 readiness closure 之後，只允許使用 deterministic fixtures，在 memory 中測試 backtest panel、policy schedule application 與 controlled metric computation。

## 9A8 readiness closure 與 9B 的關係

Phase 9A8 已彙整 engine contract、result output contract、metric formula registry、output location policy、caveat policy、result safety validator contract、fixtures 與 writer contract。9B 只允許 synthetic harness，不得宣稱已驗證書籍策略、歷史績效、景氣模型或 point-in-time 可交易性。

## 為什麼 9B 是 synthetic harness，不是 production backtest

9B 不讀取外部 market data，不呼叫 FRED，不接 dashboard，不寫 result file，也不建立 output directory。它只用 fixture data 驗證 arithmetic flow，因此不是 production backtest、不是書籍策略重現，也不是可發布結果。

## Prototype fixture data

Fixture 位於：

```text
specs/portfolio/controlled_real_backtest_prototype_fixtures.yaml
```

每個 case 都必須標記 `data_mode=controlled_fixture_only`、`backtest_only=true`、`synthetic_fixture_only=true`、`economic_validity_established=false`、`book_fidelity_validated=false` 與 `point_in_time_validated=false`。Policy 權重只能使用 `backtest_policy_weights`，不得使用 live allocation、current allocation、target weight、buy/sell/add/reduce signal 或 current market recommendation。

## In-memory calculation flow

Prototype runner 只在 memory 中執行：

1. 載入 controlled fixture YAML。
2. 驗證 prohibited fields 與 prohibited text 不存在。
3. 檢查 period、asset return series 與 backtest policy weight series 長度一致。
4. 計算每期 portfolio return。
5. 建立 in-memory portfolio value path。
6. 計算 controlled fixture metrics。
7. 輸出 summary flags 與 counts。

## Controlled metrics

Phase 9B 允許從 fixture data 在 memory 中計算：

- `total_return`
- `annualized_return`
- `volatility`
- `max_drawdown`
- `turnover`

CLI 只輸出 `computed_metric_count` 與 safety flags，不輸出完整 metric table。

## No output write by default

Phase 9B 不寫任何 result file，不建立 `data/backtests/research`，不寫入 `data/backtests`、`public`、`docs`、`site`、`dashboard` 或 `github_pages`。Future output writer 必須另有 explicit writer runtime phase、explicit user command 與 result safety validation。

## Prohibited outputs

Prototype fixture、runner 與 CLI 均不得產生 live allocation、current market recommendation、target weight、portfolio action、buy/sell/add/reduce signal、phase override、decision override 或 dashboard output。

## Safety flags

CLI 必須輸出：

```text
in_memory_only=true
synthetic_fixture_only=true
controlled_metric_computation_allowed=true
economic_validity_established=false
book_fidelity_validated=false
point_in_time_validated=false
result_file_written=false
data_backtests_output_written=false
public_output_written=false
output_directory_created=false
allocation_output_generated=false
trade_signal_generated=false
live_recommendation_generated=false
dashboard_integration=false
result=passed
```

## 為什麼暫停 9B1

QA0 完成審核前暫停 9B1。9B 只驗證 controlled synthetic arithmetic flow；尚未建立 book-to-code traceability、point-in-time release/vintage protection、cash-flow-aware book benchmark methodology 或 calibration holdout policy。

## Caveats

- controlled prototype only
- fixture-only
- in-memory only
- no result file
- no dashboard integration
- no live allocation
- no trade signal
- not investment advice
- 不構成投資建議

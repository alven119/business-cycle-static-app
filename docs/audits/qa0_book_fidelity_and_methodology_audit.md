# QA0 book fidelity and methodology audit

## 背景

QA0 暫停 Phase 9B1，對 book fidelity、temporal integrity、cash-flow methodology、calibration leakage、context anchoring、indicator coverage、book benchmark、regime gap、exogenous shock overlay 與 dashboard semantics 做收斂稽核。

QA0 pass 只代表 audit 完整、findings 已分類、P0 有 blocking gate、unsupported claims 已移除，且 real backtest progression 維持 blocked。它不代表模型已驗證、point-in-time backtest 已完成、書中策略已重現或可作為投資依據。

## Book-to-code traceability

Machine-readable traceability 位於：

```text
specs/audits/book_method_traceability.yaml
```

每列包含 requirement、book page reference、fidelity class、implementation status、paths、limitations、divergence、severity 與 remediation phase。缺失與 conflicting rows 會阻擋 `book_alignment_claim_allowed`。

## Temporal integrity

Temporal policy 位於：

```text
specs/audits/temporal_integrity_policy.yaml
specs/common/series_release_lag_registry.yaml
```

最低 point-in-time 條件是：

```text
observation_date <= as_of
available_at <= as_of
vintage_date <= as_of
```

QA1 後，38 個 discovered series 都有明確 availability status。這只代表 metadata inventory complete，不代表 strict point-in-time cache coverage complete。

Temporal modes 已拆分為 `revised`、`release_lag_adjusted_revised_proxy`、`initial_release_only` 與 `vintage_as_of`。發布延遲 proxy 不屬於 strict vintage mode；initial-release-only 也不等同歷史 as-of 當日可見的最新 vintage。Strict `vintage_as_of` 必須使用 date-level `realtime_start` / `realtime_end` interval，並以 end-of-day as-of policy 解讀。缺 metadata 或 cache 時必須 fail closed。

因此 `point_in_time_backtest_ready=false` 仍維持。即使 selector/provider/cache 已建立，real backtest progression 仍需等待後續書籍方法、market total-return 與 calibration gates。

## Cash-flow methodology

QA0 在 metric registry 中加入 cash-flow-aware methodology。若 external cashflows 存在，禁止使用 `ending_value / beginning_value - 1` 當策略收益。Book benchmark 必須使用 terminal wealth、total contributions、net investment gain、TWR、money-weighted return / XIRR、unitized NAV 與 unitized NAV drawdown。

## Calibration leakage

目前 dotcom、GFC、COVID、euro debt、late-cycle 2018 都已用於 development / diagnostics，不得視為 unused final holdout。Final holdout 必須在 parameter freeze 前保留，且結果不得再用於調參。

## Context ablation

QA0 建立 synthetic ablation，量化 baseline context 對 final state machine phase、confidence 與 display hint 的影響。若 context 改變會改變 final phase 或 confidence，則 `external_context_dependency_detected=true` 且 `data_only_model_validated=false`。

## Indicator coverage

Book indicator coverage 位於：

```text
specs/audits/book_indicator_coverage.yaml
```

Modern extensions 如 yield curve、financial conditions、credit spreads、policy rate 與 oil pressure 必須標為 modern extension，不得取代 missing book core 後宣稱完整書籍對齊。

## Book strategy golden benchmark

Golden benchmark spec 位於：

```text
specs/portfolio/book_strategy_golden_benchmark.yaml
```

它定義 1994 到 2018、10,000 USD 初始投入、每年最後交易日追加 10,000 USD、每年第一交易日再平衡、五組策略、70/50/30 rule 與 7 年以上美國長期政府公債要求。此 spec 不執行市場回測。

## Regime gap

Productivity / inflation regime gap 位於：

```text
specs/audits/productivity_inflation_regime_gap.yaml
```

目前 formal regime layer 與 regime-aware portfolio policy 都未完成，因此不能宣稱完整書籍 regime 對齊。

## Exogenous shock overlay

Shock overlay spec 位於：

```text
specs/audits/exogenous_shock_overlay_gap.yaml
```

Overlay 不得直接產生 portfolio action，不得自動 override phase，且 COVID 不得直接用一般週期 lead-time performance 來概化評價。

## Dashboard semantics

Dashboard semantics contract 位於：

```text
specs/audits/dashboard_semantics_contract.yaml
```

Dashboard 必須區分 data completeness、freshness、indicator confidence、phase evidence strength、model confidence、transition risk、decision confidence 與 external context dependency。

## Phase 9B classification

Phase 9B 只能稱為 controlled synthetic in-memory calculation harness。它不驗證書籍策略、歷史績效、景氣模型或 point-in-time 可交易性。

## Phase QA0.1 inventory reconciliation

QA0 是 initial audit baseline。QA0.1 補上 canonical requirement manifest、repository inventory、inventory reconciliation 與 anti-hardcoding checks。

QA0.1 要求：

- 每個 canonical requirement 恰好有一個 traceability row。
- 每個 formal / experimental indicator 都有 provenance mapping。
- 每個 discovered series 都被 temporal audit inventory 納入。
- 每個 canonical indicator requirement 都有 coverage row，即使狀態是 missing。
- QA0 aggregate summary 必須由 specs / inventory 動態計算，不得使用固定 count。

QA0.1 pass 只代表清冊完整與 drift detection 可運作，不代表 book alignment、point-in-time readiness、real backtest readiness 或 investment readiness。

QA1 taxonomy 補充 `source_authority`、`book_fidelity_class` 與 `readiness_criticality`。Modern methodology 可以是 P0，但不得標為 `book_core`。`canonical_book_indicator_requirement_count` 表示 40 個 canonical indicator requirements；`phase_role_indicator_coverage_row_count` 表示 63 筆 phase-specific coverage rows。兩者不再共用含義不明的 count。

## Next phase

QA0.1 完成後 recommended next phase 仍是 QA1，不是 9B1。QA1 應處理 temporal integrity P0 blockers 與 methodology gaps。

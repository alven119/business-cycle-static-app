# Book-Aligned Indicator Implementation Plan

Phase 7F 建立書籍方法論對齊指標的實作計畫，但不修改 scoring、phase resolver、FRED provider 或 live dashboard。

Machine-readable spec：

```text
specs/backtests/book_aligned_indicator_implementation_plan.yaml
```

查看摘要：

```bash
python scripts/show_book_indicator_plan.py
```

## 為什麼不再硬調 breadth rule

Phase 7E.1 的 breadth sensitivity 顯示，單靠 recession breadth rule 無法同時滿足所有 acceptance targets。較嚴格的 `v4_core_plus_financial` / `v6_strict_core` 可以擋掉 COVID 2019 early false recession，但會漏掉 dotcom 與金融海嘯的 recession detection；較寬鬆的 `v2_current_breadth` / `v3_core_required` / `v5_no_trade_as_core` 可以保留 dotcom 與金融海嘯，卻擋不掉 COVID 2019 false positive。

這代表問題不只是 breadth rule 太鬆或太嚴，而是 MVP 指標覆蓋仍不足。繼續硬調 breadth 容易在單一歷史案例上 overfit。

## 為什麼要補書籍方法論指標

目前 MVP 指標已涵蓋就業、消費、投資、進出口、利率與原物料，但對三個關鍵環節仍不夠完整：

- 衰退確認：需要更多就業廣度、廣義消費、投資訂單、信用壓力與金融條件確認。
- 榮景結束：需要更完整的利率曲線、信用利差、金融壓力、油價壓力與生產/訂單轉弱訊號。
- 衰退落底：需要高峰反轉、政策寬鬆已到位、信用壓力緩和與需求止跌訊號。

Phase 7F 先定義候選指標與驗收方法，後續才分批工程化。

## 實作批次

Phase 7F1：衰退確認指標

- 續領失業救濟金人數。
- 投保失業率。
- 失業 15 週以上人數。
- 實質個人消費支出。
- 金融壓力指數。
- 信用利差。

Phase 7F1 已先把這批指標做成 experimental candidate outputs：

```text
specs/backtests/recession_confirmation_candidate_indicators.yaml
specs/common/experimental_indicator_groups.yaml
```

檢查本機 raw cache coverage：

```bash
python scripts/check_recession_confirmation_candidate_coverage.py
```

對單一 as-of 日期計算 candidate scores：

```bash
python scripts/score_recession_confirmation_candidates.py --as-of 2019-02-28
```

輸出位於：

```text
data/backtests/candidate_indicators/recession_confirmation/<as_of>/candidate_indicator_scores.json
```

這些分數只供 recession confirmation diagnostics 與後續 calibration 使用，不接正式 phase scoring、不改 resolver，也不會出現在 live dashboard。Phase 7F1.2 才會把 candidate indicators 放進 calibration experiment 檢查。

## Phase 7F1.1 Candidate FRED Cache

Phase 7F1.1 新增 candidate series cache updater，先把 recession confirmation candidate FRED series 下載到本機 raw cache，讓 experimental scoring 可以產生實際分數。

Dry run：

```bash
python scripts/update_recession_confirmation_candidate_data.py --dry-run
```

只檢查本機 cache、不呼叫 API：

```bash
python scripts/update_recession_confirmation_candidate_data.py --no-api
```

真實下載需本機環境有 `FRED_API_KEY`：

```bash
python scripts/update_recession_confirmation_candidate_data.py
```

下載後可重新檢查 coverage 與 candidate scores：

```bash
python scripts/check_recession_confirmation_candidate_coverage.py
python scripts/score_recession_confirmation_candidates.py --as-of 2019-02-28
```

Raw cache 仍寫入 ignored `data/raw/fred/`，不得 commit。這些資料只供 experimental candidate indicators 使用，不會接入 live dashboard，也不構成投資建議。

## Phase 7F1.2 Candidate Recession Diagnostics

Phase 7F1.2 將 candidate scores 放進歷史案例 diagnostic points，比較 COVID 2019 early false recession、COVID 2020 真實衝擊、dotcom/GFC recession window，以及 euro debt / 2018 non-recession cases。

Diagnostic windows：

```text
specs/backtests/candidate_recession_diagnostic_windows.yaml
```

執行：

```bash
python scripts/run_candidate_recession_diagnostics.py
```

輸出：

```text
data/backtests/candidate_indicators/recession_confirmation_diagnostics/candidate_recession_diagnostics.json
```

此 diagnostic 會計算 candidate indicator 的 high signal、strong signal、group breadth 與 weighted confirmation score。這些門檻只供診斷，不是正式模型規則，不會改 live dashboard，也不構成投資建議。

## Phase 7F1.3 Experimental Confirmation Rule

Phase 7F1.3 在 candidate diagnostics 上新增 experimental recession confirmation rule：

```text
specs/backtests/candidate_recession_confirmation_rule.yaml
```

執行：

```bash
python scripts/run_candidate_recession_diagnostics.py
python scripts/run_candidate_recession_rule.py
```

此 rule 同時使用：

- group breadth。
- high confidence high signal count。
- high signal count。
- weighted confirmation score。

分類結果為 `confirmed`、`watch`、`weak`、`none`。它不是正式 phase scoring，也不會修改 resolver 或 live dashboard。若結果合理，下一步 Phase 7F1.4 才能做 full-horizon experimental transition overlay。本內容不構成投資建議。

## Phase 7F1.4 Full-Horizon Overlay

Phase 7F1.4 將 experimental candidate recession confirmation rule 疊加到 full-horizon scenario timeline 上，檢查原始 timeline 的 confirmed recession 是否得到 candidate rule 支持。

```bash
python scripts/run_candidate_recession_overlay.py --experiment-id candidate_recession_overlay_v1
```

輸出：

```text
data/backtests/candidate_indicators/recession_confirmation_overlay/candidate_recession_overlay_report.json
```

Overlay 只新增 diagnostics 欄位，不覆寫既有 timeline，也不修改正式 resolver。它的用途是觀察 candidate rule 是否能降低 false confirmed recession，同時保留 GFC / COVID 2020 等明確衰退案例。若結果合理，下一步 Phase 7F1.5 才討論 experimental phase scoring / transition control integration design。本內容不構成投資建議。

## Phase 7F1.5 Integration Design

Phase 7F1.5 將 candidate recession diagnostics、rule report 與 full-horizon overlay 的結果整理成整合設計與 guardrails：

```text
specs/backtests/candidate_recession_integration_design.yaml
docs/candidate_recession_integration_design.md
```

設計結論是：candidate rule 可以作為 diagnostics 或 soft confirmation filter 的候選基礎，但目前不能作為 hard gate。原因是 dotcom_bubble 在 overlay 中被降級為 watch，若只允許 candidate confirmed 才能 confirmed recession，可能漏掉歷史衰退案例。

因此 Phase 7F1.5 不接入正式 scoring、不改 resolver、不影響 live dashboard。下一步應進 Phase 7F2 補強榮景期結束與衰退前風險指標，而不是直接把 recession confirmation rule 正式啟用。本內容不構成投資建議。

Phase 7F2：榮景期結束指標

- 10Y-3M 與 10Y-2Y yield curve。
- Baa-Aaa 信用利差。
- 工業生產。
- 耐久財訂單精煉訊號。
- 油價壓力。
- Fed 政策反轉訊號。

## Phase 7F2 Boom Ending Candidate Indicators

Phase 7F2 已先把第一批榮景期結束 / late-cycle transition 指標做成 experimental candidate outputs：

```text
specs/backtests/boom_ending_candidate_indicators.yaml
```

本階段只支援 coverage check、candidate data updater 與獨立 scoring，不接正式 phase scoring、不改 resolver，也不會讓 live dashboard 使用這批指標。

檢查本機 raw cache coverage：

```bash
python scripts/check_boom_ending_candidate_coverage.py
```

Dry run / no-api cache check：

```bash
python scripts/update_boom_ending_candidate_data.py --dry-run
python scripts/update_boom_ending_candidate_data.py --no-api
```

對單一 as-of 日期計算 candidate scores：

```bash
python scripts/score_boom_ending_candidates.py --as-of 2019-02-28
```

輸出位於：

```text
data/backtests/candidate_indicators/boom_ending/<as_of>/candidate_indicator_scores.json
```

這些分數只供榮景期結束與衰退前風險 diagnostics 使用。下一步 Phase 7F2.1 才會建立 boom ending diagnostics / overlay。本階段不構成投資建議。

## Phase 7F2.1 Boom Ending Diagnostics

Phase 7F2.1 建立 boom ending candidate diagnostics，目標是檢查這批指標是否能在 confirmed recession 之前，較早提示榮景期結束或 late-cycle risk。

```bash
python scripts/run_boom_ending_diagnostics.py
```

輸出：

```text
data/backtests/candidate_indicators/boom_ending_diagnostics/boom_ending_diagnostics.json
```

此 diagnostics 會比較 dotcom、GFC、COVID、late cycle 2018 與 euro debt 等固定 as-of points，並計算 group breadth、high signal count、weighted boom-ending score 與 `strong/watch/weak/none` 狀態。

這些結果只用於模型校準與 early-warning 診斷，不接 live model、不產生配置建議，也不構成投資建議。

## Phase 7F2.2 Attribution And Refinement Plan

Phase 7F2.2 針對 boom ending diagnostics 做 attribution 與 scoring refinement plan。7F2.1 顯示 dotcom 與 COVID 2019 可達 watch，但 GFC 2006 / 2007 仍偏 weak，GFC 2008 也只是 watch。因此本階段先解釋指標貢獻與缺口，不直接調 scoring。

```bash
python scripts/run_boom_ending_diagnostics.py
python scripts/run_boom_ending_attribution.py
python scripts/show_boom_ending_refinement_plan.py
```

Refinement plan：

```text
specs/backtests/boom_ending_refinement_plan.yaml
```

目前建議優先檢查 yield curve lead-time pressure、`credit_spread_baa_10y` proxy 適用性、financial conditions delta、Fed policy peak/pause signal，以及 experimental boom ending watch rule。這些仍不接 live model，也不構成投資建議。

## Phase 7F2.3 Scoring Refinement Experiment

Phase 7F2.3 依據 7F2.2 refinement plan 實作 experimental scoring refinements，並比較 baseline 與 refined diagnostics。

```bash
python scripts/run_boom_ending_diagnostics.py
python scripts/run_boom_ending_refinement_experiment.py
```

Refinement 包含：

- yield curve lead-time pressure。
- credit spread velocity 與 BAA - AAA / BAA - DGS10 proxy 比較。
- financial conditions delta。
- Fed policy peak / pause pressure。

輸出：

```text
data/backtests/candidate_indicators/boom_ending_refinement/boom_ending_refinement_experiment.json
```

這仍是 experimental comparison，不接正式 phase scoring、不改 resolver、不進 live dashboard，也不構成投資建議。

## Phase 7F2.4 Boom Ending Watch Rule

Phase 7F2.4 將 refined boom ending diagnostics 轉成 experimental watch rule。Rule 狀態包含：

- `strong_late_cycle_warning`
- `watch`
- `weak`
- `none`

`watch` 的用途是 early warning / 減碼風險提示研究，不是 confirmed recession，也不是正式投資配置建議。Rule 支援 rates-policy cluster watch：當 yield curve / Fed policy 多個訊號集中於 rates policy 群組時，可形成 watch，但不能直接升為 strong。

此階段仍不接 live model、不改正式 phase scoring、不改 resolver、不進 dashboard，也不構成投資建議。

## Phase 7F2.5 Boom Ending Watch Overlay

Phase 7F2.5 將 experimental boom ending watch rule 疊加到 full-horizon scenario timeline，檢查 watch 是否早於 confirmed recession 出現，以及 non-recession 案例是否出現過度長期警報。

```bash
python scripts/run_boom_ending_watch_overlay.py
```

輸出：

```text
data/backtests/candidate_indicators/boom_ending_watch_overlay/boom_ending_watch_overlay_report.json
```

Overlay 只新增 experimental diagnostics，不覆寫既有 timeline，不改 current phase，也不把 boom ending watch 解讀為 confirmed recession。COVID 這類外生衝擊案例需保留 caveat：boom ending 指標可能是同步壓力反映，不代表事前預測。

此階段不接 live model、不改正式 phase scoring、不改 resolver、不進 dashboard，也不構成投資建議。

## Phase 7F2.6 Boom Ending Watch Integration Guardrails

Phase 7F2.6 根據 full-horizon overlay 建立 boom ending watch integration guardrails。Guardrails 的核心結論是：watch 可作為 early-warning diagnostics，但不得直接 confirmed recession，也不得直接觸發 portfolio action。

```bash
python scripts/show_boom_ending_watch_integration_guardrails.py
```

Guardrails 要求未來 live integration 前必須定義 watch density 上限、persistence、cooldown、外生衝擊 caveat 與 portfolio backtest。下一步應進 Phase 7F3，補齊 recession trough / recovery candidate indicators，讓減碼與再加碼流程更完整。

本階段不接 live model、不改正式 phase scoring、不改 resolver、不進 dashboard，也不構成投資建議。

Phase 7F3：衰退落底與復甦反轉指標

- 初領失業救濟金高峰反轉。
- 短期失業人數高峰反轉。
- 消費與耐久財落底。
- 訂單落底。
- 寬鬆政策已到位。
- 信用壓力緩和。

## Phase 7F3 Recession Trough / Recovery Candidate Indicators

Phase 7F3 實作第一批 recession trough / recovery candidate indicators。這些指標只供 experimental diagnostics 使用，不加入正式 `indicator_catalog.yaml`、不改 phase scoring、不改 resolver，也不會讓 live dashboard 使用。

Candidate spec：

```text
specs/backtests/recovery_candidate_indicators.yaml
```

執行方式：

```bash
python scripts/check_recovery_candidate_coverage.py
python scripts/update_recovery_candidate_data.py --dry-run
python scripts/update_recovery_candidate_data.py --no-api
python scripts/score_recovery_candidates.py --as-of 2009-03-31
```

這批 candidate indicators 聚焦於：

- 初領 / 續領失業救濟金與短期失業人數高點反轉。
- 實質零售銷售、PCE、耐久財訂單與工業生產落底回升。
- 信用利差與金融壓力緩解。
- Fed policy easing support。

下一步 Phase 7F3.1 才會把這些 candidate scores 放進 recovery diagnostics / overlay，檢查它們是否能辨識衰退落底與復甦起點。本階段不構成投資建議。

## Phase 7F3.1 Recovery Diagnostics

Phase 7F3.1 將 recovery candidate scores 放進固定 historical diagnostic points，用來檢查 recession trough / recovery candidates 是否能合理辨識衰退中段、落底附近與復甦初期。

```bash
python scripts/run_recovery_diagnostics.py
```

輸出：

```text
data/backtests/candidate_indicators/recovery_diagnostics/recovery_diagnostics.json
```

Diagnostics 明確限制：policy easing 只能作為 support signal，不得單獨確認 recovery；`recovery watch` 不等於正式復甦確認。COVID 類外生衝擊案例需標記 caveat，快速反彈不等同一般景氣循環復甦。

本階段不接正式模型、不改 phase scoring、不改 resolver、不進 dashboard，也不構成投資建議。

## Phase 7F3.2 Recovery Attribution And Refinement Plan

Phase 7F3.2 針對 7F3.1 diagnostics 的 mismatch 做 attribution 與 refinement plan。重點問題包括：euro debt 2011 被判為 strong、late-cycle 2018 被判為 watch、dotcom 2002-03 與 COVID 2020-04 recovery watch miss。

```bash
python scripts/run_recovery_diagnostics.py
python scripts/run_recovery_attribution.py
python scripts/show_recovery_refinement_plan.py
```

輸出：

```text
data/backtests/candidate_indicators/recovery_diagnostics/recovery_attribution.json
specs/backtests/recovery_refinement_plan.yaml
```

此階段結論聚焦於後續需要 `recession_context_gate` 與 `policy_and_financial_support_cap`：policy / financial easing 可支持 recovery，但不得單獨確認 recovery。下一步 Phase 7F3.3 才會實作 experimental scoring refinements。本階段不改正式模型、不進 dashboard，也不構成投資建議。

## Phase 7F3.3 Recovery Scoring Refinement Experiment

Phase 7F3.3 實作 experimental recovery scoring refinements，加入 recession-context gate 與 policy/financial support cap，並比較 baseline diagnostics 與 refined diagnostics。

```bash
python scripts/run_recovery_diagnostics.py
python scripts/run_recovery_refinement_experiment.py
```

輸出：

```text
data/backtests/candidate_indicators/recovery_refinement/recovery_refinement_experiment.json
```

Refinement 目標是降低 euro debt / 2018 non-recession false positives，同時保留 GFC trough / recovery evidence，並改善 dotcom 與 COVID trough watch。COVID 仍需保留 exogenous shock caveat。此階段仍不接正式模型、不改 phase scoring、不改 resolver、不進 dashboard，也不構成投資建議。

## Phase 7F3.4 Recovery Watch Rule

Phase 7F3.4 在 7F3.3 refined recovery diagnostics 上建立 experimental recovery watch rule，用於判斷 `strong_recovery_watch`、`recovery_watch`、`weak`、`none`。

```bash
python scripts/run_recovery_diagnostics.py
python scripts/run_recovery_refinement_experiment.py
python scripts/run_recovery_watch_rule.py
```

輸出：

```text
data/backtests/candidate_indicators/recovery_watch_rule/recovery_watch_rule_report.json
```

此 rule 明確保留 recession-context gate 與 support-signal cap：policy easing 與 financial easing 不得單獨確認 recovery；沒有 recession context 時最多只能是 weak。COVID 類外生衝擊可以有 caveated recovery watch，但不得被解讀為一般景氣循環復甦確認。

本階段只做 experimental diagnostics / future portfolio policy research，不接正式模型、不改 phase scoring、不改 resolver、不進 dashboard，也不構成投資建議。

## Phase 7F3.5 Recovery Watch Overlay

Phase 7F3.5 將 experimental recovery watch rule 疊加到 full-horizon scenario timeline，用來檢查 recovery watch 在完整歷史案例中是否太密集、太早或太晚。

```bash
python scripts/run_recovery_watch_overlay.py
```

輸出：

```text
data/backtests/candidate_indicators/recovery_watch_overlay/recovery_watch_overlay_report.json
```

Overlay 只新增 diagnostics 欄位，不改原始 `current_phase_id`、不覆寫 resolver decision，也不產生 portfolio action。驗收重點包括 GFC / dotcom 是否在 trough 或 recovery initial 附近出現 watch、COVID 是否保留外生衝擊 caveat，以及 euro debt / 2018 是否避免 excessive recovery watch。

`recovery watch` 不等於正式復甦確認，也不是買進訊號。本階段不接 live model，也不構成投資建議。

## Phase 7F3.6 Recovery Watch Integration Guardrails

Phase 7F3.6 建立 recovery watch integration guardrails，明確規定 recovery watch 未來只能先作為 diagnostics / evidence display / research input，不能直接成為正式復甦確認，也不能直接觸發買進或加碼。

```bash
python scripts/show_recovery_watch_integration_guardrails.py
```

Guardrails 要求 live integration 前必須定義 persistence、cooldown、recession context gate、policy / financial support cap、COVID exogenous shock caveat，以及 portfolio backtest。下一步應進 Phase 7G，整合 recession confirmation、boom ending watch 與 recovery watch 三類 transition evidence architecture。

本階段只做設計與驗收 guardrails，不接正式模型、不改 resolver、不進 dashboard，也不構成投資建議。

## Phase 7G Cycle Transition Evidence Architecture

Phase 7G 將 recession confirmation、boom ending watch、recovery watch 三類 experimental evidence 收斂成統一 architecture。

```bash
python scripts/show_cycle_transition_evidence_architecture.py
```

這個 architecture 定義 evidence family、allowed uses、prohibited uses、dashboard diagnostics contract、future transition risk contract 與 future portfolio policy contract。Watch 類訊號不得等同正式 phase confirmation，也不得等同買賣訊號。

下一步可進 Phase 7G1 設計 evidence badge schema；若改走投資策略研究，則必須等 Phase 8 / Phase 9 portfolio backtest。本階段不接 dashboard、不改 resolver、不改正式 scoring，也不構成投資建議。

## Phase 7G1 Transition Evidence Badge Schema

Phase 7G1 設計 future dashboard diagnostics 的 evidence badge schema，統一 recession confirmation、boom ending watch、recovery watch 三類 evidence 的 badge levels、required fields、prohibited fields 與 caveats。

```bash
python scripts/show_transition_evidence_badge_schema.py
```

此 schema 明確限制：badge 不得改變 `current_phase_id` 或 `decision_status`，不得包含買進、賣出、配置或 phase override 欄位。Watch 類訊號不是買賣訊號，且所有 badge 都必須保留 experimental diagnostics 與不構成投資建議 caveat。

Phase 7G1 只做 schema / validator / docs / tests，不接 dashboard renderer、不產生 `public/` output、不改正式模型。

## Phase 7G2 Transition Evidence Badge Fixtures

Phase 7G2 新增 transition evidence badge fixtures 與 batch validator，將合法 badge 與刻意非法 badge 都納入測試。

```bash
python scripts/validate_transition_evidence_badge_fixtures.py
```

合法 fixture 必須是 diagnostics-only、不得影響正式決策、不得產生買賣或 allocation 欄位，且必須包含不構成投資建議 caveat。非法 fixture 必須被拒絕，包含 `buy_signal`、`sell_signal`、`allocation`、`current_phase_override`、`diagnostics_only=false` 或 `formal_decision_impact` 非 `none` 等情況。

本階段只做 static validator / fixtures，不接 dashboard renderer、不產生 `public/` output、不改正式模型。

## Phase 7G3 Transition Evidence Badge Renderer Contract

Phase 7G3 設計 transition evidence badge 的 future renderer contract，定義 renderer 可以接受的 input、可以輸出的 safe display model、level display mapping、required caveats、forbidden fields 與 prohibited text patterns。

```bash
python scripts/show_transition_evidence_badge_renderer_contract.py
```

Renderer contract 明確要求 badge 仍為 diagnostics-only，不得改變 `current_phase_id` 或 `decision_status`，不得包含買賣、配置、target weight 或 phase override 欄位，且顯示文字不得把 watch 說成正式階段確認或投資建議。

Phase 7G3 不改 dashboard templates、不產生 `public/` output、不改正式模型。

## Phase 7G4 Transition Evidence Badge Display Fixtures

Phase 7G4 建立 renderer display model fixtures 與 batch validator，用合法與非法 display model 測試 future renderer contract。

```bash
python scripts/validate_transition_evidence_badge_display_fixtures.py
```

合法 display model 必須保留 global caveats，且仍為 diagnostics-only。非法 display model 必須被拒絕，包含 `buy_signal`、`sell_signal`、`allocation`、`current_phase_override`、`decision_status_override`、`diagnostics_only=false`、`formal_decision_impact` 非 `none` 或 prohibited text pattern。

本階段不改 dashboard templates、不產生 `public/` output、不改正式模型。

## Phase 7G5 Dashboard Evidence Integration Readiness

Phase 7G5 彙整 Phase 7G 到 7G4 的 schema、fixtures、renderer contract、display model fixtures 與 validator，建立 dashboard evidence integration readiness checklist。

```bash
python scripts/show_dashboard_evidence_integration_readiness.py
```

Readiness checklist 結論是：Phase 7G 已完成 dashboard evidence display 的規格與安全驗證，可收斂為 fully specified but not wired。Dashboard wiring 仍被 blocker 擋住，直到 data adapter schema、generated site validation、HTML text-safety tests、accessibility / empty state 與 no formal decision impact tests 完成。

下一步建議轉 Phase 8A：portfolio policy research planning。本階段不接 dashboard、不產生 `public/` output、不改正式模型。

## Phase 8A Portfolio Policy Research Planning

Phase 8A 建立 portfolio policy research planning，將書中景氣循環投資概念轉成 future backtest-only policy templates。

```bash
python scripts/show_portfolio_policy_research_plan.py
```

本階段定義榮景期逐步防守、衰退期防守、復甦再加碼三類研究模板，並要求未來 backtest 納入 max drawdown、turnover、false de-risk cost、false re-risk cost、交易成本與 sensitivity tests。70/50/30 只可作為 backtest-only parameters，不得作為 live allocation 或目前配置建議。

Phase 8A 不產生 allocation、不接 dashboard、不改 resolver、不改正式 scoring，也不構成投資建議。

## Phase 8B Portfolio Policy Template Schema

Phase 8B 新增 portfolio policy template schema、fixtures 與 static validator。

```bash
python scripts/show_portfolio_policy_template_schema.py
python scripts/validate_portfolio_policy_template_fixtures.py
```

此階段將 boom de-risking、recession defense、recovery re-risking 三個研究模板限制為 research-only / backtest-only。Validator 會拒絕 live allocation、trade signal、target weight、current market recommendation 與 prohibited text。70/50/30 只允許作為 backtest-only parameters，不是目前配置建議。本階段不產生 allocation、不接 dashboard、不改正式模型，也不構成投資建議。

## Phase 8C Portfolio Backtest Input Contract

Phase 8C 建立 portfolio backtest input contract 與 scenario mapping。

```bash
python scripts/show_portfolio_backtest_input_contract.py
```

Input contract 定義 future backtest 可接受的 phase / evidence inputs、rebalance assumptions、transaction cost / slippage assumptions、required risk metrics 與 prohibited outputs。Scenario mapping 將 dotcom、GFC、COVID、euro debt slowdown、late-cycle 2018 對應到 policy template research questions。

本階段只定義 backtest input，不跑正式回測、不產生 allocation、不輸出買賣訊號、不產生 `data/backtests` 或 `public/` output，也不構成投資建議。

## Phase 8D Portfolio Backtest Input Fixtures

Phase 8D 新增 portfolio backtest input fixtures 與 batch validator。

```bash
python scripts/validate_portfolio_backtest_input_fixtures.py
```

合法 input fixtures 必須是 research-only / backtest-only，並使用已知 scenario、已知 policy template 與允許的 rebalance settings。非法 fixtures 必須被拒絕，包含 live allocation、target weight、buy/sell signal、public dashboard output、unknown scenario、unknown policy template、缺少核心 metrics、缺少 caveat 或目前建議文字。

本階段仍不跑正式 portfolio backtest、不產生 allocation、不產生 `data/backtests` 或 `public/` output，也不構成投資建議。

## Phase 8E Portfolio Backtest Dry-Run Contract

Phase 8E 定義 portfolio backtest dry-run engine contract。

```bash
python scripts/show_portfolio_backtest_dry_run_contract.py
```

Dry-run 只做 structural validation，不計算 total return、max drawdown、turnover 等績效，也不得輸出 portfolio weights、allocation、target weight、buy/sell signal、`data/backtests` 或 `public/` output。此階段為 Phase 8F dry-run fixtures / output validator 做準備，仍不跑正式回測，也不構成投資建議。

## Phase 8F Portfolio Backtest Dry-Run Fixtures

Phase 8F 新增 dry-run output fixtures 與 validator。

```bash
python scripts/validate_portfolio_backtest_dry_run_fixtures.py
```

合法 dry-run output 只可作 structural validation summary；非法 output 若包含 performance metrics、allocation、target weight、buy/sell signal、public dashboard output、output-written flags、缺少不構成投資建議 caveat 或 prohibited text，必須被拒絕。

本階段仍不跑正式 portfolio backtest、不計算績效、不產生 allocation、不產生 `data/backtests` 或 `public/` output，也不構成投資建議。

## Phase 8G Portfolio Structural Dry-Run Runner

Phase 8G 新增 portfolio structural dry-run runner。

```bash
python scripts/run_portfolio_backtest_structural_dry_run.py
```

Runner 只載入 contract / mapping / valid input fixtures，完成 validation 後產生 in-memory structural dry-run outputs，並將 aggregate summary 印到 stdout。它不得計算績效、不得輸出 allocation 或交易訊號、不得寫入 `data/backtests` 或 `public/` output。

本階段仍不是正式 portfolio backtest，也不構成投資建議。

## Phase 8H Portfolio Research Safety Closure

Phase 8H 新增 `specs/portfolio/portfolio_research_safety_closure.yaml` 與 closure validator。此階段彙整 Phase 8A-8G 的 portfolio research artifacts、validators、fixtures、dry-run contract 與 stdout-only structural runner，確認目前只完成 research-only / structural dry-run-only 安全閉環。

```bash
python scripts/show_portfolio_research_safety_closure.py
```

Closure 明確標記尚未執行正式回測、尚未計算績效、尚未產生 allocation、尚未產生交易訊號，也未寫入 `data/backtests` 或 `public`。真正 backtest 前仍需 real engine contract、result output contract、metric registry、result caveat validator 與 output location policy。

本階段仍不改正式模型、不接 dashboard、不跑回測，也不構成投資建議。

## Phase 8I Real Backtest Prototype Readiness Gate

Phase 8I 新增 `specs/portfolio/real_backtest_prototype_readiness_gate.yaml` 與 readiness gate validator。此階段只定義從 research-only / structural dry-run-only 進入 real backtest prototype 前的前置條件。

```bash
python scripts/show_real_backtest_prototype_readiness_gate.py
```

Gate 明確禁止本階段實作 real backtest engine、計算績效、產生 backtest result、產生 allocation、產生交易訊號、寫入 `data/backtests` 或 `public`。真正 prototype 前必須先定義 engine contract、result output contract、metric formula registry、result safety validator、output location policy 與 result caveat policy。

Recommended next phase 是 9A：real backtest engine contract，但 9A 仍只能做 contract design。

## Phase 9A Real Backtest Engine Contract

Phase 9A 新增 `specs/portfolio/real_backtest_engine_contract.yaml` 與 engine contract validator。此階段只設計 future real backtest engine 的 scope、input contracts、dependency contracts、stage contract 與 safety guards。

```bash
python scripts/show_real_backtest_engine_contract.py
```

Contract 明確禁止本階段實作 engine runtime、執行 backtest、計算績效、產生 result、產生 allocation、產生 trade signal、寫入 `data/backtests` 或 `public`。Compute metrics 必須等 metric formula registry；build result output 必須等 result output contract；write research output 必須等 output location policy。

Recommended next phase 是 9A1：backtest result output contract。

## Phase 9A1 Backtest Result Output Contract

Phase 9A1 新增 `specs/portfolio/backtest_result_output_contract.yaml` 與 result output contract validator。此階段只定義 future backtest result schema 與安全邊界，不產生任何 result。

```bash
python scripts/show_backtest_result_output_contract.py
```

Contract 可列出 future metric fields，例如 total return、annualized return、volatility、max drawdown 與 turnover，但本階段 `metric_values_allowed_now=false`，不得計算績效。Contract 禁止 live allocation、target weight、buy/sell signal、current recommendation、phase override、decision override 與 public dashboard output，並要求 backtest-only、不代表未來績效、不構成投資建議 caveats。

Recommended next phase 是 9A2：backtest metric formula registry。

## Phase 9A2 Backtest Metric Formula Registry

Phase 9A2 新增 `specs/portfolio/backtest_metric_formula_registry.yaml` 與 formula registry validator。此階段只定義 future backtest metric formulas，不計算任何 metric values。

```bash
python scripts/show_backtest_metric_formula_registry.py
```

Registry 定義 total return、annualized return、volatility、max drawdown、turnover、whipsaw、false de-risk cost、false re-risk cost、missed recovery cost、late exit cost 與 late re-entry cost。每個 metric 都必須有 category、formula text、required inputs、output unit、directionality，且 `compute_allowed_now=false`。

本階段仍不執行回測、不產生 result、不產生 allocation、不產生 trade signal、不寫入 `data/backtests` 或 `public`。Recommended next phase 是 9A3：backtest output location policy。

## Phase 9A3 Backtest Output Location Policy

Phase 9A3 新增 `specs/portfolio/backtest_output_location_policy.yaml` 與 output location policy validator。此階段只定義 future result 的 output location policy，不建立 output directory，也不寫 result file。

```bash
python scripts/show_backtest_output_location_policy.py
```

Policy 定義 `data/backtests/research` 只能作為 future controlled research path，且必須等 explicit output writer phase、result safety validator、result caveat policy 與 explicit user command 完成後才可使用。Policy 同時禁止 public、docs、site、dashboard、github_pages、data/backtests、data/raw、specs、src、tests auto-write。

本階段仍不執行 backtest、不計算績效、不產生 result、不產生 allocation、不產生 trade signal、不寫入 `data/backtests` 或 `public`。Recommended next phase 是 9A4：backtest result caveat policy。

## Phase 9A4 Backtest Result Caveat Policy

Phase 9A4 新增 `specs/portfolio/backtest_result_caveat_policy.yaml` 與 caveat policy validator。此階段只定義 future result 必須附帶的 caveats 與禁止語意，不產生任何 result。

```bash
python scripts/show_backtest_result_caveat_policy.py
```

Policy 要求 future result 必須標記 backtest-only、不是目前配置建議、回測結果不代表未來績效、本結果僅供研究與模型驗證、不構成投資建議。Policy 同時要求 revised data、transaction cost、false signal cost、scenario-specific 與 COVID exogenous shock caveats。

本階段仍不執行 backtest、不計算績效、不產生 result、不建立 output directory、不寫入 `data/backtests` 或 `public`。Recommended next phase 是 9A5：backtest result safety validator contract。

## Phase 9A5 Backtest Result Safety Validator Contract

Phase 9A5 新增 `specs/portfolio/backtest_result_safety_validator_contract.yaml` 與 safety validator contract validator。此階段只定義 future validator contract，不實作 runtime，也不驗證真實 result。

```bash
python scripts/show_backtest_result_safety_validator_contract.py
```

Contract 定義 prohibited field checks、prohibited text checks、required caveat checks、caveat visibility checks、output location checks、metadata caveat checks、scenario-specific caveat checks 與 no-live-decision checks。Future validator 必須能阻擋 live allocation、target weight、buy/sell signal、current recommendation、public auto-output 與 caveat 缺失。

本階段仍不執行 backtest、不計算績效、不產生 result、不建立 output directory、不寫入 `data/backtests` 或 `public`。Recommended next phase 是 9A6：backtest result safety validator fixtures。

## Phase 9A6 Backtest Result Safety Validator Fixtures

Phase 9A6 新增 `specs/portfolio/backtest_result_safety_validator_fixtures.yaml` 與 fixture-only validator。此階段只驗證合法與非法 result fixtures，不驗證真實 result，也不實作 runtime validator。

```bash
python scripts/validate_backtest_result_safety_validator_fixtures.py
```

Valid fixtures 是 schema/safety samples，必須標記 sample-only、fixture-only、不是真實績效，且包含 required caveats 與 output flags false。Invalid fixtures 故意覆蓋 live allocation、target weight、buy/sell signal、current recommendation、public dashboard output、phase override、prohibited text、caveat 缺失、caveat visibility 與 output location violation。

本階段仍不執行 backtest、不計算績效、不產生 result、不建立 output directory、不寫入 `data/backtests` 或 `public`。

## Phase 9A7 Backtest Result Writer Contract

Phase 9A7 新增 `specs/portfolio/backtest_result_writer_contract.yaml` 與 writer contract validator。此階段只定義 future writer contract，不實作 writer runtime，也不寫任何 result file。

```bash
python scripts/show_backtest_result_writer_contract.py
```

Contract 要求 future writer 必須由 explicit user command 觸發，且寫入前必須通過 result output contract、metric registry、output location policy、result caveat policy、safety validator runtime 與 result safety validation。Future controlled research path `data/backtests/research` 只作為 contract definition，本階段不得建立或寫入。

本階段仍不執行 backtest、不計算績效、不產生 result、不建立 output directory、不寫入 `data/backtests` 或 `public`。Recommended next phase 是 9A8：real backtest execution readiness closure。

## Phase 9A8 Real Backtest Execution Readiness Closure

Phase 9A8 新增 `specs/portfolio/real_backtest_execution_readiness_closure.yaml` 與 readiness closure validator。此階段只檢查 9A–9A7 contract stack 是否具備進入 controlled 9B prototype 的前置條件。

```bash
python scripts/show_real_backtest_execution_readiness_closure.py
```

Closure 要求 source artifact count 為 10、contract stack complete，並明確保留 no execution、no runtime implementation、no metric computation、no result generation、no output directory、no `data/backtests` / public write、no allocation、no trade signal。9B 可開始 controlled in-memory prototype，但預設不得寫 output、不接 dashboard、不產生 live allocation 或 trade signal。

## Phase 9B Controlled Synthetic In-Memory Harness

Phase 9B 新增 `specs/portfolio/controlled_real_backtest_prototype_fixtures.yaml` 與 controlled synthetic in-memory runner。此階段只使用 deterministic fixtures，不讀外部 market data、不呼叫 FRED、不寫任何 result file。

```bash
python scripts/run_controlled_real_backtest_prototype.py
```

Prototype 可在 memory 中計算 controlled fixture arithmetic metrics，包含 total return、annualized return、volatility、max drawdown 與 turnover。CLI 只輸出 counts 與 safety flags，且必須維持 no result file、no output directory、no `data/backtests` / public write、no dashboard integration、no allocation、no trade signal。QA0 完成前暫停 9B1；9B 不得宣稱書籍策略、歷史績效、景氣模型或 point-in-time 可交易性已完成驗證。

## 驗收方式

後續實作不得只看單一 scenario。至少要用既有 backtest / calibration review 檢查：

- COVID 2019 early false recession 應降低，或至少降為 transition_watch。
- dotcom 與 GFC 仍需在合理 recession window 內偵測。
- euro debt slowdown 與 late cycle 2018 不應新增 confirmed recession。
- 新指標必須保留中文 reason、資料 freshness、confidence 與 phase impact。

本計畫使用 revised data 作為第一版診斷基礎，不等同當時投資人可見資料。所有內容僅供模型校準與總經研究，不構成投資建議。

## QA4 Scope Update

QA4 turns the book-aligned implementation plan into an explicit scope contract.
The future book-faithful candidate model must preserve independent roles for
recovery, growth, boom, recession confirmation, trough, regime, and portfolio
rules. Candidate specs and experimental diagnostics do not count as formal
completion.

Missing book-core roles remain blockers. Modern extensions such as yield curve,
credit spread, financial conditions, policy rate, mortgage-rate pressure, and
oil pressure remain separate support evidence and cannot replace book-core
requirements.

QA4 does not tune parameters or activate the proposed v2 model. QA5 must handle
book-core data contracts and shadow formal implementation before any candidate
model version can be frozen.

## QA5 Data Contract Update

QA5 converts the book-core indicator roles into explicit data contracts. Every
canonical indicator role has one contract row, including roles that are still
blocked by source identity, access, transformation, or missing implementation.
Blocked roles remain visible and are not replaced by modern extensions.

The QA5 shadow evidence model is feature-gated and non-production. It provides
role evidence and phase evidence profiles for structural diagnostics only. It
does not activate proposed v2, does not define weights or thresholds, and does
not register a candidate holdout.

The next step is QA6: pre-register aggregation rules for the shadow evidence
model and validate the structural candidate model before any decision-active
model freeze.

## QA6 Aggregation Update

QA6 adds typed evidence routing and major-group aggregation invariants for the
shadow evidence model. Book-core groups remain explicit: modern supporting
evidence cannot satisfy missing core groups, boom-ending risk does not count as
boom presence, and watch evidence does not become confirmation evidence.

No weights or thresholds are introduced. The output is structural eligibility
only, with candidate selection disabled. QA7 will handle threshold
pre-registration and candidate-selection freeze.

## QA7 Evidence Rule Update

QA7 adds evidence-rule provenance and candidate-selection preregistration for
the shadow model. It does not promote indicators, change production defaults,
or define production thresholds.

The book-core roles remain explicit. Raw transforms do not become supportive or
contradictory evidence until a future phase implements allowed evaluators. The
2019 250000 claims value is contextual only, the three-month moving average is
a smoothing rule, and qualitative default-rate jump language remains unresolved.

Synthetic candidate fixtures validate no-weight selection mechanics and
ambiguity preservation. Real-data candidate selection remains disabled and
emits no candidate phase. QA8 will implement book-explicit evaluators and
prospective shadow diagnostics.

## QA8 Evaluator Update

QA8 implements the first operationally complete book-explicit shadow evaluator:
the calendar-time three-month initial-claims moving-average noise filter. The
implementation is frequency-aware and uses calendar windows rather than a fixed
row count.

The evaluator does not promote a production indicator, does not define weights,
does not add production thresholds, and does not confirm a phase. Claims
reversal, durable-orders improvement, and claims-new-low continuation remain
blocked where lookback, persistence, turning-point, or reference-window
semantics are incomplete.

The forward-only prospective shadow protocol is registered but not started and
is separate from holdout governance. Production v1 remains unchanged.

## QA9 Registry Update

QA9 adds the append-only prospective shadow registry and forward-only gate for
future observation provenance. It does not add new evidence thresholds, does
not make the smoothing evaluator directional, and does not enable candidate
selection.

The registry is armed but not started. No real prospective record is written,
real result inspection remains zero, and holdout remains unregistered. Any
future model or rule version change requires successor lineage rather than
backfilling old periods.

QA10 will continue with unresolved book-rule operationalization and candidate
capability expansion while production v1 remains isolated.

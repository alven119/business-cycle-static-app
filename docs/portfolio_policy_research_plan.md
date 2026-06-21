# Portfolio Policy Research Plan

## 背景

Phase 7F 建立 recession confirmation、boom ending watch、recovery watch 三類 transition evidence。Phase 7G 將 evidence display 規格收斂為 fully specified but not wired。Phase 8A 開始 portfolio policy research planning，但仍只做研究規格，不產生 allocation、不接 dashboard、不構成投資建議。

## 為什麼 Phase 8 先做 Research Planning

Portfolio policy 牽涉績效、風險、交易成本、錯誤訊號成本與使用者解讀風險。直接實作配置輸出會跳過必要驗證。Phase 8A 先定義 policy taxonomy、future backtest parameters、風險邊界與 acceptance gates。

## 與 Phase 7F / 7G Transition Evidence 的關係

Phase 7F / 7G 的 evidence 可作為 future research input，但不能直接觸發交易。Boom ending watch 不是衰退確認，recovery watch 不是正式復甦確認，所有 watch 都必須先經 persistence、cooldown、phase confirmation 與 backtest。

## 榮景期逐步防守研究模板

此模板研究在 boom phase 與 late-cycle evidence 出現時，是否逐步降低股票曝險。70/50/30 只作為 future backtest-only parameter，用來比較不同防守程度，不是目前配置建議。

## 衰退期防守研究模板

此模板研究 recession phase / recession confirmation evidence 是否可用於維持防守或降低風險曝險。Recession confirmation evidence 不得單獨產生交易訊號。

## 復甦再加碼研究模板

此模板研究 recovery watch、recession context、labor reversal、real activity confirmation、credit / financial easing 與 phase confidence 是否可作為衰退後再提高風險曝險的條件。Recovery watch 不得直接視為買進或加碼訊號。

## 為什麼 70/50/30 只能是 Backtest-Only Parameters

70/50/30 是書中景氣循環投資概念的研究參數。未完成 historical backtest、transaction cost、turnover、false signal cost 與 sensitivity tests 前，不能把任何比例當成 current market allocation。

## Evidence Watch 為什麼不能直接變成交易訊號

Watch evidence 可能太早、太晚、太密集或受外生衝擊影響。若不經 backtest 與 cooldown / persistence，直接交易會放大 whipsaw 與 false signal cost。

## 必要回測維度

Backtest 至少要涵蓋 dotcom、GFC、COVID、euro debt slowdown、late-cycle 2018，並做 persistence、cooldown、confidence threshold、evidence density、transaction cost、monthly / quarterly rebalance sensitivity。

## 必要風險指標

至少要計算 total return、max drawdown、volatility、turnover、whipsaw count、false de-risk cost、false re-risk cost、missed recovery cost、late exit cost、late reentry cost。

## False Signal Cost

False de-risk cost 衡量過早防守造成的機會成本。False re-risk cost 衡量過早加風險造成的 downside。兩者都必須明確定義，否則 policy backtest 不完整。

## Transaction Cost

任何 policy backtest 都必須加入交易成本假設，並比較 monthly vs quarterly rebalance 對 turnover 和績效的影響。

## Data Limitations

研究必須標記 revised data bias、vintage data unavailable initially、publication lag、signal revision risk。修訂後資料不等於當時投資人可見資料。

## Required Acceptance Before Policy Backtest

進入 policy backtest 前必須定義 policy template schema、backtest metric schema、transaction cost policy、false signal cost policy，並確認不產生 live allocation、不使用目前建議語言、不構成投資建議。

## Recommended Next Phase

下一步是 Phase 8B：portfolio policy template schema and static validator。8B 仍應是 static validation 層，確保權重只作 backtest-only parameters，禁止 live allocation 與交易建議文字。

## Phase 8B Portfolio Policy Template Schema

Phase 8B 新增 `specs/portfolio/portfolio_policy_template_schema.yaml` 與 `specs/portfolio/portfolio_policy_template_fixtures.yaml`。Schema 定義 research-only / backtest-only policy template 的 required fields、allowed template IDs、prohibited fields、prohibited text patterns 與 template-specific rules。

Validator 會接受合法的 boom / recession / recovery 三個研究模板，並拒絕 live allocation、trade signal、target weight、current recommendation、phase override 與禁止文字。70/50/30 只能出現在 `stock_weight_levels_for_backtest_only`，且必須搭配 backtest-only caveat。

```bash
python scripts/show_portfolio_policy_template_schema.py
python scripts/validate_portfolio_policy_template_fixtures.py
```

本階段仍不產生 allocation、不接 dashboard、不改 resolver、不改正式 scoring，也不構成投資建議。

## Phase 8C Portfolio Backtest Input Contract

Phase 8C 新增 `specs/portfolio/portfolio_backtest_input_contract.yaml` 與 `specs/portfolio/portfolio_backtest_scenario_mapping.yaml`。這兩個 spec 只定義 future portfolio backtest 的輸入契約與 scenario mapping，不跑正式回測、不產生 allocation。

Input contract 定義可用 policy templates、scenario ids、monthly as-of 對齊、phase / evidence inputs、rebalance assumptions、transaction cost / slippage sensitivity、risk metrics 與 output safety boundaries。Scenario mapping 將 dotcom、GFC、COVID、euro debt slowdown、late-cycle 2018 對應到 boom de-risking、recession defense、recovery re-risking 的研究問題。

```bash
python scripts/show_portfolio_backtest_input_contract.py
```

Validator 會確認所有 allowed scenarios 都已 mapping、policy templates 與 evidence families 都是已知 id，並阻擋 live allocation、target weight、buy/sell signal、current recommendation 與 public dashboard output。所有權重仍只能是 backtest-only parameters，不構成投資建議。

## Phase 8D Portfolio Backtest Input Fixtures

Phase 8D 新增 `specs/portfolio/portfolio_backtest_input_fixtures.yaml` 與 batch validator。Fixtures 提供 future portfolio backtest input 的合法與非法樣本，但仍不跑正式 backtest、不產生回測結果、不輸出 allocation。

合法 fixtures 必須是 research-only / backtest-only，使用已知 scenario、已知 policy template、允許的 rebalance frequency，並包含必要 metrics、必要 period inputs 與不構成投資建議 caveat。非法 fixtures 則刻意包含 live allocation、target weight、buy/sell signal、public output、unknown scenario、unknown policy template、缺少核心 metrics、缺少 caveat 或目前建議文字，用來確保 validator 能阻擋 unsafe input。

```bash
python scripts/validate_portfolio_backtest_input_fixtures.py
```

本階段仍不產生 `data/backtests`、不接 dashboard、不改 resolver、不改正式 scoring，也不構成投資建議。

## Phase 8E Portfolio Backtest Dry-Run Contract

Phase 8E 新增 `specs/portfolio/portfolio_backtest_dry_run_contract.yaml`。Dry-run engine contract 只定義 future dry-run engine 的輸入、輸出、stdout 與安全邊界，用來確認 input contract 和 fixtures 是否足以支援後續 structural dry-run。

Dry-run 只做 structural validation，不計算 `total_return`、`max_drawdown`、`turnover` 等績效，不產生 portfolio weights、不產生 allocation、不產生 buy/sell signal，也不寫入 `data/backtests` 或 `public`。

```bash
python scripts/show_portfolio_backtest_dry_run_contract.py
```

本階段為 Phase 8F dry-run fixtures / output validator 做準備，仍不跑正式 backtest、不產生回測結果，也不構成投資建議。

## Phase 8F Portfolio Backtest Dry-Run Fixtures

Phase 8F 新增 `specs/portfolio/portfolio_backtest_dry_run_fixtures.yaml` 與 dry-run output validator。Fixtures 提供合法 structural summary 與非法 output 範例，用來驗證 future dry-run engine 的 output safety。

合法 dry-run output 只包含 dry-run id、backtest input id、scenario id、policy template id、validation status、structural summary、required metric/input count、caveats 與 next required phase。非法 fixtures 會被拒絕，包含 `total_return`、`max_drawdown`、`allocation`、`target_weight`、`buy_signal`、`public_dashboard_output`、`output_written=true`、`data_backtests_output_written=true`、缺少不構成投資建議 caveat 或買進訊號文字。

```bash
python scripts/validate_portfolio_backtest_dry_run_fixtures.py
```

本階段仍不跑正式 backtest、不計算績效、不產生 allocation、不寫入 `data/backtests` 或 `public`，也不構成投資建議。

## Phase 8G Portfolio Structural Dry-Run Runner

Phase 8G 新增 stdout-only structural dry-run runner。Runner 會載入 dry-run contract、backtest input contract、scenario mapping 與 backtest input fixtures，只處理 valid input fixtures，先通過 validator，再產生 in-memory structural dry-run outputs。

```bash
python scripts/run_portfolio_backtest_structural_dry_run.py
```

Runner 只回報 aggregate structural summary，例如 dry-run 數量、scenario/template 數量與安全 flags。它不計算 total return、max drawdown、turnover 等績效，不產生 portfolio weights、不產生 allocation、不輸出 trade signal，也不寫入 `data/backtests` 或 `public`。Runner output 不是 backtest result，不構成投資建議。

## Caveats

- 此為 research-only planning，不是正式投資策略。
- 所有權重都是 future backtest-only parameters，不是 live allocation。
- Watch evidence 不是買賣訊號。
- 不構成投資建議。

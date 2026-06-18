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

Phase 7F3：衰退落底與復甦反轉指標

- 初領失業救濟金高峰反轉。
- 短期失業人數高峰反轉。
- 消費與耐久財落底。
- 訂單落底。
- 寬鬆政策已到位。
- 信用壓力緩和。

## 驗收方式

後續實作不得只看單一 scenario。至少要用既有 backtest / calibration review 檢查：

- COVID 2019 early false recession 應降低，或至少降為 transition_watch。
- dotcom 與 GFC 仍需在合理 recession window 內偵測。
- euro debt slowdown 與 late cycle 2018 不應新增 confirmed recession。
- 新指標必須保留中文 reason、資料 freshness、confidence 與 phase impact。

本計畫使用 revised data 作為第一版診斷基礎，不等同當時投資人可見資料。所有內容僅供模型校準與總經研究，不構成投資建議。

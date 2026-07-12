# Phase 133：歷史政策時間軸與固定權重敏感度

Phase 133 完成 Phase 129–133 路線的最後一段：把 Phase 131 的歷史事件、Phase 125 的 strict
PIT evidence 與 cash-flow-aware 結果、以及 Phase 128 的書籍配置規則接到私人 NAS 的配置研究
與歷史重播頁。

## 歷史註解邊界

- 五個情境共有 156 個月度節點。
- NBER peak/trough chronology 只作事後研究註解，不得進入 current runtime、evaluator 或 rule tuning。
- Peak 後至 trough 的 28 個月標為衰退，可回放書籍 `recession_stock_weight_100`。
- NBER expansion 不能辨識書籍的復甦、成長、榮景，因此不推測 phase age 或政策權重。
- 網路泡沫、GFC、歐債三情境維持 explicit PIT blocker；COVID 與 2018–2019 可執行 strict 研究。

## 固定權重研究

頁面比較既有 Phase 125 的 12 組預註冊結果：股票 100／70／50／30 搭配現金，以及股票
70／50 搭配長債代理。顯示年化 TWR、XIRR、最大回撤、回撤恢復月數、turnover、交易成本、
錯失復甦與錯誤去風險機會成本。

結果依固定參數順序呈現，不排序、不挑選歷史最佳權重，也不產生目前配置或交易指令。
NASDAQ-100 與 DGS10 duration model 的替代風險維持可見。

## 測試策略

沿用 `tests/test_research_dashboard_bundle.py` 與 `tests/test_product_capability_progress.py`，沒有新增
test file。新增一個整合測試，並擴充既有 Phase 125 surface test；直接驗證 156 月註解、12 組
結果、metric provenance、no-result-tuning、no-best-selection 與兩個 NAS 頁面文字。

## 後續邊界

工程產品面完成不等於模型已完成前瞻驗證。F2 維持 96%，prospective registry 仍為 0 筆，
並依 Phase 127 calendar gate 等待第一個合法 as-of 與至少 12 個完整月份。

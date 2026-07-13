# Phase 138：NY Fed SCE 指標探索、發布日曆與事故下鑽

Phase 138 把 Phase 137 已匯入 PostgreSQL 的 11 條 NY Fed Survey of Consumer
Expectations 官方直接元件接到私人 NAS 產品面。這是 source-reliability 路線的產品化延伸，
不改寫 Phase 136 的 consumer-confidence equivalence 結論。

## 指標探索器

`/indicators` 新增獨立的「NY Fed 家庭預期旁證」區塊。每個元件都有：

- 繁體中文名稱與技術 series ID；
- 最新 revised 觀察值、單位、新鮮度與來源 lineage；
- 數值較高／較低在家庭就業、所得支出、信用或財務預期上的意涵；
- YTD、過去一年與過去五年互動圖，沿用日期／數值游標與手機觸控；
- `official_modern_supporting_context`、`revised_supporting_only` 與不可取代書籍 exact evidence 的明確標籤。

元件維持官方直接值，不建立任意 composite、weight、threshold 或信心分數。它們不能單獨
形成 phase evidence、transition watch、transition confirmation 或配置動作。書中 exact role
仍是 Conference Board Consumer Confidence Index，未取得授權時維持 access blocked。

## 官方發布日曆與事故中心

runtime release diagnostics 在原有 13 個 book-core family 外增加一個 supporting family：
NY Fed SCE。Phase 138 登錄官方日曆已公布的 2026-07-07 與 2026-08-07 11:00 ET 事件，
並保留日期可能變更的 caveat。原 Phase 114 的 13-family／28-series closure 不被改寫。

來源失敗仍只建立一個 `NYFED_SCE_CONTEXT` 父 workbook incident。事故卡片可下鑽查看
11 個受影響元件、概念群組、受影響 role／transition lane 與 operator 下一步，不會產生
11 筆重複事故，也不會把 unavailable 當 neutral。

## 為什麼配置研究不自動決定比例

頁面目前有六類有效限制：

1. 景氣階段切換必須由受治理 preview／confirmation／receipt 完成。
2. 書中 70／50／30 是固定研究模板，不含個人現金流、期限與風險承受度適配。
3. 五個歷史情境中只有兩個具完整 strict PIT inputs。
4. NASDAQ-100 與 DGS10 duration model 仍是市場研究代理，不是正式書籍 total-return benchmark。
5. 前瞻驗證尚未累積完成，歷史敏感度不能證明未來績效。
6. 系統刻意不持有券商權限，也不自動下單。

系統仍會顯示 declared phase 對應的書籍研究位置、固定模板與歷史取捨；「不決定比例」指的是
不替使用者自動挑選個人化比例，不是沒有配置研究內容。

## Strict PIT 重新核對

更新 revised 來源架構與 SCE 歷史資料後，strict PIT 結論仍是 2／5：COVID 與
2018–2019 可完整研究；網路泡沫、GFC 與歐債情境仍有當時可得官方 vintage 缺口。
原因是 revised history 只描述後來整理過的歷史值，不能證明某個歷史 as-of 當時已經可見。
NY Fed workbook 自 2013 年起提供 revised 月資料，但沒有各歷史 as-of 的 vintage
availability interval，因此不能用它解除早期 strict blocker。

這不影響 revised diagnostics、指標學習或 current source monitoring；缺漏月份在 strict replay
必須繼續 abstain，不能以 revised fallback 假裝完整。

## 測試與交付

Phase 138 沿用 `tests/test_postgres_macro_warehouse_contract.py`、
`tests/test_product_capability_progress.py` 與 `tests/test_ci_workflows.py`，沒有新增 test file。
full closure 以 Phase 138 取代 Phase 137，Phase 137 留在 nightly lineage；因此 default test
selection 與 full closure 數量不增加。

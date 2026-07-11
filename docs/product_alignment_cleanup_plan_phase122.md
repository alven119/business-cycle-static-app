# Phase 122：統一資料正確性與台美科技製造循環

Phase 122 沿用最少 Phase 路線，把資料正確性與使用者要求的台美科技製造研究頁合併完成，沒有新增獨立景氣分類器或任意分數。

## 官方資料接線

- `DGORDER`：美國耐久財製造業新訂單，既有 PostgreSQL revised history。
- `A34SNO`：美國電腦及電子產品製造業新訂單，Census M3／FRED。
- `A34HNO`：美國其他電子元件製造業新訂單，Census M3／FRED。
- `TW_MOEA_ICT_EXPORT_ORDERS`：經濟部資訊與通信產品外銷訂單官方 CSV。
- `TW_MOEA_ELECTRONICS_EXPORT_ORDERS`：經濟部電子產品外銷訂單官方 CSV。

新增四條序列都透過既有 PostgreSQL `series_registry`、`source_artifact` 與 `observation_revised` 儲存；raw artifact 只留在 NAS named volume。匯入可重跑、逐序列保留結果，測試不連網。

## 判讀與資料風險

五條序列的主要圖表都使用 causal 年增率，YTD／1Y／5Y 圖仍保留原始名目百萬美元與來源 artifact lineage。

- A34SNO 範圍廣於半導體。
- A34HNO 的「其他電子元件製造業」不等於半導體訂單；Census 2010 年後分類揭露方式有變。
- 台灣外銷訂單是廠商接單，不是出口實績或台灣境內生產。
- 所有序列均為名目金額；年增率會受價格、匯率、基期與修訂影響。
- 台灣資料只作供應鏈 supporting context，不替代美國 book-core role。

## 產品邊界

科技製造頁不輸出 candidate/current phase，不以單月年增確認轉折，不改 production v1、portfolio policy 或 prospective registry。首頁仍以 declared boom 與合法下一階段 recession 為核心，Phase 123 才把既有 book-aligned evidence evaluators 接到 live ordered-cycle lanes。

## 測試治理

本 Phase 不新增測試檔，擴充既有 PostgreSQL、Dashboard、runtime、CI 與能力進度測試。Full closure 以 Phase 122 取代 Phase 121，Phase 121 保留在 nightly，維持 full tier 最多 12 支 closure scripts 與 default product-core 最多 30 個檔案。

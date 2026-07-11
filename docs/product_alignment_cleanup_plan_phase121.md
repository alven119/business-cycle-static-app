# Phase 121：指標判讀轉換與學習語意

Phase 121 修正私人 NAS 儀表板把官方原始 observation 直接當成主要判讀圖的系統性錯位。
PostgreSQL 仍保存官方原始值；Dashboard 另外產生受治理、可追溯的判讀值。

## 盤點結果

- canonical economic roles：39
- 年增率主圖：23
- causal 移動平均主圖：8
- 保留水準值：6
- 明確 blocked：2
- 修正前以原始水準代替主要判讀值：31
- 修正後未處理錯位：0

年增率適用於耐久財新訂單、實質消費、投資、進出口、核心價格指數、庫存水準與工業生產等水準序列。
初領／續領失業救濟使用 4 期移動平均，短期失業人數使用 3 期移動平均。
儲蓄率、逾期率、信用利差、聯邦基金利率及庫存變動流量保留水準值，避免把率、差或流量誤套一般年增率。

## 顯示與教學契約

每個角色固定顯示：

- 官方原始值與官方原始單位
- 主要判讀方式、公式與判讀單位
- 數值升高／走強通常代表的意義
- 數值降低／走弱通常代表的意義
- declared boom 到 legal-next recession 的當下脈絡
- nominal／real、頻率、涵蓋範圍或 qualitative-rule 限制

顯示轉換只改善可讀性，不會自動產生 watch、confirmation、candidate phase 或 current phase。
核心 CPI／PCE 年增率只代表 component context，不會被自動解讀為「可持續通膨」。

## 時間與資料完整性

5 年 YoY 圖需要 6 年原始 lookback。前年同期缺失、基期為零、移動平均觀察不足或頻率跨度異常時必須 abstain，不填零、不退回原始水準冒充判讀值。

## 後續規劃原則

Phase 122 前重新以最少 Phase 規劃，但資料完整性、書籍語意與正式 production gate 優先於 Phase 數量。台美科技製造循環頁必須先確認官方 series identity、定義連續性、單位與修訂政策；不連續或只能 supporting 的序列會顯示風險，不會靜默補成 book-core。

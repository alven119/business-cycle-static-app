# Phase 130：四階段 revised/current 資料倉儲完成

Phase 130 將 recovery、growth、boom、recession／trough 的 40 個 canonical requirements
整理成單一 `role → phase lane → transformation → raw series → PostgreSQL storage` 矩陣。
其中 39 個是經濟角色，`recovery_publication_lag_awareness` 是 F1 時間完整性要求，
不列入指標分母，也不製造假數值。

## 完成結果

- 37 個經濟角色的 revised raw inputs 可由 26 個 canonical official series 重建。
- direct raw series 存入 PostgreSQL；7 個 derived／composite roles 保留 component lineage，於 read path 重建。
- 新增 `UMCSENT` 自動 revised supporting context，固定排程補抓。
- `UMCSENT` 明示 FRED 依來源要求延遲一個月，只能旁證 Conference Board confidence。
- `PAYEMS` 已在 warehouse，但只能旁證 ADP employment，不能替代 ADP。
- `/source-operations` 顯示四階段 readiness、缺值、授權 blocker、旁證與使用者影響。

## 安全邊界

資料入庫只代表 revised/current input ready，不代表 phase evidence、transition confirmation、
point-in-time 完整、candidate phase 或 current phase。Phase 130 不新增 threshold、weight、
role-count voting、配置指令或 production v1 behavior。

## 下一步

Phase 131 依既定路線處理五個歷史情境的 strict PIT 缺口與 governed transition event
registry；無官方早期 vintage 時必須保留 abstain，不得用 revised history 冒充 PIT。

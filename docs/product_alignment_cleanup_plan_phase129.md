# Phase 129：受治理景氣階段轉換、Receipt 與 Correction

Phase 129 沿用 Phase 113 的私人 NAS cycle-state volume、authenticated route、
preview hash、atomic write 與 rollback 基礎，擴充為完整 ordered-cycle transition core。

## 使用者流程

1. 先確認目前 declared phase 的精確起始日或合理日期區間。
2. 檢閱 continuation、watch、confirmation 的支持、反對、mixed 與 abstention。
3. 系統只提供唯一合法下一階段，不允許同階段或跨階段跳轉。
4. 輸入下一階段生效日或日期區間，查看 before/after preview。
5. 明確確認後，active registry 與新階段起始資訊以同一次 atomic write 更新。
6. 產生 hash-chained append-only event 與 immutable receipt。
7. Rollback 不刪除原事件，而是新增 correction receipt 並恢復前一 registry。

Evidence 只供檢閱，不會自動推論或套用 declared phase。確認理由只保存 hash，避免
私人文字進入 receipt artifact。

## Phase 132 安全依賴

Phase 123 live evaluator、Phase 124 portfolio context 與目前主要 Dashboard 內容仍以 boom
為 runtime contract。為避免 active registry 已切成 recession、其他頁面仍顯示 boom lanes，
NAS live transition activation 在 Phase 129 預設關閉。Preview、核心 apply、receipt、hash chain
與 correction 已在隔離 registry 完整驗證；Phase 132 完成全頁原子 phase routing 後才能打開
activation environment gate。

目前 boom 起始日／區間確認不受此 gate 影響，仍可在 `/cycle-state` 使用。

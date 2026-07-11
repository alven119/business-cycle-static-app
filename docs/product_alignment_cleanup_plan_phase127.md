# Phase 127：前瞻驗證日曆門檻與等待狀態

Phase 127 將 QA12 已凍結的第一期前瞻監控契約接入私人 NAS。頁面只顯示日曆、資料完整度、append-only registry metadata 與下一步，不讀取前瞻結果，也不啟動 candidate phase。

## 當前狀態

- observation period：`2026-07`
- canonical as-of：`2026-08-31`
- earliest possible manual append：`2026-10-31`
- protocol：registered / armed / not started
- real registry records / write attempts：`0 / 0`
- minimum evaluation：12 個完整月份與 12 個 complete strict dates
- recommended next action：`WAIT_FOR_FIRST_ELIGIBLE_AS_OF`

## 不可繞過的邊界

- 不自動啟動、不回填、不寫 registry。
- 不偷看前瞻結果，不依結果調整 rule、threshold 或 weight。
- 模型變更會重置未來評估窗；既有 append-only records 保留。
- calendar wait surface 完成不等於 economic validation 或正式 production seal。

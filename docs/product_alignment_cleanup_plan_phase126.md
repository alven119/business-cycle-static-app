---
phase_id: 126
phase_label: private_nas_v1_operational_acceptance
---

# Phase 126：私人 NAS v1.0 操作驗收

Phase 126 將已存在的 refresh、PIT、strict replay、research backtest、備份還原、
Tailscale 與 dashboard 路徑收斂成一個可驗證的私人 NAS v1.0 research service。

## 驗收內容

- strict replay/backtest 連續重跑，輸入相同時 `artifact_hash` 必須一致；
- 每次 Phase 125 live run 留下 immutable JSON 與 SHA-256 sidecar；
- PostgreSQL custom dump 在隔離 staging database 還原並比對五個資料表；
- source artifacts 在暫存目錄還原並逐檔驗證 checksum；
- 實際切回 Phase 124 image，通過 health 後 forward 回 Phase 126；
- rollback 前後 Postgres row count 與 Phase 125 artifact hash 不變；
- 延用已接受的 Tailscale private HTTPS/mobile gate，再驗證目前 login、首頁、
  繁體中文導覽與 mobile viewport；
- 提供繁體中文 operator runbook 與 operations/readyz 狀態。

## 邊界

此處的 v1.0 只表示私人 NAS research service 通過工程與維運驗收。Dotcom、GFC、
歐債早期 PIT、正式 broad-market／long-Treasury benchmark、dynamic policy timeline 與
至少 12 個月 prospective validation 仍未完成，因此不宣稱 economic validation、
book alignment production seal 或投資建議能力。

## 下一階段

Phase 127 只能依 calendar gate 累積 prospective observations；不得以工程 Phase 跳過
12 個完整月份與獨立驗證要求。

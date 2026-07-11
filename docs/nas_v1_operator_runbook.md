# 私人 NAS v1.0 操作手冊

本手冊適用於 DS925+ 上的 `business-cycle-research` 私人研究服務。所有配置、
回測與景氣內容均為 research-only，不是個人化投資建議；NAS 維運驗收也不代表
模型已完成經濟或前瞻驗證。

## daily_health_check

每日先檢查 Container Manager 三個容器為 healthy，再查看 `/healthz`、`/readyz`
與「官方資料維運」頁。`readyz` 必須顯示 live Postgres、refresh、strict replay 與
NAS v1 acceptance 狀態；失敗時不要以舊資料冒充最新資料。

## source_refresh

正常來源更新由 worker 依台北時間 03:30 與受驗證的官方發布日曆執行。FRED key
只存在 NAS `.env`。失敗來源先使用 source-operations retry preview，再由 worker
端明確確認；不得從瀏覽器執行資料庫命令。

## strict_replay_rerun

Phase 125 重跑必須使用 worker 內的
`python -m business_cycle.validation.nas_strict_replay_backtest --execute-live`。
每次執行都保存 immutable snapshot；相同輸入的 `artifact_hash` 必須相同。早期 PIT
缺口仍應 abstain，不得回退 revised。

## artifact_retention

Phase 125 snapshots 位於 private volume 的 `phase125/runs`。保留預覽以最近七份成功、
三份失敗為操作基準，未知格式全部保留。v1.0 不自動刪除；任何清除都需另行確認並
先完成 backup。

## backup_restore

使用既有 Phase 115 worker command 建立 PostgreSQL custom dump 與 source-artifact
snapshot。還原只能在隔離 staging database 與暫存目錄驗證，資料列與 checksum 一致後
刪除 staging database；不得覆寫 live database。

## rollback

rollback 前先確認 Phase 124 image、`compose.phase124-before125.yaml`、目前 compose 與
Postgres/source-artifact volumes 都存在。短暫切回前一 image，通過 health/ready 後立即
forward 回 Phase 126；前後資料列與 artifact 必須保持一致。rollback 不回復資料 volume。

## tailscale_mobile

外出使用手機時只走 Tailscale Serve private HTTPS。Funnel 必須關閉，路由器不得開 public
port-forward。驗收 `/login`、首頁、配置研究、歷史重播與官方資料維運頁，並確認繁體中文
導覽、viewport 與 Secure/HttpOnly/SameSite cookie。

## incident_response

服務異常時依序保存 Container Manager logs、檢查 `/readyz`、refresh status、最近 immutable
artifact 與 backup status。先停止有寫入能力的 worker，再判斷 app rollback；不要刪 volume、
不要重設資料庫、不要把 secret 貼入 issue 或 commit。

## known_limits

目前 Dotcom、GFC、歐債三個情境缺完整官方早期 PIT；NASDAQ-100 是科技偏重替代，DGS10
長債採 duration proxy，不能宣稱書籍正式 benchmark。前瞻驗證仍需至少 12 個完整月份，
NAS v1.0 acceptance 不會解除這些 blocker。

# Phase 125：Strict PIT Replay 與 Cash-Flow-Aware Research Backtest

Phase 125 將 Phase 119 的真實 PIT timeline、Phase 123 evidence evaluator、Phase 124
互動頁與 Phase 78 cash-flow methodology 串成第一條受治理的歷史執行路徑。

## Strict evidence replay

- 2018–2019 與 COVID 的 48 個月份具有 26/26 direct PIT inputs，可執行五個
  transition-critical roles 與四條 lanes。
- Dotcom、GFC、歐債共 108 個月份因官方早期 PIT 不完整而 abstain。
- 不讀 historical labels、不回退 revised、不輸出 historical current phase。

## Portfolio research execution

- 股票使用 FRED `NASDAQXNDX` 總報酬指數，能涵蓋 1999 後情境，但偏重科技，
  只能作 supporting substitute。
- 現金使用 FRED `DFF` 月均利率 proxy。
- 長債使用 FRED `DGS10` 與明示 8 年 duration model；不是官方 total-return index，
  風險標記為 high，不能宣稱書籍 benchmark。
- 僅執行八組固定參數 sensitivity；recession／recovery 動態 policy 因沒有受治理
  historical state timeline 而保持 blocked。
- Annual contribution、10 bps cost、unitized NAV、TWR、XIRR、drawdown、turnover
  均保留完整 lineage。

## 安全邊界

結果只允許寫入 `/tmp` 或 NAS `phase125` source-artifact volume。結果不會改 evaluator、
declared state、candidate/current phase、portfolio runtime 或 prospective registry，也不構成
投資建議。

## 下一階段

Phase 126 執行私人 NAS v1.0 operational acceptance：重跑、排程、retention、backup/restore、
rollback、Tailscale/mobile 與 source-risk runbook。Phase 127 的 prospective validation
calendar gate 仍不可提前。

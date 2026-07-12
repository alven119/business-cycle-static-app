# Phase 131：歷史 PIT 缺口與 governed transition event registry

Phase 131 完成五個歷史情境的 PIT 狀態與事件治理。COVID、2018–2019 late-cycle 可使用
既有 strict evidence replay；Dotcom、GFC、歐債情境因早期官方 release vintage 不完整，
維持明確 abstain 與 uncertainty window。

七條缺口 series 均記錄官方 archive、缺漏影響與可重現 blocker。Census 歷史 PDF、DOL
weekly claims archive、Federal Reserve charge-off release、BEA historical NIPA 均是官方候選，
但目前修訂歷史值不會被當成 PIT。後續若新增 parser，必須保留 artifact checksum、發布日、
parser version 與原始 release identity。

歷史重播新增 scenario window、shock、uncertainty window，以及由 strict evidence 首次支持
狀態衍生的 watch／confirmation annotation。這些事件只供研究呈現，不輸出 candidate/current
phase、不改寫 declared state、不調整規則或權重，也不產生配置指令。

## 測試策略

本 Phase 沿用 `tests/test_postgres_macro_warehouse_contract.py` 與
`tests/test_research_dashboard_bundle.py`，沒有新增 test file。新增 assertion 聚焦 registry、
runtime event extraction、revised/PIT 視覺分離與 closure，避免重複 CLI-only 測試。

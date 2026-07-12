# Phase 132：Phase-aware Dashboard 原子切換

Phase 132 讓 private NAS Dashboard 從同一份 active declared-state registry 取得研究脈絡。
首頁、轉折雷達、優先指標、指標學習說明、配置研究與歷史重播共享同一 context hash；
任何合法 transition 套用後，不需要重新 build image 才能切換研究位置。

四個 declared states 均有專屬 legal next phase、transition lanes、五個 priority roles、學習文案
與 portfolio template context。Boom 已有 Phase 123 live evaluator；其餘三個階段在 evaluator
尚未 operationalize 時只呈現 input readiness 與 explicit abstention，不使用 boom evaluator，
也不把 unavailable 當作 neutral。

Compose 的 transition activation gate 已開啟，但仍保留 Phase 129 的 preview token、合法順序、
evidence review acknowledgement、operator confirmation、append-only receipt 與 correction rollback。
最新資料不會自動改寫 declared state。

## 測試策略

沿用 `tests/test_research_dashboard_bundle.py`、`tests/test_postgres_macro_warehouse_contract.py`
與 `tests/test_ci_workflows.py`，不新增 test file。四狀態 matrix 共享 fixture，驗證 13 條 lanes、
20 個 priority card、16 個跨 surface context-hash checks 與 mobile phase context。

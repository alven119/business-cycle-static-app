# Product Capability 100% Completion Plan: Phase 87-91

本計畫記錄 Phase 86 後的最短工程路線。目標是在不改變產品 doctrine、不建立 standalone current phase classifier、不輸出 phase rank / score / winner、不提供投資建議的前提下，把八項產品能力推進到 dashboard / research production 使用所需的 100% readiness。

重要限制：若正式 production 定義包含未來前瞻經濟驗證，該 gate 仍受日曆與 prospective evidence 限制，不能用工程 phase 繞過。

## Phase 90 supersession note

Phase 90 之後，GitHub Pages 不再是 product deployment target。下表保留
Phase 87-89A 的能力收斂紀錄，但 Phase 89B 之後的部署路線已由
`docs/nas_dynamic_service_architecture.md` 與
`specs/common/nas_dynamic_service_contract.yaml` 接手。新的後續重點是：

- Phase 91：PIT-ready Postgres schema。
- Phase 92：revised macro data completeness。
- Phase 93：vintage/PIT backfill。
- Phase 94+：NAS dynamic dashboard runtime。

| Phase | 主題 | 主要補齊能力 |
|---|---|---|
| 87 | Research dashboard production-readiness rehearsal | 已完成 migration rehearsal、renderer caveats、rollback checklist、production boundary drill |
| 88 | Portfolio policy replay research surface completion | 已完成 policy templates、costs、turnover、research-only caveats、no-advice validators |
| 89A | Portfolio policy wording and research allocation template alignment | 已完成 research-only allocation template wording、no personalized trading instruction guard、dashboard token 與 closure wiring |
| 89B | Research dashboard migration record | 已完成 research dashboard artifact migration；Phase 90 已改以 NAS dynamic service 取代 Pages 作為部署方向 |
| 90 | NAS dynamic service architecture and Pages retirement | Pages workflow 退場、FastAPI/Postgres/Tailscale-first 架構立約、revised-first/vintage-followup 資料路線入檔 |
| 91 | PIT-ready Postgres warehouse | 建立 schema 與 migration scaffolding，不要求 default test 連線真實 DB |

能力目標：

| 能力 | Phase 86 後 | 目標 | 主要缺口 |
|---|---:|---:|---|
| 景氣階段判讀 | 100% | 100% | migration rehearsal 中維持 declared-state 語意 |
| 轉折風險偵測 | 100% | 100% | migration rehearsal 中維持 watch / confirmation 分離 |
| 解釋能力 | 100% | 100% | portfolio / replay surfaces 解釋一致性 |
| Portfolio policy research | 89% | 100% | research policy replay、成本、turnover、禁止用途 |
| 歷史重播與回測 | 93% | 100% | replay/backtest artifacts、attribution、data-mode drilldown |
| 安全輸出治理 | 100% | 100% | no-advice 與 migration boundary gates 保持 |
| 時間完整性與 abstention | 100% | 100% | replay migration 中維持 release / freshness / PIT 語意 |
| 模型治理與前瞻驗證 | 97% | 100% | migration rehearsal / rollback readiness；前瞻驗證仍受日曆 gate 約束 |

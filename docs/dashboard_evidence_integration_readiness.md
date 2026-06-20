# Dashboard Evidence Integration Readiness

## 背景

Phase 7G 系列將 recession confirmation、boom ending watch、recovery watch 三類 experimental evidence 收斂為 future dashboard diagnostics 可使用的 schema 與 validator。Phase 7G5 是收斂關卡：確認規格已完整，但 dashboard wiring 仍被刻意阻擋。

## Phase 7G 到 7G4 已完成什麼

- Phase 7G：cycle transition evidence architecture consolidation。
- Phase 7G1：transition evidence badge schema。
- Phase 7G2：badge fixtures 與 static validator。
- Phase 7G3：renderer contract planning。
- Phase 7G4：display model fixtures 與 contract validator。

## Readiness Checklist 的目的

Readiness checklist 用來回答：若未來要把 evidence badge 接入 dashboard diagnostics，哪些 artifact 已完成、哪些 validator 已完成、哪些安全條件仍阻擋 dashboard wiring。

## 已完成 Artifact

已完成的規格包含：

- `specs/common/cycle_transition_evidence_architecture.yaml`
- `specs/common/transition_evidence_badge_schema.yaml`
- `specs/common/transition_evidence_badge_fixtures.yaml`
- `specs/common/transition_evidence_badge_renderer_contract.yaml`
- `specs/common/transition_evidence_badge_display_fixtures.yaml`

## 已完成 Validator

目前可執行：

- `python scripts/show_transition_evidence_badge_schema.py`
- `python scripts/validate_transition_evidence_badge_fixtures.py`
- `python scripts/show_transition_evidence_badge_renderer_contract.py`
- `python scripts/validate_transition_evidence_badge_display_fixtures.py`

這些 validator 確保 badge 與 display model 不含 trade signal、allocation、phase override，也保留 diagnostics-only caveats。

## 尚未允許 Dashboard Wiring 的原因

Dashboard wiring 尚未允許，因為：

- 尚未修改 dashboard renderer 或 templates。
- 尚未更新 generated site validation。
- 尚未加入 HTML / accessibility / text safety tests。
- 尚未定義 live data mapping。
- Evidence display 不得影響 `current_phase_id` 或 `decision_status`。

## Dashboard Integration Blockers

Active blockers 是刻意保留的安全阻擋，不是失敗狀態。它們表示 Phase 7G 已可收斂，但還不能接 dashboard output。

## Required Before Dashboard Wiring

接 dashboard 前必須完成：

- dashboard evidence badge data adapter schema。
- generated site validation 更新。
- HTML text safety tests。
- accessibility 與 empty state 設計。
- 規劃階段不得產生 `public/` output。
- no formal decision impact tests。

## Allowed Future Work

允許下一步做 `7H1` dashboard evidence badge data adapter design，但仍不得產生 public output。也可轉向 `8A` portfolio policy research planning。`7H2` template prototype 需要等 adapter 與 generated-site validation plan 完成後才可進行。

## 為什麼可以收斂 Phase 7G

Phase 7G 已完成 schema、fixtures、renderer contract 與 display model validation。這代表 dashboard evidence display 已達到 fully specified but not wired 狀態，可以關閉架構收斂階段。

## 為什麼下一步可轉 Phase 8A

Transition evidence display 已有安全邊界，但尚未接 dashboard。下一步可以開始規格化書中榮景減碼與衰退後再加碼策略，作為 portfolio policy research 的前置設計。這仍然不是交易建議，也不產生 allocation。

## Caveats

- 此為 dashboard integration readiness checklist，不代表 dashboard 已接入。
- Evidence badge 僅供 diagnostics display。
- Evidence badge 不會改變 `current_phase_id` 或 `decision_status`。
- Watch 類訊號不是買賣訊號。
- 不構成投資建議。

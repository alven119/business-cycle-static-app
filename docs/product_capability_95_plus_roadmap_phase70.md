# Product Capability 95 Plus Roadmap Through Phase 84

Phase 75 resets the near-term route. The prior Phase 74-80 plan was too
dashboard-heavy and would not bring portfolio policy research, historical
replay/backtest, and model governance close enough to formal production use.

The new route targets all eight governed capabilities at 95% or better by
Phase 84. Percentages remain governed orientation numbers. They are not
economic validation, investment advice, or a formal current phase decision.

## Capability Targets

| Capability | Phase 74 | Target By Phase 84 | Main Gap |
|---|---:|---:|---|
| C1 景氣階段判讀能力 | 100% | 100% | Preserve declared-state semantics while portfolio/replay layers mature |
| C2 轉折風險偵測能力 | 99% | 100% | Release accumulation and confirmation display |
| C3 解釋能力 | 100% | 100% | Extend explanation to portfolio and replay/backtest artifacts |
| C4 Portfolio policy research 能力 | 38% | 95% | Policy templates, replay schedules, costs, turnover, caveats |
| C5 歷史重播與回測能力 | 54% | 95% | Strict/revised replay, cash-flow-aware kernel, research artifacts |
| C6 安全輸出治理能力 | 94% | 98% | Forbidden-field gates for portfolio/replay/backtest surfaces |
| F1 時間完整性與 abstention | 94% | 98% | Revised vs point-in-time replay and missing-input abstention |
| F2 模型治理與前瞻驗證 | 70% | 95% | Lineage, migration rehearsal, rollback, prospective wait-state handoff |

## Planned Phases

| Phase | Primary Outcome | Capabilities Advanced |
|---|---|---|
| 75 | All-capability roadmap reset and portfolio research baseline | C4, C5, C6, F1, F2 |
| 76 | Book benchmark portfolio policy templates | C4, C6 |
| 77 | Portfolio policy replay schedule engine | C4, C5, C6 |
| 78 | Cash-flow-aware backtest kernel | C4, C5, C6 |
| 79 | Historical replay runner with strict/revised separation | C2, C5, F1 |
| 80 | Research-only backtest artifact generation | C4, C5, C6 |
| 81 | Portfolio and replay dashboard integration | C3, C4, C5 |
| 82 | Replay/backtest reproducibility and provenance hardening | C5, C6, F1, F2 |
| 83 | Governance migration rehearsal | C6, F2 |
| 84 | All-capability 95 percent readiness review | C1-C6, F1-F2 |

## Phase 75 Baseline

Phase 75 creates a portfolio policy research baseline contract with eight
research-only, backtest-only template slots:

- passive all-stock baseline
- stock/cash initial
- stock/cash advanced
- stock/long Treasury initial
- stock/long Treasury advanced
- boom 70/50/30 template
- recession defense research template
- recovery re-risk research template

This baseline is not a live allocation engine. It does not run a backtest,
does not emit a trade action, and does not publish portfolio output.

## Guardrails

- No standalone current phase classifier.
- No phase rank, winner, role-count vote, or arbitrary phase score as product
  answer.
- No current or candidate phase emission before a separate explicit migration
  gate.
- No buy/sell signal, trade action, or current allocation recommendation.
- No historical result tuning.
- No public, backtest, or prospective repo output unless a later phase opens a
  governed output gate.
- Portfolio policy work remains research-only until later validation and
  migration gates explicitly allow stronger usage.

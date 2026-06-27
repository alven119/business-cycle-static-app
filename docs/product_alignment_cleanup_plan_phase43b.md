---
phase_id: "43B"
status: cleanup_doctrine_enforcement
created_at: "2026-06-27"
doctrine_contract: specs/common/investment_cycle_product_doctrine.yaml
legacy_boundary_contract: specs/common/legacy_production_v1_boundary.yaml
---

# Phase 43B Doctrine Enforcement Cleanup Plan

Phase 43B does not delete code, change production behavior, add dashboard
features, run live refresh, run backtests, or implement the ordered state
machine. It converts Phase 43A doctrine into concrete repo boundaries so future
agents do not restart standalone current-phase classifier work.

## Wording Reframed

- `docs/project_north_star.md` now describes the mature answer as declared
  current phase plus legal transition monitoring, not phase winner selection.
- `AGENTS.md` now describes indicator evidence and transition contracts rather
  than generic scoring outputs.
- `docs/agent_workflow.md` now requires future phases to preserve the legacy v1
  boundary and answer doctrine questions before implementation.
- `docs/prompt_templates.md` now tells future prompts to read the legacy v1
  boundary when touching scoring, resolver, state-machine, pipeline, snapshot,
  Pages workflow, or dashboard output.

## Legacy Quarantine

`docs/legacy_production_v1_boundary.md` and
`specs/common/legacy_production_v1_boundary.yaml` classify these artifacts as
legacy production v1 baseline:

- `src/business_cycle/phases/scoring.py`
- `src/business_cycle/phases/batch_scoring.py`
- `src/business_cycle/phases/state_machine.py`
- `src/business_cycle/phases/data_only_resolver.py`
- `scripts/run_cycle_pipeline.py`
- `scripts/build_cycle_snapshot.py`
- `.github/workflows/pages.yml`

They are not removed because production v1 remains the current compatibility
baseline. They also are not the mature doctrine path. Future work must either
wrap them as diagnostic inputs or build a doctrine-aligned path behind an
explicit migration gate.

## Code That Cannot Move In Phase 43B

Phase 43B must not change:

- production v1 scoring weights or scoring logic
- production resolver or state-machine behavior
- production dashboard behavior
- GitHub Pages workflow behavior
- portfolio policy engine behavior
- historical replay/backtest execution behavior
- prospective registry, dates, or freezes

## Future Phase Scope

### Phase 44

Phase 44 should implement only:

- declared phase registry
- ordered legal transition state machine
- declared phase start and phase age
- transition lineage and abstention rules

Phase 44 should not implement portfolio policy, historical replay/backtest, or
boom transition monitor scope.

### Phase 45

Phase 45 should focus on boom continuation, boom-ending watch, recession watch,
and recession confirmation because the current user premise may treat the
declared state as boom.

### Phase 46

Phase 46 should implement portfolio policy research templates. Template weights
must remain research assumptions and must not become current allocation
recommendations.

### Phase 47

Phase 47 should implement a historical replay/backtest vertical slice centered
on transition timing, evidence attribution, policy replay, cash-flow-aware
returns, drawdowns, false-signal cost, and missed-recovery cost.

## Enforcement

`scripts/audit_product_doctrine_enforcement.py` provides a lightweight guard
for future CI or closure checks. It verifies:

- North Star doctrine wording is reframed.
- AGENTS, workflow, and prompt templates reference the doctrine and legacy
  boundary.
- Legacy v1 boundary files exist and inventory the required artifacts.
- Raw book PDF and `data/raw` files are not tracked.
- Product-answer wording does not drift back toward standalone classifier,
  rank/winner, isolated candidate classifier, or current allocation
  recommendation semantics.

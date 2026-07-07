---
version: "1.0"
status: active
created_at: "2026-06-27"
contract_path: specs/common/legacy_production_v1_boundary.yaml
---

# Legacy Production v1 Boundary

Production v1 remains a preserved baseline for historical compatibility and
static-site continuity. It is not the mature product doctrine described by
`docs/project_north_star.md` and `docs/investment_cycle_product_doctrine.md`.

This boundary does not delete or rename legacy v1 runtime artifacts. It records
how future phases must treat the existing v1 phase scoring, resolver, pipeline,
and snapshot after the GitHub Pages workflow has migrated to the doctrine-aligned
research dashboard.

## Legacy Inventory

| Artifact | Boundary classification | Required handling |
|---|---|---|
| `src/business_cycle/phases/scoring.py` | legacy phase-score diagnostic | May be maintained for compatibility; must not be product answer |
| `src/business_cycle/phases/batch_scoring.py` | legacy batch score artifact writer | May continue producing v1 artifacts; future doctrine path must label or wrap it |
| `src/business_cycle/phases/state_machine.py` | legacy score-driven state-machine-like resolver | Not the mature ordered cycle state machine until migrated through a gate |
| `src/business_cycle/phases/data_only_resolver.py` | legacy data-only resolver | Not a standalone current phase classifier for future product work |
| `scripts/run_cycle_pipeline.py` | legacy production v1 pipeline entry | Keep behavior unchanged until explicit migration |
| `scripts/build_cycle_snapshot.py` | legacy snapshot builder | Keep output semantics quarantined as v1 baseline |
| `.github/workflows/pages.yml` | migrated research dashboard deployment workflow | No longer a legacy v1 output path after explicit user authorization |

## Boundary Rules

- Legacy v1 phase scores are diagnostics, not the mature product answer.
- Legacy v1 resolver output is a baseline artifact, not the doctrine state
  machine.
- Phase score, rank, winner, selected output, or role-count vote must not be
  promoted into a mature product answer.
- Future candidate phase semantics must mean legal transition candidate.
- Future Phase44 work should create a doctrine-aligned declared-state registry
  and ordered legal transition path, or explicitly wrap legacy inputs as
  diagnostic inputs.
- Future Phase44 must not implement portfolio policy, historical replay,
  historical backtest, or boom transition monitor scope.
- Future Phase45 should focus on boom continuation, boom-ending watch,
  recession watch, and recession confirmation because the current user premise
  may treat the declared state as boom.
- Future Phase46 should implement portfolio policy research templates.
- Future Phase47 should implement historical replay/backtest vertical slice.

## Migration Gate

Any future migration from legacy production v1 to the doctrine-aligned path
must explicitly document:

- replacement artifacts and tests
- user-visible wording changes
- rollback behavior
- production behavior impact
- candidate/current phase output gates
- data lineage preservation
- dashboard and Pages deployment changes

The Pages deployment migration gate is now open for research-dashboard output.
Legacy v1 scoring, resolver, pipeline, and snapshot artifacts remain
quarantined as compatibility baselines and must not be promoted into the mature
product answer.

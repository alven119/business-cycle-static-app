# Phase 90 Product Alignment Cleanup Plan

Phase 90 changes the deployment doctrine from GitHub Pages to a private NAS
dynamic service. It is an architecture and retirement phase, not a model logic
phase.

## Completed In This Phase

- GitHub Pages deployment workflow retired.
- Pages-specific builder and validator scripts removed.
- Pages-specific workflow tests replaced with retirement tests.
- NAS dynamic-service contract added.
- PIT-ready Postgres direction recorded.
- Revised-first and vintage-followup data completion path recorded.
- `grill-me` project skill added under `.agents/skills/grill-me/`.

## Preserved Boundaries

- No standalone current phase classifier.
- No phase score/rank/winner product answer.
- No candidate or current phase emission.
- No production resolver or legacy v1 behavior change.
- No portfolio policy execution.
- No backtest execution.
- No `public/`, `data/backtests`, or `data/prospective` output.

## Next Phase

Phase 91 should implement the first PIT-ready Postgres warehouse contract and
schema scaffolding for the NAS dynamic service. It should not yet require live
database connectivity in default tests.

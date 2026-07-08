---
phase_id: 93
phase_label: vintage_pit_backfill_availability_accounting
status: completed_research_only
---

# Phase 93 Product Alignment Cleanup Plan

Phase 93 extends the Phase 92 revised macro import dry-run into vintage/PIT
backfill availability accounting for the future NAS/Postgres service.

## Completed

- Added `specs/common/vintage_pit_backfill_availability_contract.yaml`.
- Added a no-write availability manifest builder for vintage/PIT backfill
  planning.
- Accounted for 39 roles, 28 series keys, 25 registry-covered series, 24 direct
  future vintage requests, and one derived same-as-of PIT plan.
- Kept five role-level blockers visible: two source/import blockers and three
  derived reversal/bottoming roles that still need explicit derived lineage.
- Added Phase 93 closure checks and CI closure wiring.
- Updated the product capability progress view to Phase 93.

## Explicit Non-Goals

- No live ALFRED/FRED fetch.
- No live database connection.
- No Postgres write.
- No `observation_vintage` rows.
- No strict point-in-time result.
- No candidate or current phase output.
- No portfolio or trade output.

## Next Gap

Phase 94 should materialize revised rows and PIT availability accounting into a
NAS service indicator snapshot/view-model while preserving the revised/PIT
separation.

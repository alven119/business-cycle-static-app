---
version: "1.0"
status: closed
phase_id: 92
---

# Phase 92 Product Alignment Cleanup Plan

Phase 92 adds a revised macro data completeness import dry-run for the private
NAS dynamic service path.

## What Changed

- Added `specs/common/revised_macro_data_import_contract.yaml`.
- Added `src/business_cycle/storage/revised_macro_data_import.py`.
- Added a CLI dry-run writer limited to `/tmp`.
- Added Phase 92 closure checks and CI closure wiring.
- Updated the product capability progress view to Phase 92.

## Product Boundary

The dry-run maps the current official or accepted macro source set into the
Phase 91 warehouse shape:

- `series_registry`
- `source_artifact`
- `observation_revised`

It does not connect to a live Postgres database, write Postgres rows, fetch live
FRED data, import vintage observations, emit a candidate/current phase, execute
replay/backtest, or produce portfolio instructions.

## Deferred Work

- Phase 93: vintage/PIT backfill and availability accounting.
- Later: executed NAS Postgres migration, live DB smoke test, service API, and
  dynamic dashboard read path.

---
version: "1.0"
status: closed
phase_id: 91
---

# Phase 91 Product Alignment Cleanup Plan

Phase 91 adds the PIT-ready Postgres macro warehouse schema contract for the
private NAS dynamic service direction.

## What Changed

- Added `specs/common/postgres_macro_warehouse_contract.yaml`.
- Added deterministic schema helper code in
  `src/business_cycle/storage/postgres_macro_warehouse.py`.
- Added Phase 91 closure checks and CI closure wiring.
- Updated the product capability progress view to Phase 91.

## Doctrine Alignment

This phase does not create a standalone current phase classifier, phase score,
phase rank, candidate phase, current phase emission, personalized allocation
instruction, or trade signal.

The schema is designed for:

- revised macro observations,
- vintage point-in-time observations,
- release-calendar metadata,
- immutable source artifact provenance,
- indicator and evidence snapshots,
- dashboard snapshots,
- research-only backtest and portfolio policy run lineage.

## Deferred Work

- Phase 92: revised macro data completeness import.
- Phase 93: vintage/PIT backfill and availability accounting.
- Later: executed migrations, NAS DB smoke test, service endpoints, and private
  mobile dashboard verification.

---
phase_id: 104
phase_label: nas_postgres_revised_import_backup_rehearsal
status: completed
---

# Phase 104 Product Alignment Cleanup Plan

Phase 104 advances the NAS migration path from private-LAN reachability to a
Postgres revised macro data import and backup rehearsal. It does not connect to
the NAS database, execute schema migrations, run backup commands, import a
Container Manager bundle, fetch live macro data, or write repository outputs.

## Added

- `specs/common/nas_postgres_revised_import_rehearsal_contract.yaml`
- `src/business_cycle/storage/nas_postgres_revised_import_rehearsal.py`
- `scripts/show_nas_postgres_revised_import_rehearsal.py`
- `scripts/run_nas_postgres_revised_import_rehearsal.py`
- `specs/audits/phase104_nas_postgres_revised_import_closure.yaml`
- `src/business_cycle/audits/phase104_nas_postgres_revised_import_closure.py`
- `scripts/show_phase104_nas_postgres_revised_import_closure.py`

## Product Alignment

- Preserves the declared cycle state and legal transition model.
- Treats revised macro data as revised service data, not point-in-time
  evidence.
- Produces only import, backup, restore verification, and SQL-preview
  artifacts under `/tmp`.
- Keeps portfolio policy research as research-only and emits no current
  allocation, target weight, or trade action.

## Deferred

- Actual NAS Postgres connection.
- Actual schema migration.
- Actual import execution.
- Actual backup and restore execution.
- Private authenticated NAS service operation.

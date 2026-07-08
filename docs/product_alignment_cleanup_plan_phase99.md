---
phase_id: 99
phase_label: nas_postgres_readonly_smoke_and_ds925_package_assessment
status: closed_candidate
---

# Phase 99 Product Alignment Cleanup Plan

Phase 99 advances the NAS migration by validating the database-read side of the
future service without connecting to a live database.

## Completed In This Phase

- Added a governed fixture-backed Postgres read-only smoke contract.
- Reused Phase 92 warehouse-shaped rows as the fixture data source.
- Validated four read-only query contracts:
  - `series_registry`
  - `source_artifact`
  - `observation_revised`
  - `dashboard_snapshot`
- Rejected forbidden SQL prefixes for write, schema, and privilege-changing
  statements.
- Added a DS925+ package assessment and deployment phase estimate.

## DS925+ Package Direction

Recommended path:

1. Container Manager for app/Postgres/refresh-worker containers.
2. PostgreSQL official container image for the macro warehouse.
3. Tailscale for private phone access.
4. Web Station or DSM reverse proxy only if useful after the private service is
   stable.
5. Hyper Backup / Snapshot Replication for later volume and config protection.

## Product Alignment

The phase keeps the declared-state product shape unchanged. It does not add a
standalone current phase classifier, phase score, phase rank, role-count vote,
candidate phase output, current phase output, portfolio instruction, backtest
execution, live database read, or schema migration.

## Deferred Gaps

- Container Manager compose/service bundle dry-run.
- Actual private ASGI service startup.
- Real DS925+ read-only Postgres smoke with controlled credentials.
- Revised macro data import execution into the NAS database.
- Backup/restore rehearsal for the Postgres volume.
- Private phone browser acceptance over Tailscale.

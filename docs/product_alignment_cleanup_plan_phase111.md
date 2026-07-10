# Phase 111 Product Alignment Plan

## Outcome

Phase 111 connects the active private NAS dashboard to the Phase 110 Postgres
warehouse. Server-side reads materialize the 39 governed role cards: 37 have
revised values and charts, while consumer confidence and ADP employment remain
explicitly source-blocked.

The read session enforces `default_transaction_read_only=on` and a statement
timeout. When `BUSINESS_CYCLE_DATABASE_URL` is configured, a database or schema
failure blocks service startup; the service does not silently substitute the
old bundled snapshot.

## User Surface

- Traditional Chinese role names remain the primary labels.
- Each available role shows its latest revised value, unit, freshness, and
  source lineage.
- Each available role can expand server-rendered YTD, trailing-one-year, and
  trailing-five-year trend charts.
- Revised data is labeled diagnostic-only and is not described as point-in-time
  evidence.

## Doctrine Boundary

This phase does not infer the current phase, select a candidate phase, rank
phases, vote by role count, or emit portfolio actions. It changes only the new
private NAS dashboard runtime; legacy production v1 behavior is unchanged.

## Deferred Work

- Schedule and govern the official-source refresh worker.
- Create a dedicated least-privilege database login for dashboard reads.
- Backfill exact vintages into `macro.observation_vintage`.
- Rehearse Postgres/source-artifact restore.
- Confirm the declared boom start date or interval and complete legal
  transition confirmation semantics.

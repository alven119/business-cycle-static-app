# Phase 116: Fixed-Time Release-Aware Refresh And Backup Retention

## Product outcome

Phase 116 replaces the drifting 86,400-second worker loop with a governed wall
clock schedule. The private NAS refreshes all 26 canonical direct revised series
at 03:30 Asia/Taipei each day. Verified exact release events may create a
second, source-family subset job after a configurable 180-minute ingestion
observation buffer.

The buffer is not an official availability claim. Cadence-only and
reference-only source families never receive fabricated release triggers; they
continue through the daily fallback.

## Restart and failure semantics

The worker persists a bounded schedule-job ledger. Restart recomputes the next
wall-clock run and can catch up an exact release follow-up missed within 24
hours. A failed source job is recorded by the existing Phase 112 status and is
not placed in an automatic tight retry loop; Phase 115's token-bound retry gate
remains the remediation path.

## Backup retention

Private backup retention is preregistered as seven successful and three failed
runs. Unknown legacy runs are preserved. Phase 116 exposes a hash-bound preview
but does not automatically delete any backup; destructive execution remains a
future operator gate.

## Historical data completeness

The live warehouse contains the full available revised histories requested for
26 canonical direct FRED/ALFRED series. Derived dashboard roles are computed
from those inputs on read. This is not the same as all macro history being
complete:

- `observation_vintage` remains empty;
- `release_calendar` remains empty until reference-period semantics are safely
  normalized;
- two source-blocked roles remain visible;
- strict point-in-time replay is not ready.

The dashboard and closure explicitly preserve this distinction.

## Test consolidation

No new test file is added. Fixed-time scheduling, release subset selection,
restart ledger semantics, retention preview, renderer, compose, CLI, and closure
coverage extend existing NAS/Postgres and runtime tests.

## Deferred gap

Phase 117 should begin the first governed ALFRED exact-vintage backfill slice
for transition-critical roles and normalize verified release-calendar rows into
Postgres without relabeling revised history as point-in-time evidence.

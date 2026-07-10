# Phase 112 Product Alignment Plan

## Product Outcome

Phase 112 turns the Phase 110 revised importer into an operational private-NAS
refresh loop. The useful product change is simple: the dashboard can keep its
official revised macro history current and explain whether the source refresh
is healthy, running, scheduled, or degraded.

This phase advances cycle assessment, transition monitoring, explanation, safe
output governance, temporal labeling, and operations. It does not infer a
current phase, select a candidate phase, or calculate a portfolio action.

## Runtime Shape

- `macro_refresh_worker` runs once per day after an initial 24-hour delay.
- A network-disabled one-shot init service assigns the dedicated artifact
  volume to UID 1000; the long-running worker itself stays non-root.
- An operator confirmation remains present in the private compose environment.
- A non-blocking file lock rejects overlapping executions.
- The existing 26-series Phase 110 importer performs idempotent revised upserts.
- Each run keeps checksummed artifacts under the NAS source-artifact volume.
- `refresh-status.json` is written atomically and contains no credential value.
- The dashboard reads PostgreSQL with a read-only transaction and refreshes its
  materialized shell at most every 15 minutes.
- A transient dashboard rematerialization failure serves the last good snapshot
  and marks it stale rather than silently presenting it as current.

## User Surface

The overview page adds a Traditional Chinese source-refresh section with:

- current schedule state;
- last completed timestamp;
- next scheduled timestamp;
- completed/requested source count;
- aggregate source health;
- a revised-data-only caveat.

## Safety Boundaries

- Tests use injected import runners and never call FRED.
- Only the worker may write PostgreSQL; the dashboard remains read-only.
- No source secret is persisted in status, artifacts, logs, or Git.
- `observation_vintage` remains separate and empty until a later PIT phase.
- No candidate/current phase, rank, score, winner, trade, or allocation output
  is introduced.
- No prospective registry or legacy production-v1 behavior is changed.

## Test Consolidation

Phase 112 adds no test file. Scheduler behavior is added to the existing NAS
PostgreSQL contract test, TTL behavior extends the existing runtime server test,
and closure indexing extends the existing CI workflow test. This preserves the
30-file default product-core boundary and avoids duplicate CLI-only tests.

## Deferred Gaps

- Governed confirmation of the declared boom start date or interval.
- Per-series official release-calendar scheduling and detailed source drill-down.
- ALFRED/exact-vintage backfill and strict point-in-time replay.
- Backup restore rehearsal and dedicated least-privilege credential rotation.

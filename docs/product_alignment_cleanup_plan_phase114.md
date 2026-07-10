# Phase 114: Per-source Official Release Calendar And Refresh Failure Drilldown

## Product outcome

Phase 114 turns the aggregate Phase 112 refresh banner into an operator-facing
source-operations surface. The private NAS now distinguishes:

- an official release that is not due yet;
- an official release that is due and waiting for the next governed refresh;
- a local refresh failure;
- a series skipped because an earlier source failed;
- a stale series after a successful refresh;
- a source whose official calendar is only cadence/reference precision and
  therefore cannot safely support a delay claim.

The page is available only behind the existing private NAS login at
`/source-operations`, with JSON at `/api/source-operations.json`.

## Source-calendar evidence

The 26 NAS direct series map to 12 release families. Nine have explicit 2026
official schedule entries from BLS, BEA, Census, DOL, or Federal Reserve release
pages. Moody/FRED business-day observations and H.15 monthly averages retain
cadence-only precision. Federal Reserve charge-off/delinquency data retain
reference-only precision because a safely automatable future schedule was not
verified.

Observation dates are never treated as release dates. A missing local refresh
after an official date is reported as `release_delayed_or_refresh_missing`, not
as proof that the agency delayed publication.

## Refresh failure preservation

The scheduled refresh status now stores only redacted per-series fields:
series ID, imported/resumed/failed state, observation count, error class for a
failed source, and a governed reason code. It does not retain API keys, database
URLs, raw exception messages, candidate phase output, or portfolio instructions.
Partial success remains preserved.

## Test consolidation

No test file was added. Coverage extends the existing Postgres/NAS contract and
runtime-server test files. The default product-core file count remains 30.

## Deferred gap

Phase 115 should add a governed operator retry and restore drill: preview the
failed series set, execute only through the existing worker boundary, and prove
database/source-artifact backup restoration without exposing secrets.

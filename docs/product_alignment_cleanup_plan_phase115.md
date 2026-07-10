# Phase 115: Governed Source Retry And Backup-Restore Drill

## Product outcome

Phase 115 closes two private-NAS operating gaps without changing economic
decision logic:

- a failed official source can be retried as a canonical subset after an
  operator reviews a token-bound preview;
- the revised Postgres warehouse and private source artifacts are backed up and
  restored into isolated verification locations before the result is accepted.

Successful sources are never included merely because a retry was requested.
The dashboard only displays readiness and verification status; it cannot issue
database commands or start a refresh.

## Retry boundary

The preview reads the existing Phase 112 refresh status. Candidates are limited
to an explicit failed series and canonical series not attempted after that
failure. A preview token binds both the refresh-status hash and ordered candidate
IDs. Execution requires the Phase 115 confirmation phrase and delegates to the
existing scheduled-refresh worker with a validated series subset.

Tests use fake providers and temporary directories. They do not access FRED or
Postgres.

## Backup and restore boundary

The live drill creates:

- a custom-format `pg_dump` in the private source-artifact volume;
- a checksum-protected tar snapshot of existing source artifacts, excluding the
  Phase 115 backup directory itself;
- an isolated staging database for `pg_restore` verification;
- a temporary source-artifact extraction for member-path and checksum checks.

The app image pins Debian bookworm and installs `postgresql-client-16` from the
official PostgreSQL Apt repository. Before any dump, the worker compares the
`pg_dump` and server major versions and abstains on mismatch. This prevents a
newer custom-archive header or session setting from creating a backup that the
PostgreSQL 16 server cannot restore.

Five warehouse table counts must match before success. The staging database is
dropped even after a verification failure. Status is atomically written and
contains no database password, API key, raw database URL, or raw exception text.

## Dashboard and doctrine alignment

The authenticated `/source-operations` page now explains retry candidates and
the latest backup/restore status in Traditional Chinese. It remains research
operations metadata, not a current-phase classifier, transition confirmation,
portfolio instruction, replay, or backtest.

No new test file was added. Phase 115 extends the existing consolidated NAS and
Postgres test surface, preserving the reduced default suite shape.

## Deferred gap

Phase 116 should automate official-calendar synchronization and define private
backup retention, then continue exact-vintage/PIT accumulation. Those are
separate from this one-time restore proof and must retain the same private NAS,
abstention, and no-silent-fallback boundaries.

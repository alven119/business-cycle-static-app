# Phase 118: Broader ALFRED/PIT Coverage And Strict Replay Input Audit

## Product outcome

Phase 118 expands the private NAS PostgreSQL warehouse from 13 to all 26
direct official series in the current source contract. The live database now
contains 76,848 ALFRED realtime-interval rows while preserving the existing
22,131 revised observations. The broader import added 33,891 intervals and
used the Phase 117 checkpointed importer rather than creating a second data
path.

This phase does not execute a historical replay, classify a current or
candidate phase, calculate accuracy or performance, or run a portfolio policy.

## Revision-aware release calendar

The calendar schema now identifies a release by `release_event_id`, allowing
multiple initial and revision events for the same series and reference period.
It stores 85 normalized expected events:

- 12 weekly DOL claims rows use explicit reference-week rules;
- 21 rows are revision events rather than overwritten initial releases;
- zero rows infer release availability from observation dates;
- `actual_release_at_utc` remains null until independently verified.

For DOL weekly claims, initial claims use the week ending five days before the
Thursday publication and continued claims use the week ending twelve days
before publication. These rules reflect the official weekly release layout and
do not invent a fixed availability lag for other source families.

## Strict replay input audit

The read-only audit checks whether each direct series has at least one interval
that was available at each preregistered scenario start. It does not invoke the
evidence evaluator or decision runtime and does not claim sufficient lookback.

| Scenario start | Available | Missing | Status |
|---|---:|---:|---|
| 2000-01-31 | 19 | 7 | partial official PIT history |
| 2007-01-31 | 21 | 5 | partial official PIT history |
| 2011-01-31 | 23 | 3 | partial official PIT history |
| 2018-01-31 | 26 | 0 | all direct series present |
| 2020-01-31 | 26 | 0 | all direct series present |

Missing early intervals remain explicit blockers. Revised history is not used
as a silent fallback.

## Operator safety and live acceptance

Before migration, the existing Phase 115 backup/restore drill restored the
five core table counts into an isolated staging database and removed staging
after verification. The calendar migration used a transaction guard requiring
the known 59-row Phase 117 state and zero actual-release timestamps. The live
app, worker, and Postgres containers are healthy on the Phase 118 image; LAN
health and read-only readiness pass, and the tailnet-only Tailscale Serve proxy
to `127.0.0.1:18080` remains configured.

## Test consolidation

No test file was added. Phase 118 extends the existing NAS/Postgres consolidated
suite with the migration guard, weekly/revision semantics, operator gate,
checkpointed importer, read-only scenario audit, compose wiring, CLI, and live
closure assertions.

## Deferred gap

Phase 119 should rehearse strict replay with partial-input abstention and clear
lookback requirements. It must not turn missing early official intervals into
revised fallback or enable a standalone current-phase classifier.

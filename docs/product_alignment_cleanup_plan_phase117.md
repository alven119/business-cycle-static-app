# Phase 117: Transition-Critical ALFRED/PIT Backfill And Release Calendar

## Product outcome

Phase 117 restores the private dashboard's PC/mobile reachability and starts
the governed point-in-time warehouse. The NAS now stores 42,957 ALFRED
realtime-interval rows for 13 series used by boom-to-recession and
recession-to-recovery research. The existing 22,131 revised observations remain
unchanged and continue to power the current dashboard.

This does not classify a current or candidate phase. It prepares historical
inputs for later strict replay and transition attribution.

## Private access repair

Phase 116 accidentally deployed the app only on `127.0.0.1:18080`, so direct
LAN access failed. The active compose now binds both:

- `127.0.0.1:18080` for Tailscale Serve HTTPS;
- `192.168.1.116:18080` for the private home LAN.

It does not bind every host interface. The authenticated dashboard should be
used through `https://mao-family-nas.tailb97dc1.ts.net/` whenever Tailscale is
available, because the session cookie remains HTTPS-only.

## PIT scope and availability semantics

The governed subset is `AAA`, `BAA`, `CCSA`, `DGORDER`, `EXPGS`, `FPIC1`,
`ICSA`, `IMPGS`, `INDPRO`, `PCEC96`, `PCEDGC96`, `RRSFS`, and `UEMPLT5`.
ALFRED output type 1 preserves observation date and realtime start/end rather
than copying revised history into the vintage table.

ALFRED supplies date-level realtime metadata, not a guaranteed release time.
The warehouse therefore treats the row as available at the end of its
`realtime_start` day in UTC. This conservative timestamp prevents same-day
look-ahead and is explicitly not described as an official publication time.

Official history is not uniformly available from 1998. CCSA and ICSA realtime
history begins in 2009, DGORDER in 1999, and RRSFS in 2001. Earlier strict
replay must abstain rather than use revised fallback.

## Normalized release calendar

The nine exact-schedule release families expand to 85 series/event rows. The
Phase 91 table can safely store 59 rows with explicit monthly or quarterly
reference periods. Twelve weekly rows remain blocked because the source
contract does not identify a reference-period date. Fourteen later GDP
revision events remain deferred because the existing primary key stores one
event per series/reference period/family.

No observation date is treated as a release date. `actual_release_at_utc`
remains null until independently verified.

## Test consolidation

Phase 117 adds no test file. PIT normalization/import, operator gate, calendar
blocking, dual private bindings, runtime counts, CLI, and closure assertions
extend the existing NAS/Postgres product-core suite.

## Deferred gap

Phase 118 should broaden PIT coverage beyond the 13 transition-critical
series, add a revision-event-capable release calendar schema, and audit strict
replay coverage without enabling a standalone phase classifier or portfolio
execution.

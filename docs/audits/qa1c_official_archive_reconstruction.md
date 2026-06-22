# Phase QA1C Official Archive Reconstruction

QA1C separates partial official query support from full required-horizon strict
coverage. A series can have a valid ALFRED/FRED response and still be blocked if
the response does not cover every required scenario as-of date.

The seven formal temporal gaps are:

- `DCOILWTICO`
- `DGORDER`
- `DGS10`
- `ICSA`
- `MORTGAGE30US`
- `RRSFS`
- `RSAFS`

Official archive reconstruction is not the same evidence class as ALFRED
`realtime_start` / `realtime_end` intervals. QA1C recognizes strict-ready
evidence only when it is one of:

- `exact_vintage_interval`
- `official_release_archive`
- `official_observational_archive`
- `derived_point_in_time`

Current historical values plus an arbitrary release lag are not strict
point-in-time evidence. Initial release data are not as-of latest visible
vintages. Substitutes require temporal, economic, and signal equivalence review;
high correlation alone is not sufficient.

The remediation matrix is
`specs/audits/formal_temporal_gap_remediation.yaml`. It records official source
candidates, prohibited shortcuts, current blocker class, and whether each series
is full-horizon strict-ready. As of QA1C, all seven rows remain blocked pending
deterministic official archive parsers or validated observational archive
evidence. Production revised scoring, scoring weights, resolver logic, and
dashboard behavior are unchanged.

Phase 9B1, real historical backtest progression, book benchmark execution, and
dashboard portfolio integration remain blocked until later gates explicitly
authorize them.

## QA1E Census/EIA Boundary

QA1E adds explicit denominator semantics for leaf source dependencies versus
derived formal outputs. `RRSFS` is treated as a derived output candidate from
same-as-of `RSAFS` and `CPIAUCSL`, so source-series coverage uses leaf
dependencies and derived-output readiness is reported separately.

`CPIAUCSL` may be live-verified through ALFRED vintage intervals, but that does
not make `RRSFS` full-horizon strict-ready unless `RSAFS` is strict-ready and
the official `RRSFS` formula, unit, base period, and seasonal-adjustment
compatibility are validated. EIA WTI parsed rows also remain non-strict until
official availability and correction/revision policy evidence is complete.

As of QA1E, Census `DGORDER` and `RSAFS` official artifacts are downloaded or
probed but deterministic historical release parsers are still blocked.
`DCOILWTICO`, `DGORDER`, `RSAFS`, and `RRSFS` must not contribute strict
official archive coverage from metadata-only entries, zero-row parses, revised
history plus lag, or direct revised fallback.

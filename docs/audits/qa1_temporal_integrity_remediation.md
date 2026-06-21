# Phase QA1 Temporal Integrity Remediation

QA1 separates temporal metadata completeness from strict point-in-time coverage.
Inventory completeness means every discovered series has an explicit availability
status. It does not mean the project has a tradable historical backtest.

## Data Modes

- `revised`: latest revised values. This remains the production live default.
- `release_lag_adjusted_revised_proxy`: revised values delayed by a release-lag
  rule. This is only a sensitivity diagnostic and is not point-in-time data.
- `initial_release_only`: first published value for each observation. It is useful
  for revision diagnostics, but it is not the as-of latest visible vintage.
- `vintage_as_of`: strict date-level as-of selection using `realtime_start` and
  `realtime_end`. This is the only strict point-in-time mode.

ALFRED real-time dates are date-level availability intervals interpreted as
end-of-day. The project does not claim intraday point-in-time precision.

## QA1 Boundary

Strict mode fails closed when cache rows or real-time metadata are missing. It
does not silently use revised data or a release-lag proxy.

## QA1B Backfill Verification

QA1B is the live formal vintage backfill and coverage verification step. It uses
bulk per-series ALFRED/FRED requests plus local cache selection; it must not send
one network request per monthly as-of date. The cache manifest records row count,
checksum, observation range, realtime range, duplicate-row count, query mode, and
quality class without API keys.

Formal readiness requires 15 formal direct dependencies and 3420 formal
series-date coverage pairs to pass strict `vintage_as_of` selection. If
`FRED_API_KEY` is absent, official API coverage cannot be attempted and formal
coverage remains blocked as an environment configuration issue. That condition
must recommend a retry after loading the key, not an official-data remediation
phase.

QA1B.1 separates registry-declared support from live-verified support. A registry
entry marked exact-vintage-ready only describes expected provider capability; it
does not count as live verification until an ALFRED/FRED response has been
cached and strict as-of selection succeeds. If no official request has been
attempted, the blocker is `official_query_not_attempted` or
`environment_configuration_blocked`, not `official_series_unsupported`.

Only after an actual official query shows that a formal dependency is
unsupported or lacks the needed historical vintage range should the blocker move
to QA1C. If any official series lacks usable vintage coverage, that series must
remain blocked; revised data, release-lag proxy, and initial-release-only are
not acceptable substitutes.

The live dashboard default is unchanged. Resolver decision logic, phase weights,
and dashboard behavior are unchanged.

Phase 9B remains a synthetic harness. Phase 9B1, book benchmark execution, and
real historical backtest progression remain blocked until later methodology,
market total-return, book-label, and calibration gates are complete.

## QA1C Archive Reconstruction Boundary

QA1C adds temporal evidence classes so partial official query support is not
confused with full required-horizon strict coverage. ALFRED history
insufficiency does not mean the economic indicator is invalid or nonexistent; it
means the ALFRED realtime interval cache cannot by itself reconstruct every
required scenario as-of date.

Official release archive reconstruction and official observational archives are
separate evidence classes from ALFRED vintage intervals. They may support strict
point-in-time only when source artifact metadata, publication or availability
rules, revision behavior, parser identity, checksum, and no-future-data
selection are explicit.

Current revised history plus an arbitrary lag remains a proxy, not strict
point-in-time. Initial release data remain first-release sensitivity data, not
as-of latest visible vintage. QA1C does not change formal scoring weights,
resolver logic, dashboard defaults, or production revised-mode behavior.

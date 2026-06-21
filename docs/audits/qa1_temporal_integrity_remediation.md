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
coverage remains blocked. If any official series lacks usable vintage coverage,
that series must remain blocked; revised data, release-lag proxy, and
initial-release-only are not acceptable substitutes.

The live dashboard default is unchanged. Resolver decision logic, phase weights,
and dashboard behavior are unchanged.

Phase 9B remains a synthetic harness. Phase 9B1, book benchmark execution, and
real historical backtest progression remain blocked until later methodology,
market total-return, book-label, and calibration gates are complete.

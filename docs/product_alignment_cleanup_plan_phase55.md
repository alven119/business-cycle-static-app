# Phase 55 Macro Indicator Coverage Readiness Matrix

Phase 55 turns the Phase 51-54 source work into a product-facing coverage
matrix. It does not classify the current phase, select a candidate phase, or
change production behavior.

## Product Purpose

The user-facing problem is no longer only "is this role missing?" The dashboard
must explain:

- which macro role is missing or abstained
- whether there is an official direct source
- whether the source is an official derived or composite path
- whether direct use requires authorized private or user-supplied input
- whether a public proxy is supporting-only
- what data risk remains
- what the next implementation gap is

This phase therefore adds `macro_indicator_coverage_readiness_matrix` as a
research-only dashboard gap burn-down layer.

## Boundaries

The matrix preserves the project doctrine:

- no standalone current phase classifier
- no phase rank, score, winner, or role-count vote
- no candidate/current phase emission
- no production v1 behavior change
- no portfolio policy output
- no backtest or replay execution
- no `public`, `data/backtests`, or `data/prospective` output

Supporting proxies remain display-only. PAYEMS does not replace ADP, and UMich
sentiment does not replace the book-core consumer confidence role. The matrix
shows these sources with data-risk labels so the user can understand the gap
without silently filling it.

## Result

Phase 55 adds:

- `specs/common/macro_indicator_coverage_readiness_matrix.yaml`
- `src/business_cycle/audits/macro_indicator_coverage_readiness_matrix.py`
- `scripts/show_macro_indicator_coverage_readiness_matrix.py`
- Phase 55 closure spec, audit, script, and tests

The matrix currently covers 39 macro evidence roles across recovery, growth,
boom, and recession. It produces a dashboard-ready view model named
`macro_indicator_coverage_readiness`.

## Next Gap

Phase 56 should wire the matrix role cards into indicator detail rendering with
actual value context, freshness, release timing, source-risk explanation, and
why-not-evidence caveats.

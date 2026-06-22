# Phase QA1F Temporal Coverage Governance

QA1F closes QA1 with explicit historical gaps. It does not fill the remaining
archive gaps and it does not authorize historical performance backtests.

## Readiness Layers

QA1F separates three questions:

- Date-local readiness: whether a series, indicator, or phase score can be
  calculated for one `as_of` date with strict temporal evidence.
- Scenario readiness: whether every required date in a named scenario is
  strict-ready, or only a subset is ready.
- Use-case readiness: whether the data tier may be used for diagnostics,
  context ablation, calibration, validation, holdout, performance backtest, book
  benchmark, or dashboard output.

`strict_partial` dates and scenarios may support diagnostics and context
ablation, but they cannot support scenario-level performance claims,
calibration acceptance, validation, untouched holdout, or book benchmark
execution.

## QA1E.2 Archive Checkpoint

QA1E.2 is recorded as a blocked archive checkpoint. The MARTS release calendar
was parsed, OCR prerequisites were available, and controlled OCR was attempted.
Ambiguous OCR was rejected by design. That rejection is fail-closed behavior,
not a data success.

The unresolved register records `RSAFS`, `RRSFS`, `DGORDER`, `DGS10`, `ICSA`,
`MORTGAGE30US`, and `DCOILWTICO`. These gaps are not silently ignored. Archive
research should not automatically retry OCR in every phase; it requires an
explicit archive research command or a new official structured source.

## Strict Abstention

Strict scoring has three statuses:

- `scored`
- `abstained_missing_temporal_evidence`
- `failed_invalid_data`

Temporal abstention does not emit a zero score and does not reduce the formal
denominator to make a phase score appear complete. A partial strict score may
be displayed only as a diagnostic partial score. It cannot be sent to the
formal resolver.

## QA2 Boundary

QA2 is allowed only as structural context-ablation work. QA2 may use synthetic
fixtures or strict-complete dates. QA2 must not run performance backtests, tune
parameters, execute book benchmarks, generate portfolio results, or alter
formal scoring weights, resolver behavior, or dashboard defaults.

QA2 must also distinguish temporal eligibility from methodological and final
eligibility. A strict-complete scenario may be temporally eligible for a future
calibration study, but the current scenarios have all been repeatedly observed;
therefore they are not final validation, untouched holdout, or performance
backtest candidates.

QA2's data-only path is structural. It may prove that external context and
display-stage text do not alter data-only decisions, but it does not prove that
the data-only model is economically accurate.

The following remain blocked after QA1F:

- full formal historical coverage
- book benchmark temporal readiness
- real backtest temporal readiness
- Phase 9B1
- portfolio result generation

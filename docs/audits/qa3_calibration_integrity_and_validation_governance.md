# Phase QA3 Calibration Integrity and Validation Governance

QA3 closes precalibration governance for the data-only diagnostic path. It does
not calibrate the model, does not validate economic accuracy, and does not run a
historical performance backtest.

## Closure Status

QA3 establishes a complete parameter inventory, scenario exposure tracking,
production hard-coding checks, a frozen data-only research baseline, a
pre-registered future validation protocol, parameter-selection leakage
disclosure, data-only shadow diagnostics, and production context dependency
governance.

The current closure status is
`closed_precalibration_governance_ready`. This means the governance framework is
ready. It does not mean the data-only model has passed economic validation.

## Current Scenario Exposure

The five known scenarios are all development and diagnostics scenarios:

- `dotcom_bubble`
- `global_financial_crisis`
- `covid_recession`
- `euro_debt_slowdown`
- `late_cycle_2018`

All five have been used in diagnostics, acceptance review, sensitivity work,
documentation, or tests. They must not be described as unused holdout samples,
independent validation samples, or final performance evidence.

Temporal completeness and methodological validation are separate. A strict
complete date can support structural diagnostics, but it does not make a
scenario eligible for final validation claims.

## Production Context Dependency

QA2 showed that production context dependency is real and material. QA3 records
it as `phase_selection`.

Production default behavior is preserved. QA3 does not remove production
context, does not decouple the production wrapper, and does not change dashboard
production behavior. Context-derived output must be disclosed and must not be
labeled as data-only.

## Frozen Data-Only Baseline

QA3 freezes `data_only_baseline_v1` as a research comparison baseline. The
freeze records parameter manifest hash, source/spec file hashes, formal
indicator catalog hash, phase spec hashes, state-machine config hash, and
transition-control config hashes.

The freeze is not an accuracy claim. Current statuses remain:

- `economic_validation_status=not_validated`
- `independent_validation_status=not_started`
- `holdout_status=not_started`

Any future parameter or decision-source change must create a new model version.
Old holdout accumulation cannot be carried forward after such a change, and the
freeze hash must not be silently updated.

## Parameter Contamination

QA3 intentionally records parameters selected after observing existing scenario
results. These parameters are marked
`contaminated_for_independent_validation=true`.

This is expected. The purpose is to prevent hidden data snooping, not to make
the count disappear.

## Pre-Registered Future Validation

Prospective prequential holdout is registered from the first complete
observation period after the freeze: `2026-07`.

The protocol requires no parameter change after registration, parameter changes
reset holdout, no result peeking for model changes, at least one unseen
transition event, at least one unseen non-recession stress event, and strict
complete dates for formal comparison.

Current historical external validation is not available. Final untouched
holdout status is `not_started`.

## Shadow Diagnostics

The data-only shadow harness compares frozen data-only decisions with the
preserved production wrapper. It does not select parameters, compute portfolio
returns, compute performance metrics, write `data/backtests`, or write `public`.

Shadow outputs are diagnostics only. They are not economic validation.

## Remaining Blockers

The following remain false:

- `data_only_model_economically_validated`
- `independent_validation_ready`
- `final_holdout_ready`
- `real_backtest_progression_allowed`
- `phase_9b1_allowed`

The next allowed phase is QA4: Book Fidelity Remediation and Formal Model Scope
Freeze.

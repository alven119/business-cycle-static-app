# QA9 Prospective Shadow Observation Registry

QA9 adds forward-only registry infrastructure for future shadow diagnostics.
The registry is armed but not started. No real prospective record is written in
QA9, and the protocol is not a holdout.

## Runtime Wiring

The only implemented evaluator remains the three-calendar-month initial-claims
moving-average noise filter. QA9 distinguishes contract evaluability,
runtime executability, runtime output availability, directional evidence, and
candidate-selection eligibility.

The evaluator is registered and executable in the shadow runtime. The 2019
revised diagnostic abstains because the retrospective runner does not load the
same-data-mode ICSA history window for that real diagnostic. This is reported
as missing runtime history, not as phase evidence. The smoothing output remains
non-directional and cannot confirm a phase.

## Registry Contract

`prospective_shadow_observation_registry_v1` is append-only. Records use
canonical JSON hashing, deterministic key order, UTF-8 serialization, and a
previous-record hash chain. Existing records cannot be overwritten, replaced,
deleted, compacted, or rewritten.

The default future path is `data/prospective/shadow_observations/`, which is
ignored by git. QA9 CLIs use dry-run/no-write behavior and do not create a real
record.

## Forward-Only Gate

The protocol is registered and armed, but `protocol_started=false` and
`real_record_count=0`. The first eligible observation period remains
`2026-07`, with first eligible complete as-of `2026-08-31`.

The real CLI does not accept arbitrary historical `as_of` values for record
creation. Test clocks are allowed only in explicit test mode with temporary
registry paths. Backfill, pre-start writes, noncanonical as-of values, model or
protocol version mismatches, and candidate output without capability all fail
closed.

## Inspection Governance

QA9 allows metadata and operational-health inspection for synthetic records
only. Real evidence fields, candidate phases, model comparisons, threshold
changes, and performance comparisons remain prohibited. Result inspection count
is zero.

## Freeze

`prospective_shadow_monitoring_v1` freezes the monitoring infrastructure only.
It references `book_faithful_shadow_v2_alpha4` and the QA8 protocol. It does
not change evaluator rules, candidate-selection behavior, production behavior,
or any scheduler.

QA10 will address unresolved book-rule operationalization and candidate
capability expansion. Production v1 remains unchanged; real backtest
progression and Phase 9B1 remain blocked.

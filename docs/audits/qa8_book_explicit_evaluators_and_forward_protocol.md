# QA8 Book-Explicit Evaluators and Forward Protocol

QA8 implements only operationally complete book-explicit shadow evaluators and
registers a forward-only prospective diagnostic protocol for
`book_faithful_shadow_v2_alpha4`.

## Blocker Accounting

Primary status and secondary blocker counts have different semantics. Primary
statuses are mutually exclusive and sum to the 40 canonical roles. Secondary
blocker codes can overlap because a role can be raw-transform-only while also
missing a preregistered threshold. Therefore `threshold_not_preregistered=24`
does not need to equal the primary blocked-threshold count.

## Implemented Evaluators

QA8 implements one operationally complete explicit evaluator: the
three-month initial-claims moving-average noise filter. It is a smoothing rule,
not phase confirmation, not directional support, and not candidate-selection
evidence.

Incomplete explicit rules remain blocked:

- claims new-low three-quarter continuation needs a preregistered reference
  window before it can run
- claims and short-term-unemployment reversal need causal turning-point
  windows and confirmation semantics
- durable orders no-longer-worsening needs lookback and persistence semantics

The 2019 250000 initial-claims value remains a contextual example and is not a
universal threshold. Qualitative language such as significant jump remains
unquantified until a later preregistered evaluator exists.

## Diagnostics

Retrospective data runs may report individual rule evaluations, abstentions,
role readiness, and provenance. They do not emit a candidate phase, current
phase, decision status, expected-label comparison, accuracy metric, portfolio
metric, or production output.

The forward-only protocol is registered but not started. It reuses the QA3
first eligible observation period, begins only after the first complete period,
rejects pre-start and backdated candidate emission, and treats incomplete
evidence as abstention. Prospective diagnostics are not a holdout.

## Freeze

`book_faithful_shadow_v2_alpha4` has parent
`book_faithful_shadow_v2_alpha3`. The alpha3 freeze is preserved as the QA7
snapshot; QA8 records new evaluator, primitive, protocol, and gate hashes in
alpha4 instead of rewriting alpha3.

Production v1 remains unchanged. QA8 does not tune weights, add non-book
thresholds, change resolver or state-machine defaults, inspect prospective
results, register holdout, or change dashboard behavior. Real backtest
progression and Phase 9B1 remain blocked.

## QA9 Successor Boundary

QA9 keeps the alpha4 evaluator freeze intact when only registry infrastructure
is added. The prospective registry is armed but not started, writes no real
record, and keeps result inspection at zero. The initial-claims smoothing
evaluator is runtime-wired but remains non-directional and ineligible for
candidate selection.

## QA10 Successor Boundary

QA10 keeps the alpha4 evaluator rule unchanged while fixing the shadow runtime
history-window supply. The evaluator can produce a revised diagnostic smoothing
output, but the output is not a phase signal and does not enable candidate
selection.

# QA7 Evidence Rule and Candidate Selection Freeze

QA7 pre-registers evidence-rule provenance and synthetic candidate-selection
mechanics for `book_faithful_shadow_v2_alpha3`. It does not turn the shadow
model into a formal decision model and does not change production v1 behavior.

## Evaluability

QA7 audits why the 40 canonical roles remain non-evaluable:

- canonical roles: 40
- evaluable roles: 0
- raw-transform-only roles: 24
- blocked data roles: 14
- blocked rule roles: 2

This is not treated as a global bug. The ready roles are raw transforms without
pre-registered evidence thresholds, while blocked roles retain explicit source,
access, temporal, or transformation reasons.

## Book Statements

QA7 classifies book statements before turning any statement into a rule:

- the three-month initial-claims moving average is a book smoothing/noise-filter
  rule, not phase confirmation by itself
- the 250000 initial-claims value in the 2019 discussion is a contextual
  historical example, not a cross-cycle threshold
- directional turning-point language remains directional until a future
  evaluator preregisters lookback and persistence rules
- qualitative terms such as significant jump remain unresolved until defensible
  preregistration exists

Contaminated legacy thresholds are not allowed for independent-validation
candidate freeze.

## Candidate Mechanics

Synthetic candidate selection is enabled only for structural mechanics. It uses
phase-presence evidence, major-group states, aggregation eligibility,
provenance, and temporal completeness. It does not use numeric weights,
equal-weight averaging, role-count votes, arbitrary phase priority, transition
watch evidence, regime evidence, context priors, labels, dates, or portfolio
returns.

The synthetic fixture suite has 18 fixtures and validates selection, abstention,
ambiguity preservation, and forbidden-input rejection. Synthetic candidate
output is not economic validation.

## Real Data

Real-data candidate selection remains disabled. The required diagnostics for
2000, 2008, 2019 vintage, and 2019 revised data all abstain and emit no
candidate phase. They report provenance and coverage only.

## Freeze

`book_faithful_shadow_v2_alpha3` freezes the QA7 evidence-rule and
candidate-selection preregistration contracts. It freezes no numeric weights,
changes no production thresholds, registers no holdout, and allows no resolver,
state-machine, dashboard, or production integration.

QA8 is the next allowed phase for book-explicit evaluator implementation and
prospective shadow candidate diagnostics. Real backtest progression and Phase
9B1 remain blocked.

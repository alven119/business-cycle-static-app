# QA4 Book Fidelity Remediation and Formal Scope Freeze

QA4 defines the book-faithful formal scope without implementing a new decision
model. The current production v1 remains book-informed and keeps its known
context dependency; it is not represented as a fully faithful book model.

## Freeze And Holdout Semantics

`data_only_baseline_v1` remains a research baseline for structural comparison.
It is not economically validated, its book fidelity is incomplete, and its
prospective observations cannot be transferred automatically to a later
book-faithful candidate model.

`book_faithful_scope_v1` is scope-only. It defines required layers, book-core
roles, allowed modern extensions, prohibited substitutions, promotion gates,
and unresolved gaps. It does not freeze new decision parameters, weights, or
thresholds.

A later candidate model must use a new model version and a fresh prospective
registration after book-core decision-active implementation is complete.

## Formal Layers

QA4 separates five layers:

- `normal_cycle_phase_model`: future data-only four-phase model using book-core
  evidence and model-generated state history.
- `transition_evidence_layer`: watch/confirmation evidence only; it does not
  override formal phase or produce portfolio action.
- `exogenous_shock_overlay`: modern extension for non-normal shocks; it is not
  runtime-ready and cannot directly override phase.
- `secular_regime_layer`: productivity, inflation, and mixed regime scope; it
  does not enter the four-phase score and is not runtime-ready.
- `portfolio_policy_layer`: backtest-only benchmark and research scope; it may
  not feed back into phase decisions or output live allocation.

## Scope Findings

The scope contract expands every canonical requirement into one scope item:

- total scope items: 98
- book-core scope items: 77
- book-supporting scope items: 7
- project methodology / modern-methodology items: 14

Book fidelity remains incomplete. Missing and conflicting rows are preserved as
blockers rather than relabeled as ready.

Major unresolved areas:

- long-cycle regime evidence and asset-policy implications
- growth roles such as saving rate, income/consumption relation, payrolls, ADP,
  residential investment, core CPI, and core PCE
- boom roles such as confidence, government spending/revenue, inventory, and
  delinquency/default evidence
- production v1 context dependency versus the book requirement that objective
  data determine phase

## Indicator Matrix

The formal indicator scope matrix covers all 38 existing indicators and adds
missing book-core roles. Modern extensions such as yield curve, credit spreads,
financial conditions, policy rates, mortgage rates, and oil pressure remain
supporting or early-warning evidence. They do not replace missing book-core
roles.

QA4 proposes no new weights and no threshold changes.

## Portfolio Boundary

Book portfolio rules are scoped as benchmark/research contracts only. The
70/50/30 boom schedule is an allocation schedule for future benchmark research,
not a phase-duration rule. Generic bonds are not accepted as substitutes for
7+ year U.S. Treasury exposure, and monthly rebalancing is not treated as the
book annual benchmark.

## Closure

QA4 closes only the formal scope governance step:

- proposed v2 scope is defined but not implemented
- proposed v2 has no economic validation
- proposed v2 has no candidate holdout registration
- production behavior change count is zero
- real backtest progression remains blocked
- Phase 9B1 remains blocked

The next allowed phase is QA5: Book-Core Indicator Data Contracts and Shadow
Formal Model Implementation.

## QA5 Follow-Up Boundary

QA5 keeps the QA4 scope freeze intact while adding data contracts and a shadow
evidence implementation. It does not turn proposed v2 into a decision model.
The shadow model remains feature-gated, excludes production context, and emits
evidence profiles only.

Missing book-core roles remain blockers. Revised diagnostics are not
point-in-time validation evidence, and the shadow candidate has no registered
holdout. Production v1 remains unchanged.

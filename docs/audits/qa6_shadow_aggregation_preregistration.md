# QA6 Shadow Aggregation Rule Pre-Registration

QA6 pre-registers the shadow aggregation schema for
`book_faithful_shadow_v2_alpha2`. It does not select a candidate phase and does
not create a formal decision model.

## Freeze Lineage

QA6 preserves the original QA4 scope-freeze artifact and records the QA5
promotion-gate hash update as lineage. The QA5 update is scope-only:

- decision behavior changed: false
- production behavior changed: false
- holdout reset required: false

The lineage record prevents the QA4 freeze hash from being silently overwritten.

## Readiness Semantics

QA6 separates structural readiness from evidence evaluability:

- structurally mapped roles: 40
- data contracts defined: 40
- source verified roles: 24
- temporal data available roles: 24
- transformation available roles: 24
- evidence evaluable roles: 0
- aggregation eligible roles: 0

Structural routing does not imply usable directional evidence. Raw transforms
remain non-evaluable until future thresholds are pre-registered.

## Typed Evidence

QA6 introduces typed evidence families for recovery entry, growth stability,
boom presence, boom ending risk, recession confirmation, trough watch, recovery
watch, regime, and modern supporting evidence.

Typed evidence rules preserve these boundaries:

- boom-ending evidence is not boom phase support
- recession watch is not recession confirmation
- recovery watch is not formal recovery
- regime evidence does not enter the normal four-phase model
- modern supporting evidence does not satisfy book-core major groups
- raw transform output is not directional evidence

## Aggregation Schema

The aggregation schema is pre-registered with no numeric weights and no new
thresholds. It accepts typed role evidence, major-group mapping, role type,
temporal status, provenance, and contamination disclosure.

It excludes scenario ids, historical labels, acceptance windows, portfolio
returns, external context priors, display hints, production phase output, and
historical outcome labels.

## Structural Eligibility

Structural eligibility only answers whether a phase profile has the complete
typed evidence shape needed for a later candidate-selection rule. It does not
choose a phase. Real-data diagnostics currently have `evidence_evaluable_role_count=0`
and `aggregation_eligible_phase_count=0`, which is expected while thresholds
remain unregistered.

Synthetic fixtures validate routing, abstention, ambiguity preservation, and
context/display rejection. They do not test historical accuracy, transition
timing, or investment performance.

## Closure

QA6 keeps:

- `candidate_selection_enabled=false`
- `formal_candidate_phase_computed=false`
- `formal_decision_model_ready=false`
- `holdout_registered=false`
- `production_book_fidelity_ready=false`
- `book_alignment_claim_allowed=false`

QA7 is the next allowed phase for evidence-threshold pre-registration and
candidate-selection freeze. Real backtest progression and Phase 9B1 remain
blocked.

## QA7 Follow-Up

QA7 keeps the QA6 aggregation architecture intact and adds evidence-rule
provenance, book-statement operationalization, role evaluation contracts, and a
candidate-selection freeze. The QA7 synthetic fixtures can select a candidate
phase only to validate mechanics. Real data selection remains disabled and
emits no candidate phase.

Contextual historical examples, including the 2019 250000 initial-claims
discussion, are not universal thresholds. The three-month moving average is a
book smoothing/noise-filter rule. Qualitative significant-jump language remains
unresolved until a later phase preregisters a defensible evaluator.

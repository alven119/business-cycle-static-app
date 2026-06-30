---
phase: "51"
status: complete_when_closure_passes
---

# Phase 51：Declared Start Governance And Macro Gap Alternatives

Phase 51 follows Phase 50's transition surface data-risk work. It keeps the
declared current phase as `boom`, preserves the legal next transition
`boom -> recession`, and adds two research-only capabilities:

1. Governed confirmation package for the declared boom start date or start
   window.
2. Full current-gap inventory for recovery, growth, boom, and recession roles,
   with best available alternative source candidates, substitution degree,
   data-risk labels, and suggested remediation phases.

## Declared Boom Start Governance

The declared registry is not modified in this phase. The phase-start package
prepares three governed choices:

- exact user-declared start date
- governed user-declared start window
- keep unknown until more evidence is available

If no exact date is supplied, phase age remains `unknown_or_user_required`.
This avoids false precision and keeps phase age out of transition gating.

## Macro Gap Alternatives

Missing inputs are no longer treated as an opaque wall. Each missing or
observation-only role receives at least one reviewed candidate source. The
candidate is labeled by:

- source family
- credibility tier
- substitution degree
- automation feasibility
- data-risk level
- planned resolution phase

Official or near-direct official candidates can be wired in a later source
adapter phase. Licensed, private, or supporting-only candidates remain visible
as research options, but they are not silently promoted to book-core evidence.

## Planned Remediation Stages

- `Phase52_official_macro_source_adapter_wiring`: wire direct official and
  FRED/BEA/BLS/Census/Federal Reserve candidates.
- `Phase53_composite_transformation_and_rule_semantics`: implement same-as-of
  composites, derived turning-point transforms, and qualitative rule contracts.
- `Phase54_licensed_or_proxy_source_review`: review ADP, consumer confidence,
  and other non-official or licensed candidates with explicit user risk
  acceptance.
- `Phase55_current_dashboard_gap_reduction`: connect approved sources and
  transforms to the current research dashboard without production migration.

## Safety

This phase does not:

- write the declared registry
- infer the current phase from current data
- emit candidate/current phase
- add phase score, phase rank, or winner
- change legacy production v1 behavior
- write public, backtest, prospective, raw data, or cache outputs

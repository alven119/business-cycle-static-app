# Phase 52 Official Macro Source Adapter Wiring

Phase 52 wires the Phase 51 macro gap alternatives into official current
research source identifiers. It does not infer the current phase, compute a
phase score, rank phases, select a winner, or modify legacy production v1.

## Product Scope

- Declared current cycle state remains the source of current phase context.
- Legal next phase remains `recession` from the ordered cycle state machine.
- Phase 52 improves the transition and indicator surfaces by resolving
  semantic aliases such as `initial_jobless_claims` into official FRED/ALFRED
  series such as `ICSA`.
- Source risk, substitution degree, release metadata, and current-refresh
  availability are exposed for explanation.

## Source Wiring Notes

- Phase 52 covers 29 Phase 51 roles planned for official macro source adapter
  wiring.
- All 29 are wired to official current-refresh series.
- The wiring uses 22 unique official series.
- Direct DOL release adapters for initial claims remain a future refinement;
  current research uses FRED/ALFRED official redistribution with explicit
  deferral labels.
- `real_personal_consumption_expenditures` is corrected from the Phase 51
  candidate `PCECC96` to the repository's existing official `PCEC96` identity.

## Product Capability Reporting

Phase 52 adds a governed product capability progress view. Percentages are
orientation estimates for project planning. They are not production readiness,
economic validation, investment advice, or a formal current phase decision.

The affected capabilities are:

- C1 business-cycle phase assessment
- C2 transition risk detection
- C3 explainability and attribution
- C6 safe output governance
- F1 temporal integrity and abstention

## Deferred Work

- Phase 53 should address composite transformation and rule semantics.
- Phase 54 should address licensed, manual, and proxy source risk handling.
- The declared boom start date still requires governed user confirmation.
- Dashboard indicator detail can later surface the resolved official series
  more directly.

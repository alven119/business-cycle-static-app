---
phase_id: "45"
status: declared_registry_and_legal_order_ready
created_at: "2026-06-29"
declared_registry: specs/common/declared_cycle_state_registry.yaml
ordered_state_machine: specs/common/ordered_cycle_state_machine.yaml
---

# Phase 45 Declared Cycle State And Ordered Legal Transition Plan

Phase 45 implements the first doctrine-aligned runtime core after the product
doctrine reset. It creates a declared current cycle-state registry and an
ordered legal transition contract.

This phase intentionally does not build a standalone current phase classifier,
phase score selector, phase ranking surface, phase winner, boom transition
monitor, portfolio policy engine, or replay/backtest vertical slice.

## Declared State

The initial declared state is:

- `declared_current_phase: boom`
- `declaration_source: user_declared`
- `declaration_status: active_research_default`
- `formal_current_phase_inference_enabled: false`

The declared phase start date is not inferred in this phase. The registry keeps
`declared_phase_start_date: null` and reports
`phase_age_status: unknown_or_user_required` to avoid false precision.

## Ordered Legal Transition

The legal cycle order remains:

```text
recession -> recovery -> growth -> boom -> recession
```

Therefore the legal next phase for the declared boom state is recession, and
the legal previous phase is growth. Self-transitions, skips, and reverse
transitions are rejected unless a future explicit override contract is opened.

## View Model Boundary

The view model is dashboard or artifact ready, but it labels the value as a
declared state. It must not be treated as inferred current phase output and it
must not emit candidate phase, selected phase, phase rank, phase score, or
portfolio action fields.

## Deferred Gaps

- User-declared phase start date is required for precise phase age.
- Boom continuation and boom-ending/recession monitor are deferred to Phase46.
- Portfolio policy research engine is deferred to Phase47.
- Historical replay/backtest vertical slice is deferred to Phase48.

---
phase_id: "49"
status: declared_boom_transition_dashboard_surface_ready_no_phase_selection
surface_contract: specs/common/boom_transition_dashboard_surface.yaml
---

# Phase 49 Declared Boom Transition Dashboard Surface

Phase 49 renders the Phase 48 boom-to-recession transition monitor into a
research-only dashboard surface. It keeps the same product shape introduced by
Phase 45-48:

- declared current cycle state
- ordered legal transition
- phase-specific transition monitor
- evidence explanation
- explicit missing-data abstention

This phase intentionally does not infer the current phase from current data. It
does not emit a selected phase, phase winner, phase rank, phase score,
candidate phase, portfolio output, public output, or action field.

## Dashboard Surface

The surface is designed to preserve the useful indicator-level presentation
style already present in the current research dashboard. Each priority role is
displayed with:

- role meaning
- source series
- lane mapping
- current status
- blocker or abstention reason
- book-logic summary
- watch versus confirmation boundary

## Declared State Context

The declared state remains:

- `declared_current_phase: boom`
- `legal_next_phase: recession`
- `declared_phase_start_date: null`
- `phase_age_status: unknown_or_user_required`

The surface labels this as declared state, not inferred current phase output.

## Preserved Boundaries

- Watch evidence remains separate from confirmation evidence.
- Missing evidence is displayed as explicit abstention, never neutral.
- Recession confirmation is not derived from watch-only evidence.
- Production v1 and GitHub Pages workflows remain unchanged.
- Preview output is only allowed under `/tmp` or test `tmp_path`.

## Deferred Gaps

- A governed or user-confirmed phase start date is still required for precise
  phase age.
- Live/current source refresh remains opt-in and outside default tests.
- The production Pages dashboard remains a legacy v1 boundary until an
  explicit migration phase opens that gate.

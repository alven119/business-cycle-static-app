---
phase_id: "46"
status: boom_transition_monitor_ready_no_phase_selection
created_at: "2026-06-29"
monitor_contract: specs/common/boom_transition_monitor.yaml
evidence_contract: specs/common/boom_transition_evidence_contract.yaml
---

# Phase 46 Boom Transition Monitor Plan

Phase 46 implements the first phase-specific transition monitor on top of the
Phase 45 declared current cycle-state registry.

The declared state remains:

- `declared_current_phase: boom`
- `legal_next_phase: recession`
- `declared_phase_start_date: null`
- `phase_age_status: unknown_or_user_required`

This phase does not infer the current phase from current data. It does not
emit selected phase, phase winner, phase rank, phase score, candidate phase,
portfolio output, or any action field.

## Monitor Lanes

The monitor exposes four lanes:

- `boom_continuation`
- `boom_ending_watch`
- `recession_watch`
- `recession_confirmation`

All lane inputs come from existing book phase-evidence rule rows and current
evidence readiness rows. When current fixture or cache inputs are missing, the
lane remains structurally ready but reports abstention and blockers rather than
forcing a signal.

Watch lanes remain separate from confirmation. Boom-ending watch cannot become
recession confirmation, and recession watch cannot change the declared state.

## Phase Age Context

Because the registry does not yet contain a declared phase start date, Phase 46
reports:

- `phase_age_context_available=false`
- `phase_age_status=unknown_or_user_required`
- `phase_age_used_as_transition_gate=false`

No duration, including book contextual timing language, is used as a transition
threshold in this phase.

## Future Capability: phase_start_research_assistant

Phase 46 adds the future capability `phase_start_research_assistant` to the
cleanup roadmap.

Purpose:

- Research candidate start dates for a declared cycle phase.
- Produce evidence-backed candidate start-date artifacts.
- Preserve source, rule, and timing provenance.
- Help the dashboard explain phase-age context.

Boundaries:

- It must not automatically modify the declared phase registry.
- 不得自動改 declared phase registry.
- It must not use phase age alone to decide a transition.
- It must not emit candidate/current phase.
- A user or governed declaration is required before a start date is written to
  the declared registry.

Recommended timing: implement `phase_start_research_assistant` before Phase47/48
product surfaces that depend on declared-state timeline context. The reason is
that portfolio policy research and historical replay will be easier to explain
safely if phase-age context has already moved from `unknown_or_user_required`
to a provenance-backed candidate start-date review artifact. This does not
block the Phase46 boom transition monitor, because Phase46 explicitly abstains
from phase-age gating.

## Deferred Gaps

- `phase_start_research_assistant` is planned but not implemented in Phase 46.
- Portfolio policy research engine remains deferred.
- Historical replay/backtest vertical slice remains deferred.
- Production dashboard behavior remains unchanged.

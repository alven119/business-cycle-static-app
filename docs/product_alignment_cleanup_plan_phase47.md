---
phase_id: "47"
status: phase_start_research_assistant_ready_registry_unchanged
created_at: "2026-06-29"
assistant_contract: specs/common/phase_start_research_assistant.yaml
hypothesis_contract: specs/common/phase_start_research_hypotheses.yaml
phase48_wiring_plan: docs/phase48_boom_monitor_evidence_wiring_plan.md
---

# Phase 47 Phase Start Research Assistant

Phase 47 implements a small research assistant for the declared boom phase
start context. It is not a current phase classifier and it does not update the
declared registry.

The declared state remains:

- `declared_current_phase: boom`
- `legal_next_phase: recession`
- `declared_phase_start_date: null`
- `phase_age_status: unknown_or_user_required`

## Hypotheses

The assistant always emits at least two hypotheses.

1. `user_prior_hypothesis`

   This records the user's rough prior: boom may have started before mid-2025,
   and April-May 2026 may be a recovery-to-boom transition revision window.
   This is user-provided context, not a system conclusion.

2. `evidence_based_research_hypothesis`

   This reviews existing macro evidence contracts, current evidence readiness,
   source provenance, and book traceability. When current evidence is missing,
   stale, observation-only, or rule-blocked, the hypothesis reports
   `insufficient_evidence` and does not provide a date.

## Boundaries

- The assistant must not modify `specs/common/declared_cycle_state_registry.yaml`.
- The assistant must not automatically declare a recovery-to-boom transition.
- The assistant must not use phase age as a transition gate.
- The assistant must not emit candidate phase, current phase, phase score,
  phase rank, phase winner, portfolio output, or trade action.
- User confirmation or a governed declaration is required before any
  `declared_phase_start_date` can be written in a later phase.

## Phase 48 Preparation

Phase 47 also creates `docs/phase48_boom_monitor_evidence_wiring_plan.md`.
The plan is product-progress work, not governance-only scaffold: it identifies
which existing roles should be wired first into the boom continuation,
boom-ending watch, recession watch, and recession confirmation lanes.

## Deferred Gaps

- The declared registry still lacks a confirmed start date.
- Evidence-based start-date research currently abstains when current evidence
  is missing or only metadata-level.
- Phase 48 should wire the highest-product-value monitor inputs before adding
  broader dashboard surfaces.
- Production v1 remains unchanged.

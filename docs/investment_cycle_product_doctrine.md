---
doctrine_version: "1.0"
status: active
approved_at: "2026-06-27"
contract_path: specs/common/investment_cycle_product_doctrine.yaml
---

# Investment Cycle Product Doctrine

This doctrine amends, and does not replace, `docs/project_north_star.md`. Its
purpose is to keep future work anchored to the user's actual long-term product:
a durable business-cycle investing assistant based on the logic of
`docs/景氣循環投資.pdf`, official data, explainable evidence, safe portfolio
policy research, historical replay, and strict governance.

The product is not a short-term research toy and not a standalone four-way
classifier. It should help the user understand where the economy is in an
ordered cycle, whether evidence is building for the next legal transition, what
data is missing or contradictory, and how book-based portfolio policy templates
would have behaved in comparable historical periods.

The local book PDF is a source for semantic review only. It must not be
committed, copied into outputs, or used as runtime data. Repository contracts
should store only short statement identifiers, page references, and operational
rule semantics.

## Primary User Goal

The mature system should support long-term, even lifetime, cycle-investing
research. It should:

1. Track the current declared business-cycle state.
2. Follow the book's ordered cycle logic to monitor whether the economy is
   moving from the current phase toward the next legal phase.
3. Explain evidence before, during, and after transitions, including strength,
   reliability, missing inputs, source lineage, and caveats.
4. Provide book-based portfolio policy research templates, including stock/cash,
   stock/long Treasury, passive all-stock baseline, and boom de-risking
   templates such as 70/50/30.
5. Replay and backtest historical episodes such as Dotcom, GFC, COVID, Euro
   debt, 2018 late cycle, and custom periods.
6. Educate the user through the dashboard: current declared phase, declared
   phase age, indicators used, why they are used, source provenance,
   transformations, rules, limitations, and caveats.
7. Preserve safety governance: no automatic trade instruction, no promised
   return, no hidden data gaps, and no confusion between research and
   production.

## Core Product Model

The product shape is:

```text
current_declared_cycle_phase
+ ordered cycle state machine
+ phase-specific transition monitor
+ evidence explanation
+ portfolio policy research template
+ historical replay/backtest
```

The cycle order is:

```text
recession -> recovery -> growth -> boom -> recession
```

The system must not treat every period as a blank four-way vote among
recession, recovery, growth, and boom. If the user or a governed model declares
the current phase, the system should monitor that state and its legal next
transition. Evidence from other phases can be shown as explanation or warning,
but it must not directly rewrite the current phase.

The current user premise is that the cycle can initially be treated as boom.
Therefore the near-term product should emphasize boom continuation, boom ending
watch, recession watch, and recession confirmation. The architecture must still
support the full cycle after that:

- boom -> recession
- recession -> recovery
- recovery -> growth
- growth -> boom

## Prohibited Product Shapes

The mature product should not be shaped around:

- standalone current phase classifier
- phase rank, phase winner, or numeric phase score as the main answer
- role-count voting phase selector
- isolated candidate phase classifier
- current evidence profile used as a current phase picker
- historical validation as only a static-label accuracy contest
- governance scaffolding that does not support the product journey
- dashboard wording that implies a formal current decision before migration
- portfolio output that reads like a current allocation recommendation

Candidate phase, if retained, must mean a legal state-machine transition
candidate, not the winner of an isolated classifier.

## Required Product Shapes

The mature product must preserve or build:

- official data refresh from FRED, ALFRED, BEA, BLS, DOL, Census, EIA, and
  other official or licensed sources
- release-lag and frequency-aware freshness semantics
- strict separation of revised diagnostics and point-in-time evidence
- evidence with source, transformation, rule, major group, phase or transition
  role, and provenance
- ordered cycle state machine
- declared current phase registry
- legal next transition monitor
- phase age and declared start tracking
- phase-specific transition monitor:
  - boom: continuation, ending watch, recession confirmation
  - recession: depth, trough watch, recovery confirmation
  - recovery: recovery confirmation, growth transition readiness
  - growth: healthy expansion, overheating or boom transition readiness
- portfolio policy research templates
- historical replay and backtest
- dashboard education layer

## Portfolio Policy Research

Portfolio policy work is a research template layer until an explicit future
gate authorizes stronger usage. It may show book template weights and scenario
replay assumptions, but it must not emit trade actions or current allocation
recommendations.

Required policy templates include:

- passive all-stock baseline
- stock/cash initial
- stock/cash advanced
- stock/long Treasury initial
- stock/long Treasury advanced
- boom 70/50/30 de-risking template
- recession and recovery re-risking research templates

Every policy view must preserve caveats: research-only, backtest-only when
appropriate, no future performance guarantee, and not investment advice.

## Historical Replay And Backtest

Historical replay and backtest are product-critical, but they must be more than
a label comparison exercise. They should answer:

- Did the system detect the transition?
- Was detection early, late, or correctly abstained?
- What evidence was available at the time?
- What did revised diagnostics change?
- How would book policy templates have behaved?
- What were drawdowns, turnover, false-signal costs, and missed-recovery costs?

Required scenarios:

- Dotcom cycle
- Global Financial Crisis
- COVID recession
- Euro debt slowdown
- 2018 late cycle
- custom user periods

Required modes:

- revised diagnostic replay
- strict point-in-time replay

Required outputs:

- transition timing
- evidence attribution
- portfolio policy replay
- cash-flow-aware returns
- drawdown metrics
- false signal cost
- missed recovery cost

## Dashboard Education Layer

The dashboard should answer:

- What is the current declared phase?
- When did the declared phase start?
- How long has it persisted?
- What is the next legal phase?
- Which evidence supports continuation?
- Which evidence supports transition?
- Which evidence is missing, stale, or unresolved?
- Why are these indicators used?
- How does each indicator map to the book logic?
- Which portfolio research template is relevant?
- Which historical scenarios are similar enough for replay or backtest?

The dashboard must label research-only surfaces clearly and must not imply
formal production decisions when the migration gate is closed.

## Cleanup Policy

Phase 43A is an audit and doctrine reset. It does not delete code. Deviation
candidates should be classified as:

- keep
- keep but rename or reframe
- consolidate
- quarantine
- deprecate
- remove candidate
- convert to state-machine transition monitor
- convert to backtest or replay support

Cleanup must proceed in later phases. Do not remove production v1 behavior or
legacy tests until a specific cleanup phase audits blast radius, replacement
coverage, and migration gates.

## Future Phase Policy

Every future phase must report:

- product_doctrine_alignment_status
- cycle_state_machine_alignment_status
- standalone_classifier_added_count
- phase_rank_or_score_added_count
- legal_transition_semantics_preserved
- portfolio_policy_research_alignment
- historical_replay_backtest_alignment
- deviation_cleanup_needed_count
- production_behavior_change_count
- semantic_drift_count

Every future phase must answer:

1. Does this move the system closer to long-term cycle investing?
2. Does this preserve ordered cycle state-machine semantics?
3. Does this help transition detection, portfolio policy research,
   replay/backtest, or dashboard education?
4. Did it add standalone classifier, ranking, or scoring behavior that should
   not exist as a mature product shape?
5. Did it add governance-only scaffold without product progress?

Phases that only add governance scaffolding are not sufficient unless they are
explicitly framed as cleanup, audit, or safety-blocker phases.

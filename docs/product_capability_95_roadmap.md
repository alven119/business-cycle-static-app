# Product Capability 95 Percent Roadmap

Phase 55 established the macro indicator coverage readiness matrix. This
roadmap records the next product-oriented phases needed to raise the three
highest-priority capabilities to 95 percent of formal production use:

- 景氣階段判讀能力
- 轉折風險偵測能力
- 解釋能力

The plan is bounded to nine phases, leaving one contingency phase inside the
user-requested limit of ten phases. Percentages remain governed orientation
numbers, not economic validation, portfolio advice, or a formal current phase
decision.

## Scope

This roadmap advances the dashboard and runtime surfaces that answer:

1. What is the declared current cycle phase?
2. What is the legal next phase?
3. Which indicators support continuation, transition watch, confirmation, or
   abstention?
4. Which inputs are missing, stale, proxy-only, or license/user-supplied?
5. Why is the system abstaining instead of over-claiming?

It does not create a standalone current phase classifier, phase score, phase
rank, phase winner, role-count vote, current allocation recommendation, or
trade action.

## Target Trajectory

| Capability | Phase 55 Baseline | Target By Phase 64 |
|---|---:|---:|
| 景氣階段判讀能力 | 66% | 95% |
| 轉折風險偵測能力 | 71% | 95% |
| 解釋能力 | 75% | 95% |

## Planned Phases

| Phase | Main Outcome | C1 | C2 | C3 |
|---|---|---:|---:|---:|
| 56 | Indicator detail source-risk and value rendering | 70 | 74 | 80 |
| 57 | Boom-to-recession transition surface completion | 74 | 79 | 83 |
| 58 | Full ordered-cycle transition lane templates | 78 | 83 | 86 |
| 59 | Governed declared boom start and phase-age confirmation | 82 | 86 | 88 |
| 60 | Evidence freshness, release timing, and current value continuity | 86 | 89 | 90 |
| 61 | Major-group evidence profile and readiness explanation | 89 | 91 | 92 |
| 62 | Indicator-to-dashboard explanation drill-down | 91 | 93 | 94 |
| 63 | Research-only transition timing replay preview | 93 | 94 | 95 |
| 64 | Production-use readiness rehearsal for declared-state dashboard surfaces | 95 | 95 | 95 |

## Phase Details

### Phase 56

Wire Phase 55 role cards into indicator detail rendering. Each indicator should
show source tier, data risk, current value context when available, freshness,
release timing, transformation, and why-not-evidence caveats.

### Phase 57

Complete the boom-to-recession transition surface. It should distinguish boom
continuation, boom-ending watch, recession watch, recession confirmation,
contradictory evidence, and abstention without changing the declared phase.

### Phase 58

Generalize transition lanes across the full legal order:

`recession -> recovery -> growth -> boom -> recession`

Each lane must preserve watch vs confirmation and supporting-only vs book-core
roles.

### Phase 59

Implement governed declared boom start confirmation. If the start date is
user-declared, the dashboard must show provenance and phase-age caveats instead
of false precision.

### Phase 60

Improve current value continuity, freshness semantics, release timing, and
stale/missing explanations for the indicator and transition surfaces.

### Phase 61

Build major-group evidence profiles that summarize supportive, contradictory,
mixed, incomplete, unavailable, raw-observation-only, and rule-unresolved
states. These profiles are explanation inputs, not selectors.

### Phase 62

Add explanation drill-down from dashboard cards to role, source, transformation,
rule, provenance, data mode, and abstention reason.

### Phase 63

Add a research-only transition timing replay preview. It should show how
transition evidence evolved in historical periods without computing investment
returns or turning static label accuracy into the product answer.

### Phase 64

Create a production-use readiness rehearsal for the declared-state dashboard
surfaces. This phase should verify wording, safety labels, forbidden fields,
source-risk display, accessibility, mobile readability, and doctrine alignment
before any explicit production migration gate.

## Guardrails

- No standalone current phase classifier.
- No phase rank, winner, or arbitrary phase score as the product answer.
- No candidate/current phase emission before an explicit migration gate.
- No supporting proxy promoted to book-core evidence.
- No portfolio action, target weight, buy/sell signal, or investment advice.
- No historical result tuning.
- No public output unless the relevant phase explicitly opens that gate.
- No raw data, cache, book PDF, or secret commit.

## Deferred Beyond This Roadmap

These areas remain outside the 95 percent target for the three prioritized
capabilities:

- full portfolio policy replay
- cash-flow-aware backtest
- economic performance metrics
- prospective validation completion
- production migration of portfolio or trade-related outputs

## Post-Target Enablers

After Phase 64, the project keeps adding small enablers that protect the
95%-plus product surfaces without reopening the original nine-phase target
roadmap:

- Phase 65 reduced the default suite to product-core tests and quarantined
  legacy/archive regression coverage.
- Phase 66 split archive regression into nightly shards.
- Phase 67 added transition timing replay preview and verified GitHub Actions
  test efficiency.
- Phase 68 adds governed phase-start intake continuity, explicit numeric cache
  overlay support, and a dynamic test-suite index so new tests first check for
  related existing coverage.
- Phase 69 wires the declared boom start confirmation package into the
  dashboard, showing rough start-window context, evidence abstention, data
  risk, phase-age caveats, and the next governed action without writing the
  declared registry or selecting a phase.

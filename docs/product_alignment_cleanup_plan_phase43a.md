---
phase_id: "43A"
status: audit_only
created_at: "2026-06-27"
doctrine_contract: specs/common/investment_cycle_product_doctrine.yaml
---

# Phase 43A Product Alignment Cleanup Plan

Phase 43A is a product doctrine reset and alignment audit. It does not delete
code, modify runtime behavior, add dashboard features, run live refresh, run
backtests, add a freeze, or execute full pytest. The goal is to record where
the repository supports the user's long-term cycle-investing product, where it
may drift toward a static classifier or governance-only sprawl, and what safe
cleanup sequence should follow.

The audit reviewed `docs`, `specs`, `src`, `scripts`, `tests`, `.github`,
`AGENTS.md`, `docs/agent_workflow.md`, `docs/prompt_templates.md`,
`docs/project_north_star.md`, `specs/common/project_north_star_contract.yaml`,
and the local book source `docs/景氣循環投資.pdf`. The PDF is an untracked local
review source and must remain uncommitted.

## Audit Summary

| Field | Value |
|---|---:|
| rg-file universe reviewed | 1824 |
| phase-score/current-phase related file hits | 115 |
| candidate/selected/winning phase related file hits | 620 |
| phase-specific audit/freeze/closure file hits | 435 |
| portfolio/backtest/replay related file hits | 156 |
| state-machine/transition related file hits | 151 |
| standalone_current_phase_classifier_count | 5 |
| phase_rank_or_score_output_count | 4 |
| isolated_candidate_phase_classifier_count | 1 |
| governance_only_scaffold_candidate_count | 18 |
| remove_candidate_count | 2 |
| consolidate_candidate_count | 6 |
| convert_to_state_machine_candidate_count | 5 |
| convert_to_backtest_replay_candidate_count | 4 |
| required_product_gap_count | 16 |
| code_cleanup_required | true |

Counts are audit categories, not a deletion list. Most hits are safe guards,
contracts, or disabled diagnostics. The cleanup action is to classify and
sequence work, not to remove files now.

## Current Implemented Capability Inventory

| Capability | Representative artifacts | Doctrine mapping | Product progress | Scaffold risk |
|---|---|---|---|---|
| Official data refresh and cache | `src/business_cycle/current/current_data_refresh.py`, FRED and archive providers | official data refresh | Directly useful | Low |
| Frequency-aware freshness | `src/business_cycle/current/current_freshness_semantics.py` | release-lag and freshness | Directly useful | Low |
| Evidence evaluators and major groups | `src/business_cycle/shadow_model/`, book-core specs | evidence explanation | Directly useful if reframed by transition state | Medium |
| Current evidence dashboard profile | Phase42 current snapshot/dashboard files | dashboard education | Useful as explanation only | Medium if treated as classifier |
| Transition watch separation | transition badge specs, recession/boom/recovery watch modules | transition monitor | Directly useful | Low |
| Production v1 phase scoring | `src/business_cycle/phases/scoring.py`, `batch_scoring.py`, `state_machine.py` | legacy current decision path | Useful as legacy baseline | High if treated as mature doctrine |
| Research validation artifacts | Phase20-36 validation modules and docs | historical replay/backtest support | Partly useful | Medium if accuracy-only |
| Portfolio policy contracts | `specs/portfolio/`, `docs/portfolio_policy_research_plan.md` | portfolio policy research | Directly useful but not complete | Low |
| Safety scans and output validators | `scripts/run_ci_safety_scans.py`, validator contracts | safe output governance | Directly useful | Low |
| Phase-specific freezes/closures | `specs/audits/`, `src/business_cycle/audits/`, show scripts | model governance | Useful lineage but sprawling | High consolidation candidate |

## Top Deviation Candidates

| Rank | File or module | Current behavior | Why it may deviate | Risk if kept as-is | Recommended action | Cleanup phase |
|---:|---|---|---|---|---|---|
| 1 | `AGENTS.md` | Lists `current phase` and `phase scores` as core outputs | Reads like static scoring product | Future agents may optimize phase scores instead of transitions | keep but rename/reframe | Phase 43B |
| 2 | `docs/project_north_star.md` | Describes current/candidate phase outputs broadly | Needs stateful amendment | Could preserve isolated classifier interpretation | keep but amend | Phase 43A done |
| 3 | `src/business_cycle/phases/scoring.py` | Computes phase scores from indicators | Static score can become product center | Encourages phase winner/ranking behavior | convert to state-machine transition monitor input | Phase 43B/44 |
| 4 | `src/business_cycle/phases/batch_scoring.py` | Writes `phase_scores.json` | Output can look like phase competition | Dashboard/user may interpret highest score as phase | quarantine then convert | Phase 43B |
| 5 | `src/business_cycle/phases/state_machine.py` | Uses scores, thresholds, ranked scores, candidate id | Has state-machine shape but still score-driven | Legal transition semantics can be diluted by numeric gates | keep but rename/reframe | Phase 44 |
| 6 | `src/business_cycle/phases/data_only_resolver.py` | Resolves current phase from model scores | Looks like standalone current phase resolver | Future production migration could skip doctrine | quarantine as legacy v1 | Phase 43B |
| 7 | `scripts/run_cycle_pipeline.py` and `scripts/build_cycle_snapshot.py` | Build phase score and current decision outputs | Production path still emits v1 phase artifacts | Dashboard may imply formal current decision | keep as legacy until migration | Phase 43B/44 |
| 8 | `.github/workflows/pages.yml` | Builds live public dashboard from production v1 pipeline | Deployment remains old product shape | Public output can outrun doctrine if changed casually | keep, add future migration gate | Phase 43B |
| 9 | Historical accuracy metric modules | Compute research-only label metrics | Static-label accuracy is not enough | Validation may optimize labels, not transition timing/policy value | convert to replay/backtest support | Phase 47 |
| 10 | Phase-specific closure/freeze/audit stack | Many phase-bound scripts and specs | Governance can grow without product movement | Maintenance cost and false sense of progress | consolidate | Phase 43B |

## Items Not Needed As Mature Product Core

- Standalone current phase detection as a four-way classifier.
- Phase rank, phase winner, or numeric phase score as the primary answer.
- Current evidence profile used as a classifier.
- Candidate phase unrelated to legal state transition.
- Historical validation that only asks whether a static label matched.
- Tests that enforce standalone four-phase classification as the mature path.
- Phase-specific closure scaffolding that no longer serves product progress.
- Duplicate scripts, audits, and freezes that can be consolidated.
- Dashboard views that imply current phase decision before migration.
- Unsupported production or investment wording.

## Items To Keep Or Reuse

- Live refresh, cache, fixture mode, and source lineage.
- Frequency-aware freshness semantics.
- Book-core evidence evaluators and major-group evidence, reframed as
  transition-monitor inputs.
- Transition watch and confirmation separation.
- Research dashboard, especially education and provenance surfaces.
- Historical replay artifacts, label comparisons, and coverage metrics when
  used for replay/backtest diagnostics rather than final product claims.
- Portfolio policy contracts and safety validators.
- CI safety scans, secret scans, generated-output scans, and point-in-time
  contracts.

## Missing Product-Critical Capabilities

1. Ordered state machine aligned to the doctrine.
2. Current declared phase registry.
3. Legal transition monitor.
4. Phase age and declared start tracking.
5. Boom -> recession monitor.
6. Recession -> recovery monitor.
7. Recovery -> growth monitor.
8. Growth -> boom monitor.
9. Portfolio policy template engine.
10. Policy dashboard.
11. Historical replay UI.
12. Strict point-in-time backtest.
13. Cash-flow-aware portfolio engine.
14. Backtest result dashboard.
15. Production migration with rollback.
16. Long-term automation and deployment operations.

## Safe Cleanup Sequence

### Phase 43B: Code/Test Cleanup And Doctrine Enforcement

- Add lightweight doctrine checks where appropriate.
- Rename/reframe legacy references from standalone phase scores toward legacy
  production v1 or transition-monitor inputs.
- Quarantine legacy current phase score outputs from shadow/current research
  docs.
- Consolidate duplicate closure/audit show scripts where safe.
- Do not delete production v1 behavior.

### Phase 44: Ordered State Machine

- Add declared current phase registry.
- Represent legal transitions explicitly.
- Track declared phase start and phase age.
- Ensure phase changes require legal transition evidence, confirmation, and
  lineage.
- Preserve candidate/current output gates until an explicit migration phase.

### Phase 45: Boom Transition Monitor

- Because the current user premise is boom, prioritize boom continuation,
  boom-ending watch, recession watch, and recession confirmation.
- Use Phase42 current evidence and existing boom/recession evidence as inputs.
- Do not emit portfolio action.

### Phase 46: Portfolio Policy Template Engine

- Convert existing portfolio contracts into a research template engine.
- Support passive all-stock, stock/cash, stock/long Treasury, and boom 70/50/30
  templates.
- Keep all outputs research-only with caveats.

### Phase 47: Historical Replay And Backtest Vertical Slice

- Build a scenario replay UI and backtest slice around transition timing, policy
  replay, cash-flow-aware returns, drawdowns, false-signal cost, and
  missed-recovery cost.
- Use label metrics as supporting diagnostics, not the product center.

### Phase 48+

- Extend remaining transition monitors.
- Expand dashboard education layers.
- Plan controlled production migration only after doctrine-aligned validation.

## Phase 43A Non-Actions

- No runtime logic changed.
- No dashboard feature added.
- No code cleanup executed.
- No tests deleted.
- No full pytest run.
- No live refresh run.
- No backtest run.
- No freeze created.
- No production behavior changed.

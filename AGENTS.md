# AGENTS.md

## Project identity

This repository implements a Python-first static web app for business-cycle investing.

The mature product is an ordered-cycle investing assistant, not a standalone
four-way classifier. It tracks a declared cycle state, monitors legal
transitions, explains evidence, supports portfolio policy research templates,
and enables historical replay/backtest research.

The legal business-cycle order is:

1. recession
2. recovery
3. growth
4. boom

The output is a static dashboard deployable to GitHub Pages and readable on iPhone Safari.

## Core principle

Do not classify the economic phase from a single latest data point.

Do not build future work around a standalone current phase classifier, phase
winner, phase ranking, role-count vote, or arbitrary numeric phase score.
Evidence should support the declared state, legal next transition monitoring,
abstention, or research replay/backtest.

Most indicators must be interpreted through trend, momentum, reversal,
percentile, persistence, confidence rules, release timing, and source
provenance.

The project must produce explainable outputs:

- declared current phase and declared phase age
- legal next phase
- transition watch and confirmation evidence
- transition radar
- indicator-level reasoning
- data freshness
- confidence
- missing-data impact

## Architecture preference

Prefer:

- Python-first implementation
- deterministic evidence computations
- YAML specs for indicator, transition, and legacy phase definitions
- CSV/Parquet for raw and normalized data
- JSON for public static-site output
- Jinja2 or simple static HTML rendering
- pytest tests for evidence behavior and legacy scoring compatibility

Avoid:

- hidden LLM-based phase decisions
- opaque scoring
- hardcoded latest-value threshold-only classification
- database dependency in the MVP
- frontend API keys
- private investment data in public GitHub Pages output

## Data policy

FRED API key must never be committed.

Use environment variables locally and GitHub Actions secrets in CI.

Public files under public/ must not include secrets, personal holdings, personal notes, or raw copyrighted book content.

## Indicator Evidence And Transition Contracts

Every indicator evidence, transition-readiness, or legacy scoring implementation
must define:

- input series
- frequency
- direction
- transformation
- trend window
- confirmation window
- evidence state or legacy diagnostic output range
- confidence impact
- stale_after_days
- fallback behavior
- human-readable explanation
- source provenance
- relation to declared phase, legal next transition, or portfolio research template
- explicit prohibited outputs when the artifact is research-only or legacy-only

Legacy production v1 scoring, resolver, pipeline, and GitHub Pages deployment
remain historical compatibility baselines until an explicit migration phase.
They must not be presented as the mature product direction. Future work must
not convert legacy phase scores, ranks, winners, or selected outputs into the
product answer without a doctrine-aligned migration gate.

## Testing expectations

When changing scoring logic, add or update tests.

At minimum run:

```bash
pytest
```

# Agent Operating Contract

## Mission

This repository builds a deterministic, auditable business-cycle diagnostics and strategy-research system. Agent changes must preserve model safety, reproducibility, and separation between experimental diagnostics and live decisions.

## Non-negotiable boundaries

- Do not modify formal indicator_catalog.yaml unless explicitly requested.
- Do not modify formal phase scoring weights unless explicitly requested.
- Do not modify resolver / state machine live decision logic unless explicitly requested.
- Do not modify FRED provider behavior unless explicitly requested.
- Do not wire experimental candidate indicators into the live dashboard unless explicitly requested.
- Do not modify GitHub Pages workflow unless explicitly requested.
- Do not create investment advice or direct buy/sell recommendations.
- Do not classify the current economic phase from a latest snapshot.
- Do not present phase score, phase rank, or phase winner as the product answer.
- Candidate phase must mean legal transition candidate, never isolated classifier winner.
- Portfolio template weights are research assumptions, not current allocation recommendations.
- Do not use manual_review_required.
- Do not commit generated data, raw cache, public output, pyc, pytest cache, ruff cache, or secrets.
- Never print, persist, or commit FRED_API_KEY.

## Self-repair loop

For every implementation task:

1. Implement the requested change.
2. Run required quality commands.
3. Run domain-specific diagnostics / experiment commands.
4. Inspect stdout and JSON output.
5. Compare against phase acceptance gates.
6. If any hard gate fails, debug, modify, and rerun.
7. Repeat until all hard gates pass or a real blocker is reached.
8. Do not report intermediate failed results unless blocked.

## Reporting rule

Only report final results when:

- pytest passed.
- ruff passed.
- secret scan passed.
- tracked generated-file scan passed.
- all phase hard gates passed.
- remaining warnings are explicitly classified as allowed soft warnings.

If blocked, report:

- exact failing hard gate
- suspected root cause
- files inspected
- attempted fixes
- why further automated repair is unsafe

## Project North Star Contract

Before planning or implementing any phase, read:

- docs/project_north_star.md
- specs/common/project_north_star_contract.yaml
- docs/investment_cycle_product_doctrine.md
- specs/common/investment_cycle_product_doctrine.yaml
- docs/phase_execution_standing_contract.md
- specs/common/phase_execution_standing_contract.yaml

Every phase must map its work to at least one product capability and must not conflict with the North Star semantics.

The following distinctions are mandatory:

- observation != phase evidence
- watch != confirmation
- candidate phase != current phase
- revised diagnostic != point-in-time result
- structural readiness != economic validation
- portfolio research != investment recommendation
- current evidence profile != standalone current phase classifier
- candidate phase != isolated classifier winner
- phase score != product answer

Every final report must include:

- north_star_alignment_status
- product_capabilities_advanced
- web_surfaces_advanced
- deferred_capability_gaps
- semantic_drift_count
- production_behavior_change_count
- product_doctrine_alignment_status
- cycle_state_machine_alignment_status
- standalone_classifier_added_count
- phase_rank_or_score_added_count
- legal_transition_semantics_preserved
- portfolio_policy_research_alignment
- historical_replay_backtest_alignment
- deviation_cleanup_needed_count

A phase must not be marked complete when semantic_drift_count > 0.

## Investment Cycle Product Doctrine

Before any implementation phase, Codex must read:

- docs/project_north_star.md
- docs/investment_cycle_product_doctrine.md
- specs/common/investment_cycle_product_doctrine.yaml
- docs/phase_execution_standing_contract.md
- specs/common/phase_execution_standing_contract.yaml

Every future phase must answer:

1. Does this move the system closer to long-term cycle investing?
2. Does this preserve ordered cycle state-machine semantics?
3. Does this help transition detection, portfolio policy research,
   replay/backtest, or dashboard education?
4. Did it add standalone classifier, ranking, or scoring behavior that should
   not exist as a mature product shape?
5. Did it add governance-only scaffold without product progress?

The default future product shape is:

- current_declared_cycle_phase
- ordered cycle state machine
- phase-specific transition monitor
- evidence explanation
- portfolio policy research template
- historical replay/backtest

Do not delete existing legacy production v1 or governance artifacts merely
because they are cleanup candidates. Record cleanup scope first, preserve
lineage, and migrate only through an explicit phase gate.

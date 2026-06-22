# Phase QA2 Context Ablation

QA2 measures external context dependency without changing production behavior.

## Decision Layers

- `raw_phase_scores`: phase scores before sequence constraints.
- `score_only_candidate`: highest-score candidate.
- `sequence_constrained_data_only_decision`: scores plus model-generated state
  history and state-machine rules, with no external context or display text.
- `context_prior_counterfactual_decision`: diagnostic path that explicitly
  accepts external context priors.
- `production_final_decision`: existing production wrapper, preserved in QA2.
- `display_stage_hint`: display-only text with no decision impact.

## Boundaries

QA2 may use synthetic fixtures and strict-complete dates for structural
diagnostics. It must not run historical performance backtests, tune parameters,
use untouched holdout validation, execute book benchmarks, generate portfolio
outputs, alter scoring weights, change transition thresholds, or change
production resolver/dashboard defaults.

External context dependency in production may be detected and reported. The
data-only model remains economically unvalidated, and real backtest progression
and Phase 9B1 remain blocked.

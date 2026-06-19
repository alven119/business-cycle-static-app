# Business Cycle Static App

Python-first static dashboard for business-cycle investing.

This repository now supports deterministic indicator scoring, phase scoring, current-phase resolution, and a generated static dashboard deployable to GitHub Pages.

## Current structure

- `src/business_cycle/`: Python package root.
- `data_sources` package: data providers for public macro data providers such as FRED.
- `src/business_cycle/storage/`: filesystem helpers for raw, normalized, and public outputs.
- `src/business_cycle/indicators/`: indicator catalog loading and trend-aware scoring.
- `src/business_cycle/phases/`: phase scoring, state-machine resolution, and cycle context loading.
- `src/business_cycle/render/`: Traditional Chinese static dashboard rendering.
- `specs/indicator_catalog.yaml`: indicator metadata and FRED candidate series.
- `specs/phases/`: four phase specs for recovery, growth, boom, and recession.
- `specs/common/current_cycle_context.yaml`: current external baseline context; default is `榮景期第一年剛結束`.
- `scripts/update_data.py`: CLI for updating raw FRED CSV cache.
- `scripts/score_today.py`: CLI skeleton for scoring.
- `scripts/build_site.py`: CLI skeleton for static site generation.
- `tests/test_project_imports.py`: package import smoke test.

## Design constraints

- No database in the MVP skeleton.
- No frontend framework in Phase 0A.
- No API keys in source code or public output.
- No business-cycle phase decision from a single latest value.
- Future scoring must use trend, momentum, reversal, percentile, persistence, coverage, and confidence rules.

## Run tests

```bash
pytest
```

## FRED API key

Create a local `.env` file for development:

```bash
FRED_API_KEY = your_fred_api_key_here
```

Do not commit `.env` or any API key. `scripts/update_data.py` loads `FRED_API_KEY` from the environment or local `.env`.

Dry-run does not require an API key:

```bash
python scripts/update_data.py --dry-run
```

Download one series into `data/raw/fred/`:

```bash
python scripts/update_data.py --series-id UNRATE
```

Refresh a cached series:

```bash
python scripts/update_data.py --series-id UNRATE --force-refresh
```

## Live smoke test

Live FRED checks are manual and are not part of the default pytest suite. After setting `FRED_API_KEY` in local `.env`, run:

```bash
python scripts/fred_smoke_test.py
```

See `docs/fred_live_smoke_test.md` for the full safe workflow.

## Phase 2A transformations

Phase 2A adds deterministic indicator time-series transformations in `src/business_cycle/indicators/transformations.py`: cleaning, moving averages, percent changes, rolling slopes, rolling z-scores, rolling percentiles, and trailing peak/trough detection. These functions support later trend-aware scoring but do not produce phase decisions.

## Phase 2B indicator scoring

Phase 2B adds single-indicator scoring methods in `src/business_cycle/indicators/scoring.py`. Each method returns a 0-100 score and 0-1 confidence for one indicator using trend-aware evidence such as percentiles, moving-average slopes, growth momentum, or confirmed peak/trough reversals. These methods do not produce phase scores or `current_phase`.

## Phase 2C indicator dispatcher

Phase 2C adds `IndicatorScoringSpec` and `score_indicator(...)` to bind indicator specs to single-indicator scoring methods. The dispatcher handles method selection, parameter validation, `as_of` filtering, stale-data confidence handling, and dispatch metadata, but still does not perform phase scoring.

## Phase 2D catalog loader

Phase 2D adds an indicator catalog loader for `specs/indicator_catalog.yaml`. Catalog entries can now be loaded into `IndicatorScoringSpec` objects and passed to `score_indicator(...)` for single-indicator scoring. This remains indicator-layer work and does not produce phase scores or `current_phase`.

## Phase 2E FRED catalog verification

Phase 2E adds a manual verifier for FRED `candidate_series` in the indicator catalog. It writes local JSON output under ignored `data/derived/` and is not part of the default pytest flow.

```bash
python scripts/verify_fred_catalog.py
python scripts/verify_fred_catalog.py --indicator-id unemployment_rate
python scripts/verify_fred_catalog.py --series-id UNRATE
```

## Phase 2F batch indicator scoring

Phase 2F adds batch indicator scoring from local raw CSV cache into ignored `data/derived/indicator_scores.json`.

```bash
python scripts/score_indicators.py
python scripts/score_indicators.py --indicator-id unemployment_rate
python scripts/score_indicators.py --as-of 2024-12-31
```

## Phase 3A phase specs

Phase 3A adds phase-level spec schemas and a YAML loader for files such as `specs/phases/recovery.yaml`. These specs define indicator weights, roles, minimum available weight, confidence policy, and stage thresholds for future phase scoring, but they do not compute phase scores or `current_phase`.

## Phase 3B phase scoring

Phase 3B adds single-phase score aggregation from `PhaseScoringSpec` and indicator-level `IndicatorScoreResult` inputs. It computes phase score, confidence, available weight, missing indicators, contributing indicators, and stage hints, but it does not select `current_phase` or make a four-phase decision.

## Phase 3C batch phase scoring

Phase 3C adds batch phase scoring from ignored `data/derived/indicator_scores.json` and `specs/phases` into ignored `data/derived/phase_scores.json`.

```bash
python scripts/score_phases.py
python scripts/score_phases.py --phase-id recovery
python scripts/score_phases.py --as-of 2024-12-31
```

## Phase 3D phase signal mapping

Phase 3D adds phase-specific `signal_transform` support for phase indicators. Phase scoring now converts each indicator's original score into a phase signal score using `as_is` or `inverted` before weighted aggregation, while still avoiding `current_phase` selection.

## Phase 3E MVP four-phase specs

Phase 3E adds MVP specs for `growth`, `boom`, and `recession` alongside the existing `recovery` spec. Batch phase scoring can now produce scores for all four phases, but this still does not select `current_phase` or make a final cycle-state decision.

## Phase 4A current phase resolver

Phase 4A adds a deterministic current phase resolver with state-machine ordering. It can produce `data/derived/current_phase_decision.json` from phase scores and an optional previous phase, while blocking non-adjacent jumps and avoiding investment advice.

```bash
python scripts/resolve_current_phase.py
python scripts/resolve_current_phase.py --previous-phase-id boom
```

## Phase 4B cycle snapshot

Phase 4B combines `indicator_scores.json`, `phase_scores.json`, and `current_phase_decision.json` into ignored `data/derived/cycle_snapshot.json`. The snapshot is dashboard-ready data, but it is not a dashboard and does not contain investment advice.

```bash
python scripts/build_cycle_snapshot.py
```

## Phase 4C local pipeline

Phase 4C adds a local end-to-end pipeline. It can refresh FRED catalog raw cache manually, then produce indicator scores, phase scores, current phase decision, and the final cycle snapshot under ignored `data/derived/`.

```bash
python scripts/update_catalog_data.py --dry-run
python scripts/update_catalog_data.py --force-refresh
python scripts/run_cycle_pipeline.py
python scripts/run_cycle_pipeline.py --update-data --force-refresh
```

By default, `run_cycle_pipeline.py` reads `specs/common/current_cycle_context.yaml`. The current external baseline context is `榮景期第一年剛結束`, used as previous-phase context for the deterministic resolver. To override that context explicitly:

```bash
python scripts/run_cycle_pipeline.py --previous-phase-id boom
```

## Phase 5A static dashboard

Phase 5A renders ignored `data/derived/cycle_snapshot.json` into a minimal local static dashboard under `public/`. It uses no frontend framework and does not deploy to GitHub Pages.
`python scripts/build_site.py` writes ignored local output: `public/index.html` and `public/data/cycle_snapshot.json`. Re-run `build_site.py` whenever you need to regenerate the dashboard from the latest local snapshot.

The dashboard is Traditional Chinese first. Chinese phase and indicator wording aligns with the book-style cycle terms `復甦期 -> 成長期 -> 榮景期 -> 衰退期`, while technical ids remain visible in small debug text.

```bash
python scripts/run_cycle_pipeline.py
python scripts/build_site.py
python -m http.server 8000 -d public
```

## Phase 5D dashboard UX polish

Phase 5D turns the generated dashboard into a mobile-first Traditional Chinese homepage. The page uses book-aligned wording, groups indicators by observation theme, and keeps technical ids in small debug text.

The current phase badge comes from the deterministic resolver output, not from the highest phase score. Indicator sections are grouped by employment, consumption, investment, trade, rates/financial conditions, and commodities.

## Phase 5F headline summary and explainability

Phase 5F adds a dashboard headline summary, score explainability, and educational indicator explanations. The homepage now explains cycle position, current phase evidence score, turning risk, confidence, and conservative period focus.

Phase scores are explained as evidence that data resembles a given cycle phase, not as a generic "better economy" score. Indicator cards include cycle meaning and phase impacts from `specs/common/indicator_explanations_zh.yaml`. The dashboard remains a macro research aid and does not provide investment advice.

## Phase 5E deployment validation

Phase 5E adds generated-site sanity checks and a deployment/mobile QA checklist. After building locally, validate the generated `public/` output with:

```bash
python scripts/run_cycle_pipeline.py
python scripts/build_site.py
python scripts/validate_generated_site.py
```

For GitHub Pages deployment checks and iPhone Safari QA, see `docs/deployment_validation.md`.

## Phase 6A backtest scenario specs

Phase 6A adds historical backtest scenario specs without running a backtest runner. Scenario definitions live in `specs/backtests/scenarios.yaml` and can be inspected with:

```bash
python scripts/list_backtest_scenarios.py
python scripts/list_backtest_scenarios.py --scenario-id global_financial_crisis
```

Initial scenarios use `data_mode: revised`, meaning current revised historical data. This is useful for framework validation, but it is not the same as realtime vintage data available at the historical date.

## Phase 6B backtest runner skeleton

Phase 6B adds a monthly historical backtest runner skeleton that writes timeline JSON under ignored `data/backtests/`.

```bash
python scripts/run_backtest.py --scenario-id global_financial_crisis --max-periods 3
python scripts/run_backtest.py --scenario-id global_financial_crisis
```

Use `--max-periods` for smoke tests. The runner uses local cached raw CSV files and does not call the FRED API.

## Phase 6C backtest diagnostics report

Phase 6C summarizes a generated timeline into diagnostics JSON:

```bash
python scripts/summarize_backtest.py --scenario-id global_financial_crisis
```

The report is written to `data/backtests/<scenario_id>/report.json`. Backtest outputs under `data/backtests/` are generated ignored files and should not be committed.

Phase 6C.1 adds `plausibility_warning_count` and `plausibility_warnings` to the report. These warnings flag model-diagnostic issues such as short phase segments, direct confirmed transitions without watch periods, and rapid round trips; they do not change the model result.

## Phase 6D backtest smoke summary

Phase 6D runs limited backtests across the scenario catalog and writes an aggregate diagnostics summary.

```bash
python scripts/run_backtest_smoke.py --max-periods 24
python scripts/run_backtest_smoke.py --max-periods 12 --scenario-id global_financial_crisis
```

The summary is written to `data/backtests/smoke_summary.json` by default. Backtest outputs under `data/backtests/` are generated ignored files and should not be committed. The smoke summary uses revised historical data and is for model diagnosis, not investment advice.

## Phase 6E backtest transition attribution

Phase 6E explains transition events and plausibility warnings from existing backtest outputs.

```bash
python scripts/diagnose_backtest_transitions.py --scenario-id global_financial_crisis
```

The attribution output is written to `data/backtests/<scenario_id>/transition_attribution.json`. It compares phase scores and indicator scores around transition periods, links plausibility warnings, and uses intermediate contribution data when available. Outputs under `data/backtests/` are generated ignored files and should not be committed.

## Phase 6F attribution smoke summary

Phase 6F aggregates transition attribution across scenarios.

```bash
python scripts/run_backtest_smoke.py --max-periods 12
python scripts/run_attribution_smoke.py --max-periods 12 --reuse-existing
```

The summary is written to `data/backtests/attribution_summary.json` by default. It is generated ignored output, uses revised historical data, and is for model diagnosis rather than investment advice.

## Phase 7A model calibration plan

Phase 7A adds a machine-readable calibration plan without changing model behavior.

```text
specs/backtests/calibration_plan.yaml
docs/model_calibration.md
```

Inspect the plan summary with:

```bash
python scripts/show_calibration_plan.py
```

The plan defines diagnosed issues, candidate controls, scenario splits, and acceptance criteria for future calibration work. It keeps the revised data caveat, avoids single-scenario overfitting, and does not modify scoring, resolver logic, or FRED provider behavior.

## Phase 7B transition confirmation controls

Phase 7B adds feature-gated transition controls for backtest calibration experiments. The config lives at:

```text
specs/backtests/transition_controls_experiment.yaml
```

It is disabled by default and has no live dashboard impact. To pass it explicitly in a backtest:

```bash
python scripts/run_backtest.py --scenario-id global_financial_crisis --max-periods 12 --transition-controls specs/backtests/transition_controls_experiment.yaml
```

Without `--transition-controls`, the resolver keeps baseline behavior.

## Phase 7C calibration experiments

Phase 7C compares baseline backtests with enabled transition controls.

```bash
python scripts/run_calibration_experiment.py --experiment-id transition_controls_v1 --max-periods 12
```

The summary is written to `data/backtests/calibration/<experiment_id>/calibration_summary.json`. This is generated ignored output. The live dashboard and GitHub Pages workflow remain unaffected.

## Phase 7C.1 calibration acceptance review

Phase 7C.1 reviews a calibration experiment against expected scenario windows.

```bash
python scripts/review_calibration_experiment.py --experiment-id transition_controls_v1
```

The review is written to `data/backtests/calibration/<experiment_id>/calibration_acceptance_review.json`. This is generated ignored output and remains a diagnostics aid; it does not enable transition controls or affect the live dashboard.

## Phase 7C.2 full-horizon calibration review

Phase 7C.2 runs calibration experiments over each scenario's full historical window and adds COVID early false-positive attribution.

```bash
python scripts/run_full_horizon_calibration.py --experiment-id transition_controls_v1_full
python scripts/diagnose_covid_false_positive.py --experiment-id transition_controls_v1_full
```

Outputs are written under `data/backtests/calibration/<experiment_id>/`, including `calibration_acceptance_review.json` and `covid_false_positive_diagnostic.json`. These files are generated ignored diagnostics and do not affect the live dashboard.

## Phase 7D book-aligned indicator gap analysis

Phase 7D documents the gap between the MVP indicator set and book-aligned boom-ending, recession-confirmation, and recession-trough/recovery signals.

```bash
python scripts/show_book_indicator_gap.py
```

The spec lives at `specs/backtests/book_indicator_gap_analysis.yaml`, with narrative docs in `docs/book_indicator_gap_analysis.md`. This phase only adds planning/spec validation and does not change scoring, resolver behavior, or the live dashboard.

## Phase 7E recession breadth confirmation

Phase 7E adds feature-gated recession-specific breadth confirmation for calibration experiments.

```bash
python scripts/run_calibration_experiment.py --experiment-id transition_controls_v2_breadth --controls specs/backtests/transition_controls_recession_breadth_experiment.yaml
python scripts/run_full_horizon_calibration.py --experiment-id transition_controls_v2_breadth_full --controls specs/backtests/transition_controls_recession_breadth_experiment.yaml
```

The config is `specs/backtests/transition_controls_recession_breadth_experiment.yaml`. It is not used by the live dashboard unless explicitly passed to a backtest/calibration command.

## Phase 7E.1 breadth rule sensitivity

Phase 7E.1 compares multiple recession breadth variants.

```bash
python scripts/run_breadth_sensitivity.py --experiment-id breadth_sensitivity_v1
python scripts/run_breadth_sensitivity.py --experiment-id breadth_sensitivity_v1 --variant-id v4_core_plus_financial
```

The matrix lives at `specs/backtests/breadth_sensitivity_matrix.yaml`. Output is written under `data/backtests/calibration/breadth_sensitivity/<experiment_id>/` and is generated ignored diagnostics.

## Phase 7E.2 calibration output reuse

Phase 7E.2 adds conservative `--reuse-existing` and `--force` flags for long-running calibration commands.

```bash
python scripts/run_full_horizon_calibration.py --experiment-id transition_controls_v2_breadth_full --controls specs/backtests/transition_controls_recession_breadth_experiment.yaml --reuse-existing
python scripts/run_breadth_sensitivity.py --experiment-id breadth_sensitivity_v1 --reuse-existing
python scripts/run_breadth_sensitivity.py --experiment-id breadth_sensitivity_v1 --force
```

Reuse only applies when required generated JSON outputs exist and parse successfully. It does not change model behavior or live dashboard output.

## Phase 7F book-aligned indicator implementation plan

Phase 7F turns the Phase 7E.1 result into an implementation plan for book-aligned recession confirmation, boom-ending, and recession-trough/recovery indicators.

```text
specs/backtests/book_aligned_indicator_implementation_plan.yaml
docs/book_aligned_indicator_implementation_plan.md
```

Inspect the plan summary with:

```bash
python scripts/show_book_indicator_plan.py
```

This phase only defines candidate indicators, data sources, scoring method notes, and acceptance checks. It does not change scoring, resolver logic, FRED provider behavior, or live dashboard output.

## Phase 7F1 recession confirmation candidate indicators

Phase 7F1 implements experimental recession confirmation candidate indicators without connecting them to live phase scoring.

```bash
python scripts/show_book_indicator_plan.py
python scripts/update_recession_confirmation_candidate_data.py --dry-run
python scripts/update_recession_confirmation_candidate_data.py
python scripts/check_recession_confirmation_candidate_coverage.py
python scripts/score_recession_confirmation_candidates.py --as-of 2019-02-28
python scripts/run_candidate_recession_diagnostics.py
python scripts/run_candidate_recession_rule.py
python scripts/run_candidate_recession_overlay.py --experiment-id candidate_recession_overlay_v1
python -m json.tool data/backtests/candidate_indicators/recession_confirmation_overlay/candidate_recession_overlay_report.json | head -n 260
python -m json.tool data/backtests/candidate_indicators/recession_confirmation_rule/candidate_recession_rule_report.json | head -n 220
python -m json.tool data/backtests/candidate_indicators/recession_confirmation_diagnostics/candidate_recession_diagnostics.json | head -n 220
```

Candidate scores are written under `data/backtests/candidate_indicators/`, which is generated ignored output. Missing local raw cache is reported as warnings/failures; the command does not download FRED data.

## Phase 7F1.5 candidate recession integration design

Phase 7F1.5 turns the candidate recession overlay result into integration guardrails. It documents why candidate recession confirmation is useful as diagnostics, but not yet safe as a hard gate because dotcom was downgraded to watch in the full-horizon overlay.

```text
specs/backtests/candidate_recession_integration_design.yaml
docs/candidate_recession_integration_design.md
```

Inspect the design summary with:

```bash
python scripts/show_candidate_recession_integration_design.py
```

This phase does not change formal phase scoring, resolver logic, FRED provider behavior, live dashboard output, or GitHub Pages deployment.

## Phase 7F2 boom ending candidate indicators

Phase 7F2 implements experimental boom ending / late-cycle transition candidate indicators without connecting them to formal phase scoring or the live dashboard.

```bash
python scripts/check_boom_ending_candidate_coverage.py
python scripts/update_boom_ending_candidate_data.py --dry-run
python scripts/update_boom_ending_candidate_data.py --no-api
python scripts/update_boom_ending_candidate_data.py
python scripts/score_boom_ending_candidates.py --as-of 2019-02-28
```

Candidate scores are written under `data/backtests/candidate_indicators/boom_ending/`, which is generated ignored output. These indicators are for boom-ending diagnostics and future calibration only; they do not affect live dashboard decisions.

## Phase 7F2.1 boom ending diagnostics

Phase 7F2.1 runs fixed historical diagnostic points for the boom ending candidate indicators.

```bash
python scripts/run_boom_ending_diagnostics.py
python -m json.tool data/backtests/candidate_indicators/boom_ending_diagnostics/boom_ending_diagnostics.json | head -n 260
```

The output is generated ignored diagnostics. It is used to evaluate late-cycle early-warning behavior and does not change formal phase scoring, resolver logic, or live dashboard output.

## Phase 7F2.2 boom ending attribution and refinement plan

Phase 7F2.2 explains the boom ending diagnostics and records the scoring refinement plan.

```bash
python scripts/run_boom_ending_diagnostics.py
python scripts/run_boom_ending_attribution.py
python scripts/show_boom_ending_refinement_plan.py
```

The attribution output is written under ignored `data/backtests/candidate_indicators/boom_ending_diagnostics/`. The plan lives at `specs/backtests/boom_ending_refinement_plan.yaml`. This phase does not change scoring or live dashboard behavior.

## Phase 7F2.3 boom ending scoring refinement experiment

Phase 7F2.3 compares baseline boom ending diagnostics with refined experimental scoring.

```bash
python scripts/run_boom_ending_diagnostics.py
python scripts/run_boom_ending_refinement_experiment.py
python -m json.tool data/backtests/candidate_indicators/boom_ending_refinement/boom_ending_refinement_experiment.json | head -n 320
```

The refined helpers test yield-curve lead-time pressure, credit-spread velocity, financial-conditions delta, and Fed peak/pause pressure. Output is generated ignored diagnostics and does not affect formal phase scoring or the live dashboard.

## Phase 7F2.4 boom ending watch rule

Phase 7F2.4 applies an experimental watch rule to the refined boom ending diagnostics.

```bash
python scripts/run_boom_ending_diagnostics.py
python scripts/run_boom_ending_refinement_experiment.py
python scripts/run_boom_ending_watch_rule.py
python -m json.tool data/backtests/candidate_indicators/boom_ending_watch_rule/boom_ending_watch_rule_report.json | head -n 260
```

The rule classifies `strong_late_cycle_warning`, `watch`, `weak`, and `none`. It is for early-warning diagnostics and future strategy design only: boom ending watch is not confirmed recession, does not affect formal phase scoring, and does not affect the live dashboard.

## Phase 7F2.5 boom ending watch overlay

Phase 7F2.5 applies the experimental boom ending watch rule across full-horizon scenario timelines.

```bash
python scripts/run_boom_ending_watch_overlay.py
python -m json.tool data/backtests/candidate_indicators/boom_ending_watch_overlay/boom_ending_watch_overlay_report.json | head -n 360
```

The overlay output is generated ignored diagnostics under `data/backtests/`. It does not overwrite timelines, does not confirm recession, does not affect formal phase scoring, and does not affect the live dashboard.

## Phase 7F2.6 boom ending watch integration guardrails

Phase 7F2.6 records guardrails for any future use of boom ending watch.

```text
specs/backtests/boom_ending_watch_integration_guardrails.yaml
docs/boom_ending_watch_integration_guardrails.md
```

Inspect the guardrails summary with:

```bash
python scripts/show_boom_ending_watch_integration_guardrails.py
```

The guardrails explicitly prohibit direct recession confirmation and direct portfolio action. They do not change formal phase scoring, resolver logic, FRED provider behavior, or live dashboard output.

## Phase 7F3 recovery candidate indicators

Phase 7F3 implements experimental recession trough / recovery candidate indicators without connecting them to formal phase scoring or the live dashboard.

```bash
python scripts/check_recovery_candidate_coverage.py
python scripts/update_recovery_candidate_data.py --dry-run
python scripts/update_recovery_candidate_data.py --no-api
python scripts/update_recovery_candidate_data.py
python scripts/score_recovery_candidates.py --as-of 2009-03-31
python scripts/score_recovery_candidates.py --as-of 2020-04-30
```

Candidate scores are written under `data/backtests/candidate_indicators/recovery/`, which is generated ignored output. These indicators are for recession-trough and recovery diagnostics only; they do not affect live dashboard decisions.

## Phase 7F3.1 recovery diagnostics

Phase 7F3.1 runs fixed historical diagnostic points for recovery / recession trough candidate indicators.

```bash
python scripts/run_recovery_diagnostics.py
python -m json.tool data/backtests/candidate_indicators/recovery_diagnostics/recovery_diagnostics.json | head -n 360
```

The diagnostics output is generated ignored data. Recovery watch is not formal recovery confirmation, policy easing cannot confirm recovery by itself, and the output does not affect formal phase scoring or the live dashboard.

## Phase 5B GitHub Pages deployment

Phase 5B adds the GitHub Actions workflow at `.github/workflows/pages.yml`. The repository must define the `FRED_API_KEY` repository secret for scheduled or manual dashboard deployment. Local generated output under `public/` remains ignored and is not committed; GitHub Pages is deployed from the CI-generated `public` artifact.

See `docs/github_pages_deployment.md` for setup and troubleshooting.

## Next steps

1. Add YAML loading and validation for `specs/indicator_catalog.yaml`.
2. Validate FRED metadata and cache freshness for catalog series.
3. Implement trend-aware indicator scoring with tests for rising, falling, flat, spike, missing, stale, and insufficient-history cases.
4. Implement the phase transition engine with persistence, coverage, confidence, and static snapshot state.
5. Generate public JSON and a simple static HTML dashboard.

# Business Cycle Research Service

Python-first research service for business-cycle investing.

The product direction is now a private NAS-hosted dynamic research service. The
mature path uses a declared cycle state, legal ordered transition monitoring,
indicator-level explanations, research-only portfolio policy templates, and
historical replay/backtest research surfaces. GitHub Pages deployment has been
retired; the GitHub repository may remain as source control and CI during the
NAS migration, but it is no longer the user-facing deployment target.

## Current structure

- `src/business_cycle/`: Python package root.
- `data_sources` package: data providers for public macro data providers such as FRED.
- `src/business_cycle/storage/`: filesystem helpers for raw, normalized, and public outputs.
- `src/business_cycle/indicators/`: indicator catalog loading and trend-aware scoring.
- `src/business_cycle/phases/`: legacy phase scoring, resolver compatibility, and cycle context loading.
- `src/business_cycle/cycle_state/`: declared cycle state and ordered legal transition state.
- `src/business_cycle/render/`: Traditional Chinese research dashboard rendering.
- `specs/indicator_catalog.yaml`: indicator metadata and FRED candidate series.
- `specs/phases/`: four phase specs for recovery, growth, boom, and recession.
- `specs/common/current_cycle_context.yaml`: current external baseline context; default is `榮景期第一年剛結束`.
- `scripts/update_data.py`: CLI for updating raw FRED CSV cache.
- `scripts/score_today.py`: CLI skeleton for scoring.
- `scripts/serve_research_validation_dashboard.py`: local research dashboard preview helper.
- `scripts/build_site.py`: legacy static site generation helper retained for compatibility.
- `tests/test_project_imports.py`: package import smoke test.

## Design constraints

- First NAS service target: FastAPI-style Python web service, Postgres, and a
  private mobile access path such as Tailscale or VPN.
- Postgres schema planning must support point-in-time/vintage data from the
  start, even if the first data-completeness sprint fills revised data first.
- Frontend code must not connect directly to Postgres or carry API keys.
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

## Temporal Integrity Status

QA1C distinguishes ALFRED vintage intervals from official release archives,
official observational archives, and derived point-in-time reconstructions.
Partial official history is not full required-horizon strict coverage. Current
historical values plus an arbitrary lag are not strict point-in-time data, and
substitute series require temporal, economic, and signal equivalence review.

QA1E separates source-series coverage from derived output readiness. `RRSFS`
may be derived only from same-as-of `RSAFS` and `CPIAUCSL`; it is not strict
unless both inputs and the official formula/unit/base-period contract are
validated. Parsed EIA or Census artifacts with incomplete availability,
revision, or parser evidence remain blocked and do not count as strict archive
coverage.

QA1E.1 adds end-to-end formal indicator output coverage. It separates leaf
series coverage from strict derived output readiness and final indicator output
readiness. Candidate `RRSFS` derived snapshots are not strict coverage until the
official derivation contract and input archive evidence are complete.

Production live scoring still defaults to revised data unless a point-in-time
mode is explicitly requested. Phase 9B1, real historical backtesting, book
benchmark execution, and dashboard portfolio integration remain blocked.

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

GitHub Pages deployment has been retired. Future mobile QA should target the
private NAS dynamic service over the governed private access path.

## Phase 6A backtest scenario specs

Phase 6A adds historical backtest scenario specs without running a backtest runner. Scenario definitions live in `specs/backtests/scenarios.yaml` and can be inspected with:

```bash
python scripts/list_backtest_scenarios.py
python scripts/list_backtest_scenarios.py --scenario-id global_financial_crisis
```

Initial scenarios use `data_mode: revised`, meaning current revised historical data. This is useful for framework validation, but it is not the same as realtime vintage data available at the historical date.

## Phase QA1 temporal integrity

QA1 adds a date-level point-in-time data model, ALFRED/FRED vintage provider,
ignored local cache, coverage audit, and optional scoring data modes.

The four supported data modes are:

- `revised`: latest revised values; still the live production default.
- `release_lag_adjusted_revised_proxy`: revised values delayed by a release-lag rule; diagnostics only.
- `initial_release_only`: first release values; not the same as as-of latest vintage.
- `vintage_as_of`: strict date-level ALFRED real-time interval selection using end-of-day as-of policy.

Inventory complete does not mean strict point-in-time coverage is complete.
Strict mode fails closed when cache rows or `realtime_start` / `realtime_end`
metadata are missing, and it does not fall back to revised data.

Useful QA1 commands:

```bash
python scripts/update_point_in_time_data.py --formal-only --scenario-horizons --reuse-existing
python scripts/audit_point_in_time_coverage.py
python scripts/compare_revised_vs_point_in_time.py --scenario-id global_financial_crisis --formal-only --max-periods 12
```

Phase 9B remains a synthetic harness. Phase 9B1, book benchmark execution, real
backtest progression, and portfolio dashboard integration remain blocked.

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

## Phase 7F3.2 recovery attribution and refinement plan

Phase 7F3.2 attributes recovery diagnostics mismatches and records the next refinement plan.

```bash
python scripts/run_recovery_diagnostics.py
python scripts/run_recovery_attribution.py
python scripts/show_recovery_refinement_plan.py
python -m json.tool data/backtests/candidate_indicators/recovery_diagnostics/recovery_attribution.json | head -n 320
```

The attribution output is generated ignored data under `data/backtests/`. The plan lives at `specs/backtests/recovery_refinement_plan.yaml`. This phase does not change formal phase scoring, resolver logic, FRED provider behavior, or live dashboard output.

## Phase 7F3.3 recovery scoring refinement experiment

Phase 7F3.3 compares baseline recovery diagnostics with refined experimental scoring.

```bash
python scripts/run_recovery_diagnostics.py
python scripts/run_recovery_refinement_experiment.py
python -m json.tool data/backtests/candidate_indicators/recovery_refinement/recovery_refinement_experiment.json | head -n 420
```

The refined comparison adds a recession-context gate and caps policy/financial-only support signals. The output is generated ignored data and does not affect formal phase scoring, resolver logic, FRED provider behavior, or live dashboard output.

## Phase 7F3.4 recovery watch rule

Phase 7F3.4 evaluates an experimental recovery watch rule on the refined recovery diagnostics.

```bash
python scripts/run_recovery_diagnostics.py
python scripts/run_recovery_refinement_experiment.py
python scripts/run_recovery_watch_rule.py
python -m json.tool data/backtests/candidate_indicators/recovery_watch_rule/recovery_watch_rule_report.json | head -n 320
```

The report is generated ignored output. Recovery watch is not formal recovery confirmation, policy/financial easing cannot confirm recovery by itself, and the rule is not connected to formal phase scoring, resolver logic, FRED provider behavior, portfolio allocation, or the live dashboard.

## Phase 7F3.5 recovery watch overlay

Phase 7F3.5 runs a full-horizon experimental recovery watch overlay.

```bash
python scripts/run_recovery_watch_overlay.py
python -m json.tool data/backtests/candidate_indicators/recovery_watch_overlay/recovery_watch_overlay_report.json | head -n 420
```

The overlay output is generated ignored data. It preserves original timeline phase and decision fields, does not confirm recovery, does not create portfolio actions, and does not affect formal phase scoring, resolver logic, FRED provider behavior, or live dashboard output.

## Phase 7F3.6 recovery watch integration guardrails

Phase 7F3.6 records guardrails for future recovery watch integration.

```text
specs/backtests/recovery_watch_integration_guardrails.yaml
docs/recovery_watch_integration_guardrails.md
```

Inspect the guardrails summary with:

```bash
python scripts/show_recovery_watch_integration_guardrails.py
```

The guardrails prohibit direct recovery confirmation and direct portfolio action. They do not change formal phase scoring, resolver logic, FRED provider behavior, GitHub Pages workflow, or live dashboard output.

## Phase 7G cycle transition evidence architecture

Phase 7G consolidates recession confirmation, boom ending watch, and recovery watch into one evidence architecture.

```text
specs/common/cycle_transition_evidence_architecture.yaml
docs/cycle_transition_evidence_architecture.md
```

Inspect the architecture summary with:

```bash
python scripts/show_cycle_transition_evidence_architecture.py
```

This phase only defines evidence usage boundaries. It does not connect evidence to the dashboard, resolver, formal phase scoring, FRED provider, GitHub Pages workflow, or portfolio allocation.

## Phase 7G1 transition evidence badge schema

Phase 7G1 defines the future dashboard diagnostics badge schema for transition evidence.

```text
specs/common/transition_evidence_badge_schema.yaml
docs/transition_evidence_badge_schema.md
```

Inspect the schema summary with:

```bash
python scripts/show_transition_evidence_badge_schema.py
```

This phase only defines a schema and validator. It does not connect evidence badges to dashboard output, resolver logic, formal phase scoring, FRED provider behavior, GitHub Pages workflow, or portfolio allocation.

## Phase 7G2 transition evidence badge fixtures

Phase 7G2 adds static fixtures and a batch validator for transition evidence badges.

```text
specs/common/transition_evidence_badge_fixtures.yaml
```

Validate the fixtures with:

```bash
python scripts/validate_transition_evidence_badge_fixtures.py
```

The validator requires valid badges to pass and invalid badges with action, allocation, buy/sell signal, or phase override fields to fail. This phase still does not connect badges to dashboard output, resolver logic, formal phase scoring, FRED provider behavior, GitHub Pages workflow, or portfolio allocation.

## Phase 7G3 transition evidence badge renderer contract

Phase 7G3 defines the future renderer contract for safe transition evidence badge display models.

```text
specs/common/transition_evidence_badge_renderer_contract.yaml
docs/transition_evidence_badge_renderer_contract.md
```

Inspect the contract summary with:

```bash
python scripts/show_transition_evidence_badge_renderer_contract.py
```

This phase only defines a renderer contract and validator. It does not modify dashboard templates, generate `public/`, alter formal phase scoring, resolver logic, FRED provider behavior, GitHub Pages workflow, or portfolio allocation.

## Phase 7G4 transition evidence badge display fixtures

Phase 7G4 adds renderer display model fixtures and a batch validator for the renderer contract.

```text
specs/common/transition_evidence_badge_display_fixtures.yaml
```

Validate the display fixtures with:

```bash
python scripts/validate_transition_evidence_badge_display_fixtures.py
```

The validator requires safe display models to pass and display models with action, allocation, buy/sell signal, phase override, or prohibited text to fail. This phase still does not modify dashboard templates, generate `public/`, alter formal phase scoring, resolver logic, FRED provider behavior, GitHub Pages workflow, or portfolio allocation.

## Phase 7G5 dashboard evidence integration readiness

Phase 7G5 closes Phase 7G with a dashboard evidence integration readiness checklist.

```text
specs/common/dashboard_evidence_integration_readiness.yaml
docs/dashboard_evidence_integration_readiness.md
```

Inspect the readiness summary with:

```bash
python scripts/show_dashboard_evidence_integration_readiness.py
```

Phase 7G is now fully specified but not wired. Dashboard wiring remains blocked until a data adapter schema, generated-site validation updates, HTML text-safety tests, accessibility handling, and no-formal-decision-impact tests are defined.

## Phase 8A portfolio policy research planning

Phase 8A starts portfolio policy research planning without producing allocation output.

```text
specs/portfolio/portfolio_policy_research_plan.yaml
docs/portfolio_policy_research_plan.md
```

Inspect the plan summary with:

```bash
python scripts/show_portfolio_policy_research_plan.py
```

This phase only defines research templates, backtest-only parameters, risk metrics, sensitivity tests, and acceptance gates. It does not produce live allocation, current market recommendations, dashboard portfolio actions, public output, resolver integration, or trade signals.

## Phase 8B portfolio policy template schema

Phase 8B adds the static schema and fixtures for research-only portfolio policy templates.

```text
specs/portfolio/portfolio_policy_template_schema.yaml
specs/portfolio/portfolio_policy_template_fixtures.yaml
```

Inspect and validate with:

```bash
python scripts/show_portfolio_policy_template_schema.py
python scripts/validate_portfolio_policy_template_fixtures.py
```

The validator accepts only backtest-only templates and rejects live allocation, trade signals, target weights, current market recommendations, and prohibited recommendation text. It does not produce allocation output or public dashboard output.

## Phase 8C portfolio backtest input contract

Phase 8C defines the future portfolio backtest input contract and scenario mapping.

```text
specs/portfolio/portfolio_backtest_input_contract.yaml
specs/portfolio/portfolio_backtest_scenario_mapping.yaml
```

Inspect the contract and mapping summary with:

```bash
python scripts/show_portfolio_backtest_input_contract.py
```

This phase only defines future backtest inputs, rebalance assumptions, cost assumptions, risk metrics, output safety boundaries, and scenario mapping. It does not run a portfolio backtest, produce allocation output, generate `data/backtests`, or publish dashboard output.

## Phase 8D portfolio backtest input fixtures

Phase 8D adds valid and invalid portfolio backtest input fixtures plus a batch validator.

```text
specs/portfolio/portfolio_backtest_input_fixtures.yaml
```

Validate the fixtures with:

```bash
python scripts/validate_portfolio_backtest_input_fixtures.py
```

The validator accepts only research-only / backtest-only inputs and rejects live allocation, target weights, buy/sell signals, current recommendations, public dashboard output, unknown scenarios, and unknown policy templates. It does not run a portfolio backtest or generate `data/backtests`.

## Phase 8E portfolio backtest dry-run contract

Phase 8E defines the dry-run engine contract for future structural portfolio backtest validation.

```text
specs/portfolio/portfolio_backtest_dry_run_contract.yaml
```

Inspect the contract with:

```bash
python scripts/show_portfolio_backtest_dry_run_contract.py
```

The dry-run contract allows input/schema validation and stdout-only structural summaries. It forbids performance calculations, allocation output, trade signals, `data/backtests` output, and public dashboard output.

## Phase 8F portfolio backtest dry-run fixtures

Phase 8F adds dry-run output fixtures and a validator for structural summaries.

```text
specs/portfolio/portfolio_backtest_dry_run_fixtures.yaml
```

Validate the fixtures with:

```bash
python scripts/validate_portfolio_backtest_dry_run_fixtures.py
```

The validator accepts structural dry-run summaries and rejects performance metrics, allocation fields, target weights, trade signals, public dashboard output, output-written flags, and prohibited recommendation text. It does not run a portfolio backtest or generate `data/backtests`.

## Phase 8G portfolio structural dry-run runner

Phase 8G adds a stdout-only structural dry-run runner.

```bash
python scripts/run_portfolio_backtest_structural_dry_run.py
```

The runner loads contracts, scenario mapping, and valid input fixtures; validates them; builds in-memory structural summaries; and prints aggregate safety flags. It does not compute performance, produce allocation, write `data/backtests`, or generate public output.

## Phase 8H portfolio research safety closure

Phase 8H closes Phase 8A-8G as research-only / structural dry-run-only.

```text
specs/portfolio/portfolio_research_safety_closure.yaml
docs/portfolio_research_safety_closure.md
```

Inspect the closure checklist with:

```bash
python scripts/show_portfolio_research_safety_closure.py
```

The checklist confirms Phase 8A-8G produced no formal backtest, performance conclusion, allocation, trade signal, `data/backtests` output, or public output. It blocks real backtest work until a real engine contract, result output contract, metric registry, result caveat validator, and output location policy are defined.

## Phase 8I real backtest prototype readiness gate

Phase 8I defines the readiness gate before any real backtest prototype.

```text
specs/portfolio/real_backtest_prototype_readiness_gate.yaml
docs/real_backtest_prototype_readiness_gate.md
```

Inspect the gate with:

```bash
python scripts/show_real_backtest_prototype_readiness_gate.py
```

This phase only allows contract design for future backtesting. It keeps real backtest execution, performance metrics, result output, allocation, trade signals, `data/backtests` output, and public output blocked until the required engine, result, metric, safety, caveat, and output-location contracts are defined.

## Phase 9A real backtest engine contract

Phase 9A defines the future real backtest engine contract.

```text
specs/portfolio/real_backtest_engine_contract.yaml
docs/real_backtest_engine_contract.md
```

Inspect the contract with:

```bash
python scripts/show_real_backtest_engine_contract.py
```

This phase is contract-only. It defines engine scope, stages, dependencies, prohibited outputs, prohibited write locations, and required safety guards. It does not implement a runtime, execute backtests, compute performance metrics, produce allocation, write `data/backtests`, or generate public output.

## Phase 9A1 backtest result output contract

Phase 9A1 defines the future backtest result output contract.

```text
specs/portfolio/backtest_result_output_contract.yaml
docs/backtest_result_output_contract.md
```

Inspect the contract with:

```bash
python scripts/show_backtest_result_output_contract.py
```

This phase is contract-only. It defines result schema, future metric field names, prohibited result fields, required caveats, output-location dependency, result-safety dependency, and caveat-policy dependency. It does not compute metric values, write result files, produce allocation, write `data/backtests`, or generate public output.

## Phase 9A2 backtest metric formula registry

Phase 9A2 defines the future backtest metric formula registry.

```text
specs/portfolio/backtest_metric_formula_registry.yaml
docs/backtest_metric_formula_registry.md
```

Inspect the registry with:

```bash
python scripts/show_backtest_metric_formula_registry.py
```

This phase is formula-only. It defines performance, risk, trading behavior, false signal cost, and opportunity cost formulas for future backtests, but every metric has `compute_allowed_now=false`. It does not calculate metric values, produce result files, produce allocation, write `data/backtests`, or generate public output.

## Phase 9A3 backtest output location policy

Phase 9A3 defines the future backtest output location policy.

```text
specs/portfolio/backtest_output_location_policy.yaml
docs/backtest_output_location_policy.md
```

Inspect the policy with:

```bash
python scripts/show_backtest_output_location_policy.py
```

This phase is policy-only. It defines future controlled research path requirements, prohibited auto-write locations, write preconditions, and safety dependencies. It does not create output directories, write result files, write `data/backtests`, or generate public output.

## Phase 9A4 backtest result caveat policy

Phase 9A4 defines the future backtest result caveat policy.

```text
specs/portfolio/backtest_result_caveat_policy.yaml
docs/backtest_result_caveat_policy.md
```

Inspect the policy with:

```bash
python scripts/show_backtest_result_caveat_policy.py
```

This phase is policy-only. It defines required global/contextual caveats, display requirements, prohibited text patterns, prohibited interpretations, and future validation rules. It does not compute metric values, produce result files, create output directories, write `data/backtests`, or generate public output.

## Phase 9A5 backtest result safety validator contract

Phase 9A5 defines the future backtest result safety validator contract.

```text
specs/portfolio/backtest_result_safety_validator_contract.yaml
docs/backtest_result_safety_validator_contract.md
```

Inspect the contract with:

```bash
python scripts/show_backtest_result_safety_validator_contract.py
```

This phase is contract-only. It defines required check groups, prohibited fields, prohibited text, caveat checks, output location enforcement, and future validator result fields. It does not implement validator runtime, validate real results, produce result files, create output directories, write `data/backtests`, or generate public output.

## Phase 9A6 backtest result safety validator fixtures

Phase 9A6 defines fixture-only safety validator examples.

```text
specs/portfolio/backtest_result_safety_validator_fixtures.yaml
```

Validate the fixtures with:

```bash
python scripts/validate_backtest_result_safety_validator_fixtures.py
```

This phase is fixture-only. It provides valid sample results and intentionally invalid examples for live allocation, target weight, buy/sell signal, current recommendation, public dashboard output, phase override, prohibited text, caveat visibility, and output-location violations. It does not implement validator runtime, validate real results, produce result files, create output directories, write `data/backtests`, or generate public output.

## Phase 9A7 backtest result writer contract

Phase 9A7 defines the future backtest result writer contract.

```text
specs/portfolio/backtest_result_writer_contract.yaml
docs/backtest_result_writer_contract.md
```

Inspect the contract with:

```bash
python scripts/show_backtest_result_writer_contract.py
```

This phase is contract-only. It defines explicit user command requirements, future controlled research path policy, pre-write validations, writer status fields, prohibited write locations, and prohibited result fields. It does not implement writer runtime, create output directories, write result files, write `data/backtests`, or generate public output.

## Phase 9A8 real backtest execution readiness closure

Phase 9A8 closes the Phase 9A contract stack and checks readiness for a controlled Phase 9B prototype.

```text
specs/portfolio/real_backtest_execution_readiness_closure.yaml
docs/real_backtest_execution_readiness_closure.md
```

Inspect the closure with:

```bash
python scripts/show_real_backtest_execution_readiness_closure.py
```

This phase is readiness-only. It confirms the 9A–9A7 contracts, policies, fixtures, and writer contract are in place for 9B entry, while still blocking execution, runtime implementation, metric computation, result generation, output directory creation, `data/backtests` writes, public output, allocation, and trade signals. QA0 reclassifies Phase 9B as a controlled synthetic in-memory calculation harness with no default output writing.

## Phase 9B controlled synthetic in-memory harness

Phase 9B is now classified as a controlled synthetic in-memory calculation harness.

```text
specs/portfolio/controlled_real_backtest_prototype_fixtures.yaml
src/business_cycle/portfolio/controlled_backtest_prototype.py
docs/controlled_real_backtest_prototype.md
```

Run the prototype summary with:

```bash
python scripts/run_controlled_real_backtest_prototype.py
```

This phase uses controlled synthetic fixtures only. It may compute arithmetic fixture metrics in memory, but it does not validate book strategy fidelity, historical performance, the business-cycle model, or point-in-time tradability. It does not write result files, create output directories, write `data/backtests`, generate public output, connect dashboard rendering, produce allocation output, or produce trade signals.

## QA0 methodology audit pause

Phase 9B1 is paused until QA0 findings are reviewed.

Current limits:

- Phase 9B is only a synthetic arithmetic harness.
- Revised historical data is not point-in-time data.
- The current five historical scenarios have all been used for development or diagnostics and are not unused holdout samples.
- The book benchmark has not been reproduced.
- No investment decision should rely solely on current outputs.
- Real backtest progression remains blocked until QA0 and follow-up gates explicitly allow it.

## Phase QA0.1 inventory reconciliation

Phase QA0 is the initial audit baseline. Phase QA0.1 adds the inventory reconciliation layer:

```bash
python scripts/show_qa0_repository_inventory.py
python scripts/run_qa0_inventory_reconciliation.py
python scripts/run_qa0_integrity_audit.py
```

QA0.1 verifies that canonical book requirements, repository indicators, series references, provenance mappings, release-lag registry rows, and book indicator coverage rows reconcile without drift. A QA0.1 pass does not mean model validation. Current hard limits remain: `book_alignment_claim_allowed=false`, `point_in_time_backtest_ready=false`, `real_backtest_progression_allowed=false`, and Phase 9B1 remains blocked. The next methodology phase is QA1 temporal integrity remediation.

## Phase QA1F temporal coverage governance

QA1F closes the temporal integrity work with explicit historical gaps. It
records that QA1E.2 archive reconstruction remains blocked for early Census and
other unresolved sources, and it prevents those gaps from being silently reused
in calibration, validation, holdout, performance backtests, or book benchmark
execution.

The safe next step is QA2 context ablation only. QA2 may use synthetic fixtures
or dates with strict-complete temporal evidence. It is not a historical
performance backtest and it does not authorize portfolio output, book benchmark
execution, Phase 9B1, scoring-weight calibration, or resolver changes.

## Phase QA2 context ablation

QA2 adds external-context inventory, a decision-layer contract, and a pure
data-only resolver path for diagnostics. It separates score-only candidates,
sequence-constrained data-only decisions, context-prior counterfactuals,
production decisions, and display-stage hints.

QA2 measures whether external cycle context can change the current production
wrapper, but it does not remove that context from production and does not claim
economic validation for the data-only path. The data-only path is structurally
validated: changing external context or display text must not change data-only
decision fields.

QA2 keeps all methodology blockers in place. It does not run historical
performance backtests, parameter calibration, untouched holdout validation, book
benchmark execution, scoring-weight changes, resolver default changes,
dashboard behavior changes, portfolio output, or trade signals. The next
allowed phase is QA3, while Phase 9B1 and real backtest progression remain
blocked.

## Phase QA3 calibration integrity governance

QA3 establishes calibration-integrity governance without tuning parameters or
running a performance backtest. It adds a complete model parameter inventory,
scenario exposure registry, production hard-coding audit, frozen data-only
baseline, pre-registered future validation protocol, calibration leakage audit,
data-only shadow diagnostics, and context dependency governance.

Production context dependency has been confirmed and is classified as
`phase_selection`. The production default still preserves context; QA3 does not
remove production context, change resolver defaults, or change dashboard
production behavior. Context-derived output must not be labeled data-only.

The data-only path is structurally validated only. It is not economically
validated. The current five scenarios remain development and diagnostics
scenarios, even when a date is strict complete. Temporal completeness is not the
same as methodological validation, and the current scenarios are not final
holdout evidence.

QA3 records parameter contamination explicitly. Prospective holdout must begin
after the frozen baseline, starting with the next complete data period, and any
parameter or decision-source change resets holdout. QA3 does not execute
calibration, portfolio return computation, book benchmark execution, or Phase
9B1. The next allowed phase is QA4: Book Fidelity Remediation and Formal Model
Scope Freeze.

## Phase QA4 book fidelity scope

QA4 defines `book_faithful_scope_v1` as a formal scope contract. Current
production v1 remains book-informed rather than book-faithful: it still has a
known `phase_selection` context dependency, and production defaults are
preserved.

The proposed v2 scope is defined but not implemented. QA4 separates normal
cycle phase logic, transition evidence, exogenous shock overlay, secular regime
research, and portfolio policy research. Modern extensions remain separate from
book-core roles and cannot substitute for missing book evidence.

`data_only_baseline_v1` remains a research baseline for structural comparison.
Its prospective observations do not become validation evidence for a later
book-faithful candidate model. Any decision-active implementation change must
create a new model version and a fresh prospective registration.

QA4 does not define new weights or thresholds, does not promote indicators to
production, does not run a performance backtest, and does not change dashboard
or resolver behavior. QA5 is the next allowed phase; real backtest progression
and Phase 9B1 remain blocked.

## Phase QA5 book-core data contracts

QA5 adds book-core indicator data contracts and a shadow evidence model for
`book_faithful_shadow_v2_alpha1`. The shadow evidence model is diagnostic-only:
it emits role evidence and phase evidence profiles, but it does not compute a
candidate phase, current phase, decision status, portfolio action, allocation,
or trade signal.

production v1 remains unchanged. QA5 does not remove production context, change
resolver defaults, change dashboard behavior, tune weights, define thresholds,
or register a candidate holdout. Missing strict evidence abstains instead of
falling back to revised data or zero-filling.

QA5 reconciles scope counts across 98 canonical scope requirements, 40
canonical indicator roles, 38 existing indicators, and 54 indicator matrix
rows. The shadow candidate freeze records contract and source hashes only; it
does not freeze decision parameters or validate economic accuracy. QA6 is the
next allowed phase for shadow aggregation rule pre-registration and structural
candidate validation. Real backtest progression and Phase 9B1 remain blocked.

## Phase QA6 shadow aggregation preregistration

QA6 pre-registers typed evidence vocabulary, layer routing, major-group
aggregation invariants, structural eligibility, and the
`book_faithful_shadow_v2_alpha2` aggregation architecture freeze.

Structural readiness is separate from evidence evaluability. Current real-data
diagnostics can have `evidence_evaluable_role_count=0`; raw transforms are not
directional signals, and missing evidence is not zero-filled. QA6 defines no
numeric weights, no new thresholds, and no candidate-selection rule.

Candidate selection remains disabled:
`candidate_selection_enabled=false`, `formal_candidate_phase_computed=false`,
and `holdout_registered=false`. Production v1 is unchanged, and real backtest
progression plus Phase 9B1 remain blocked. QA7 is the next allowed phase.

## Phase QA7 evidence-rule preregistration

QA7 pre-registers evidence-rule provenance and candidate-selection mechanics
for `book_faithful_shadow_v2_alpha3`. It explains why all 40 canonical roles
remain non-evaluable in real data: 24 are raw-transform-only without
pre-registered evidence thresholds, and the remaining roles are blocked by
data, source, access, or rule gaps.

Book statements are classified before use. The three-month initial-claims
moving average is a book smoothing/noise-filter rule. The 250000 initial-claims
value from the 2019 discussion is contextual, not a universal threshold.
Qualitative language such as significant jump remains unresolved until a later
phase preregisters a defensible evaluator.

Synthetic candidate selection is enabled only to validate mechanics. Real-data
candidate selection remains disabled, emits no candidate phase, and writes only
explicit `/tmp` diagnostics when requested. Production v1 remains unchanged,
holdout is not registered, real backtest progression remains blocked, and Phase
9B1 remains blocked. QA8 is the next allowed phase.

## Phase QA8 book-explicit evaluators and forward protocol

QA8 reconciles primary versus secondary blocker accounting and implements only
operationally complete book-explicit shadow evaluators for
`book_faithful_shadow_v2_alpha4`.

The three-month initial-claims moving average is implemented as a calendar-time
noise filter. It does not confirm a phase and does not become candidate
selection evidence. Claims reversal, durable-orders improvement, and
claims-new-low continuation rules remain blocked where lookback, persistence,
turning-point, or reference-window semantics are incomplete.

The 2019 250000 initial-claims value remains a contextual example, qualitative
significant-jump language is not numericized, and contaminated legacy rules are
not used for future validation claims. Retrospective diagnostics may report
rule execution, provenance, and abstention only; candidate phase output remains
disabled.

The prospective shadow diagnostic protocol is registered but not started. It
uses the QA3 first eligible observation period, rejects pre-start and backdated
candidate emission, and is not a holdout. Production v1 remains unchanged;
real backtest progression and Phase 9B1 remain blocked. QA9 is the next allowed
phase.

## Phase QA9 prospective shadow registry

QA9 adds forward-only registry infrastructure for future shadow diagnostics.
The registry is `armed_not_started`: `protocol_registered=true`,
`protocol_started=false`, and `real_record_count=0`. Registry arming is not a
holdout and does not create forward evidence.

The implemented initial-claims evaluator is runtime-wired, but it remains a
three-calendar-month smoothing/noise filter only. It is not directional phase
evidence, not confirmation evidence, and not candidate-selection evidence.
Candidate capability remains false, candidate monitoring remains disabled, and
no candidate phase is emitted.

Prospective records are append-only, hash-chained, and protected against
overwrite, delete, rewrite, backfill, pre-start writes, arbitrary real
`as_of` overrides, and model/protocol version mixing. QA9 does not create an
automatic schedule, does not write a real record, and does not inspect real
prospective results.

Production v1 remains unchanged. Real backtest progression and Phase 9B1
remain blocked. QA10 is the next allowed phase.

## Phase QA10 shadow runtime and pre-start monitoring

QA10 verifies QA8 alpha4 and QA9 monitoring freeze lineage, then connects the
shadow runtime path from same-data-mode history windows to typed evidence or
abstention records. The 2019 revised diagnostic now supplies the required
ICSA history window and produces one smoothing output.

Runtime readiness remains separate from candidate capability. The initial
claims evaluator is still a smoothing/noise-filter evaluator only; it is not
directional phase evidence, does not emit a candidate phase, and does not
produce a current phase decision.

The prospective registry remains pre-start. First eligible period is
`2026-07`; first canonical eligible as-of is `2026-08-31`. Before then no real
record may be written. Revised mode is limited to diagnostics and temporary
fixtures, not real prospective registry records.

Registry records are append-only, hash-chained, and contain typed evidence or
abstention metadata only. Corrections append a new record and preserve the
original. QA10 adds no automatic schedule. Production v1 is unchanged, holdout
is not registered, real backtest progression remains blocked, and Phase 9B1
remains blocked. QA11 is the next allowed phase.

## Phase QA11 book-core evaluator and forward data gaps

QA11 splits monitoring readiness into evidence-recording runtime,
single-role observation monitoring, multi-role observation monitoring,
major-group observation monitoring, phase-evidence monitoring, and candidate
monitoring gates. Observation readiness is not phase evidence readiness.

The 40 canonical roles now have separate historical strict and forward capture
status. Historical strict gaps do not automatically block future capture, and
forward capture readiness does not imply historical point-in-time readiness.
ADP and other access/source gaps remain blocked rather than silently
substituted.

observation-only evaluators now cover multiple forward-ready roles. They may
record raw direction, raw level, raw growth, or smoothed level metadata, but
raw direction is not a turning point, one-period movement is not confirmation,
and the three-month claims moving average remains only a noise filter.

The prospective registry remains pre-start with `real_registry_record_count=0`
and first eligible period `2026-07`. Candidate capability remains false,
candidate monitoring remains disabled, holdout is not registered, production
v1 is unchanged, real backtest progression remains blocked, and Phase 9B1
remains blocked. QA12 is the next allowed phase.

## Phase QA12 major-group manual start readiness

QA12 reconciles major-group readiness semantics and adds the manual-start
preflight stack for the first forward observation period. Observation contract
readiness, live no-write source preflight, period completeness, phase-evidence
readiness, and candidate capability are separate gates.

The first eligible period remains `2026-07`, and the first canonical as-of
remains `2026-08-31`. QA12 builds a first-period manifest and preview bundle
only; the protocol is not started, no real registry record is written, and
candidate monitoring remains disabled.

After QA12 the recommended next action is
`WAIT_FOR_FIRST_ELIGIBLE_AS_OF`. Production v1 is unchanged, holdout is not
registered, real backtest progression remains blocked, and Phase 9B1 remains
blocked.

## Phase 10 book-core official source adapter remediation

Phase 10 runs on the development remediation track. It reconciles the 16
forward-blocked book-core roles from canonical contracts, verifies source
identity and economic equivalence for all 40 canonical roles, implements every
safely available official shadow-only adapter, and records genuine blockers
where authorized access, a public official equivalent, or release semantics are
still unavailable.

The remediation adds 11 shadow-only official-source adapters and moves 11 roles
into forward capture readiness. The remaining five roles are explicit genuine
blockers: ADP employment, consumer confidence, publication-lag awareness, real
disposable income versus consumption relation, and sustainable inflation
interpretation. Source identity verified does not imply historical strict
readiness; adapter implemented does not imply phase evidence readiness;
observation runtime readiness does not imply candidate readiness.

The prospective track is unchanged: observation period `2026-07`, canonical
as-of `2026-08-31`, earliest possible manual append `2026-10-31`, zero real
registry records, zero write attempts, protocol not started, candidate
monitoring disabled, and next action `WAIT_FOR_FIRST_ELIGIBLE_AS_OF`. New
adapters remain shadow-only, production v1 is unchanged, QA12 first-period
freeze is preserved, holdout is not registered, real backtest progression
remains blocked, and Phase 9B1 remains blocked. Phase 11 can continue
book-core phase-evidence evaluator work without touching the prospective clock.

## Phase 11 North Star and book-core phase evidence

Phase 11 institutionalizes the project North Star in
`docs/project_north_star.md` and `specs/common/project_north_star_contract.yaml`.
Future phases must map work to product capabilities, web surfaces, mandatory
semantic distinctions, and the final definition of done before claiming
closure.

Phase 11 also expands shadow-only book-core phase-evidence evaluators. Raw
observations, transition watches, confirmations, candidate phases, current
phases, and production decisions remain separate. The three-month claims moving
average remains a noise filter, not phase support. Safe evaluators now emit
governed research-only evidence states for book-core roles whose source,
transformation, and rule semantics are complete without arbitrary thresholds or
weights.

Remaining gaps stay explicit: source/access blockers, composite interpretation
rules, unresolved qualitative semantics, and methodology requirements do not
count as completed phase evidence. Candidate capability remains false,
production v1 is unchanged, prospective registry records remain zero, the
prospective track continues to wait for `WAIT_FOR_FIRST_ELIGIBLE_AS_OF`, and
real backtest progression plus Phase 9B1 remain blocked.

## Agent workflow / self-repair

Agent implementation tasks should follow the repo operating contract and phase acceptance gates before reporting completion.

Reference files:

```text
AGENTS.md
docs/agent_workflow.md
specs/backtests/phase_acceptance_gates.yaml
docs/prompt_templates.md
```

The workflow requires implementation, tests, domain command execution, JSON/stdout inspection, hard-gate comparison, repair, and rerun until all hard gates pass or a real blocker is reached. It does not change formal scoring, resolver logic, FRED provider behavior, dashboard output, or GitHub Pages workflow.

## Retired GitHub Pages deployment

GitHub Pages deployment is retired as of Phase 90. The repository keeps CI and
source-control workflows, but no workflow may configure, upload, or deploy
GitHub Pages artifacts. Local generated output under `public/` remains ignored
and must not be committed.

The new deployment path is a private NAS dynamic service with Postgres-backed
data and a private mobile access model.

## Next steps

1. Add YAML loading and validation for `specs/indicator_catalog.yaml`.
2. Validate FRED metadata and cache freshness for catalog series.
3. Implement trend-aware indicator scoring with tests for rising, falling, flat, spike, missing, stale, and insufficient-history cases.
4. Implement the phase transition engine with persistence, coverage, confidence, and static snapshot state.
5. Generate public JSON and a simple static HTML dashboard.

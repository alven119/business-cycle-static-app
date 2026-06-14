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

## Phase 5B GitHub Pages deployment

Phase 5B adds the GitHub Actions workflow at `.github/workflows/pages.yml`. The repository must define the `FRED_API_KEY` repository secret for scheduled or manual dashboard deployment. Local generated output under `public/` remains ignored and is not committed; GitHub Pages is deployed from the CI-generated `public` artifact.

See `docs/github_pages_deployment.md` for setup and troubleshooting.

## Next steps

1. Add YAML loading and validation for `specs/indicator_catalog.yaml`.
2. Validate FRED metadata and cache freshness for catalog series.
3. Implement trend-aware indicator scoring with tests for rising, falling, flat, spike, missing, stale, and insufficient-history cases.
4. Implement the phase transition engine with persistence, coverage, confidence, and static snapshot state.
5. Generate public JSON and a simple static HTML dashboard.

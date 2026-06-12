# Business Cycle Static App

Python-first static dashboard for business-cycle investing.

This repository is currently in early implementation. It has a minimal FRED data provider and raw CSV cache, but does not yet score indicators, classify phases, or render the final dashboard.

## Current structure

- `src/business_cycle/`: Python package root.
- `data_sources` package: data providers for public macro data providers such as FRED.
- `src/business_cycle/storage/`: filesystem helpers for raw, normalized, and public outputs.
- `src/business_cycle/indicators/`: future indicator catalog loading and trend-aware scoring.
- `src/business_cycle/phases/`: future phase scoring and transition engine.
- `src/business_cycle/render/`: future static dashboard rendering.
- `specs/indicator_catalog.yaml`: minimal indicator metadata examples.
- `specs/phases/recovery.yaml`: minimal recovery phase spec example.
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
FRED_API_KEY=your_fred_api_key_here
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

## Next steps

1. Add YAML loading and validation for `specs/indicator_catalog.yaml`.
2. Validate FRED metadata and cache freshness for catalog series.
3. Implement trend-aware indicator scoring with tests for rising, falling, flat, spike, missing, stale, and insufficient-history cases.
4. Implement the phase transition engine with persistence, coverage, confidence, and static snapshot state.
5. Generate public JSON and a simple static HTML dashboard.

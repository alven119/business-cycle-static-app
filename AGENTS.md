# AGENTS.md

## Project identity

This repository implements a Python-first static web app for business-cycle investing.

The system maps macroeconomic indicators to four economic-cycle phases:

1. recession
2. recovery
3. growth
4. boom

The output is a static dashboard deployable to GitHub Pages and readable on iPhone Safari.

## Core principle

Do not classify the economic phase from a single latest data point.

Most indicators must be interpreted through trend, momentum, reversal, percentile, persistence, and confidence rules.

The project must produce explainable outputs:
- current phase
- phase scores
- transition radar
- indicator-level reasoning
- data freshness
- confidence
- missing-data impact

## Architecture preference

Prefer:
- Python-first implementation
- deterministic scoring
- YAML specs for indicator and phase definitions
- CSV/Parquet for raw and normalized data
- JSON for public static-site output
- Jinja2 or simple static HTML rendering
- pytest tests for all scoring behavior

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

## Scoring rules

Every indicator scoring implementation must define:
- input series
- frequency
- direction
- transformation
- trend window
- confirmation window
- score range
- confidence impact
- stale_after_days
- fallback behavior
- human-readable explanation

## Testing expectations

When changing scoring logic, add or update tests.

At minimum run:

```bash
pytest
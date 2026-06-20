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

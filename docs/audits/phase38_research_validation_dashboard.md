# Phase 38 Research Validation Dashboard

Phase 38 adds a local, research-only dashboard vertical slice for the historical
validation artifacts built through alpha34. The dashboard is generated from
runtime builders, not from committed generated JSON.

Local build:

```bash
.venv/bin/python scripts/build_research_validation_dashboard.py \
  --output-dir /tmp/business_cycle_phase38_dashboard
```

Local preview:

```bash
.venv/bin/python scripts/serve_research_validation_dashboard.py \
  --directory /tmp/business_cycle_phase38_dashboard \
  --host 127.0.0.1 \
  --port 8765
```

The dashboard presents five historical scenarios: two comparable scenarios and
three not-comparable scenarios. It displays research decision states, offline
validation label buckets, comparison status, preregistered historical metric
artifacts, evidence rows, PIT gaps, blocker diagnostics, and freeze lineage.

Safety boundaries:

- The dashboard is local research-only and not production output.
- Candidate and current outputs remain disabled.
- Historical labels do not enter runtime rules or evaluators.
- Blocked and abstained scenarios are not counted as wrong predictions.
- Economic performance metrics and portfolio backtests remain unavailable.
- QA12 dates, prospective registry state, and production behavior remain
  unchanged.

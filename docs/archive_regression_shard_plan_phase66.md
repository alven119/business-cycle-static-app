# Phase66 Archive Regression Shard Plan

Phase66 keeps the Phase65 default product-core suite small while making archive
regression visible and diagnosable.

The archive suite is not deleted. It is split into shards:

- `legacy_v1_compatibility`
- `phase_closure_history`
- `historical_validation_replay`
- `portfolio_policy_research`
- `source_provider_cache`
- `book_core_shadow_governance`
- `dashboard_rendering_archive`
- `infrastructure_misc_archive`

## Why This Exists

The default pytest loop protects current product work: declared state, legal
transition monitoring, indicator explanations, source risk, chart payloads, and
dashboard surfaces.

The archive shards protect history. They make nightly failures actionable by
showing whether a regression belongs to legacy v1 compatibility, historical
closure seals, data-source plumbing, book-core governance, dashboard rendering,
or miscellaneous infrastructure.

## Product Capability Impact

This phase does not raise product capability percentages. It improves delivery
speed and fault isolation for the capabilities the user prioritizes:

- C1 business-cycle phase assessment
- C2 transition-risk detection
- C3 explainability and attribution
- dashboard current research surfaces

Future product phases can keep improving transition timing replay, actual chart
coverage, and indicator explanations without rerunning the entire historical
engineering archive on every local loop.

## Safety Boundaries

The shard plan does not:

- delete legacy or closure tests
- weaken safety scans
- run live optional tests
- enable candidate/current phase output
- change production behavior
- write public, backtest, prospective, raw, cache, or secret outputs

# Phase65 Test Suite Reduction Plan

Phase65 turns the default test loop into a product-core suite instead of a
full repository-history regression run.

The mature product direction remains:

- declared current cycle state
- ordered legal transition monitoring
- indicator and major-group explanations
- source risk and freshness visibility
- dashboard surfaces for research and education

The default suite is capped at 30 test files and protects the current priority
capabilities:

- C1 business-cycle phase assessment
- C2 transition-risk detection
- C3 explainability and attribution
- dashboard current research surfaces

## Phase Closure Tests

Phase closure tests are historical acceptance seals. They prove that a past
phase met its hard gates at the time it was implemented: no candidate/current
phase emission, no unsafe output, no production behavior change, no forbidden
repository output, and valid freeze or lineage assertions.

These tests are useful for traceability, but they should not all run in every
normal development loop. Phase65 keeps them as archive regression coverage and
nightly regression inputs while removing them from default pytest and full-ci.

## Legacy V1 Tests

Legacy production v1 tests no longer represent the mature product direction.
They are not deleted in this phase because they still document compatibility
boundaries and help catch accidental production migration. They are marked as
archive regression and excluded from default pytest.

## CI Tiers

- fast-ci: lint, whitespace, safety scans, QA0, and the highest-value product
  core subset.
- full-ci: default product-core pytest, lint, safety scans, and current product
  closure checks.
- nightly-ci: archive regression pytest and the full historical closure bundle.

## Integration With The Capability Roadmap

This phase is a delivery-speed enabler for the existing 95 percent capability
roadmap. It does not raise or lower capability percentages by itself. It keeps
the remaining work focused on completing C1/C2/C3 and dashboard usability
instead of spending every loop rerunning archived scaffolding.

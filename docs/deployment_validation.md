# Deployment Validation

This checklist validates the GitHub Pages research dashboard after deployment.
It checks generated-site usability and doctrine boundaries. It does not change
legacy scoring, resolver behavior, portfolio policy logic, or source provider
behavior.

## GitHub Actions Checks

- `workflow_dispatch` starts successfully.
- `pytest` passes without `FRED_API_KEY`.
- `ruff check .` passes.
- `scripts/build_github_pages_research_dashboard.py --output-dir public` passes.
- `scripts/validate_github_pages_research_dashboard.py --site-dir public` passes.
- `public/index.html` exists.
- `public/latest-evidence.html` exists.
- `public/portfolio-replay.html` exists.
- `public/data/dashboard_bundle.json` exists.
- `actions/upload-pages-artifact` succeeds.
- `actions/deploy-pages` succeeds.
- GitHub Pages URL is produced.

## Page Checks

- The homepage opens.
- The page is labeled as a research dashboard.
- The page does not present a standalone phase winner, phase score answer, or
  live current phase classifier.
- Declared cycle state and legal next transition context are visible.
- `latest-evidence.html` opens.
- Indicator cards show source, method, freshness, provenance, and explanation.
- Indicator cards expose trend drilldown targets.
- YTD, trailing 1Y, and trailing 5Y chart controls or payload markers are
  present.
- Transition risk evidence accumulation is visible and separates watch from
  confirmation.
- `portfolio-replay.html` opens.
- Portfolio policy templates are labeled as research templates.
- Portfolio replay/backtest surfaces do not provide personalized trade
  instructions.
- The page states that research templates are not live allocation advice.

## iPhone Safari QA

- Homepage opens on iPhone Safari.
- `latest-evidence.html` and `portfolio-replay.html` are reachable.
- Cards do not overflow horizontally.
- Chart controls are tappable.
- Text remains readable in narrow viewport.
- Trust metadata and caveats are visible.

## Common Issues

`Pages 404`

Confirm repository Pages source is `GitHub Actions`, and confirm the deploy job
completed. Pages may need a short cache refresh window after deployment.

`workflow passed but the page still looks old`

Open the deployment URL in a private window or hard refresh. Confirm the
deployed commit includes `scripts/build_github_pages_research_dashboard.py` in
`.github/workflows/pages.yml`.

`latest-evidence.html is missing`

The workflow may still be using the legacy site builder. The Pages build step
must call `scripts/build_github_pages_research_dashboard.py`.

`Deploy failed, try again later`

GitHub Pages sometimes fails after artifact creation. Re-run the workflow once.
If the failure repeats, inspect repository Pages settings and deploy job logs.

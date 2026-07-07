from pathlib import Path


WORKFLOW_PATH = Path(".github/workflows/pages.yml")


def test_pages_workflow_exists() -> None:
    assert WORKFLOW_PATH.is_file()


def test_pages_workflow_does_not_require_fred_secret_for_research_dashboard() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "FRED_API_KEY: ${{ secrets.FRED_API_KEY }}" not in workflow
    assert "FRED_API_KEY" + "=" not in workflow
    assert "your_fred_api_key" not in workflow


def test_pages_workflow_uploads_public_artifact() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "actions/configure-pages@v6" in workflow
    assert "actions/upload-pages-artifact@v5" in workflow
    assert "actions/deploy-pages@v5" in workflow
    assert "path: public" in workflow


def test_pages_workflow_uses_node24_pages_actions_without_unsecure_node20_fallback() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "actions/configure-pages@v5" not in workflow
    assert "actions/upload-pages-artifact@v3" not in workflow
    assert "actions/deploy-pages@v4" not in workflow
    assert "ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION" not in workflow


def test_pages_workflow_does_not_commit_generated_public_output() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    forbidden_commands = [
        "git add public",
        "git add -A",
        "git commit",
        "git push",
    ]
    for command in forbidden_commands:
        assert command not in workflow


def test_pages_workflow_uses_research_dashboard_builder_not_legacy_site() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "python scripts/build_github_pages_research_dashboard.py" in workflow
    assert "python scripts/build_site.py" not in workflow
    assert "python scripts/run_cycle_pipeline.py" not in workflow
    assert "python scripts/update_catalog_data.py" not in workflow


def test_pages_workflow_validates_research_dashboard_site() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "python scripts/validate_github_pages_research_dashboard.py" in workflow
    assert "test -f public/latest-evidence.html" in workflow
    assert "test -f public/portfolio-replay.html" in workflow
    assert "test -f public/data/dashboard_bundle.json" in workflow

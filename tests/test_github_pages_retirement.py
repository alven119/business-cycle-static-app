from __future__ import annotations

from pathlib import Path


def test_github_pages_workflow_is_retired() -> None:
    assert not Path(".github/workflows/pages.yml").exists()


def test_remaining_ci_workflows_do_not_use_pages_actions() -> None:
    workflow_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in Path(".github/workflows").glob("*.yml")
    )

    forbidden = [
        "actions/configure-pages",
        "actions/upload-pages-artifact",
        "actions/deploy-pages",
        "build_github_pages_research_dashboard",
        "validate_github_pages_research_dashboard",
    ]
    for marker in forbidden:
        assert marker not in workflow_text

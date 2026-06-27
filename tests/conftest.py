from __future__ import annotations

import os
from pathlib import Path

import pytest

from business_cycle.audits.test_suite_doctrine_quarantine import markers_for_test_path


def pytest_configure() -> None:
    """Make subprocess(["python", ...]) use the project virtualenv."""

    venv_bin = Path(__file__).resolve().parents[1] / ".venv" / "bin"
    os.environ["PATH"] = f"{venv_bin}{os.pathsep}{os.environ.get('PATH', '')}"


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Apply doctrine quarantine markers from the curated high-risk test map."""

    for item in items:
        for marker_name in markers_for_test_path(Path(str(item.fspath))):
            item.add_marker(getattr(pytest.mark, marker_name))

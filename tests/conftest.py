from __future__ import annotations

import os
from pathlib import Path


def pytest_configure() -> None:
    """Make subprocess(["python", ...]) use the project virtualenv."""

    venv_bin = Path(__file__).resolve().parents[1] / ".venv" / "bin"
    os.environ["PATH"] = f"{venv_bin}{os.pathsep}{os.environ.get('PATH', '')}"

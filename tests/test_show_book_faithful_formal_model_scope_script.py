from __future__ import annotations

import subprocess
import sys


def test_show_book_faithful_formal_model_scope_script() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/show_book_faithful_formal_model_scope.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "book_faithful_scope_contract_ready=true" in completed.stdout
    assert "book_faithful_scope_complete=false" in completed.stdout


from __future__ import annotations

import subprocess
import sys

from business_cycle.validation.controlled_pit_backfill import (
    build_controlled_pit_backfill_plan,
    summarize_controlled_pit_backfill,
    write_controlled_pit_backfill,
)


def test_controlled_pit_backfill_is_no_write_without_live_credential(
    monkeypatch,
) -> None:
    monkeypatch.delenv("FRED" + "_API_KEY", raising=False)
    build_controlled_pit_backfill_plan.cache_clear()
    summary = summarize_controlled_pit_backfill()

    assert summary["controlled_pit_backfill_ready"] is True
    assert summary["network_attempted"] is False
    assert summary["cache_write_attempted"] is False
    assert summary["backfill_executed_series_count"] == 0
    assert summary["secret_logged_count"] == 0
    assert summary["raw_data_committed_count"] == 0


def test_run_controlled_pit_backfill_script(tmp_path) -> None:
    output = tmp_path / "phase37_controlled_pit_backfill.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_controlled_pit_backfill.py",
            "--output",
            str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert output.is_file()
    assert "controlled_pit_backfill_ready=True" in result.stdout
    assert "network_attempted=False" in result.stdout
    assert "result=passed" in result.stdout


def test_controlled_pit_backfill_refuses_repo_output_path() -> None:
    try:
        write_controlled_pit_backfill(
            build_controlled_pit_backfill_plan(),
            output="data/backtests/phase37.json",
        )
    except ValueError as exc:
        assert "under /tmp" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("expected repo output path to be rejected")

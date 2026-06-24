from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from business_cycle.validation.historical_comparison_coverage_metrics import (
    load_historical_comparison_coverage_metrics_contract,
)


def test_run_historical_comparison_coverage_metrics_script(tmp_path: Path) -> None:
    output_dir = tmp_path / "phase23_comparison_coverage_metrics"

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_historical_comparison_coverage_metrics.py",
            "--output-dir",
            str(output_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    stdout = completed.stdout
    output_file = output_dir / "comparison_coverage_metrics.json"
    payload = json.loads(output_file.read_text(encoding="utf-8"))
    forbidden = set(
        load_historical_comparison_coverage_metrics_contract()[
            "forbidden_metric_fields"
        ]
    )
    assert "comparison_coverage_metrics_contract_ready=true" in stdout
    assert "comparison_coverage_metrics_runtime_ready=true" in stdout
    assert "comparison_coverage_metric_count=14" in stdout
    assert "metric_computation_enabled=true" in stdout
    assert "metric_computation_scope=comparison_coverage_only" in stdout
    assert "historical_accuracy_metric_count=0" in stdout
    assert "economic_performance_metric_count=0" in stdout
    assert "predicted_label_output_count=0" in stdout
    assert output_file.is_file()
    assert payload["metric_computation_scope"] == "comparison_coverage_only"
    assert forbidden.isdisjoint(_all_keys(payload))


def test_run_historical_comparison_coverage_metrics_rejects_repo_output() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_historical_comparison_coverage_metrics.py",
            "--output-dir",
            "data/backtests/phase23",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode != 0
    assert "under /tmp" in completed.stderr


def test_comparison_coverage_script_does_not_write_forbidden_repo_outputs(
    tmp_path: Path,
) -> None:
    subprocess.run(
        [
            sys.executable,
            "scripts/run_historical_comparison_coverage_metrics.py",
            "--output-dir",
            str(tmp_path / "phase23_comparison_coverage_metrics"),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    for root in ("data/backtests", "data/prospective", "public"):
        path = Path(root)
        assert not path.exists() or not any(item.is_file() for item in path.rglob("*"))


def _all_keys(value: Any) -> set[str]:
    if isinstance(value, dict):
        keys = set(value)
        for item in value.values():
            keys.update(_all_keys(item))
        return keys
    if isinstance(value, list):
        keys: set[str] = set()
        for item in value:
            keys.update(_all_keys(item))
        return keys
    return set()

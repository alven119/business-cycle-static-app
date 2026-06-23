from __future__ import annotations

import json
from pathlib import Path

import pytest

from business_cycle.validation.historical_validation_dry_run import (
    run_historical_validation_dry_run,
)
from business_cycle.validation.historical_validation_result_writer import (
    validate_historical_validation_result_artifact,
    write_historical_validation_dry_run_results,
)


def test_historical_validation_result_writer_writes_tmp_artifacts(
    tmp_path: Path,
) -> None:
    dry_run = run_historical_validation_dry_run()
    output = write_historical_validation_dry_run_results(
        dry_run,
        output_dir=tmp_path,
    )

    assert output["scenario_result_artifact_write_count"] == 5
    assert output["summary_artifact_written"] is True
    assert output["written_file_count"] == 6
    for path in output["written_files"]:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        assert payload


def test_historical_validation_result_writer_rejects_non_tmp_output() -> None:
    dry_run = run_historical_validation_dry_run()

    with pytest.raises(ValueError, match="under /tmp"):
        write_historical_validation_dry_run_results(
            dry_run,
            output_dir=Path("data/backtests/phase20"),
        )


def test_historical_validation_result_artifact_validator_rejects_metrics() -> None:
    dry_run = run_historical_validation_dry_run()
    artifact = dict(dry_run["result_artifacts"][0])
    artifact["historical_accuracy"] = 1.0

    validation = validate_historical_validation_result_artifact(artifact)

    assert validation["artifact_schema_valid"] is False
    assert validation["prohibited_result_field_count"] == 1

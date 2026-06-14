"""Run full-horizon calibration experiments and acceptance review."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from business_cycle.backtests.calibration_experiment import (
    CalibrationExperimentError,
    run_calibration_experiment,
)
from business_cycle.backtests.calibration_review import write_calibration_acceptance_review

DEFAULT_CONTROLS_PATH = Path("specs/backtests/transition_controls_enabled_experiment.yaml")
DEFAULT_OUTPUT_DIR = Path("data/backtests/calibration")
DEFAULT_WINDOWS_PATH = Path("specs/backtests/calibration_acceptance_windows.yaml")

ExperimentRunner = Callable[..., dict[str, Any]]
ReviewWriter = Callable[..., Path]


def run_full_horizon_calibration(
    *,
    experiment_id: str,
    catalog_path: str | Path = Path("specs/backtests/scenarios.yaml"),
    controls_config_path: str | Path = DEFAULT_CONTROLS_PATH,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    scenario_id: str | None = None,
    windows_path: str | Path = DEFAULT_WINDOWS_PATH,
    experiment_runner: ExperimentRunner | None = None,
    review_writer: ReviewWriter | None = None,
) -> dict[str, Any]:
    """Run calibration across full scenario windows and write acceptance review."""

    return write_full_horizon_calibration_outputs(
        experiment_id=experiment_id,
        catalog_path=catalog_path,
        controls_config_path=controls_config_path,
        output_dir=output_dir,
        scenario_id=scenario_id,
        windows_path=windows_path,
        experiment_runner=experiment_runner,
        review_writer=review_writer,
    )


def write_full_horizon_calibration_outputs(
    *,
    experiment_id: str,
    catalog_path: str | Path = Path("specs/backtests/scenarios.yaml"),
    controls_config_path: str | Path = DEFAULT_CONTROLS_PATH,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    scenario_id: str | None = None,
    windows_path: str | Path = DEFAULT_WINDOWS_PATH,
    experiment_runner: ExperimentRunner | None = None,
    review_writer: ReviewWriter | None = None,
) -> dict[str, Any]:
    """Run full-horizon calibration and write the acceptance review JSON."""

    if not experiment_id:
        raise CalibrationExperimentError("experiment_id must be non-empty")
    controls_path = Path(controls_config_path)
    if not controls_path.exists():
        raise CalibrationExperimentError(f"transition controls config does not exist: {controls_path}")
    runner = experiment_runner or run_calibration_experiment
    summary = runner(
        experiment_id=experiment_id,
        catalog_path=catalog_path,
        controls_config_path=controls_path,
        output_dir=output_dir,
        max_periods=None,
        scenario_id=scenario_id,
    )

    experiment_root = Path(output_dir) / experiment_id
    summary_path = Path(summary.get("output_path") or experiment_root / "calibration_summary.json")
    output_path = experiment_root / "calibration_acceptance_review.json"
    writer = review_writer or write_calibration_acceptance_review
    review_path = writer(
        summary_path=summary_path,
        windows_path=windows_path,
        output_path=output_path,
    )
    summary["acceptance_review_path"] = str(review_path)
    summary["full_horizon"] = True
    return summary

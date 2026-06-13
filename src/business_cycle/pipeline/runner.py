"""Local end-to-end cycle pipeline runner."""

from __future__ import annotations

import subprocess
import sys
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


@dataclass(frozen=True)
class PipelineRunResult:
    """Result of a local pipeline run."""

    indicator_scores_path: Path
    phase_scores_path: Path
    current_phase_decision_path: Path
    cycle_snapshot_path: Path
    steps: list[dict[str, str | int]]
    success: bool
    message: str


StepRunner = Callable[[str, list[str]], int]


def run_cycle_pipeline(
    *,
    as_of: str | None = None,
    previous_phase_id: str | None = None,
    update_data: bool = False,
    force_refresh: bool = False,
    indicator_ids: list[str] | None = None,
    phase_ids: list[str] | None = None,
    output_dir: str | Path = "data/derived",
    step_runner: StepRunner | None = None,
) -> PipelineRunResult:
    """Run local pipeline steps in order using existing script entry points."""

    output_root = Path(output_dir)
    indicator_scores_path = output_root / "indicator_scores.json"
    phase_scores_path = output_root / "phase_scores.json"
    current_phase_decision_path = output_root / "current_phase_decision.json"
    cycle_snapshot_path = output_root / "cycle_snapshot.json"
    runner = step_runner or _default_step_runner

    steps_to_run = _build_steps(
        as_of=as_of,
        previous_phase_id=previous_phase_id,
        update_data=update_data,
        force_refresh=force_refresh,
        indicator_ids=indicator_ids,
        phase_ids=phase_ids,
        indicator_scores_path=indicator_scores_path,
        phase_scores_path=phase_scores_path,
        current_phase_decision_path=current_phase_decision_path,
        cycle_snapshot_path=cycle_snapshot_path,
    )

    completed_steps: list[dict[str, str | int]] = []
    for step in steps_to_run:
        step_name = step["name"]
        args = step["args"]
        exit_code = runner(step_name, args)
        completed_steps.append({"name": step_name, "exit_code": exit_code, "output_path": step["output_path"]})
        if exit_code != 0:
            return PipelineRunResult(
                indicator_scores_path=indicator_scores_path,
                phase_scores_path=phase_scores_path,
                current_phase_decision_path=current_phase_decision_path,
                cycle_snapshot_path=cycle_snapshot_path,
                steps=completed_steps,
                success=False,
                message=f"Pipeline step failed: {step_name} exit_code={exit_code}",
            )

    return PipelineRunResult(
        indicator_scores_path=indicator_scores_path,
        phase_scores_path=phase_scores_path,
        current_phase_decision_path=current_phase_decision_path,
        cycle_snapshot_path=cycle_snapshot_path,
        steps=completed_steps,
        success=True,
        message="Pipeline completed successfully.",
    )


def _build_steps(
    *,
    as_of: str | None,
    previous_phase_id: str | None,
    update_data: bool,
    force_refresh: bool,
    indicator_ids: list[str] | None,
    phase_ids: list[str] | None,
    indicator_scores_path: Path,
    phase_scores_path: Path,
    current_phase_decision_path: Path,
    cycle_snapshot_path: Path,
) -> list[dict[str, list[str] | str]]:
    steps: list[dict[str, list[str] | str]] = []
    if update_data:
        update_args: list[str] = []
        if force_refresh:
            update_args.append("--force-refresh")
        for indicator_id in indicator_ids or []:
            update_args.extend(["--indicator-id", indicator_id])
        steps.append({"name": "update_catalog_data", "args": update_args, "output_path": "data/raw"})

    indicator_args = ["--output-path", str(indicator_scores_path)]
    if as_of:
        indicator_args.extend(["--as-of", as_of])
    for indicator_id in indicator_ids or []:
        indicator_args.extend(["--indicator-id", indicator_id])
    steps.append(
        {
            "name": "score_indicators",
            "args": indicator_args,
            "output_path": str(indicator_scores_path),
        }
    )

    phase_args = ["--indicator-scores-path", str(indicator_scores_path), "--output-path", str(phase_scores_path)]
    if as_of:
        phase_args.extend(["--as-of", as_of])
    for phase_id in phase_ids or []:
        phase_args.extend(["--phase-id", phase_id])
    steps.append({"name": "score_phases", "args": phase_args, "output_path": str(phase_scores_path)})

    resolver_args = ["--phase-scores-path", str(phase_scores_path), "--output-path", str(current_phase_decision_path)]
    if previous_phase_id:
        resolver_args.extend(["--previous-phase-id", previous_phase_id])
    steps.append(
        {
            "name": "resolve_current_phase",
            "args": resolver_args,
            "output_path": str(current_phase_decision_path),
        }
    )

    snapshot_args = [
        "--indicator-scores-path",
        str(indicator_scores_path),
        "--phase-scores-path",
        str(phase_scores_path),
        "--current-phase-decision-path",
        str(current_phase_decision_path),
        "--output-path",
        str(cycle_snapshot_path),
    ]
    if as_of:
        snapshot_args.extend(["--as-of", as_of])
    steps.append(
        {
            "name": "build_cycle_snapshot",
            "args": snapshot_args,
            "output_path": str(cycle_snapshot_path),
        }
    )
    return steps


def _default_step_runner(step_name: str, args: list[str]) -> int:
    script_names = {
        "update_catalog_data": "update_catalog_data.py",
        "score_indicators": "score_indicators.py",
        "score_phases": "score_phases.py",
        "resolve_current_phase": "resolve_current_phase.py",
        "build_cycle_snapshot": "build_cycle_snapshot.py",
    }
    script_name = script_names.get(step_name)
    if script_name is None:
        raise ValueError(f"Unknown pipeline step: {step_name}")

    project_root = _project_root()
    script_path = project_root / "scripts" / script_name
    env = dict(os.environ)
    src_dir = str(project_root / "src")
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        src_dir if not existing_pythonpath else f"{src_dir}{os.pathsep}{existing_pythonpath}"
    )
    completed = subprocess.run(  # noqa: S603 - script path is selected from a fixed allowlist.
        [sys.executable, str(script_path), *args],
        cwd=project_root,
        env=env,
        check=False,
    )
    return completed.returncode


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]

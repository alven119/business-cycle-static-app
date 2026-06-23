"""Phase 20 label-blind dry-run result artifact writer."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


DEFAULT_DRY_RUN_CONTRACT_PATH = Path(
    "specs/common/historical_validation_dry_run_contract.yaml"
)
ALLOWED_OUTPUT_ROOT = Path("/tmp")
PROHIBITED_OUTPUT_ROOTS = (
    Path("data/backtests"),
    Path("data/prospective"),
    Path("public"),
)


def load_historical_validation_dry_run_contract(
    path: str | Path = DEFAULT_DRY_RUN_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("historical validation dry-run contract must map")
    contract = payload.get("historical_validation_dry_run_contract")
    if not isinstance(contract, dict):
        raise ValueError("historical_validation_dry_run_contract must be a mapping")
    return contract


def validate_historical_validation_result_artifact(
    artifact: dict[str, Any],
    *,
    contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    contract = contract or load_historical_validation_dry_run_contract()
    allowed_fields = set(contract["allowed_result_fields"])
    forbidden_fields = set(contract["forbidden_result_fields"])
    output_keys = set(artifact)
    forbidden_paths = _find_forbidden_output_paths(artifact, forbidden_fields)
    missing_allowed_fields = allowed_fields.difference(output_keys)
    unexpected_fields = output_keys.difference(allowed_fields)
    return {
        "artifact_schema_valid": (
            not missing_allowed_fields
            and not unexpected_fields
            and not forbidden_paths
            and artifact.get("label_used_by_runtime") is False
            and artifact.get("metric_computation_enabled") is False
            and artifact.get("backtest_execution_enabled") is False
            and artifact.get("candidate_phase_emitted") is False
            and artifact.get("current_phase_emitted") is False
            and isinstance(artifact.get("trust_metadata"), dict)
        ),
        "missing_allowed_field_count": len(missing_allowed_fields),
        "unexpected_field_count": len(unexpected_fields),
        "prohibited_result_field_count": len(forbidden_paths),
        "forbidden_output_paths": forbidden_paths,
    }


def write_historical_validation_dry_run_results(
    dry_run: dict[str, Any],
    *,
    output_dir: str | Path,
) -> dict[str, Any]:
    output_path = _validated_output_dir(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    contract = load_historical_validation_dry_run_contract()
    artifacts = dry_run["result_artifacts"]
    written_files: list[str] = []
    for artifact in artifacts:
        validation = validate_historical_validation_result_artifact(
            artifact,
            contract=contract,
        )
        if not validation["artifact_schema_valid"]:
            raise ValueError(
                "invalid historical validation result artifact: "
                f"{artifact['scenario_id']} {validation}"
            )
        artifact_path = output_path / f"{artifact['scenario_id']}.json"
        artifact_path.write_text(
            json.dumps(artifact, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        written_files.append(str(artifact_path))
    summary_path = output_path / "dry_run_summary.json"
    summary_path.write_text(
        json.dumps(_summary_payload(dry_run), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    written_files.append(str(summary_path))
    return {
        "output_dir": str(output_path),
        "scenario_result_artifact_write_count": len(artifacts),
        "summary_artifact_written": True,
        "written_file_count": len(written_files),
        "written_files": written_files,
    }


def _summary_payload(dry_run: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in dry_run.items()
        if key != "result_artifacts"
    } | {
        "result_artifact_ids": [
            artifact["scenario_id"] for artifact in dry_run["result_artifacts"]
        ],
    }


def _validated_output_dir(output_dir: str | Path) -> Path:
    path = Path(output_dir)
    resolved = path.resolve()
    if not resolved.is_relative_to(ALLOWED_OUTPUT_ROOT.resolve()):
        raise ValueError(f"Phase 20 dry-run output must be under /tmp: {output_dir}")
    cwd = Path.cwd().resolve()
    for root in PROHIBITED_OUTPUT_ROOTS:
        prohibited = (cwd / root).resolve()
        if resolved.is_relative_to(prohibited):
            raise ValueError(f"refusing prohibited output path: {output_dir}")
    return resolved


def _find_forbidden_output_paths(
    value: Any,
    forbidden: set[str],
    *,
    prefix: str = "",
) -> list[str]:
    if isinstance(value, dict):
        found: list[str] = []
        for key, item in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if key in forbidden:
                found.append(path)
            found.extend(_find_forbidden_output_paths(item, forbidden, prefix=path))
        return found
    if isinstance(value, list):
        found = []
        for index, item in enumerate(value):
            path = f"{prefix}[{index}]"
            found.extend(_find_forbidden_output_paths(item, forbidden, prefix=path))
        return found
    return []

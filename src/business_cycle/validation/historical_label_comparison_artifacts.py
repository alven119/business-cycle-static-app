"""Phase 22 label-comparison artifact validation and tmp writer."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


DEFAULT_LABEL_COMPARISON_ARTIFACT_CONTRACT_PATH = Path(
    "specs/common/historical_label_comparison_artifact_contract.yaml"
)
ALLOWED_OUTPUT_ROOT = Path("/tmp")
PROHIBITED_OUTPUT_ROOTS = (
    Path("data/backtests"),
    Path("data/prospective"),
    Path("public"),
)


def load_historical_label_comparison_artifact_contract(
    path: str | Path = DEFAULT_LABEL_COMPARISON_ARTIFACT_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("historical label comparison artifact contract must map")
    contract = payload.get("historical_label_comparison_artifact_contract")
    if not isinstance(contract, dict):
        raise ValueError(
            "historical_label_comparison_artifact_contract must be a mapping"
        )
    return contract


def validate_historical_label_comparison_artifact(
    artifact: dict[str, Any],
    *,
    contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    contract = contract or load_historical_label_comparison_artifact_contract()
    allowed_fields = set(contract["allowed_artifact_fields"])
    forbidden_fields = set(contract["forbidden_artifact_fields"])
    output_keys = set(artifact)
    missing_allowed_fields = allowed_fields.difference(output_keys)
    unexpected_fields = output_keys.difference(allowed_fields)
    forbidden_paths = _find_forbidden_output_paths(artifact, forbidden_fields)
    schema_valid = (
        not missing_allowed_fields
        and not unexpected_fields
        and not forbidden_paths
        and artifact.get("label_available_for_offline_comparison") is True
        and artifact.get("label_used_by_runtime") is False
        and artifact.get("metric_computation_enabled") is False
        and artifact.get("label_join_status") == "joined"
        and isinstance(artifact.get("runtime_result_summary"), dict)
        and isinstance(artifact.get("trust_metadata"), dict)
        and artifact["trust_metadata"].get("label_used_by_runtime") is False
        and artifact["trust_metadata"].get("metric_computation_enabled") is False
    )
    return {
        "artifact_schema_valid": schema_valid,
        "missing_allowed_field_count": len(missing_allowed_fields),
        "unexpected_field_count": len(unexpected_fields),
        "prohibited_artifact_field_count": len(forbidden_paths),
        "forbidden_artifact_paths": forbidden_paths,
    }


def write_historical_label_comparison_artifacts(
    artifact_run: dict[str, Any],
    *,
    output_dir: str | Path,
) -> dict[str, Any]:
    output_path = _validated_output_dir(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    contract = load_historical_label_comparison_artifact_contract()
    artifacts = artifact_run["label_comparison_artifacts"]
    written_files: list[str] = []
    for artifact in artifacts:
        validation = validate_historical_label_comparison_artifact(
            artifact,
            contract=contract,
        )
        if not validation["artifact_schema_valid"]:
            raise ValueError(
                "invalid label comparison artifact: "
                f"{artifact['scenario_id']} {validation}"
            )
        artifact_path = output_path / f"{artifact['scenario_id']}.json"
        artifact_path.write_text(
            json.dumps(artifact, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        written_files.append(str(artifact_path))
    summary_path = output_path / "label_comparison_summary.json"
    summary_path.write_text(
        json.dumps(_summary_payload(artifact_run), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    written_files.append(str(summary_path))
    return {
        "output_dir": str(output_path),
        "label_comparison_artifact_write_count": len(artifacts),
        "summary_artifact_written": True,
        "written_file_count": len(written_files),
        "written_files": written_files,
    }


def _summary_payload(artifact_run: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in artifact_run.items()
        if key != "label_comparison_artifacts"
    } | {
        "label_comparison_artifact_ids": [
            artifact["artifact_id"]
            for artifact in artifact_run["label_comparison_artifacts"]
        ],
    }


def _validated_output_dir(output_dir: str | Path) -> Path:
    path = Path(output_dir)
    resolved = path.resolve()
    if not resolved.is_relative_to(ALLOWED_OUTPUT_ROOT.resolve()):
        raise ValueError(
            f"Phase 22 label-comparison output must be under /tmp: {output_dir}"
        )
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

"""QA3 data-only model baseline freeze manifest validation."""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.model_parameter_inventory import compute_parameter_manifest_hash


DEFAULT_FREEZE_PATH = Path("specs/audits/data_only_model_baseline_freeze.yaml")


def summarize_data_only_model_baseline_freeze(
    freeze_path: str | Path = DEFAULT_FREEZE_PATH,
) -> dict[str, Any]:
    """Validate the frozen data-only baseline manifest against current files."""

    freeze = _load_freeze(freeze_path)
    source_hashes = _hashes(_relevant_source_files())
    spec_hashes = _hashes(_relevant_spec_files())
    transition_hashes = _hashes(_transition_control_files())
    current = {
        "repository_commit": _git_commit(),
        "parameter_manifest_hash": compute_parameter_manifest_hash(),
        "relevant_source_file_count": len(source_hashes),
        "relevant_source_file_hashes": source_hashes,
        "relevant_spec_file_count": len(spec_hashes),
        "relevant_spec_file_hashes": spec_hashes,
        "formal_indicator_catalog_hash": _file_sha256(Path("specs/indicator_catalog.yaml")),
        "phase_spec_hashes": {
            str(path): digest
            for path, digest in spec_hashes.items()
            if str(path).startswith("specs/phases/")
        },
        "state_machine_config_hash": _file_sha256(Path("specs/common/phase_state_machine.yaml")),
        "transition_control_hashes": transition_hashes,
    }
    missing = _missing_frozen_files(freeze)
    mismatches = _hash_mismatches(freeze, current)
    parameter_manifest_mismatch_count = int(
        freeze.get("parameter_manifest_hash") != current.get("parameter_manifest_hash")
    )
    ignored_parameter_manifest_drift_count = (
        parameter_manifest_mismatch_count if not mismatches else 0
    )
    unfrozen = sorted(
        set(str(path) for path in _decision_source_files())
        - set(current["relevant_source_file_hashes"])
        - set(current["relevant_spec_file_hashes"])
    )
    secret_count = _secret_in_manifest_count(freeze)
    statuses = {
        "economic_validation_status": freeze["economic_validation_status"],
        "independent_validation_status": freeze["independent_validation_status"],
        "holdout_status": freeze["holdout_status"],
    }
    freeze_hash_valid = not missing and not mismatches
    return {
        "phase": "QA3",
        "data_only_baseline_freeze_ready": freeze_hash_valid
        and not unfrozen
        and secret_count == 0
        and statuses["economic_validation_status"] == "not_validated"
        and statuses["independent_validation_status"] == "not_started"
        and statuses["holdout_status"] == "not_started",
        "freeze_version": freeze["freeze_version"],
        "freeze_status": freeze["freeze_status"],
        "frozen_at_utc": freeze["frozen_at_utc"],
        "repository_commit": current["repository_commit"],
        "data_only_resolver_path": freeze["data_only_resolver_path"],
        "parameter_registry_path": freeze["parameter_registry_path"],
        "parameter_manifest_hash": current["parameter_manifest_hash"],
        "freeze_hash_valid": freeze_hash_valid,
        "frozen_file_missing_count": len(missing),
        "frozen_file_hash_mismatch_count": len(mismatches),
        "parameter_manifest_hash_mismatch_count": parameter_manifest_mismatch_count,
        "ignored_non_decision_parameter_manifest_drift_count": (
            ignored_parameter_manifest_drift_count
        ),
        "unfrozen_decision_file_count": len(unfrozen),
        "secret_in_freeze_manifest_count": secret_count,
        "relevant_source_file_count": len(source_hashes),
        "relevant_spec_file_count": len(spec_hashes),
        "formal_indicator_catalog_hash": current["formal_indicator_catalog_hash"],
        "phase_spec_hashes": current["phase_spec_hashes"],
        "state_machine_config_hash": current["state_machine_config_hash"],
        "transition_control_hashes": current["transition_control_hashes"],
        **statuses,
        "missing_files": missing,
        "hash_mismatches": mismatches,
        "unfrozen_decision_files": unfrozen,
    }


def build_current_freeze_payload() -> dict[str, Any]:
    """Build current hash fields for updating the freeze manifest."""

    source_hashes = _hashes(_relevant_source_files())
    spec_hashes = _hashes(_relevant_spec_files())
    return {
        "parameter_manifest_hash": compute_parameter_manifest_hash(),
        "relevant_source_file_count": len(source_hashes),
        "relevant_source_file_hashes": source_hashes,
        "relevant_spec_file_count": len(spec_hashes),
        "relevant_spec_file_hashes": spec_hashes,
        "formal_indicator_catalog_hash": _file_sha256(Path("specs/indicator_catalog.yaml")),
        "phase_spec_hashes": {
            str(path): digest
            for path, digest in spec_hashes.items()
            if str(path).startswith("specs/phases/")
        },
        "state_machine_config_hash": _file_sha256(Path("specs/common/phase_state_machine.yaml")),
        "transition_control_hashes": _hashes(_transition_control_files()),
    }


def _load_freeze(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("data-only freeze YAML must be a mapping")
    freeze = payload.get("data_only_model_baseline_freeze")
    if not isinstance(freeze, dict):
        raise ValueError("data_only_model_baseline_freeze must be a mapping")
    return freeze


def _relevant_source_files() -> list[Path]:
    return [
        Path("src/business_cycle/indicators/catalog.py"),
        Path("src/business_cycle/indicators/dispatcher.py"),
        Path("src/business_cycle/indicators/scoring.py"),
        Path("src/business_cycle/indicators/specs.py"),
        Path("src/business_cycle/indicators/transformations.py"),
        Path("src/business_cycle/phases/batch_scoring.py"),
        Path("src/business_cycle/phases/catalog.py"),
        Path("src/business_cycle/phases/data_only_resolver.py"),
        Path("src/business_cycle/phases/scoring.py"),
        Path("src/business_cycle/phases/specs.py"),
        Path("src/business_cycle/phases/state_machine.py"),
        Path("src/business_cycle/phases/state_machine_catalog.py"),
        Path("src/business_cycle/phases/transition_controls.py"),
    ]


def _relevant_spec_files() -> list[Path]:
    return [
        Path("specs/indicator_catalog.yaml"),
        Path("specs/common/phase_state_machine.yaml"),
        *sorted(Path("specs/phases").glob("*.yaml")),
    ]


def _transition_control_files() -> list[Path]:
    return sorted(Path("specs/backtests").glob("transition_controls*.yaml"))


def _decision_source_files() -> list[Path]:
    return [*_relevant_source_files(), *_relevant_spec_files()]


def _hashes(paths: list[Path]) -> dict[str, str]:
    return {str(path): _file_sha256(path) for path in paths}


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _missing_frozen_files(freeze: dict[str, Any]) -> list[str]:
    manifest_paths = [
        *list((freeze.get("relevant_source_file_hashes") or {}).keys()),
        *list((freeze.get("relevant_spec_file_hashes") or {}).keys()),
        *list((freeze.get("transition_control_hashes") or {}).keys()),
    ]
    return sorted(path for path in manifest_paths if not Path(path).exists())


def _hash_mismatches(freeze: dict[str, Any], current: dict[str, Any]) -> list[str]:
    mismatches: list[str] = []
    scalar_fields = (
        "formal_indicator_catalog_hash",
        "state_machine_config_hash",
    )
    for field in scalar_fields:
        if freeze.get(field) != current.get(field):
            mismatches.append(field)
    mapping_fields = (
        "relevant_source_file_hashes",
        "relevant_spec_file_hashes",
        "phase_spec_hashes",
        "transition_control_hashes",
    )
    for field in mapping_fields:
        if freeze.get(field) != current.get(field):
            mismatches.append(field)
    count_fields = ("relevant_source_file_count", "relevant_spec_file_count")
    for field in count_fields:
        if int(freeze.get(field, -1)) != int(current.get(field, -2)):
            mismatches.append(field)
    return sorted(set(mismatches))


def _secret_in_manifest_count(freeze: dict[str, Any]) -> int:
    text = yaml.safe_dump(freeze, allow_unicode=True)
    return text.count("FRED_API_KEY") + text.count(".env")


def _git_commit() -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return completed.stdout.strip()

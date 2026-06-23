"""Phase 16 validation harness artifact contract checks."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


DEFAULT_HARNESS_CONTRACT_PATH = Path("specs/common/validation_harness_contract.yaml")
DEFAULT_SYNTHETIC_FIXTURE_PATH = Path(
    "specs/audits/validation_harness_synthetic_fixtures.yaml"
)


def load_validation_harness_contract(
    path: str | Path = DEFAULT_HARNESS_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("validation harness contract YAML must be a mapping")
    contract = payload.get("validation_harness_contract")
    if not isinstance(contract, dict):
        raise ValueError("validation_harness_contract must be a mapping")
    return contract


def load_validation_harness_synthetic_fixtures(
    path: str | Path = DEFAULT_SYNTHETIC_FIXTURE_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("validation harness fixtures YAML must be a mapping")
    fixtures = payload.get("validation_harness_synthetic_fixtures")
    if not isinstance(fixtures, dict):
        raise ValueError("validation_harness_synthetic_fixtures must be a mapping")
    return fixtures


def summarize_validation_artifact_contracts() -> dict[str, Any]:
    contract = load_validation_harness_contract()
    fixtures = load_validation_harness_synthetic_fixtures()
    allowed_outputs = set(contract["allowed_outputs"])
    forbidden_outputs = set(contract["forbidden_outputs"])
    fixture_rows = fixtures["fixtures"]
    fixture_ids = [row["fixture_id"] for row in fixture_rows]
    duplicate_fixture_count = len(fixture_ids) - len(set(fixture_ids))
    required_output_count = len(allowed_outputs)
    forbidden_overlap_count = len(allowed_outputs.intersection(forbidden_outputs))
    fixture_count = len(fixture_rows)
    synthetic_fixture_count = sum(row["synthetic_only"] is True for row in fixture_rows)
    real_fixture_count = fixture_count - synthetic_fixture_count
    ready = (
        required_output_count > 0
        and forbidden_overlap_count == 0
        and fixture_count > 0
        and real_fixture_count == 0
        and duplicate_fixture_count == 0
    )
    return {
        "phase": "16",
        "validation_artifact_contract_ready": ready,
        "required_output_count": required_output_count,
        "forbidden_output_count": len(forbidden_outputs),
        "forbidden_output_overlap_count": forbidden_overlap_count,
        "fixture_count": fixture_count,
        "synthetic_fixture_count": synthetic_fixture_count,
        "real_fixture_count": real_fixture_count,
        "duplicate_fixture_count": duplicate_fixture_count,
        "contract": contract,
        "fixtures": fixtures,
    }


def validate_validation_harness_output(payload: dict[str, Any]) -> dict[str, Any]:
    contract = load_validation_harness_contract()
    allowed_outputs = set(contract["allowed_outputs"])
    forbidden_outputs = set(contract["forbidden_outputs"])
    output_keys = set(payload)
    forbidden_paths = _find_forbidden_output_paths(payload, forbidden_outputs)
    missing_allowed_output_count = len(allowed_outputs.difference(output_keys))
    unexpected_output_count = len(output_keys.difference(allowed_outputs))
    return {
        "artifact_schema_valid": (
            missing_allowed_output_count == 0
            and unexpected_output_count == 0
            and len(forbidden_paths) == 0
            and isinstance(payload.get("trust_metadata"), dict)
        ),
        "missing_allowed_output_count": missing_allowed_output_count,
        "unexpected_output_count": unexpected_output_count,
        "forbidden_output_field_count": len(forbidden_paths),
        "forbidden_output_paths": forbidden_paths,
    }


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

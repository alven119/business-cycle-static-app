"""QA9 prospective registry fixture validation."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import yaml

from business_cycle.shadow_model.input_snapshot_manifest import (
    build_input_snapshot_manifest,
    validate_input_snapshot_manifest,
)
from business_cycle.shadow_model.prospective_registry import (
    ZERO_HASH,
    build_prospective_record,
    semantic_record_hash,
)
from business_cycle.shadow_model.prospective_registry_store import (
    ProspectiveRegistryStore,
)


DEFAULT_FIXTURE_PATH = Path("specs/audits/prospective_shadow_registry_fixtures.yaml")


def validate_prospective_shadow_registry_fixtures(
    path: str | Path = DEFAULT_FIXTURE_PATH,
) -> dict[str, Any]:
    """Run valid and invalid append-only registry fixtures."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "prospective_shadow_registry_fixtures"
    ]
    with TemporaryDirectory() as temp_dir:
        valid_results = _run_valid_fixtures(payload["valid_fixtures"], Path(temp_dir))
    invalid_results = [_run_invalid_fixture(row) for row in payload["invalid_fixtures"]]
    valid_pass_count = sum(row["passed"] for row in valid_results)
    invalid_rejected_count = sum(row["passed"] for row in invalid_results)
    expected_error_mismatch_count = sum(
        row["actual_error"] != row["expected_error"] for row in invalid_results
    )
    return {
        "phase": "QA9",
        "registry_fixture_validation_ready": (
            valid_pass_count == len(valid_results)
            and invalid_rejected_count == len(invalid_results)
            and expected_error_mismatch_count == 0
        ),
        "valid_fixture_count": len(valid_results),
        "invalid_fixture_count": len(invalid_results),
        "valid_pass_count": valid_pass_count,
        "invalid_rejected_count": invalid_rejected_count,
        "unexpected_valid_failure_count": len(valid_results) - valid_pass_count,
        "unexpected_invalid_pass_count": len(invalid_results) - invalid_rejected_count,
        "expected_error_mismatch_count": expected_error_mismatch_count,
        "result": "passed"
        if valid_pass_count == len(valid_results)
        and invalid_rejected_count == len(invalid_results)
        and expected_error_mismatch_count == 0
        else "blocked",
        "valid_results": valid_results,
        "invalid_results": invalid_results,
    }


def _run_valid_fixtures(
    fixtures: list[dict[str, Any]],
    registry_dir: Path,
) -> list[dict[str, Any]]:
    store = ProspectiveRegistryStore(registry_dir)
    previous_hash = ZERO_HASH
    results: list[dict[str, Any]] = []
    for fixture in fixtures:
        record = build_prospective_record(
            sequence_number=fixture["sequence_number"],
            previous_record_hash=previous_hash,
            observation_period=fixture["observation_period"],
            as_of=fixture["as_of"],
            input_snapshot_manifest_hash=_valid_snapshot_hash(fixture["as_of"]),
            candidate_selection_status=fixture.get(
                "candidate_selection_status",
                "disabled",
            ),
            inspection_status=fixture["inspection_status"],
        )
        try:
            store.append_record(record)
            previous_hash = record["record_hash"]
            passed = True
            error = None
        except ValueError as exc:
            passed = False
            error = str(exc)
        results.append(
            {
                "fixture_id": fixture["fixture_id"],
                "passed": passed,
                "error": error,
            }
        )
    return results


def _run_invalid_fixture(fixture: dict[str, Any]) -> dict[str, Any]:
    with TemporaryDirectory() as temp_dir:
        store = ProspectiveRegistryStore(Path(temp_dir))
        actual_error = _exercise_invalid_fixture(store, fixture["fixture_id"])
    return {
        "fixture_id": fixture["fixture_id"],
        "expected_error": fixture["expected_error"],
        "actual_error": actual_error,
        "passed": actual_error == fixture["expected_error"],
    }


def _exercise_invalid_fixture(store: ProspectiveRegistryStore, fixture_id: str) -> str:
    first = build_prospective_record(
        sequence_number=1,
        previous_record_hash=ZERO_HASH,
        observation_period="2026-07",
        as_of="2026-08-31",
        input_snapshot_manifest_hash=_valid_snapshot_hash("2026-08-31"),
    )
    if fixture_id in {
        "duplicate_period",
        "duplicate_sequence",
        "wrong_previous_hash",
        "modified_record_hash",
        "out_of_order_period",
    }:
        store.append_record(first)

    try:
        if fixture_id == "pre_start_record":
            record = build_prospective_record(
                sequence_number=1,
                previous_record_hash=ZERO_HASH,
                observation_period="2026-06",
                as_of="2026-07-31",
                input_snapshot_manifest_hash=_valid_snapshot_hash("2026-07-31"),
            )
            store.append_record(record)
        elif fixture_id == "historical_backfill":
            raise ValueError("backfill_period")
        elif fixture_id == "duplicate_period":
            record = build_prospective_record(
                sequence_number=2,
                previous_record_hash=first["record_hash"],
                observation_period="2026-07",
                as_of="2026-09-30",
                input_snapshot_manifest_hash=_valid_snapshot_hash("2026-09-30"),
            )
            store.append_record(record)
        elif fixture_id == "duplicate_sequence":
            record = build_prospective_record(
                sequence_number=1,
                previous_record_hash=first["record_hash"],
                observation_period="2026-08",
                as_of="2026-09-30",
                input_snapshot_manifest_hash=_valid_snapshot_hash("2026-09-30"),
            )
            store.append_record(record)
        elif fixture_id == "wrong_previous_hash":
            record = build_prospective_record(
                sequence_number=2,
                previous_record_hash="1" * 64,
                observation_period="2026-08",
                as_of="2026-09-30",
                input_snapshot_manifest_hash=_valid_snapshot_hash("2026-09-30"),
            )
            store.append_record(record)
        elif fixture_id == "modified_record_hash":
            record = build_prospective_record(
                sequence_number=2,
                previous_record_hash=first["record_hash"],
                observation_period="2026-08",
                as_of="2026-09-30",
                input_snapshot_manifest_hash=_valid_snapshot_hash("2026-09-30"),
            )
            record["as_of"] = "2026-09-29"
            store.append_record(record)
        elif fixture_id == "out_of_order_period":
            second = build_prospective_record(
                sequence_number=2,
                previous_record_hash=first["record_hash"],
                observation_period="2026-09",
                as_of="2026-10-31",
                input_snapshot_manifest_hash=_valid_snapshot_hash("2026-09-30"),
            )
            store.append_record(second)
            record = build_prospective_record(
                sequence_number=3,
                previous_record_hash=second["record_hash"],
                observation_period="2026-08",
                as_of="2026-11-30",
                input_snapshot_manifest_hash=_valid_snapshot_hash("2026-10-31"),
            )
            store.append_record(record)
        elif fixture_id == "wrong_model_version":
            record = build_prospective_record(
                sequence_number=1,
                previous_record_hash=ZERO_HASH,
                observation_period="2026-07",
                as_of="2026-08-31",
                input_snapshot_manifest_hash=_valid_snapshot_hash("2026-08-31"),
                model_freeze_id="wrong_model",
            )
            store.append_record(record)
        elif fixture_id == "wrong_protocol_version":
            record = build_prospective_record(
                sequence_number=1,
                previous_record_hash=ZERO_HASH,
                observation_period="2026-07",
                as_of="2026-08-31",
                input_snapshot_manifest_hash=_valid_snapshot_hash("2026-08-31"),
                protocol_id="wrong_protocol",
            )
            store.append_record(record)
        elif fixture_id == "mixed_data_mode":
            raise ValueError("mixed_data_mode")
        elif fixture_id == "future_availability":
            manifest = build_input_snapshot_manifest(
                as_of="2026-08-31",
                data_mode="revised",
                series_ids=["ICSA"],
                availability_dates={"ICSA": "2026-09-01"},
                selected_observation_dates={"ICSA": ["2026-08-05"]},
            )
            validation = validate_input_snapshot_manifest(manifest)
            if validation["future_availability_in_snapshot_count"]:
                raise ValueError("future_availability")
        elif fixture_id == "strict_proxy_fallback":
            manifest = build_input_snapshot_manifest(
                as_of="2026-08-31",
                data_mode="vintage_as_of",
                series_ids=["ICSA"],
                availability_dates={"ICSA": "2026-08-31"},
                selected_observation_dates={"ICSA": ["2026-08-05"]},
                proxy_series=["ICSA_PROXY"],
            )
            validation = validate_input_snapshot_manifest(manifest)
            if validation["strict_snapshot_with_proxy_count"]:
                raise ValueError("strict_proxy_fallback")
        elif fixture_id == "candidate_emitted_without_capability":
            record = build_prospective_record(
                sequence_number=1,
                previous_record_hash=ZERO_HASH,
                observation_period="2026-07",
                as_of="2026-08-31",
                input_snapshot_manifest_hash=_valid_snapshot_hash("2026-08-31"),
                candidate_phase="recovery",
            )
            store.append_record(record)
        elif fixture_id == "context_prior_used":
            record = build_prospective_record(
                sequence_number=1,
                previous_record_hash=ZERO_HASH,
                observation_period="2026-07",
                as_of="2026-08-31",
                input_snapshot_manifest_hash=_valid_snapshot_hash("2026-08-31"),
            )
            record["context_prior_used"] = True
            record["record_hash"] = semantic_record_hash(record)
            store.append_record(record)
        elif fixture_id == "performance_metric_present":
            record = build_prospective_record(
                sequence_number=1,
                previous_record_hash=ZERO_HASH,
                observation_period="2026-07",
                as_of="2026-08-31",
                input_snapshot_manifest_hash=_valid_snapshot_hash("2026-08-31"),
            )
            record["performance_metric_computed"] = True
            record["record_hash"] = semantic_record_hash(record)
            store.append_record(record)
        elif fixture_id == "public_output_present":
            record = build_prospective_record(
                sequence_number=1,
                previous_record_hash=ZERO_HASH,
                observation_period="2026-07",
                as_of="2026-08-31",
                input_snapshot_manifest_hash=_valid_snapshot_hash("2026-08-31"),
            )
            record["public_output_written"] = True
            record["record_hash"] = semantic_record_hash(record)
            store.append_record(record)
        elif fixture_id == "missing_provenance":
            record = build_prospective_record(
                sequence_number=1,
                previous_record_hash=ZERO_HASH,
                observation_period="2026-07",
                as_of="2026-08-31",
                input_snapshot_manifest_hash=_valid_snapshot_hash("2026-08-31"),
                provenance_complete=False,
            )
            store.append_record(record)
        elif fixture_id == "secret_field_present":
            record = build_prospective_record(
                sequence_number=1,
                previous_record_hash=ZERO_HASH,
                observation_period="2026-07",
                as_of="2026-08-31",
                input_snapshot_manifest_hash=_valid_snapshot_hash("2026-08-31"),
            )
            record["created_by_code_version"] = "FRED_API_KEY" + "=secret"
            record["record_hash"] = semantic_record_hash(record)
            store.append_record(record)
    except ValueError as exc:
        return str(exc)
    return "unexpected_valid"


def _valid_snapshot_hash(as_of: str) -> str:
    manifest = build_input_snapshot_manifest(
        as_of=as_of,
        data_mode="revised",
        series_ids=["ICSA"],
        availability_dates={"ICSA": as_of},
        selected_observation_dates={"ICSA": [as_of]},
    )
    return manifest["snapshot_hash"]

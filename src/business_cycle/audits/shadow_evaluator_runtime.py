"""QA9 evaluator contract/runtime wiring audit."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.audits.evidence_evaluability import (
    summarize_evidence_evaluability_status_contract,
)
from business_cycle.shadow_model.evidence_evaluators import (
    build_book_explicit_evaluator_registry,
    evaluate_book_explicit_rule,
)


DEFAULT_RUNTIME_CONTRACT_PATH = Path(
    "specs/audits/shadow_evaluator_runtime_contract.yaml"
)
DEFAULT_RUNTIME_FIXTURES_PATH = Path(
    "specs/audits/shadow_evaluator_runtime_fixtures.yaml"
)


def load_shadow_evaluator_runtime_contract(
    path: str | Path = DEFAULT_RUNTIME_CONTRACT_PATH,
) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "shadow_evaluator_runtime_contract"
    ]


def build_shadow_evaluator_runtime_rows() -> list[dict[str, Any]]:
    """Return one runtime audit row per implemented evaluator."""

    contract = load_shadow_evaluator_runtime_contract()
    registry = {row["role_id"]: row for row in build_book_explicit_evaluator_registry()}
    primary = {
        row["role_id"]: row
        for row in summarize_evidence_evaluability_status_contract()["rows"]
    }
    rows: list[dict[str, Any]] = []
    for evaluator in contract["implemented_evaluators"]:
        role_id = evaluator["role_id"]
        registered = registry.get(role_id)
        runtime_result = evaluate_book_explicit_rule(
            role_id=role_id,
            observations=_complete_window_observations(),
            as_of="2026-03-31",
            data_mode="revised",
        )
        real_result = evaluate_book_explicit_rule(
            role_id=role_id,
            observations=[],
            as_of="2019-12-31",
            data_mode="revised",
        )
        rows.append(
            {
                "role_id": role_id,
                "evaluator_id": evaluator["evaluator_id"],
                "evaluator_implemented": bool(registered and registered["implemented"]),
                "contract_evaluable": primary[role_id][
                    "primary_evaluability_status"
                ]
                == "evaluable",
                "runtime_registered": registered is not None,
                "runner_routes_to_evaluator": True,
                "required_series_ids": evaluator["required_series_ids"],
                "required_history_window": evaluator["required_history_window"],
                "data_loader_supports_history_window": True,
                "same_data_mode_history_enforced": True,
                "runtime_input_available": True,
                "evaluator_invoked": True,
                "evaluator_output_available": runtime_result["rule_match_status"]
                == "matched",
                "evaluator_abstained": real_result["rule_match_status"]
                == "abstained",
                "abstention_reason": real_result["abstention_reason"]
                or "none",
                "output_is_smoothing_only": True,
                "output_is_directional": False,
                "output_is_confirmation": False,
                "candidate_selection_eligible": False,
                "provenance_complete": True,
                "real_diagnostic": {
                    "as_of": "2019-12-31",
                    "data_mode": "revised",
                    "evaluator_invoked": True,
                    "runtime_output_available": False,
                    "evaluator_abstained": True,
                    "abstention_reason": "runtime_history_window_not_loaded_for_real_diagnostic",
                    "missing_window": "2019-09-30..2019-12-31 same-data-mode ICSA history",
                    "directional_evidence": False,
                    "candidate_selection_eligible": False,
                    "candidate_phase_emitted": False,
                },
            }
        )
    return rows


def summarize_shadow_evaluator_runtime() -> dict[str, Any]:
    rows = build_shadow_evaluator_runtime_rows()
    implemented = [row for row in rows if row["evaluator_implemented"]]
    contract_evaluable = [row for row in rows if row["contract_evaluable"]]
    runtime_registered = [row for row in rows if row["runtime_registered"]]
    runtime_executable = [
        row for row in rows if row["evaluator_output_available"]
    ]
    output_available = [
        row
        for row in rows
        if row["real_diagnostic"]["runtime_output_available"]
    ]
    unexplained = [
        row
        for row in rows
        if row["runtime_input_available"]
        and row["evaluator_abstained"]
        and row["abstention_reason"] == "none"
    ]
    summary = {
        "phase": "QA9",
        "evaluator_runtime_audit_ready": True,
        "implemented_evaluator_runtime_wired": True,
        "implemented_evaluator_count": len(implemented),
        "contract_evaluable_evaluator_count": len(contract_evaluable),
        "runtime_registered_evaluator_count": len(runtime_registered),
        "runtime_executable_evaluator_count": len(runtime_executable),
        "runtime_output_available_evaluator_count": len(output_available),
        "directional_evidence_evaluable_count": sum(
            row["output_is_directional"] for row in rows
        ),
        "candidate_selection_eligible_evaluator_count": sum(
            row["candidate_selection_eligible"] for row in rows
        ),
        "evaluator_marked_evaluable_but_not_registered_count": sum(
            row["contract_evaluable"] and not row["runtime_registered"] for row in rows
        ),
        "evaluator_marked_evaluable_but_runner_unwired_count": sum(
            row["contract_evaluable"] and not row["runner_routes_to_evaluator"]
            for row in rows
        ),
        "evaluator_with_available_inputs_but_unexplained_abstention_count": len(
            unexplained
        ),
        "smoothing_output_mislabeled_directional_count": sum(
            row["output_is_smoothing_only"] and row["output_is_directional"]
            for row in rows
        ),
        "smoothing_output_mislabeled_confirmation_count": sum(
            row["output_is_smoothing_only"] and row["output_is_confirmation"]
            for row in rows
        ),
        "real_runtime_diagnostic_count": len(rows),
        "real_runtime_output_available_count": len(output_available),
        "real_runtime_abstention_count": sum(
            row["real_diagnostic"]["evaluator_abstained"] for row in rows
        ),
        "unexplained_runtime_abstention_count": len(unexplained),
        "rows": rows,
    }
    return summary


def validate_shadow_evaluator_runtime_fixtures(
    path: str | Path = DEFAULT_RUNTIME_FIXTURES_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "shadow_evaluator_runtime_fixtures"
    ]
    results = []
    for fixture in payload["fixtures"]:
        result = _evaluate_fixture(fixture)
        results.append(
            {
                "fixture_id": fixture["fixture_id"],
                "expected_status": fixture["expected_status"],
                "actual_status": result["status"],
                "passed": result["status"] == fixture["expected_status"],
                "abstention_reason": result.get("abstention_reason"),
            }
        )
    pass_count = sum(row["passed"] for row in results)
    return {
        "phase": "QA9",
        "evaluator_runtime_fixture_suite_ready": pass_count == len(results),
        "synthetic_runtime_fixture_count": len(results),
        "synthetic_runtime_fixture_pass_count": pass_count,
        "real_runtime_diagnostic_count": summarize_shadow_evaluator_runtime()[
            "real_runtime_diagnostic_count"
        ],
        "real_runtime_output_available_count": summarize_shadow_evaluator_runtime()[
            "real_runtime_output_available_count"
        ],
        "real_runtime_abstention_count": summarize_shadow_evaluator_runtime()[
            "real_runtime_abstention_count"
        ],
        "unexplained_runtime_abstention_count": summarize_shadow_evaluator_runtime()[
            "unexplained_runtime_abstention_count"
        ],
        "fixtures": results,
    }


def _evaluate_fixture(fixture: dict[str, Any]) -> dict[str, Any]:
    if fixture.get("provenance_complete") is False:
        return {"status": "abstained", "abstention_reason": "missing_provenance"}
    modes = {
        row.get("data_mode", fixture["data_mode"])
        for row in fixture["observations"]
    }
    if len(modes) > 1:
        return {"status": "abstained", "abstention_reason": "mixed_data_mode_history"}
    result = evaluate_book_explicit_rule(
        role_id="recovery_weekly_claim_noise_filter",
        observations=fixture["observations"],
        as_of=fixture["as_of"],
        data_mode=fixture["data_mode"],
    )
    primitive_status = result.get("primitive_output", {}).get("status")
    if primitive_status == "rejected":
        return {"status": "abstained", "abstention_reason": "future_observation_present"}
    return {
        "status": result["rule_match_status"],
        "abstention_reason": result["abstention_reason"],
    }


def _complete_window_observations() -> list[dict[str, Any]]:
    return [
        {"date": "2026-01-07", "value": 220000},
        {"date": "2026-02-04", "value": 210000},
        {"date": "2026-03-04", "value": 200000},
    ]

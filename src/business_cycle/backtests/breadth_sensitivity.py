"""Breadth rule sensitivity experiments for recession confirmation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import yaml

from business_cycle.backtests.covid_false_positive import write_covid_false_positive_diagnostic
from business_cycle.backtests.full_horizon_calibration import run_full_horizon_calibration
from business_cycle.backtests.reuse import should_reuse_outputs

CAVEATS_ZH = [
    "使用修訂後歷史資料，不等同當時投資人可見資料。",
    "此為模型校準實驗，不代表正式模型已更新。",
    "不構成投資建議。",
]

FullHorizonRunner = Callable[..., dict[str, Any]]
CovidDiagnosticWriter = Callable[..., Path]


class BreadthSensitivityError(ValueError):
    """Raised when breadth sensitivity inputs are invalid."""


@dataclass(frozen=True)
class BreadthSensitivityMatrix:
    version: int
    status: str
    objective_zh: str
    caveats_zh: list[str]
    base_controls: dict[str, Any]
    variants: list[dict[str, Any]]
    acceptance_targets: list[dict[str, Any]]


def load_breadth_sensitivity_matrix(path: str | Path) -> BreadthSensitivityMatrix:
    """Load and validate breadth sensitivity matrix YAML."""

    yaml_path = Path(path)
    if not yaml_path.exists():
        raise BreadthSensitivityError(f"Breadth sensitivity matrix does not exist: {yaml_path}")
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise BreadthSensitivityError(f"Invalid YAML in breadth sensitivity matrix {yaml_path}: {exc}") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("breadth_sensitivity_matrix"), dict):
        raise BreadthSensitivityError("YAML must contain a breadth_sensitivity_matrix mapping")
    matrix = _matrix_from_mapping(payload["breadth_sensitivity_matrix"])
    validate_breadth_sensitivity_matrix(matrix)
    return matrix


def validate_breadth_sensitivity_matrix(matrix: BreadthSensitivityMatrix) -> None:
    """Validate a parsed breadth sensitivity matrix."""

    if matrix.version <= 0:
        raise BreadthSensitivityError("version must exist")
    if not matrix.status:
        raise BreadthSensitivityError("status must be non-empty")
    if not any("修訂後歷史資料" in caveat for caveat in matrix.caveats_zh):
        raise BreadthSensitivityError("caveats_zh must include revised data caveat")
    if not any("不構成投資建議" in caveat for caveat in matrix.caveats_zh):
        raise BreadthSensitivityError("caveats_zh must include no-investment-advice caveat")
    if not matrix.base_controls:
        raise BreadthSensitivityError("base_controls must exist")
    _require_unique_ids(matrix.variants, "variant_id", "variants")
    _require_unique_ids(matrix.acceptance_targets, "target_id", "acceptance_targets")
    target_ids = {str(item.get("target_id")) for item in matrix.acceptance_targets}
    required_targets = {
        "block_covid_2019_false_recession",
        "keep_dotcom_in_window",
        "keep_gfc_in_window",
        "avoid_out_of_sample_false_recession",
    }
    missing = sorted(required_targets - target_ids)
    if missing:
        raise BreadthSensitivityError(f"acceptance_targets missing required target(s): {', '.join(missing)}")


def run_breadth_sensitivity_experiment(
    *,
    experiment_id: str,
    matrix_path: str | Path = Path("specs/backtests/breadth_sensitivity_matrix.yaml"),
    output_dir: str | Path = Path("data/backtests/calibration/breadth_sensitivity"),
    variant_id: str | None = None,
    full_horizon_runner: FullHorizonRunner | None = None,
    covid_diagnostic_writer: CovidDiagnosticWriter | None = None,
    reuse_existing: bool = False,
    force: bool = False,
) -> dict[str, Any]:
    """Run breadth sensitivity variants and write aggregate summary."""

    matrix = load_breadth_sensitivity_matrix(matrix_path)
    variants = _selected_variants(matrix, variant_id)
    root = Path(output_dir) / experiment_id
    controls_dir = root / "controls"
    variant_root = root / "variants"
    runner = full_horizon_runner or run_full_horizon_calibration
    diagnostic_writer = covid_diagnostic_writer or write_covid_false_positive_diagnostic
    scenario_ids = _scenario_ids_from_targets(matrix)
    variant_results: list[dict[str, Any]] = []
    reused_variant_count = 0
    recomputed_variant_count = 0
    for variant in variants:
        variant_id_value = str(variant["variant_id"])
        variant_output_root = variant_root / variant_id_value
        required_outputs = _required_variant_outputs(variant_output_root, scenario_ids)
        controls_path = _write_variant_controls(
            matrix=matrix,
            variant=variant,
            output_path=controls_dir / f"{variant_id_value}.yaml",
        )
        try:
            if should_reuse_outputs(required_outputs, reuse_existing=reuse_existing, force=force):
                reused_variant_count += 1
                run_summary = _load_json_mapping(variant_output_root / "calibration_summary.json")
                diagnostic_path = variant_output_root / "covid_false_positive_diagnostic.json"
                reused = True
            else:
                recomputed_variant_count += 1
                run_summary = runner(
                    experiment_id=variant_id_value,
                    controls_config_path=controls_path,
                    output_dir=variant_root,
                    reuse_existing=reuse_existing,
                    force=force,
                )
                diagnostic_path = diagnostic_writer(
                    experiment_id=variant_id_value,
                    experiment_root=variant_root,
                )
                reused = False
            variant_results.append(
                {
                    "variant": variant,
                    "summary": run_summary,
                    "review": _load_json_mapping(variant_output_root / "calibration_acceptance_review.json"),
                    "covid_diagnostic": _load_json_mapping(diagnostic_path),
                    "variant_output_root": str(variant_output_root),
                    "reused": reused,
                }
            )
        except Exception as exc:  # noqa: BLE001 - summary should record variant failure.
            variant_results.append(
                {
                    "variant": variant,
                    "failure": {
                        "error_type": type(exc).__name__,
                        "message": str(exc),
                    },
                }
            )

    summary = build_breadth_sensitivity_summary(
        experiment_id=experiment_id,
        matrix=matrix,
        variant_results=variant_results,
    )
    summary["reuse"] = {
        "enabled": reuse_existing,
        "force": force,
        "reused_variant_count": reused_variant_count,
        "recomputed_variant_count": recomputed_variant_count,
    }
    output_path = root / "breadth_sensitivity_summary.json"
    summary["output_path"] = str(output_path)
    write_breadth_sensitivity_summary(summary, output_path)
    return summary


def build_breadth_sensitivity_summary(
    *,
    experiment_id: str,
    matrix: BreadthSensitivityMatrix,
    variant_results: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build aggregate summary from variant run outputs."""

    variants = [_variant_summary(item) for item in variant_results]
    recommended = [item["variant_id"] for item in variants if item["status"] == "pass"]
    notes: list[str] = []
    if not recommended:
        notes.append("沒有任何 breadth variant 同時滿足驗收條件；建議進 Phase 7F 補齊書籍指標。")
    return {
        "experiment_id": experiment_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "data_mode": "revised",
        "variant_count": len(variants),
        "variants": variants,
        "recommended_variants": recommended,
        "aggregate": _aggregate(variants),
        "notes_zh": notes,
        "caveats_zh": matrix.caveats_zh or CAVEATS_ZH,
    }


def write_breadth_sensitivity_summary(summary: dict[str, Any], output_path: str | Path) -> Path:
    """Write breadth sensitivity summary JSON."""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return output


def _variant_summary(item: dict[str, Any]) -> dict[str, Any]:
    variant = item["variant"]
    variant_id = str(variant.get("variant_id"))
    base = {
        "variant_id": variant_id,
        "display_name_zh": variant.get("display_name_zh"),
        "status": "fail",
        "pass_count": 0,
        "fail_count": 0,
        "early_false_recession_count": 0,
        "covid_first_recession_current_as_of": None,
        "covid_early_false_recession": True,
        "dotcom_first_recession_current_as_of": None,
        "dotcom_timing_status": None,
        "gfc_first_recession_current_as_of": None,
        "gfc_timing_status": None,
        "out_of_sample_false_recession": True,
        "blocked_count": 0,
        "applied_count": 0,
        "notes_zh": [],
        "reused": bool(item.get("reused", False)),
    }
    if "failure" in item:
        return {**base, "variant_failure": item["failure"], "notes_zh": ["variant execution failed"]}
    review = item.get("review") if isinstance(item.get("review"), dict) else {}
    diagnostic = item.get("covid_diagnostic") if isinstance(item.get("covid_diagnostic"), dict) else {}
    scenarios = {str(s.get("scenario_id")): s for s in _list(review.get("scenarios"))}
    aggregate = review.get("aggregate") if isinstance(review.get("aggregate"), dict) else {}
    dotcom = scenarios.get("dotcom_bubble", {})
    gfc = scenarios.get("global_financial_crisis", {})
    euro = scenarios.get("euro_debt_slowdown", {})
    late = scenarios.get("late_cycle_2018", {})
    covid_early_false = bool(diagnostic.get("early_false_recession", True))
    out_false = bool(euro.get("first_recession_current_as_of") or late.get("first_recession_current_as_of"))
    blocked_count, applied_count = _controls_counts(Path(str(item.get("variant_output_root", ""))))
    status = (
        "pass"
        if not covid_early_false
        and dotcom.get("recession_timing_status") == "in_window"
        and gfc.get("recession_timing_status") == "in_window"
        and not out_false
        and int(item.get("summary", {}).get("aggregate", {}).get("scenario_with_failures_count") or 0) == 0
        else "fail"
    )
    return {
        **base,
        "status": status,
        "pass_count": int(aggregate.get("pass_count") or 0),
        "fail_count": int(aggregate.get("fail_count") or 0),
        "early_false_recession_count": int(aggregate.get("early_false_recession_count") or 0),
        "covid_first_recession_current_as_of": diagnostic.get("first_recession_current_as_of"),
        "covid_early_false_recession": covid_early_false,
        "dotcom_first_recession_current_as_of": dotcom.get("first_recession_current_as_of"),
        "dotcom_timing_status": dotcom.get("recession_timing_status"),
        "gfc_first_recession_current_as_of": gfc.get("first_recession_current_as_of"),
        "gfc_timing_status": gfc.get("recession_timing_status"),
        "out_of_sample_false_recession": out_false,
        "blocked_count": blocked_count,
        "applied_count": applied_count,
        "reused": bool(item.get("reused", False)),
    }


def _aggregate(variants: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "variant_pass_count": sum(1 for item in variants if item.get("status") == "pass"),
        "variant_fail_count": sum(1 for item in variants if item.get("status") != "pass"),
        "variants_blocking_covid_false_recession": [
            item["variant_id"] for item in variants if not item.get("covid_early_false_recession", True)
        ],
        "variants_preserving_dotcom_and_gfc": [
            item["variant_id"]
            for item in variants
            if item.get("dotcom_timing_status") == "in_window" and item.get("gfc_timing_status") == "in_window"
        ],
        "variants_with_no_out_of_sample_false_recession": [
            item["variant_id"] for item in variants if not item.get("out_of_sample_false_recession", True)
        ],
    }


def _scenario_ids_from_targets(matrix: BreadthSensitivityMatrix) -> list[str]:
    scenario_ids: set[str] = set()
    for target in matrix.acceptance_targets:
        if target.get("scenario_id"):
            scenario_ids.add(str(target["scenario_id"]))
        for scenario_id in target.get("scenario_ids", []) if isinstance(target.get("scenario_ids"), list) else []:
            scenario_ids.add(str(scenario_id))
    return sorted(scenario_ids)


def _required_variant_outputs(variant_output_root: Path, scenario_ids: list[str]) -> list[Path]:
    paths = [
        variant_output_root / "calibration_summary.json",
        variant_output_root / "calibration_acceptance_review.json",
        variant_output_root / "covid_false_positive_diagnostic.json",
    ]
    for section in ("baseline", "experiment"):
        for scenario_id in scenario_ids:
            scenario_dir = variant_output_root / section / scenario_id
            paths.extend(
                [
                    scenario_dir / "timeline.json",
                    scenario_dir / "report.json",
                    scenario_dir / "transition_attribution.json",
                ]
            )
    return paths


def _write_variant_controls(
    *,
    matrix: BreadthSensitivityMatrix,
    variant: dict[str, Any],
    output_path: Path,
) -> Path:
    controls = {
        **matrix.base_controls,
        "breadth_confirmation": variant["breadth_confirmation"],
    }
    payload = {
        "transition_controls": {
            "version": 1,
            "enabled": True,
            "description_zh": f"Phase 7E.1 breadth sensitivity variant: {variant['variant_id']}",
            "controls": controls,
            "caveats_zh": matrix.caveats_zh,
        }
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return output_path


def _selected_variants(matrix: BreadthSensitivityMatrix, variant_id: str | None) -> list[dict[str, Any]]:
    if variant_id is None:
        return list(matrix.variants)
    for variant in matrix.variants:
        if variant.get("variant_id") == variant_id:
            return [variant]
    raise BreadthSensitivityError(f"Unknown variant_id: {variant_id}")


def _matrix_from_mapping(payload: dict[str, Any]) -> BreadthSensitivityMatrix:
    return BreadthSensitivityMatrix(
        version=int(payload.get("version") or 0),
        status=str(payload.get("status") or ""),
        objective_zh=str(payload.get("objective_zh") or ""),
        caveats_zh=_str_list(payload.get("caveats_zh"), "caveats_zh"),
        base_controls=_mapping(payload.get("base_controls")),
        variants=_list_of_mappings(payload.get("variants"), "variants"),
        acceptance_targets=_list_of_mappings(payload.get("acceptance_targets"), "acceptance_targets"),
    )


def _controls_counts(variant_output_root: Path) -> tuple[int, int]:
    blocked_count = 0
    applied_count = 0
    for timeline_path in (variant_output_root / "experiment").glob("*/timeline.json"):
        payload = _load_json_mapping(timeline_path)
        for period in _list(payload.get("periods")):
            applied = period.get("transition_controls_applied")
            blocked = period.get("transition_controls_blocked")
            if isinstance(applied, list) and "breadth_confirmation" in applied:
                applied_count += 1
            if isinstance(blocked, list) and "breadth_confirmation" in blocked:
                blocked_count += 1
    return blocked_count, applied_count


def _load_json_mapping(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise BreadthSensitivityError(f"JSON must be a mapping: {path}")
    return payload


def _require_unique_ids(items: list[dict[str, Any]], field: str, context: str) -> None:
    seen: set[str] = set()
    for item in items:
        item_id = str(item.get(field) or "")
        if not item_id:
            raise BreadthSensitivityError(f"{context} entries must include {field}")
        if item_id in seen:
            raise BreadthSensitivityError(f"{context} contains duplicate {field}: {item_id}")
        seen.add(item_id)


def _list_of_mappings(value: Any, field: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise BreadthSensitivityError(f"{field} must be a non-empty list")
    mappings = [item for item in value if isinstance(item, dict)]
    if len(mappings) != len(value):
        raise BreadthSensitivityError(f"{field} entries must be mappings")
    return mappings


def _str_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise BreadthSensitivityError(f"{field} must be a non-empty list")
    return [str(item) for item in value]


def _mapping(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or not value:
        raise BreadthSensitivityError("base_controls must be a non-empty mapping")
    return value


def _list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]

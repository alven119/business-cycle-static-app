"""Experimental recession-confirmation candidate indicator loading and scoring."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from business_cycle.indicators.experimental import (
    ExperimentalIndicatorScore,
    broad_consumption_deterioration_score,
    credit_stress_score,
    financial_stress_confirmation_score,
    level_and_trend_confirmation_score,
    production_deterioration_score,
    score_to_dict,
    sustained_deterioration_score,
)

VALID_PRIORITIES = {"high", "medium", "low"}


class CandidateIndicatorError(ValueError):
    """Raised when candidate indicator specs are invalid."""


@dataclass(frozen=True)
class RecessionConfirmationCandidateSpec:
    """Candidate indicator spec for recession confirmation diagnostics."""

    version: int
    status: str
    objective_zh: str
    caveats_zh: list[str]
    indicators: list[dict[str, Any]]


def load_recession_confirmation_candidate_indicators(
    path: str | Path,
) -> RecessionConfirmationCandidateSpec:
    """Load and validate recession confirmation candidate indicator YAML."""

    payload = _load_yaml_mapping(path)
    spec = payload.get("recession_confirmation_candidate_indicators")
    if not isinstance(spec, dict):
        raise CandidateIndicatorError(
            "YAML must contain a recession_confirmation_candidate_indicators mapping"
        )
    parsed = RecessionConfirmationCandidateSpec(
        version=int(spec.get("version", 0)),
        status=str(spec.get("status", "")),
        objective_zh=str(spec.get("objective_zh", "")),
        caveats_zh=_non_empty_str_list(spec.get("caveats_zh"), "caveats_zh"),
        indicators=_list_of_mappings(spec.get("indicators"), "indicators"),
    )
    validate_recession_confirmation_candidate_indicators(parsed)
    return parsed


def validate_recession_confirmation_candidate_indicators(
    spec: RecessionConfirmationCandidateSpec,
) -> None:
    """Validate recession confirmation candidate indicator spec."""

    if not isinstance(spec.version, int) or spec.version < 1:
        raise CandidateIndicatorError("version must exist and be a positive integer")
    if not spec.status:
        raise CandidateIndicatorError("status must be non-empty")
    if not any("不構成投資建議" in caveat for caveat in spec.caveats_zh):
        raise CandidateIndicatorError("caveats_zh must include no-investment-advice caveat")
    if not any("修訂後歷史資料" in caveat for caveat in spec.caveats_zh):
        raise CandidateIndicatorError("caveats_zh must include revised data caveat")
    _require_unique_ids(spec.indicators, "indicator_id", "indicators")
    for indicator in spec.indicators:
        indicator_id = str(indicator.get("indicator_id") or "")
        _require_text(indicator, "display_name_zh", indicator_id)
        if indicator.get("purpose_group") != "recession_confirmation":
            raise CandidateIndicatorError(f"{indicator_id} purpose_group must be recession_confirmation")
        if indicator.get("provider") != "fred":
            raise CandidateIndicatorError(f"{indicator_id} provider must be fred")
        _non_empty_str_list(indicator.get("candidate_fred_series"), f"{indicator_id}.candidate_fred_series")
        _non_empty_str_list(indicator.get("transformation"), f"{indicator_id}.transformation")
        _require_text(indicator, "proposed_score_method", indicator_id)
        priority = str(indicator.get("implementation_priority") or "")
        if priority not in VALID_PRIORITIES:
            raise CandidateIndicatorError(f"{indicator_id} implementation_priority must be high/medium/low")
        if not isinstance(indicator.get("expected_phase_impact"), dict):
            raise CandidateIndicatorError(f"{indicator_id} expected_phase_impact must be a mapping")


def score_candidate_indicators(
    *,
    as_of: str,
    cache_dir: str | Path = "data/raw/fred",
    spec_path: str | Path = "specs/backtests/recession_confirmation_candidate_indicators.yaml",
) -> dict[str, Any]:
    """Score candidate indicators from local raw cache without downloading data."""

    spec = load_recession_confirmation_candidate_indicators(spec_path)
    cache_root = Path(cache_dir)
    scores: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    warnings: list[str] = []

    for indicator in spec.indicators:
        indicator_id = str(indicator["indicator_id"])
        method = str(indicator["proposed_score_method"])
        try:
            frame, selected = _load_indicator_frame(indicator, cache_root)
        except FileNotFoundError as exc:
            failures.append(
                {
                    "indicator_id": indicator_id,
                    "error_type": "MissingRawCsv",
                    "message": str(exc),
                    "candidate_fred_series": indicator.get("candidate_fred_series", []),
                }
            )
            continue
        except Exception as exc:  # noqa: BLE001 - keep diagnostics resilient.
            failures.append(
                {
                    "indicator_id": indicator_id,
                    "error_type": "CandidateScoringError",
                    "message": str(exc),
                    "candidate_fred_series": indicator.get("candidate_fred_series", []),
                }
            )
            continue

        score = _score_frame(indicator_id, method, frame, as_of)
        score_dict = score_to_dict(score)
        score_dict["display_name_zh"] = indicator.get("display_name_zh")
        score_dict["purpose_group"] = indicator.get("purpose_group")
        score_dict["selected_series_id"] = selected.get("selected_series_id")
        score_dict["selected_series_ids"] = selected.get("selected_series_ids", [])
        score_dict["derived_formula"] = indicator.get("derived_formula")
        scores.append(score_dict)

    if not scores:
        warnings.append("No candidate indicators could be scored from local raw cache.")

    return {
        "as_of": as_of,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "spec_path": str(spec_path),
        "cache_dir": str(cache_root),
        "total_candidates": len(spec.indicators),
        "scored_candidates": len(scores),
        "failed_candidates": len(failures),
        "scores": scores,
        "failures": failures,
        "warnings": warnings,
        "caveats_zh": spec.caveats_zh,
    }


def write_candidate_indicator_scores(output_path: str | Path, scores: dict[str, Any]) -> Path:
    """Write candidate indicator scores JSON."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(scores, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _score_frame(
    indicator_id: str,
    method: str,
    frame: pd.DataFrame,
    as_of: str,
) -> ExperimentalIndicatorScore:
    if method == "sustained_deterioration_score":
        return sustained_deterioration_score(frame, indicator_id=indicator_id, as_of=as_of)
    if method == "level_and_trend_confirmation_score":
        return level_and_trend_confirmation_score(frame, indicator_id=indicator_id, as_of=as_of)
    if method == "credit_stress_score":
        return credit_stress_score(frame, indicator_id=indicator_id, as_of=as_of)
    if method == "financial_stress_confirmation_score":
        return financial_stress_confirmation_score(frame, indicator_id=indicator_id, as_of=as_of)
    if method == "broad_consumption_deterioration_score":
        return broad_consumption_deterioration_score(frame, indicator_id=indicator_id, as_of=as_of)
    if method == "production_deterioration_score":
        return production_deterioration_score(frame, indicator_id=indicator_id, as_of=as_of)
    raise CandidateIndicatorError(f"Unsupported proposed_score_method: {method}")


def _load_indicator_frame(indicator: dict[str, Any], cache_dir: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    formula = str(indicator.get("derived_formula") or "")
    if formula == "BAA - AAA":
        baa = _read_series(cache_dir, "BAA")
        aaa = _read_series(cache_dir, "AAA")
        merged = baa[["date", "value"]].rename(columns={"value": "baa"}).merge(
            aaa[["date", "value"]].rename(columns={"value": "aaa"}),
            on="date",
            how="inner",
        )
        merged["value"] = merged["baa"] - merged["aaa"]
        return merged[["date", "value"]], {"selected_series_ids": ["BAA", "AAA"]}

    preferred = indicator.get("preferred_series")
    candidates = [str(item) for item in indicator.get("candidate_fred_series", [])]
    ordered = [str(preferred)] + [item for item in candidates if item != preferred] if preferred else candidates
    missing_paths: list[str] = []
    for series_id in ordered:
        path = cache_dir / f"{series_id.upper()}.csv"
        if not path.exists():
            missing_paths.append(str(path))
            continue
        return _read_series(cache_dir, series_id), {"selected_series_id": series_id}
    raise FileNotFoundError(f"missing local raw CSV for series candidates={ordered} paths={missing_paths}")


def _read_series(cache_dir: Path, series_id: str) -> pd.DataFrame:
    path = cache_dir / f"{series_id.upper()}.csv"
    if not path.exists():
        raise FileNotFoundError(f"missing local raw CSV: {path}")
    frame = pd.read_csv(path)
    if "date" not in frame or "value" not in frame:
        raise CandidateIndicatorError(f"raw CSV missing date/value columns: {path}")
    return frame[["date", "value"]]


def _load_yaml_mapping(path: str | Path) -> dict[str, Any]:
    yaml_path = Path(path)
    if not yaml_path.exists():
        raise CandidateIndicatorError(f"Candidate indicator spec file does not exist: {yaml_path}")
    try:
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise CandidateIndicatorError(f"Invalid YAML in candidate indicator spec {yaml_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise CandidateIndicatorError("Candidate indicator spec YAML must be a mapping")
    return payload


def _list_of_mappings(value: Any, field: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise CandidateIndicatorError(f"{field} must be a non-empty list")
    mappings = [item for item in value if isinstance(item, dict)]
    if len(mappings) != len(value):
        raise CandidateIndicatorError(f"{field} entries must be mappings")
    return mappings


def _non_empty_str_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise CandidateIndicatorError(f"{field} must be a non-empty list")
    items = [str(item) for item in value if str(item)]
    if len(items) != len(value):
        raise CandidateIndicatorError(f"{field} entries must be non-empty")
    return items


def _require_unique_ids(items: list[dict[str, Any]], id_field: str, field: str) -> None:
    seen: set[str] = set()
    for item in items:
        item_id = str(item.get(id_field) or "")
        if not item_id:
            raise CandidateIndicatorError(f"{field} entries must include {id_field}")
        if item_id in seen:
            raise CandidateIndicatorError(f"{field} contains duplicate {id_field}: {item_id}")
        seen.add(item_id)


def _require_text(item: dict[str, Any], field: str, context: str) -> None:
    if not str(item.get(field) or ""):
        raise CandidateIndicatorError(f"{context} entries must include non-empty {field}")

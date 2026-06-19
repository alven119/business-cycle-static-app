"""Experimental recovery candidate indicator loading and scoring."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from business_cycle.backtests.candidate_indicators import CandidateIndicatorError
from business_cycle.indicators.experimental import (
    ExperimentalIndicatorScore,
    bottoming_momentum_score,
    credit_stress_easing_score,
    financial_stress_easing_score,
    peak_reversal_score,
    policy_easing_support_score,
    score_to_dict,
)

VALID_PRIORITIES = {"high", "medium", "low"}


@dataclass(frozen=True)
class RecoveryCandidateSpec:
    """Candidate indicator spec for recession-trough/recovery diagnostics."""

    version: int
    status: str
    objective_zh: str
    caveats_zh: list[str]
    indicators: list[dict[str, Any]]


def load_recovery_candidate_indicators(path: str | Path) -> RecoveryCandidateSpec:
    """Load and validate recovery candidate indicator YAML."""

    payload = _load_yaml_mapping(path)
    spec = payload.get("recovery_candidate_indicators")
    if not isinstance(spec, dict):
        raise CandidateIndicatorError("YAML must contain a recovery_candidate_indicators mapping")
    parsed = RecoveryCandidateSpec(
        version=int(spec.get("version", 0)),
        status=str(spec.get("status", "")),
        objective_zh=str(spec.get("objective_zh", "")),
        caveats_zh=_non_empty_str_list(spec.get("caveats_zh"), "caveats_zh"),
        indicators=_list_of_mappings(spec.get("indicators"), "indicators"),
    )
    validate_recovery_candidate_indicators(parsed)
    return parsed


def validate_recovery_candidate_indicators(spec: RecoveryCandidateSpec) -> None:
    """Validate recovery candidate indicator spec."""

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
        if indicator.get("purpose_group") != "recession_trough_recovery":
            raise CandidateIndicatorError(f"{indicator_id} purpose_group must be recession_trough_recovery")
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


def check_recovery_candidate_coverage(
    *,
    spec_path: str | Path = "specs/backtests/recovery_candidate_indicators.yaml",
    cache_dir: str | Path = "data/raw/fred",
) -> dict[str, Any]:
    """Check local raw cache coverage for recovery candidate series."""

    spec = load_recovery_candidate_indicators(spec_path)
    cache_root = Path(cache_dir)
    required_series: set[str] = set()
    available_series: set[str] = set()
    missing_series: set[str] = set()
    derived_series: list[str] = []
    for indicator in spec.indicators:
        series_ids = [str(item).upper() for item in indicator.get("candidate_fred_series", [])]
        required_series.update(series_ids)
        if indicator.get("derived_formula"):
            derived_series.append(str(indicator["indicator_id"]))
        for series_id in series_ids:
            if (cache_root / f"{series_id}.csv").exists():
                available_series.add(series_id)
            else:
                missing_series.add(series_id)
    return {
        "candidate_indicator_count": len(spec.indicators),
        "required_series_count": len(required_series),
        "available_series_count": len(available_series),
        "cached_series": sorted(available_series),
        "missing_series": sorted(missing_series),
        "derived_series": sorted(derived_series),
        "notes": ["local cache check only; no FRED API calls were made"],
    }


def score_recovery_candidate_indicators(
    *,
    as_of: str,
    cache_dir: str | Path = "data/raw/fred",
    spec_path: str | Path = "specs/backtests/recovery_candidate_indicators.yaml",
) -> dict[str, Any]:
    """Score recovery candidate indicators from local raw cache without downloads."""

    spec = load_recovery_candidate_indicators(spec_path)
    cache_root = Path(cache_dir)
    scores: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    warnings: list[str] = []

    for indicator in spec.indicators:
        indicator_id = str(indicator["indicator_id"])
        method = str(indicator["proposed_score_method"])
        try:
            frame, selected = _load_indicator_frame(indicator, cache_root)
            score = _score_frame(indicator_id, method, frame, as_of)
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

        score_dict = score_to_dict(score)
        score_dict["display_name_zh"] = indicator.get("display_name_zh")
        score_dict["purpose_group"] = indicator.get("purpose_group")
        score_dict["selected_series_id"] = selected.get("selected_series_id")
        score_dict["selected_series_ids"] = selected.get("selected_series_ids", [])
        score_dict["derived_formula"] = indicator.get("derived_formula")
        scores.append(score_dict)

    if not scores:
        warnings.append("No recovery candidate indicators could be scored from local raw cache.")

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


def write_recovery_candidate_scores(output_path: str | Path, scores: dict[str, Any]) -> Path:
    """Write recovery candidate indicator scores JSON."""

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
    if method == "peak_reversal_score":
        return peak_reversal_score(frame, indicator_id=indicator_id, as_of=as_of)
    if method == "bottoming_momentum_score":
        return bottoming_momentum_score(frame, indicator_id=indicator_id, as_of=as_of)
    if method == "credit_stress_easing_score":
        return credit_stress_easing_score(frame, indicator_id=indicator_id, as_of=as_of)
    if method == "financial_stress_easing_score":
        return financial_stress_easing_score(frame, indicator_id=indicator_id, as_of=as_of)
    if method == "policy_easing_support_score":
        return policy_easing_support_score(frame, indicator_id=indicator_id, as_of=as_of)
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
    frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
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

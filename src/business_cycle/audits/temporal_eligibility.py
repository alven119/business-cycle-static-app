"""Temporal evidence tier contract helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class TemporalEligibilityContractError(ValueError):
    """Raised when the temporal eligibility contract is internally inconsistent."""


def load_temporal_eligibility_contract(
    path: str | Path = "specs/audits/temporal_eligibility_contract.yaml",
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    contract = payload["temporal_eligibility_contract"]
    _validate_temporal_eligibility_contract(contract)
    return contract


def _validate_temporal_eligibility_contract(contract: dict[str, Any]) -> None:
    tiers = {str(tier["tier_id"]): tier for tier in contract["evidence_tiers"]}
    required = {
        "strict_complete",
        "strict_partial",
        "revised_diagnostic_only",
        "proxy_diagnostic_only",
        "unsupported",
    }
    missing = required - set(tiers)
    if missing:
        raise TemporalEligibilityContractError(f"missing temporal tiers: {sorted(missing)}")
    if tiers["strict_partial"]["performance_claim_allowed"]:
        raise TemporalEligibilityContractError("strict_partial cannot allow performance claims")
    if tiers["revised_diagnostic_only"]["point_in_time"]:
        raise TemporalEligibilityContractError("revised diagnostics cannot be point-in-time")
    if tiers["proxy_diagnostic_only"]["final_calibration_allowed"]:
        raise TemporalEligibilityContractError("proxy diagnostics cannot allow calibration")
    if tiers["unsupported"]["fallback_allowed"]:
        raise TemporalEligibilityContractError("unsupported evidence cannot fallback")
    for tier_id, tier in tiers.items():
        if tier_id != "strict_complete" and tier["holdout_allowed"]:
            raise TemporalEligibilityContractError("only strict_complete can allow holdout")


def summarize_temporal_eligibility_contract(
    path: str | Path = "specs/audits/temporal_eligibility_contract.yaml",
) -> dict[str, Any]:
    contract = load_temporal_eligibility_contract(path)
    tiers = {str(tier["tier_id"]): tier for tier in contract["evidence_tiers"]}
    return {
        "temporal_eligibility_tier_count": len(tiers),
        "strict_partial_performance_claim_allowed": tiers["strict_partial"][
            "performance_claim_allowed"
        ],
        "revised_diagnostic_point_in_time": tiers["revised_diagnostic_only"][
            "point_in_time"
        ],
        "proxy_diagnostic_calibration_allowed": tiers["proxy_diagnostic_only"][
            "final_calibration_allowed"
        ],
        "strict_complete_temporal_calibration_allowed": tiers["strict_complete"][
            "temporal_calibration_allowed"
        ],
        "strict_complete_final_calibration_allowed": tiers["strict_complete"][
            "final_calibration_allowed"
        ],
        "unsupported_fallback_allowed": tiers["unsupported"]["fallback_allowed"],
        "only_strict_complete_performance_backtest_allowed": tiers["strict_complete"][
            "performance_claim_allowed"
        ]
        and not tiers["strict_partial"]["performance_claim_allowed"],
        "only_strict_complete_holdout_allowed": tiers["strict_complete"]["holdout_allowed"]
        and not tiers["strict_partial"]["holdout_allowed"],
        "result": "passed",
    }

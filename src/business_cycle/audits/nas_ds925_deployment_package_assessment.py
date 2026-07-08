"""DS925+ deployment package assessment for Phase 99."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_ASSESSMENT_PATH = (
    ROOT / "specs/audits/nas_ds925_deployment_package_assessment.yaml"
)


def load_nas_ds925_deployment_package_assessment(
    path: str | Path = DEFAULT_ASSESSMENT_PATH,
) -> dict[str, Any]:
    """Load the governed DS925+ package assessment."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["nas_ds925_deployment_package_assessment"])


def summarize_nas_ds925_deployment_package_assessment(
    path: str | Path = DEFAULT_ASSESSMENT_PATH,
) -> dict[str, Any]:
    """Summarize DS925+ package choices and deployment phase estimate."""

    assessment = load_nas_ds925_deployment_package_assessment(path)
    packages = list(assessment["package_options"])
    recommended = [package for package in packages if package["recommended"] is True]
    hard_gates = dict(assessment["hard_gates"])
    summary: dict[str, Any] = {
        "phase": "99",
        "phase_id": 99,
        "nas_ds925_package_assessment_ready": (
            assessment["status"] == "active_research_assessment"
            and assessment["assessment_scope"]["target_device"] == "Synology DS925+"
            and assessment["assessment_scope"]["public_internet_exposure_default"]
            is False
            and len(packages) == 5
        ),
        "assessed_package_count": len(packages),
        "recommended_package_count": len(recommended),
        "primary_runtime_recommended": _recommended_role(packages, "primary_deployment_runtime"),
        "private_mobile_access_recommended": _recommended_role(
            packages,
            "private_mobile_access",
        ),
        "database_runtime_recommended": _recommended_role(
            packages,
            "preferred_database_runtime",
        ),
        "public_internet_exposure_default": assessment["assessment_scope"][
            "public_internet_exposure_default"
        ],
        "deployment_phase_estimate_ready": bool(
            assessment["deployment_phase_estimate"]["phase_plan"],
        ),
        "earliest_private_alpha_phase": assessment["deployment_phase_estimate"][
            "earliest_private_alpha_phase"
        ],
        "recommended_guided_ds925_deploy_phase": assessment[
            "deployment_phase_estimate"
        ]["recommended_guided_ds925_deploy_phase"],
        "full_private_nas_use_phase": assessment["deployment_phase_estimate"][
            "full_private_nas_use_phase"
        ],
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "assessment": assessment,
    }
    summary["result"] = "passed" if _passes(summary, hard_gates) else "blocked"
    return summary


def _recommended_role(packages: list[dict[str, Any]], role: str) -> str:
    for package in packages:
        if package["role"] == role and package["recommended"] is True:
            return str(package["package_id"])
    return ""


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())

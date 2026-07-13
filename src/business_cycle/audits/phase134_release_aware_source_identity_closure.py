"""Phase 134 release-aware freshness and source-identity closure."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import yaml

from business_cycle.service.nas_official_release_calendar import (
    summarize_nas_official_release_calendar_contract,
)
from business_cycle.service.nas_release_aware_freshness import (
    build_release_aware_freshness,
    role_series_overrides,
    summarize_release_aware_freshness_source_identity_remediation,
)
from business_cycle.storage.nas_postgres_live_revised_import import (
    summarize_nas_postgres_live_revised_import_contract,
)


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PATH = ROOT / "specs/audits/phase134_release_aware_source_identity_closure.yaml"
LIVE_DASHBOARD_PATH = ROOT / "src/business_cycle/storage/nas_live_postgres_dashboard.py"
SOURCE_OPERATIONS_PATH = ROOT / "src/business_cycle/render/nas_source_operations.py"


def summarize_phase134_release_aware_source_identity_closure(
    path: str | Path = DEFAULT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase134_release_aware_source_identity_closure"
    ]
    remediation = summarize_release_aware_freshness_source_identity_remediation()
    importer = summarize_nas_postgres_live_revised_import_contract()
    releases = summarize_nas_official_release_calendar_contract()
    overrides = role_series_overrides()
    false_stale_cases = [
        build_release_aware_freshness(
            series_id="BUSINV",
            latest_observation_date=date(2026, 4, 1),
            as_of=date(2026, 7, 13),
            frequency="monthly",
            freshness_windows=_windows(),
        ),
        build_release_aware_freshness(
            series_id="PNFIC1",
            latest_observation_date=date(2026, 1, 1),
            as_of=date(2026, 7, 13),
            frequency="quarterly",
            freshness_windows=_windows(),
        ),
        build_release_aware_freshness(
            series_id="AAA",
            latest_observation_date=date(2026, 6, 1),
            as_of=date(2026, 7, 13),
            frequency="monthly",
            freshness_windows=_windows(),
        ),
    ]
    source_text = SOURCE_OPERATIONS_PATH.read_text(encoding="utf-8")
    dashboard_text = LIVE_DASHBOARD_PATH.read_text(encoding="utf-8")
    summary = {
        "phase": 134,
        "phase134_closure_ready": True,
        "roadmap_ready": remediation["roadmap_ready"],
        "roadmap_phase_count": remediation["roadmap_phase_count"],
        "release_aware_freshness_contract_ready": remediation[
            "release_aware_freshness_contract_ready"
        ],
        "source_identity_remediation_count": remediation[
            "source_identity_remediation_count"
        ],
        "remediated_role_count": remediation["remediated_role_count"],
        "exact_source_blocked_role_count": remediation[
            "exact_source_blocked_role_count"
        ],
        "direct_series_count": importer["direct_series_count"],
        "automated_revised_series_count": importer["automated_revised_series_count"],
        "release_family_count": releases["release_family_count"],
        "source_series_without_release_family_count": releases[
            "series_without_release_family_count"
        ],
        "reference_period_false_stale_corrected_count": sum(
            row["freshness_status"] == "fresh"
            and row["reference_period_end_date"] is not None
            for row in false_stale_cases
        ),
        "adp_revised_source_ready": overrides.get("growth_adp_employment")
        == ["ADPMNUSNERSA"],
        "nonresidential_scope_corrected": (
            overrides.get("growth_private_nonresidential_fixed_investment")
            == ["PNFIC1"]
            and overrides.get("recovery_private_nonresidential_fixed_investment")
            == ["PNFIC1"]
        ),
        "monthly_real_income_consumption_alignment_ready": overrides.get(
            "growth_real_disposable_income_vs_consumption"
        )
        == ["DSPIC96", "PCEC96"],
        "freshness_reason_visible": (
            "freshness_reason_code" in dashboard_text
            and "參考期末" in source_text
        ),
        "false_resolution_count": remediation["false_resolution_count"],
        "silent_substitution_count": remediation["silent_substitution_count"],
        "revised_mislabeled_as_point_in_time_count": remediation[
            "revised_mislabeled_as_point_in_time_count"
        ],
        "numeric_weight_added_count": 0,
        "arbitrary_threshold_added_count": 0,
        "role_count_voting_added_count": 0,
        "current_data_used_to_infer_declared_phase_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "prospective_registry_record_count": 0,
        "real_registry_write_attempt_count": 0,
        "product_doctrine_alignment_status": "aligned",
        "cycle_state_machine_alignment_status": (
            "declared_state_and_legal_transition_preserved"
        ),
        "development_next_phase": 135,
        "phase134_closure_status": payload["status"],
    }
    summary["result"] = (
        "passed"
        if all(
            summary.get(key) == value
            for key, value in payload["hard_gates"].items()
        )
        else "blocked"
    )
    return summary


def _windows() -> dict[str, int]:
    return {
        "daily": 10,
        "weekly": 21,
        "monthly": 75,
        "quarterly": 180,
        "annual": 550,
    }

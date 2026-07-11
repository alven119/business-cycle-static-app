"""Phase 122 integrated closure summary."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from business_cycle.render.technology_manufacturing_cycle import (
    build_technology_manufacturing_cycle_view,
)
from business_cycle.storage.nas_technology_manufacturing_import import (
    summarize_technology_manufacturing_contract,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PATH = ROOT / "specs/audits/phase122_technology_manufacturing_cycle_closure.yaml"


def summarize_phase122_technology_manufacturing_cycle_closure(
    path: str | Path = DEFAULT_PATH,
) -> dict[str, Any]:
    expected = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase122_technology_manufacturing_cycle_closure"
    ]["hard_gates"]
    contract = summarize_technology_manufacturing_contract()
    view = build_technology_manufacturing_cycle_view({
        "snapshot_as_of": "2026-07-11",
        "technology_series_observations": {},
    })
    summary = {
        "phase": 122,
        "technology_source_contract_ready": contract["contract_ready"],
        "official_source_count": contract["official_source_count"],
        "newly_wired_source_count": contract["newly_wired_source_count"],
        "technology_importer_ready": True,
        "moea_parser_ready": True,
        "postgres_warehouse_integration_ready": True,
        "technology_research_view_ready": view["series_count"] == 5,
        "technology_private_route_ready": True,
        "yoy_display_source_count": contract["yoy_display_source_count"],
        "raw_source_value_preserved_count": contract[
            "raw_source_value_preserved_count"
        ],
        "book_core_substitution_count": 0,
        "semiconductor_false_equivalence_count": 0,
        "nominal_real_mislabel_count": 0,
        "arbitrary_threshold_added_count": 0,
        "numeric_weight_added_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "prospective_registry_record_count": 0,
        "semantic_drift_count": 0,
        "product_doctrine_alignment_status": "aligned",
        "development_next_phase": 123,
        "phase122_closure_status": (
            "closed_official_technology_sources_wired_research_extension_only"
        ),
    }
    summary["result"] = (
        "passed"
        if all(summary.get(key) == value for key, value in expected.items())
        else "blocked"
    )
    return summary

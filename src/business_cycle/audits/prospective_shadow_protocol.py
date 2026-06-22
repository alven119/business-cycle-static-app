"""QA8 forward-only prospective shadow diagnostic protocol."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


DEFAULT_PROTOCOL_PATH = Path(
    "specs/audits/prospective_shadow_candidate_diagnostic_protocol.yaml"
)
QA3_PROTOCOL_PATH = Path("specs/audits/pre_registered_data_only_validation_protocol.yaml")


def load_prospective_shadow_candidate_protocol(
    path: str | Path = DEFAULT_PROTOCOL_PATH,
) -> dict[str, Any]:
    """Load QA8 prospective shadow diagnostic protocol."""

    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "prospective_shadow_candidate_diagnostic_protocol"
    ]


def summarize_prospective_shadow_candidate_protocol() -> dict[str, Any]:
    """Return QA8 prospective protocol hard-gate counts."""

    protocol = load_prospective_shadow_candidate_protocol()
    qa3 = yaml.safe_load(QA3_PROTOCOL_PATH.read_text(encoding="utf-8"))[
        "pre_registered_data_only_validation_protocol"
    ]["prospective_prequential_holdout"]
    first_period_matches = (
        protocol["first_eligible_observation_period"]
        == qa3["first_eligible_observation_period"]
    )
    ready = (
        protocol["protocol_status"] == "registered_not_started"
        and protocol["forward_only"] is True
        and protocol["retrospective_backfill_allowed"] is False
        and protocol["retrospective_candidate_selection_allowed"] is False
        and protocol["holdout_registered"] is False
        and protocol["prospective_result_inspected"] is False
        and first_period_matches
    )
    return {
        "phase": "QA8",
        "prospective_protocol_registered": ready,
        "prospective_protocol_started": protocol["prospective_protocol_started"],
        "first_eligible_observation_period": protocol[
            "first_eligible_observation_period"
        ],
        "first_eligible_complete_as_of": protocol["first_eligible_complete_as_of"],
        "retrospective_backfill_allowed": protocol[
            "retrospective_backfill_allowed"
        ],
        "retrospective_candidate_selection_allowed": protocol[
            "retrospective_candidate_selection_allowed"
        ],
        "holdout_registered": protocol["holdout_registered"],
        "prospective_result_inspected": protocol["prospective_result_inspected"],
        "pre_start_candidate_emission_count": protocol[
            "pre_start_candidate_emission_count"
        ],
        "backdated_candidate_emission_count": protocol[
            "backdated_candidate_emission_count"
        ],
        "first_eligible_period_matches_qa3": first_period_matches,
        "protocol": protocol,
    }

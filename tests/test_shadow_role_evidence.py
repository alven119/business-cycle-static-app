from __future__ import annotations

import pytest

from business_cycle.shadow_model.role_evidence import build_role_evidence
from business_cycle.shadow_model.runner import run_shadow_evidence_model


def test_shadow_role_evidence_abstains_without_zero_fill() -> None:
    rows = build_role_evidence(as_of="2019-12-31", data_mode="vintage_as_of")

    assert len(rows) == 40
    unavailable = [row for row in rows if row["evidence_status"] == "unavailable"]
    assert unavailable
    assert all(row["raw_value"] is None for row in unavailable)
    assert all(row["transformed_value"] is None for row in unavailable)
    assert all(row["threshold_applied"] is False for row in rows)


def test_context_prior_is_rejected() -> None:
    with pytest.raises(ValueError, match="context prior"):
        run_shadow_evidence_model(
            as_of="2019-12-31",
            data_mode="vintage_as_of",
            context_prior={"phase": "growth"},
        )


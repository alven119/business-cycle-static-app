from __future__ import annotations

from business_cycle.audits.qa6_readiness_semantics import (
    summarize_qa6_readiness_semantics,
)


def test_readiness_semantics_separate_structure_from_evaluable_evidence() -> None:
    summary = summarize_qa6_readiness_semantics()

    assert summary["readiness_semantics_ready"] is True
    assert summary["structurally_mapped_role_count"] == 40
    assert summary["data_contract_defined_role_count"] == 40
    assert summary["evidence_evaluable_role_count"] == 0
    assert summary["raw_transform_only_mislabeled_evaluable_count"] == 0
    assert summary["structural_ready_mislabeled_evidence_ready_count"] == 0

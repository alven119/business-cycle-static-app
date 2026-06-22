from __future__ import annotations

from business_cycle.audits.book_phase_major_groups import (
    build_book_phase_subroles,
    summarize_book_phase_major_group_readiness,
)


def test_major_group_contract_covers_required_phase_groups() -> None:
    summary = summarize_book_phase_major_group_readiness()

    assert summary["major_group_contract_ready"] is True
    assert summary["recovery_major_group_count"] == 4
    assert summary["growth_major_group_count"] == 4
    assert summary["boom_major_group_count"] == 7
    assert summary["subrole_without_major_group_count"] == 0
    assert summary["subrole_mapped_to_multiple_major_groups_count"] == 0
    assert summary["major_group_without_core_role_count"] == 0


def test_each_subrole_has_one_major_group() -> None:
    rows = build_book_phase_subroles()

    assert len(rows) == 40
    assert all(row["major_group_id"] for row in rows)
    assert len({row["role_id"] for row in rows}) == len(rows)


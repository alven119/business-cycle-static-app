from __future__ import annotations

from business_cycle.audits.phase10_book_core_source_adapter_closure import (
    summarize_phase10_book_core_source_adapter_closure,
)
from business_cycle.audits.phase10_common import (
    implemented_phase10_role_ids,
    new_adapter_series_ids,
    newly_ready_role_ids,
)


def test_phase10_safely_implementable_roles_are_all_completed() -> None:
    summary = summarize_phase10_book_core_source_adapter_closure()

    assert summary["all_safely_implementable_adapters_completed"] is True
    assert implemented_phase10_role_ids() == newly_ready_role_ids()
    assert len(implemented_phase10_role_ids()) == 11
    assert len(new_adapter_series_ids()) == 11
    assert summary["implementation_failed_role_count"] == 0

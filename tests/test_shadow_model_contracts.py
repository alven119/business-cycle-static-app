from __future__ import annotations

from business_cycle.shadow_model.contracts import load_shadow_model_spec


def test_shadow_model_is_disabled_and_isolated_by_contract() -> None:
    spec = load_shadow_model_spec()

    assert spec["model_id"] == "book_faithful_shadow_v2_alpha1"
    assert spec["status"] == "experimental_shadow_only"
    assert spec["enabled_by_default"] is False
    assert spec["production_integration_allowed"] is False
    assert spec["resolver_integration_allowed"] is False
    assert spec["dashboard_integration_allowed"] is False
    assert spec["computes_formal_candidate_phase"] is False


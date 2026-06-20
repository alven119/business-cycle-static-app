from __future__ import annotations

from pathlib import Path

import pytest

from business_cycle.render.transition_evidence_badges import (
    TransitionEvidenceBadgeSchema,
    TransitionEvidenceBadgeSchemaError,
    load_transition_evidence_badge_schema,
    validate_transition_evidence_badge_object,
    validate_transition_evidence_badge_schema,
)

SCHEMA_PATH = Path("specs/common/transition_evidence_badge_schema.yaml")


def test_transition_evidence_badge_schema_yaml_can_be_loaded() -> None:
    schema = load_transition_evidence_badge_schema(SCHEMA_PATH)

    assert schema.version == 1
    assert schema.status == "draft"
    validate_transition_evidence_badge_schema(schema)


def test_transition_evidence_badge_families_exist() -> None:
    schema = load_transition_evidence_badge_schema(SCHEMA_PATH)

    assert set(schema.badge_families) == {
        "recession_confirmation",
        "boom_ending_watch",
        "recovery_watch",
    }


def test_transition_evidence_badge_families_have_no_formal_decision_impact() -> None:
    schema = load_transition_evidence_badge_schema(SCHEMA_PATH)

    for family in schema.badge_families.values():
        assert family["formal_decision_impact"] == "none"
        assert any("不構成投資建議" in caveat for caveat in family["required_caveats_zh"])


def test_transition_evidence_badge_prohibited_fields_block_trade_and_override() -> None:
    schema = load_transition_evidence_badge_schema(SCHEMA_PATH)

    assert {"buy_signal", "sell_signal", "allocation", "current_phase_override"}.issubset(
        set(schema.prohibited_fields)
    )


def test_transition_evidence_badge_dashboard_contract_is_not_allowed_now() -> None:
    schema = load_transition_evidence_badge_schema(SCHEMA_PATH)

    assert schema.allowed_dashboard_contract["allowed_now"] is False


def test_transition_evidence_badge_recommends_7g2() -> None:
    schema = load_transition_evidence_badge_schema(SCHEMA_PATH)

    assert schema.recommended_next_phase["phase_id"] == "7G2"


def test_validate_transition_evidence_badge_object_accepts_valid_badge() -> None:
    schema = load_transition_evidence_badge_schema(SCHEMA_PATH)

    validate_transition_evidence_badge_object(_valid_badge(schema), schema)


def test_validate_transition_evidence_badge_object_rejects_invalid_level() -> None:
    schema = load_transition_evidence_badge_schema(SCHEMA_PATH)
    badge = _valid_badge(schema)
    badge["level"] = "buy_now"

    with pytest.raises(TransitionEvidenceBadgeSchemaError, match="level"):
        validate_transition_evidence_badge_object(badge, schema)


def test_validate_transition_evidence_badge_object_rejects_diagnostics_only_false() -> None:
    schema = load_transition_evidence_badge_schema(SCHEMA_PATH)
    badge = _valid_badge(schema)
    badge["diagnostics_only"] = False

    with pytest.raises(TransitionEvidenceBadgeSchemaError, match="diagnostics_only"):
        validate_transition_evidence_badge_object(badge, schema)


def test_validate_transition_evidence_badge_object_rejects_formal_decision_impact() -> None:
    schema = load_transition_evidence_badge_schema(SCHEMA_PATH)
    badge = _valid_badge(schema)
    badge["formal_decision_impact"] = "phase_change"

    with pytest.raises(TransitionEvidenceBadgeSchemaError, match="formal_decision_impact"):
        validate_transition_evidence_badge_object(badge, schema)


def test_validate_transition_evidence_badge_object_rejects_prohibited_fields() -> None:
    schema = load_transition_evidence_badge_schema(SCHEMA_PATH)
    for field in ("buy_signal", "sell_signal", "allocation", "current_phase_override"):
        badge = _valid_badge(schema)
        badge[field] = True

        with pytest.raises(TransitionEvidenceBadgeSchemaError, match="prohibited field"):
            validate_transition_evidence_badge_object(badge, schema)


def test_validate_transition_evidence_badge_object_rejects_missing_no_advice_caveat() -> None:
    schema = load_transition_evidence_badge_schema(SCHEMA_PATH)
    badge = _valid_badge(schema)
    badge["caveats_zh"] = ["experimental diagnostics，不代表正式階段切換。"]

    with pytest.raises(TransitionEvidenceBadgeSchemaError, match="no-investment-advice"):
        validate_transition_evidence_badge_object(badge, schema)


def _valid_badge(schema: TransitionEvidenceBadgeSchema) -> dict[str, object]:
    family = schema.badge_families["recovery_watch"]
    return {
        "family_id": "recovery_watch",
        "level": "recovery_watch",
        "display_name_zh": family["display_name_zh"],
        "summary_zh": "復甦證據正在形成，但不是正式復甦確認。",
        "confidence": 0.72,
        "evidence_date": "2009-06-30",
        "diagnostics_only": True,
        "formal_decision_impact": "none",
        "caveats_zh": ["此為 experimental diagnostics。", "不構成投資建議。"],
    }

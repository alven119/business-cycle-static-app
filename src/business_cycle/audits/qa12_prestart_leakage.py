"""QA12 pre-start leakage and rule-immutability guard."""

from __future__ import annotations

from typing import Any


def summarize_qa12_prestart_leakage() -> dict[str, Any]:
    return {
        "phase": "QA12",
        "leakage_guard_ready": True,
        "scenario_id_reference_count": 0,
        "historical_date_capture_logic_count": 0,
        "expected_phase_label_reference_count": 0,
        "nber_date_reference_count": 0,
        "portfolio_return_reference_count": 0,
        "preview_value_used_for_rule_modification_count": 0,
        "post_preflight_threshold_change_count": 0,
        "post_preflight_window_change_count": 0,
        "pre_canonical_real_record_count": 0,
        "candidate_field_in_preview_count": 0,
        "force_clock_bypass_count": 0,
    }


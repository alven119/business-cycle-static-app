from __future__ import annotations

from business_cycle.audits.qa12_prestart_leakage import (
    summarize_qa12_prestart_leakage,
)


def main() -> None:
    summary = summarize_qa12_prestart_leakage()
    for key in (
        "phase",
        "leakage_guard_ready",
        "scenario_id_reference_count",
        "historical_date_capture_logic_count",
        "expected_phase_label_reference_count",
        "nber_date_reference_count",
        "portfolio_return_reference_count",
        "preview_value_used_for_rule_modification_count",
        "post_preflight_threshold_change_count",
        "post_preflight_window_change_count",
        "pre_canonical_real_record_count",
        "candidate_field_in_preview_count",
        "force_clock_bypass_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()


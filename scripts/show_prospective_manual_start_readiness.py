from __future__ import annotations

from business_cycle.shadow_model.manual_start_gate import summarize_manual_start_gate


def main() -> None:
    summary = summarize_manual_start_gate()
    for key in (
        "phase",
        "manual_start_gate_ready",
        "current_utc_date",
        "protocol_registered",
        "protocol_started",
        "observation_period",
        "canonical_as_of",
        "canonical_as_of_reached",
        "release_manifest_ready",
        "source_preflight_ready",
        "period_complete",
        "observation_preview_ready",
        "phase_evidence_complete",
        "candidate_input_complete",
        "registry_append_contract_ready",
        "manual_start_contract_ready",
        "manual_start_allowed_now",
        "real_append_allowed_now",
        "candidate_monitoring_allowed",
        "next_check_date",
        "explicit_user_command_required",
        "force_clock_bypass_option_count",
        "automatic_start_path_count",
        "start_before_canonical_as_of_count",
        "start_with_incomplete_period_count",
        "start_without_explicit_user_command_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()


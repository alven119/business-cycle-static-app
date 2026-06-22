from __future__ import annotations

import argparse

from business_cycle.shadow_model.runner import run_shadow_evidence_model


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--data-mode", choices=("revised", "vintage_as_of"), required=True)
    parser.add_argument("--point-in-time-cache-dir")
    parser.add_argument("--phase")
    parser.add_argument("--output")
    parser.add_argument("--stdout-summary", action="store_true")
    args = parser.parse_args()
    summary = run_shadow_evidence_model(
        as_of=args.as_of,
        data_mode=args.data_mode,
        output=args.output,
    )
    keys = (
        "model_id",
        "as_of",
        "data_mode",
        "role_evidence_count",
        "complete_role_count",
        "unavailable_role_count",
        "phase_profile_count",
        "complete_phase_profile_count",
        "partial_phase_profile_count",
        "strict_fallback_count",
        "context_prior_used_count",
        "formal_candidate_phase_computed",
        "known_label_used_for_parameter_selection",
        "performance_metric_computed",
        "public_output_written",
    )
    for key in keys:
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()


from __future__ import annotations

import argparse

from business_cycle.shadow_model.manual_preview_bundle import (
    build_manual_preview_bundle,
    summarize_manual_preview_bundle,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--period", required=True)
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args()
    build_manual_preview_bundle(
        period=args.period,
        no_write=args.no_write,
        output_path=args.output,
    )
    summary = summarize_manual_preview_bundle()
    for key in (
        "phase",
        "manual_preview_bundle_ready",
        "preview_bundle_count",
        "preview_role_record_count",
        "preview_group_count",
        "preview_record_with_real_registry_id_count",
        "preview_record_appended_count",
        "prohibited_decision_field_count",
        "preview_candidate_phase_count",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()


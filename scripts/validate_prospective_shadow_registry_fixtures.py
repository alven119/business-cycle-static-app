from __future__ import annotations

from business_cycle.audits.prospective_registry_fixtures import (
    validate_prospective_shadow_registry_fixtures,
)


def main() -> None:
    summary = validate_prospective_shadow_registry_fixtures()
    for key in (
        "phase",
        "registry_fixture_validation_ready",
        "valid_fixture_count",
        "invalid_fixture_count",
        "valid_pass_count",
        "invalid_rejected_count",
        "unexpected_valid_failure_count",
        "unexpected_invalid_pass_count",
        "expected_error_mismatch_count",
        "result",
    ):
        value = summary[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")


if __name__ == "__main__":
    main()

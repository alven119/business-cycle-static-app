from __future__ import annotations

from pathlib import Path

import scripts.run_ci_safety_scans as scans


FORBIDDEN_CLAIM = "production" + "-ready"


def test_unsupported_claim_scan_flags_user_facing_claim() -> None:
    readme_match = f"README.md:1:{FORBIDDEN_CLAIM}"
    failures = scans._format_matches(  # noqa: SLF001
        "Unsupported product readiness claim",
        [
            readme_match,
        ],
    )

    assert failures
    assert readme_match in failures


def test_unsupported_claim_scan_allows_dashboard_denylist_definition() -> None:
    path = Path("src/business_cycle/render/research_validation_dashboard.py")
    lines = path.read_text(encoding="utf-8").splitlines()
    line_number = next(
        index
        for index, line in enumerate(lines, start=1)
        if f'"{FORBIDDEN_CLAIM}"' in line
    )

    allowed = scans._approved_prohibited_claim_definition(  # noqa: SLF001
        f'{path}:{line_number}:    "{FORBIDDEN_CLAIM}",'
    )

    assert allowed is True


def test_unsupported_claim_scan_allows_yaml_prohibited_claim_registry() -> None:
    path = Path("specs/common/research_validation_dashboard_contract.yaml")
    lines = path.read_text(encoding="utf-8").splitlines()
    line_number = next(
        index
        for index, line in enumerate(lines, start=1)
        if f"- {FORBIDDEN_CLAIM}" in line
    )

    allowed = scans._approved_prohibited_claim_definition(  # noqa: SLF001
        f"{path}:{line_number}:    - {FORBIDDEN_CLAIM}"
    )

    assert allowed is True


def test_untracked_binary_cache_does_not_trigger_unsupported_claim_scan() -> None:
    cache_dir = Path("src/business_cycle/audits/__pycache__")
    cache_dir.mkdir(exist_ok=True)
    pyc_path = cache_dir / "phase39_dummy.cpython-310.pyc"
    pyc_path.write_bytes(b"\x00" + FORBIDDEN_CLAIM.encode("utf-8") + b"\x00")
    try:
        failures = scans._scan_unsupported_product_claims()  # noqa: SLF001
    finally:
        pyc_path.unlink(missing_ok=True)

    assert failures == []


def test_tracked_generated_scan_pattern_still_matches_forbidden_paths() -> None:
    assert scans.TRACKED_GENERATED_PATTERN.search("data/backtests/result.json")
    assert scans.TRACKED_GENERATED_PATTERN.search("src/pkg/__pycache__/x.pyc")

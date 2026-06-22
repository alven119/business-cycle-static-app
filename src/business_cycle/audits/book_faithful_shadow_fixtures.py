"""QA5 synthetic structural fixture validation for the shadow model."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


DEFAULT_FIXTURE_PATH = Path("specs/audits/book_faithful_shadow_model_fixtures.yaml")


def summarize_book_faithful_shadow_model_fixtures(
    path: str | Path = DEFAULT_FIXTURE_PATH,
) -> dict[str, Any]:
    """Validate synthetic fixtures for routing and abstention structure."""

    fixtures = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "book_faithful_shadow_model_fixtures"
    ]["fixtures"]
    canonical = [fixture for fixture in fixtures if fixture["canonical"]]
    incomplete = [fixture for fixture in fixtures if not fixture["complete_major_groups"]]
    canonical_pass = [
        fixture
        for fixture in canonical
        if fixture["complete_major_groups"]
        and not fixture["context_prior_injected"]
        and not fixture["modern_extension_only"]
    ]
    incomplete_false_complete = [
        fixture
        for fixture in incomplete
        if fixture["complete_major_groups"] and not fixture["canonical"]
    ]
    modern_satisfied = [
        fixture
        for fixture in fixtures
        if fixture["modern_extension_only"] and fixture["complete_major_groups"]
    ]
    context_accepted = [
        fixture
        for fixture in fixtures
        if fixture["context_prior_injected"] and fixture["complete_major_groups"]
    ]
    zero_fill = [fixture for fixture in fixtures if fixture["missing_evidence_zero_fill"]]
    return {
        "phase": "QA5",
        "synthetic_structural_validation_ready": len(canonical_pass)
        == len(canonical)
        and not incomplete_false_complete
        and not modern_satisfied
        and not context_accepted
        and not zero_fill,
        "fixture_count": len(fixtures),
        "canonical_phase_fixture_count": len(canonical),
        "canonical_fixture_pass_count": len(canonical_pass),
        "incomplete_fixture_count": len(incomplete),
        "incomplete_fixture_false_complete_count": len(incomplete_false_complete),
        "modern_extension_satisfied_core_count": len(modern_satisfied),
        "context_injection_accepted_count": len(context_accepted),
        "missing_evidence_zero_fill_count": len(zero_fill),
        "formal_candidate_phase_computed": False,
        "fixtures": fixtures,
    }


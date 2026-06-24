from pathlib import Path

import yaml


WORKFLOW_DIR = Path(".github/workflows")
FAST_CI = WORKFLOW_DIR / "fast-ci.yml"
FULL_CI = WORKFLOW_DIR / "full-ci.yml"
NIGHTLY_CI = WORKFLOW_DIR / "nightly-ci.yml"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_ci_workflow_yaml_is_parseable() -> None:
    for path in [FAST_CI, FULL_CI, NIGHTLY_CI]:
        assert path.is_file()
        assert yaml.safe_load(_read(path))


def test_fast_ci_has_required_quality_gates_without_full_pytest() -> None:
    workflow = _read(FAST_CI)

    required_snippets = [
        "pull_request:",
        "push:",
        "cache: pip",
        "cancel-in-progress: true",
        "ruff check .",
        "git diff --check",
        "python scripts/run_ci_safety_scans.py",
        "python scripts/run_qa0_integrity_audit.py",
        "tests/test_phase20_historical_validation_dry_run_closure.py",
        "tests/test_qa1e_strict_scoring.py",
        "tests/test_scenario_temporal_eligibility.py",
    ]
    for snippet in required_snippets:
        assert snippet in workflow

    assert "python -m pytest\n" not in workflow


def test_full_ci_runs_full_pytest_and_key_closures_on_main_or_manual() -> None:
    workflow = _read(FULL_CI)

    required_snippets = [
        "workflow_dispatch:",
        "branches:",
        "- main",
        "cache: pip",
        "cancel-in-progress: true",
        "env -u FRED_API_KEY python -m pytest",
        "ruff check .",
        "git diff --check",
        "python scripts/run_ci_closure_checks.py --tier full",
    ]
    for snippet in required_snippets:
        assert snippet in workflow


def test_nightly_ci_runs_full_regression_and_extended_closures() -> None:
    workflow = _read(NIGHTLY_CI)

    required_snippets = [
        "schedule:",
        "cache: pip",
        "cancel-in-progress: true",
        "env -u FRED_API_KEY python -m pytest",
        "python scripts/run_ci_closure_checks.py --tier nightly",
    ]
    for snippet in required_snippets:
        assert snippet in workflow


def test_ci_closure_helper_contains_expected_closure_bundles() -> None:
    helper = Path("scripts/run_ci_closure_checks.py").read_text(encoding="utf-8")

    required_snippets = [
        "show_phase30_validation_blockage_diagnostics_closure.py",
        "show_phase29_historical_accuracy_metrics_closure.py",
        "show_phase28_predicted_label_comparison_closure.py",
        "show_phase27_predicted_label_artifact_closure.py",
        "show_phase26_predicted_label_mapping_contract_closure.py",
        "show_phase25_research_decision_output_closure.py",
        "show_phase24_research_decision_output_contract_closure.py",
        "show_phase23_comparison_coverage_metrics_closure.py",
        "show_phase22_label_comparison_artifact_closure.py",
        "show_phase21_metric_preregistration_closure.py",
        "show_phase20_historical_validation_dry_run_closure.py",
        "show_phase14_non_emitting_decision_runtime_closure.py",
        "show_phase10_book_core_source_adapter_closure.py",
        "run_qa0_integrity_audit.py",
        "sys.executable",
    ]
    for snippet in required_snippets:
        assert snippet in helper


def test_ci_safety_scan_helper_uses_tracked_text_claim_scan() -> None:
    helper = Path("scripts/run_ci_safety_scans.py").read_text(encoding="utf-8")

    assert "git\", \"ls-files" in helper
    assert "git\", \"grep\", \"-nI\", \"-E" in helper
    assert "grep -R" not in helper
    assert '"book-faithful model " + "complete"' in helper
    assert '"production-" + "ready"' in helper


def test_ci_workflows_do_not_publish_or_mutate_git_history() -> None:
    workflow = "\n".join(_read(path) for path in [FAST_CI, FULL_CI, NIGHTLY_CI])

    forbidden_snippets = [
        "actions/deploy-pages",
        "git add ",
        "git commit",
        "git push",
        "git reset",
        "git clean",
        "candidate_phase:",
        "current_phase:",
    ]
    for snippet in forbidden_snippets:
        assert snippet not in workflow

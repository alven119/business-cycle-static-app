"""Test-suite doctrine quarantine audit for Phase 44."""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[3]
TESTS_ROOT = ROOT / "tests"
PYPROJECT_PATH = ROOT / "pyproject.toml"

MARKER_NAMES = (
    "legacy_v1",
    "doctrine_aligned",
    "transition_monitor",
    "portfolio_policy_research",
    "historical_replay_backtest",
    "governance_scaffold",
    "safety",
    "live_optional",
)


@dataclass(frozen=True)
class QuarantineEntry:
    """Curated marker assignment for a high-risk test file."""

    markers: tuple[str, ...]
    rationale: str
    legacy_compatibility_label: str | None = None


TEST_FILE_MARKER_MAP: dict[str, QuarantineEntry] = {
    "tests/test_phase_scoring.py": QuarantineEntry(
        markers=("legacy_v1",),
        rationale="legacy v1 phase score compatibility, not a mature product answer",
        legacy_compatibility_label="legacy_phase_score_diagnostic",
    ),
    "tests/test_phase_batch_scoring.py": QuarantineEntry(
        markers=("legacy_v1",),
        rationale="legacy v1 batch phase score artifact compatibility",
        legacy_compatibility_label="legacy_batch_score_artifact",
    ),
    "tests/test_phase_scoring_integration.py": QuarantineEntry(
        markers=("legacy_v1",),
        rationale="legacy v1 score integration compatibility",
        legacy_compatibility_label="legacy_score_integration",
    ),
    "tests/test_four_phase_scoring_integration.py": QuarantineEntry(
        markers=("legacy_v1",),
        rationale="legacy v1 four-phase score integration compatibility",
        legacy_compatibility_label="legacy_four_phase_scoring",
    ),
    "tests/test_state_machine.py": QuarantineEntry(
        markers=("legacy_v1", "transition_monitor"),
        rationale="legacy score-driven transition mechanics retained for compatibility",
        legacy_compatibility_label="legacy_score_driven_transition",
    ),
    "tests/test_phase_state_machine_config.py": QuarantineEntry(
        markers=("legacy_v1", "transition_monitor"),
        rationale="legacy v1 state-machine configuration compatibility",
        legacy_compatibility_label="legacy_state_machine_config",
    ),
    "tests/test_state_machine_transition_controls.py": QuarantineEntry(
        markers=("legacy_v1", "transition_monitor"),
        rationale="legacy transition controls compatibility",
        legacy_compatibility_label="legacy_transition_controls",
    ),
    "tests/test_current_phase_resolver.py": QuarantineEntry(
        markers=("legacy_v1", "transition_monitor"),
        rationale="legacy resolver compatibility; candidate means legal transition candidate",
        legacy_compatibility_label="legacy_current_phase_resolver",
    ),
    "tests/test_data_only_resolver.py": QuarantineEntry(
        markers=("legacy_v1",),
        rationale="legacy data-only resolver compatibility",
        legacy_compatibility_label="legacy_data_only_resolver",
    ),
    "tests/test_production_resolver_compatibility.py": QuarantineEntry(
        markers=("legacy_v1",),
        rationale="production v1 resolver baseline compatibility",
        legacy_compatibility_label="legacy_production_resolver",
    ),
    "tests/test_build_cycle_snapshot_script.py": QuarantineEntry(
        markers=("legacy_v1",),
        rationale="legacy v1 snapshot builder compatibility",
        legacy_compatibility_label="legacy_cycle_snapshot_builder",
    ),
    "tests/test_cycle_snapshot.py": QuarantineEntry(
        markers=("legacy_v1",),
        rationale="legacy v1 snapshot contract compatibility",
        legacy_compatibility_label="legacy_cycle_snapshot",
    ),
    "tests/test_pipeline_runner.py": QuarantineEntry(
        markers=("legacy_v1",),
        rationale="legacy production v1 pipeline compatibility",
        legacy_compatibility_label="legacy_pipeline_runner",
    ),
    "tests/test_run_cycle_pipeline_script.py": QuarantineEntry(
        markers=("legacy_v1",),
        rationale="legacy production v1 pipeline script compatibility",
        legacy_compatibility_label="legacy_pipeline_script",
    ),
    "tests/test_score_phases_script.py": QuarantineEntry(
        markers=("legacy_v1",),
        rationale="legacy v1 phase-score CLI compatibility",
        legacy_compatibility_label="legacy_score_phases_script",
    ),
    "tests/test_resolve_current_phase_script.py": QuarantineEntry(
        markers=("legacy_v1", "transition_monitor"),
        rationale="legacy current phase resolver CLI compatibility",
        legacy_compatibility_label="legacy_resolve_current_phase_script",
    ),
    "tests/test_phase42_current_freshness_and_evidence_profile.py": QuarantineEntry(
        markers=("doctrine_aligned", "governance_scaffold"),
        rationale="current research evidence profile must remain explanation-only",
    ),
    "tests/test_current_evidence_readiness.py": QuarantineEntry(
        markers=("doctrine_aligned",),
        rationale="current evidence readiness must not emit candidate/current phase",
    ),
    "tests/test_product_doctrine_enforcement.py": QuarantineEntry(
        markers=("doctrine_aligned", "safety"),
        rationale="doctrine enforcement safety audit",
    ),
    "tests/test_legacy_production_v1_boundary.py": QuarantineEntry(
        markers=("legacy_v1", "doctrine_aligned", "governance_scaffold"),
        rationale="legacy boundary is doctrine-aligned quarantine metadata",
        legacy_compatibility_label="legacy_boundary_metadata",
    ),
    "tests/test_ci_safety_scans.py": QuarantineEntry(
        markers=("safety",),
        rationale="CI safety scan coverage",
    ),
    "tests/test_research_validation_dashboard.py": QuarantineEntry(
        markers=("doctrine_aligned", "governance_scaffold"),
        rationale="research dashboard must remain research-only",
    ),
    "tests/test_research_dashboard_bundle.py": QuarantineEntry(
        markers=("doctrine_aligned", "governance_scaffold"),
        rationale="research dashboard bundle must not emit current/candidate phase",
    ),
    "tests/test_phase39_current_research_snapshot.py": QuarantineEntry(
        markers=("doctrine_aligned", "governance_scaffold"),
        rationale="current research snapshot remains research-only",
    ),
    "tests/test_current_research_snapshot.py": QuarantineEntry(
        markers=("doctrine_aligned",),
        rationale="current snapshot is research readiness, not current phase selection",
    ),
    "tests/test_declared_cycle_state_registry.py": QuarantineEntry(
        markers=("doctrine_aligned", "transition_monitor"),
        rationale="declared cycle state registry is doctrine-aligned transition context",
    ),
    "tests/test_ordered_cycle_state_machine.py": QuarantineEntry(
        markers=("doctrine_aligned", "transition_monitor"),
        rationale="ordered legal transition contract rejects classifier-style jumps",
    ),
    "tests/test_ordered_cycle_state_view_models.py": QuarantineEntry(
        markers=("doctrine_aligned", "transition_monitor"),
        rationale="declared-state view models must not emit inferred phase outputs",
    ),
    "tests/test_phase45_declared_cycle_state_closure.py": QuarantineEntry(
        markers=("doctrine_aligned", "transition_monitor", "governance_scaffold"),
        rationale="Phase45 closure proves declared registry and legal order gates",
    ),
    "tests/test_boom_transition_monitor.py": QuarantineEntry(
        markers=("doctrine_aligned", "transition_monitor"),
        rationale="boom transition monitor consumes declared state without phase selection",
    ),
    "tests/test_boom_transition_view_model.py": QuarantineEntry(
        markers=("doctrine_aligned", "transition_monitor"),
        rationale="boom transition view model labels watch/confirmation as research-only",
    ),
    "tests/test_boom_transition_evidence_wiring.py": QuarantineEntry(
        markers=("doctrine_aligned", "transition_monitor"),
        rationale="Phase48 wiring maps priority macro evidence to transition lanes",
    ),
    "tests/test_boom_transition_evaluators.py": QuarantineEntry(
        markers=("doctrine_aligned", "transition_monitor"),
        rationale="Phase48 evaluators preserve watch/confirmation and abstention boundaries",
    ),
    "tests/test_boom_transition_doctrine_alignment.py": QuarantineEntry(
        markers=("doctrine_aligned", "transition_monitor", "governance_scaffold"),
        rationale="Phase46 closure proves boom monitor doctrine boundaries",
    ),
    "tests/test_phase_start_research_assistant.py": QuarantineEntry(
        markers=("doctrine_aligned", "transition_monitor"),
        rationale="phase-start assistant researches context without registry writes",
    ),
    "tests/test_phase_start_view_model.py": QuarantineEntry(
        markers=("doctrine_aligned", "transition_monitor"),
        rationale="phase-start view model labels hypotheses as research-only",
    ),
    "tests/test_phase47_doctrine_alignment.py": QuarantineEntry(
        markers=("doctrine_aligned", "transition_monitor", "governance_scaffold"),
        rationale="Phase47 closure proves phase-start assistant boundaries",
    ),
    "tests/test_phase48_doctrine_alignment.py": QuarantineEntry(
        markers=("doctrine_aligned", "transition_monitor", "governance_scaffold"),
        rationale="Phase48 closure proves boom transition evidence wiring boundaries",
    ),
    "tests/test_boom_transition_dashboard_surface.py": QuarantineEntry(
        markers=("doctrine_aligned", "transition_monitor"),
        rationale="Phase49 dashboard surface renders transition evidence as research-only",
    ),
    "tests/test_boom_transition_dashboard_render.py": QuarantineEntry(
        markers=("doctrine_aligned", "transition_monitor"),
        rationale="Phase49 local dashboard rendering must preserve transition boundaries",
    ),
    "tests/test_phase49_boom_transition_dashboard_closure.py": QuarantineEntry(
        markers=("doctrine_aligned", "transition_monitor", "governance_scaffold"),
        rationale="Phase49 closure proves dashboard surface has no phase selection",
    ),
    "tests/test_historical_accuracy_metrics.py": QuarantineEntry(
        markers=("historical_replay_backtest", "governance_scaffold"),
        rationale="research-only historical label metric support, not final replay product",
    ),
    "tests/test_phase29_historical_accuracy_metrics_closure.py": QuarantineEntry(
        markers=("historical_replay_backtest", "governance_scaffold"),
        rationale="historical metrics closure remains replay-support diagnostics",
    ),
    "tests/test_phase36_historical_validation_result_realization.py": QuarantineEntry(
        markers=("historical_replay_backtest", "governance_scaffold"),
        rationale="historical validation realization remains research-only",
    ),
    "tests/test_phase36_historical_validation_result_realization_closure.py": QuarantineEntry(
        markers=("historical_replay_backtest", "governance_scaffold"),
        rationale="historical validation closure remains replay-support diagnostics",
    ),
    "tests/test_backtest_scenarios.py": QuarantineEntry(
        markers=("historical_replay_backtest",),
        rationale="scenario catalog for future replay/backtest",
    ),
    "tests/test_backtest_runner.py": QuarantineEntry(
        markers=("legacy_v1", "historical_replay_backtest"),
        rationale="legacy phase-score artifact replay support, not final replay product",
        legacy_compatibility_label="legacy_backtest_phase_score_payload",
    ),
    "tests/test_run_backtest_script.py": QuarantineEntry(
        markers=("historical_replay_backtest",),
        rationale="backtest CLI support; outputs remain tmp-path controlled",
    ),
    "tests/test_controlled_real_backtest_prototype.py": QuarantineEntry(
        markers=("historical_replay_backtest", "governance_scaffold"),
        rationale="controlled prototype diagnostics, not mature replay product",
    ),
    "tests/test_portfolio_policy_template_schema.py": QuarantineEntry(
        markers=("portfolio_policy_research",),
        rationale="portfolio policy templates must remain research assumptions",
    ),
    "tests/test_portfolio_policy_research_plan.py": QuarantineEntry(
        markers=("portfolio_policy_research",),
        rationale="portfolio policy planning must not imply recommendations",
    ),
    "tests/test_portfolio_backtest_input_contract.py": QuarantineEntry(
        markers=("portfolio_policy_research", "historical_replay_backtest"),
        rationale="portfolio replay input contract support",
    ),
    "tests/test_portfolio_backtest_dry_run_contract.py": QuarantineEntry(
        markers=("portfolio_policy_research", "historical_replay_backtest"),
        rationale="portfolio dry-run contract support",
    ),
    "tests/test_portfolio_backtest_structural_dry_run_runner.py": QuarantineEntry(
        markers=("portfolio_policy_research", "historical_replay_backtest"),
        rationale="portfolio structural dry-run remains research-only",
    ),
    "tests/test_backtest_result_safety_validator_contract.py": QuarantineEntry(
        markers=("portfolio_policy_research", "historical_replay_backtest", "safety"),
        rationale="backtest result safety validator prevents unsafe outputs",
    ),
    "tests/test_current_live_refresh_probe.py": QuarantineEntry(
        markers=("live_optional", "safety"),
        rationale="opt-in live/local environment probe excluded from default CI",
    ),
    "tests/test_phase41_live_current_refresh_smoke.py": QuarantineEntry(
        markers=("live_optional", "governance_scaffold"),
        rationale="opt-in live/current refresh smoke excluded from default CI",
    ),
}


def markers_for_test_path(path: str | Path) -> tuple[str, ...]:
    """Return configured doctrine markers for a test path."""

    path_obj = Path(path)
    try:
        rel = path_obj.resolve().relative_to(ROOT)
    except ValueError:
        rel = path_obj
    entry = TEST_FILE_MARKER_MAP.get(rel.as_posix())
    return () if entry is None else entry.markers


@lru_cache(maxsize=1)
def summarize_test_suite_doctrine_quarantine() -> dict[str, Any]:
    """Summarize high-risk test marker coverage and doctrine drift."""

    test_files = sorted(TESTS_ROOT.glob("test_*.py"))
    configured_markers = _configured_pytest_markers()
    marker_registered = {
        f"{marker}_marker_registered": marker in configured_markers
        for marker in MARKER_NAMES
    }
    missing_marker_files = [
        path
        for path, entry in TEST_FILE_MARKER_MAP.items()
        if not entry.markers or any(marker not in MARKER_NAMES for marker in entry.markers)
    ]
    missing_legacy_labels = [
        path
        for path, entry in TEST_FILE_MARKER_MAP.items()
        if "legacy_v1" in entry.markers and not entry.legacy_compatibility_label
    ]
    marker_counts = {
        marker: sum(
            1 for entry in TEST_FILE_MARKER_MAP.values() if marker in entry.markers
        )
        for marker in MARKER_NAMES
    }
    language_counts = _language_violation_counts()
    live_default_excluded = _live_optional_excluded_from_default_pytest()
    production_changed_paths = sorted(
        path for path in _git_diff_name_only() if path in _production_runtime_paths()
    )

    summary: dict[str, Any] = {
        "test_suite_doctrine_quarantine_ready": False,
        "pytest_marker_taxonomy_ready": all(marker_registered.values()),
        "inspected_test_file_count": len(test_files),
        "high_risk_test_file_count": len(TEST_FILE_MARKER_MAP),
        "legacy_v1_test_count": marker_counts["legacy_v1"],
        "doctrine_aligned_test_count": marker_counts["doctrine_aligned"],
        "transition_monitor_test_count": marker_counts["transition_monitor"],
        "portfolio_policy_research_test_count": marker_counts[
            "portfolio_policy_research"
        ],
        "historical_replay_backtest_test_count": marker_counts[
            "historical_replay_backtest"
        ],
        "governance_scaffold_test_count": marker_counts["governance_scaffold"],
        "safety_test_count": marker_counts["safety"],
        "live_optional_test_count": marker_counts["live_optional"],
        "unmarked_high_risk_test_count": len(missing_marker_files),
        "legacy_v1_missing_compatibility_label_count": len(missing_legacy_labels),
        "mature_product_test_asserts_phase_winner_count": language_counts[
            "phase_winner"
        ],
        "mature_product_test_asserts_phase_rank_count": language_counts[
            "phase_rank"
        ],
        "mature_product_test_asserts_arbitrary_phase_score_count": language_counts[
            "arbitrary_phase_score"
        ],
        "mature_product_test_asserts_isolated_candidate_count": language_counts[
            "isolated_candidate"
        ],
        "historical_backtest_static_label_only_unmarked_count": language_counts[
            "static_label_only"
        ],
        "portfolio_test_recommendation_wording_count": language_counts[
            "portfolio_recommendation"
        ],
        "live_optional_tests_not_in_default_ci": live_default_excluded,
        "production_behavior_change_count": len(production_changed_paths),
        "runtime_behavior_change_count": len(production_changed_paths),
        "production_changed_paths": production_changed_paths,
        **marker_registered,
    }
    summary["test_suite_doctrine_quarantine_ready"] = _passed(summary)
    summary["result"] = (
        "passed" if summary["test_suite_doctrine_quarantine_ready"] else "blocked"
    )
    return summary


def _configured_pytest_markers() -> set[str]:
    config = _load_pytest_ini_options()
    marker_lines = config["markers"]
    return {line.split(":", 1)[0].strip() for line in marker_lines}


def _load_pytest_ini_options() -> dict[str, list[str]]:
    lines = PYPROJECT_PATH.read_text(encoding="utf-8").splitlines()
    in_pytest = False
    values: dict[str, list[str]] = {"markers": [], "addopts": []}
    current_key: str | None = None
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            in_pytest = stripped == "[tool.pytest.ini_options]"
            current_key = None
            continue
        if not in_pytest:
            continue
        if stripped.startswith("markers"):
            current_key = "markers"
            continue
        if stripped.startswith("addopts"):
            current_key = "addopts"
            inline = stripped.split("=", 1)[1]
            values["addopts"].extend(re.findall(r'"([^"]+)"', inline))
            continue
        if current_key and stripped.startswith("]"):
            current_key = None
            continue
        if current_key:
            values[current_key].extend(re.findall(r'"([^"]+)"', stripped))
    return values


def _live_optional_excluded_from_default_pytest() -> bool:
    addopts = _load_pytest_ini_options()["addopts"]
    return "-m" in addopts and "not live_optional" in addopts


def _language_violation_counts() -> dict[str, int]:
    counts = {
        "phase_winner": 0,
        "phase_rank": 0,
        "arbitrary_phase_score": 0,
        "isolated_candidate": 0,
        "static_label_only": 0,
        "portfolio_recommendation": 0,
    }
    for rel_path, entry in TEST_FILE_MARKER_MAP.items():
        path = ROOT / rel_path
        text = path.read_text(encoding="utf-8")
        if "legacy_v1" not in entry.markers and _positive_match(
            text,
            ("phase winner", "winning_phase", "selected_phase"),
        ):
            counts["phase_winner"] += 1
        if "legacy_v1" not in entry.markers and _positive_match(
            text,
            ("phase rank", "phase_rank", "ranked_phase_scores"),
        ):
            counts["phase_rank"] += 1
        if "legacy_v1" not in entry.markers and _positive_phase_score_assertion(text):
            counts["arbitrary_phase_score"] += 1
        if "legacy_v1" not in entry.markers and _positive_match(
            text,
            ("isolated candidate", "classifier winner"),
        ):
            counts["isolated_candidate"] += 1
        if (
            "historical_replay_backtest" not in entry.markers
            and _positive_match(text, ("static-label accuracy", "static label accuracy"))
        ):
            counts["static_label_only"] += 1
        if "portfolio_policy_research" in entry.markers and _unsafe_portfolio_text(text):
            counts["portfolio_recommendation"] += 1
    return counts


def _positive_match(text: str, needles: tuple[str, ...]) -> bool:
    for line in text.splitlines():
        lowered = line.lower()
        if any(needle in lowered for needle in needles) and not _safe_context(lowered):
            return True
    return False


def _positive_phase_score_assertion(text: str) -> bool:
    score_pattern = re.compile(r"assert .*phase_?score|assert .*\\.score\\s*==", re.IGNORECASE)
    for line in text.splitlines():
        lowered = line.lower()
        if score_pattern.search(line) and not _safe_context(lowered):
            return True
    return False


def _unsafe_portfolio_text(text: str) -> bool:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        lowered = line.lower()
        if any(
            phrase in lowered
            for phrase in (
                "current allocation recommendation",
                "buy_signal",
                "sell_signal",
                "trade_action",
            )
        ) and not _safe_context(lowered) and not _nearby_safety_context(lines, index):
            return True
    return False


def _nearby_safety_context(lines: list[str], index: int) -> bool:
    window = "\n".join(lines[max(0, index - 5) : index + 6]).lower()
    markers = (
        "prohibited",
        "forbidden",
        "invalid",
        "unsafe",
        "reject",
        "not allowed",
        "must not",
        "target_weight",
        "current_market_recommendation",
        "live_allocation",
    )
    return any(marker in window for marker in markers)


def _safe_context(line: str) -> bool:
    markers = (
        "not ",
        "no ",
        "false",
        "forbidden",
        "prohibit",
        "reject",
        "without",
        "legacy",
        "compatibility",
        "research",
        "safety",
        "assert \"",
        "count\"] == 0",
        "is false",
    )
    return any(marker in line for marker in markers)


def _production_runtime_paths() -> set[str]:
    boundary = yaml.safe_load(
        (ROOT / "specs/common/legacy_production_v1_boundary.yaml").read_text(
            encoding="utf-8"
        )
    )["legacy_production_v1_boundary"]
    return {item["path"] for item in boundary["inventory"]}


def _git_diff_name_only() -> list[str]:
    completed = subprocess.run(
        ["git", "diff", "--name-only", "HEAD", "--"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in completed.stdout.splitlines() if line.strip()]


def _passed(summary: dict[str, Any]) -> bool:
    return (
        summary["pytest_marker_taxonomy_ready"] is True
        and summary["legacy_v1_marker_registered"] is True
        and summary["doctrine_aligned_marker_registered"] is True
        and summary["transition_monitor_marker_registered"] is True
        and summary["portfolio_policy_research_marker_registered"] is True
        and summary["historical_replay_backtest_marker_registered"] is True
        and summary["governance_scaffold_marker_registered"] is True
        and summary["safety_marker_registered"] is True
        and summary["live_optional_marker_registered"] is True
        and summary["live_optional_tests_not_in_default_ci"] is True
        and summary["unmarked_high_risk_test_count"] == 0
        and summary["legacy_v1_missing_compatibility_label_count"] == 0
        and summary["mature_product_test_asserts_phase_winner_count"] == 0
        and summary["mature_product_test_asserts_phase_rank_count"] == 0
        and summary["mature_product_test_asserts_arbitrary_phase_score_count"] == 0
        and summary["mature_product_test_asserts_isolated_candidate_count"] == 0
        and summary["historical_backtest_static_label_only_unmarked_count"] == 0
        and summary["portfolio_test_recommendation_wording_count"] == 0
        and summary["production_behavior_change_count"] == 0
        and summary["runtime_behavior_change_count"] == 0
    )

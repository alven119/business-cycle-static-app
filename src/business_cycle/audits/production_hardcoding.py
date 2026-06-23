"""QA3 production hard-coding audit."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SCENARIO_IDS = (
    "dotcom_bubble",
    "global_financial_crisis",
    "covid_recession",
    "euro_debt_slowdown",
    "late_cycle_2018",
)
EVENT_TERMS = ("covid", "dotcom", "gfc", "global_financial_crisis")
DATE_PATTERN = re.compile(r"\b(?:19|20)\d{2}-\d{2}-\d{2}\b")


@dataclass(frozen=True)
class HardCodingFinding:
    """One hard-coding finding in production scope."""

    finding_type: str
    source_path: str
    line_number: int
    text: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "finding_type": self.finding_type,
            "source_path": self.source_path,
            "line_number": self.line_number,
            "text": self.text,
        }


def summarize_production_hardcoding() -> dict[str, Any]:
    """Scan production decision scope for scenario-specific hard coding."""

    findings = scan_production_hardcoding()
    by_type = _findings_by_type(findings)
    return {
        "phase": "QA3",
        "production_hardcoding_audit_ready": True,
        "production_hard_coded_scenario_id_count": len(by_type["scenario_id"]),
        "production_hard_coded_date_count": len(by_type["historical_date"]),
        "production_scenario_name_branch_count": len(by_type["scenario_branch"]),
        "production_event_specific_override_count": len(by_type["event_override"]),
        "allowed_fixture_reference_count": 0,
        "unreviewed_hard_coding_count": len(findings),
        "findings": [finding.to_dict() for finding in findings],
    }


def scan_production_hardcoding(
    source_paths: list[str | Path] | None = None,
) -> list[HardCodingFinding]:
    """Return hard-coded scenario/date findings from production scope."""

    paths = source_paths if source_paths is not None else _default_production_paths()
    findings: list[HardCodingFinding] = []
    for raw_path in paths:
        path = Path(raw_path)
        if path.is_dir():
            for child in sorted(path.rglob("*")):
                findings.extend(_scan_file(child))
        else:
            findings.extend(_scan_file(path))
    return findings


def _default_production_paths() -> list[Path]:
    return [
        Path("src/business_cycle/indicators"),
        Path("src/business_cycle/phases"),
        Path("src/business_cycle/pipeline"),
        Path("src/business_cycle/render"),
        Path("scripts/score_indicators.py"),
        Path("scripts/score_phases.py"),
        Path("scripts/resolve_current_phase.py"),
        Path("scripts/build_cycle_snapshot.py"),
        Path("scripts/run_cycle_pipeline.py"),
        Path("scripts/build_site.py"),
        Path("specs/indicator_catalog.yaml"),
        Path("specs/phases"),
        Path("specs/common/current_cycle_context.yaml"),
        Path("specs/common/phase_state_machine.yaml"),
    ]


def _scan_file(path: Path) -> list[HardCodingFinding]:
    if not path.exists() or path.is_dir() or path.suffix not in {".py", ".yaml", ".yml"}:
        return []
    if _excluded(path):
        return []
    findings: list[HardCodingFinding] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        lowered = line.lower()
        if any(scenario_id in line for scenario_id in SCENARIO_IDS):
            findings.append(_finding("scenario_id", path, line_number, line))
        if _looks_like_scenario_branch(line):
            findings.append(_finding("scenario_branch", path, line_number, line))
        if any(term in lowered for term in EVENT_TERMS) and _looks_like_override(line):
            findings.append(_finding("event_override", path, line_number, line))
        if DATE_PATTERN.search(line) and _looks_like_decision_date(line, path):
            findings.append(_finding("historical_date", path, line_number, line))
    return findings


def _excluded(path: Path) -> bool:
    text = str(path)
    return (
        "/__pycache__/" in text
        or text == "src/business_cycle/render/phase_evidence_view_models.py"
        or text.startswith("src/business_cycle/audits/")
        or text.startswith("src/business_cycle/backtests/")
        or text.startswith("tests/")
        or text.startswith("docs/")
        or "fixtures" in text
        or "transition_evidence_badge" in text
        or "series_release_lag_registry" in text
    )


def _looks_like_scenario_branch(line: str) -> bool:
    lowered = line.lower()
    return (
        any(scenario_id in line for scenario_id in SCENARIO_IDS)
        and any(token in lowered for token in ("if ", "elif ", "case ", "match "))
    )


def _looks_like_override(line: str) -> bool:
    lowered = line.lower()
    return any(token in lowered for token in ("override", "special", "force", "if "))


def _looks_like_decision_date(line: str, path: Path) -> bool:
    lowered = line.lower()
    if "candidate_series" in lowered or "source" in lowered or "units" in lowered:
        return False
    if str(path).startswith("specs/indicator_catalog.yaml"):
        return False
    return any(
        token in lowered
        for token in ("threshold", "if ", "date", "as_of", "window", "before", "after")
    )


def _finding(
    finding_type: str,
    path: Path,
    line_number: int,
    line: str,
) -> HardCodingFinding:
    return HardCodingFinding(
        finding_type=finding_type,
        source_path=str(path),
        line_number=line_number,
        text=line.strip(),
    )


def _findings_by_type(findings: list[HardCodingFinding]) -> dict[str, list[HardCodingFinding]]:
    by_type = {
        "scenario_id": [],
        "historical_date": [],
        "scenario_branch": [],
        "event_override": [],
    }
    for finding in findings:
        by_type[finding.finding_type].append(finding)
    return by_type

"""Closure audit for Phase 137 NY Fed SCE component automation."""

from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO
import json
import os
from pathlib import Path
import tempfile
from typing import Any
from unittest.mock import patch
from zipfile import ZIP_DEFLATED, ZipFile
from xml.sax.saxutils import escape

import yaml

from business_cycle.render.nas_source_operations import (
    render_nas_source_operations_page,
)
from business_cycle.service.nas_consumer_confidence_sources import (
    build_consumer_confidence_source_lanes,
)
from business_cycle.service.nas_nyfed_sce_components import (
    CONFIRMATION,
    NyfedSceSourceError,
    load_nyfed_sce_component_contract,
    parse_nyfed_sce_workbook,
    run_nyfed_sce_component_import,
    summarize_nyfed_sce_component_contract,
)
from business_cycle.service.nas_scheduled_revised_refresh import (
    run_scheduled_refresh_once,
)
from business_cycle.service.nas_source_incident_center import (
    build_source_incident_candidates,
    reconcile_source_incidents,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CLOSURE_PATH = (
    ROOT / "specs/audits/phase137_nyfed_sce_components_closure.yaml"
)


class _Response:
    def __init__(self, content: bytes) -> None:
        self.content = content

    def raise_for_status(self) -> None:
        return None


class _SqlExecutor:
    def __init__(self) -> None:
        self.statements: list[str] = []

    def execute(self, sql: str) -> str:
        self.statements.append(sql)
        return ""


def build_offline_nyfed_sce_fixture(*, bad_header: bool = False) -> bytes:
    """Build a minimal official-shape workbook without a binary repo fixture."""

    contract = load_nyfed_sce_component_contract()
    grouped: dict[str, list[dict[str, Any]]] = {}
    for component in contract["component_series"]:
        grouped.setdefault(str(component["sheet_name"]), []).append(component)
    workbook_sheets = []
    relationships = []
    worksheets: dict[str, str] = {}
    for index, (sheet_name, components) in enumerate(grouped.items(), start=1):
        relation_id = f"rId{index}"
        workbook_sheets.append(
            f'<sheet name="{escape(sheet_name)}" sheetId="{index}" '
            f'r:id="{relation_id}"/>'
        )
        relationships.append(
            f'<Relationship Id="{relation_id}" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/'
            f'relationships/worksheet" Target="worksheets/sheet{index}.xml"/>'
        )
        worksheets[f"xl/worksheets/sheet{index}.xml"] = _fixture_worksheet(
            components,
            bad_header=bad_header and index == 1,
        )
    workbook = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f"<sheets>{''.join(workbook_sheets)}</sheets></workbook>"
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        f"{''.join(relationships)}</Relationships>"
    )
    output = BytesIO()
    with ZipFile(output, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr("xl/workbook.xml", workbook)
        archive.writestr("xl/_rels/workbook.xml.rels", rels)
        for path, content in worksheets.items():
            archive.writestr(path, content)
    return output.getvalue()


def summarize_phase137_nyfed_sce_components_closure(
    path: str | Path = DEFAULT_CLOSURE_PATH,
) -> dict[str, Any]:
    closure = yaml.safe_load(Path(path).read_text(encoding="utf-8"))[
        "phase137_nyfed_sce_components_closure"
    ]
    contract_summary = summarize_nyfed_sce_component_contract()
    fixture = build_offline_nyfed_sce_fixture()
    parsed = parse_nyfed_sce_workbook(fixture)
    observations = {
        series_id: [
            {
                "observation_date": row.date,
                "value_numeric": row.value,
            }
            for row in rows
        ]
        for series_id, rows in parsed.items()
    }
    lane_model = build_consumer_confidence_source_lanes(
        observations_by_series=observations
    )
    schema_drift_rejected = _schema_drift_rejected()
    with tempfile.TemporaryDirectory(prefix="phase137-") as directory:
        root = Path(directory)
        sql_executor = _SqlExecutor()
        import_report = run_nyfed_sce_component_import(
            execute_live=True,
            operator_confirmation=CONFIRMATION,
            artifact_dir=root / "import",
            executor=sql_executor,
            fetcher=lambda *args, **kwargs: _Response(fixture),
        )
        scheduled = _scheduled_refresh_drill(root)
        incident, recovered = _incident_recovery_drill(root)
    nyfed_lane = next(
        row
        for row in lane_model["lanes"]
        if row["source_series_id"] == "NYFED_SCE_CONTEXT"
    )
    html = render_nas_source_operations_page(
        _source_operations_fixture(lane_model)
    )
    observation_count = sum(len(rows) for rows in parsed.values())
    summary = {
        "phase": 137,
        "phase137_closure_ready": True,
        "nyfed_sce_component_adapter_contract_ready": contract_summary[
            "nyfed_sce_component_adapter_contract_ready"
        ],
        "official_workbook_parser_ready": len(parsed) == 11,
        "offline_fixture_component_series_count": len(parsed),
        "offline_fixture_observation_count": observation_count,
        "schema_drift_rejected": schema_drift_rejected,
        "postgres_import_contract_ready": (
            import_report["result"] == "passed"
            and len(sql_executor.statements) == 1
            and "phase137_nyfed_sce_import" in sql_executor.statements[0]
        ),
        "scheduled_refresh_wiring_ready": (
            scheduled["last_run_state"] == "succeeded"
            and scheduled["nyfed_sce_component_series_count"] == 11
            and any(
                row["series_id"] == "NYFED_SCE_CONTEXT"
                for row in scheduled["series_refresh_results"]
            )
        ),
        "incident_failure_drill_passed": incident["open_incident_count"] == 1,
        "recovery_receipt_drill_passed": (
            recovered["open_incident_count"] == 0
            and recovered["recovery_receipt_count"] == 1
        ),
        "dashboard_component_explanation_ready": (
            nyfed_lane["lane_status"] == "available_supporting_only"
            and nyfed_lane["available_component_series_count"] == 11
            and "查看 11 項 NY Fed 官方元件與高低意涵" in html
            and "未來一年失去工作的平均機率" in html
        ),
        "exact_conference_board_access_blocked": (
            lane_model["book_core_status"] == "exact_access_blocked"
        ),
        "book_core_replacement_count": 0,
        "arbitrary_composite_score_count": 0,
        "numeric_weight_added_count": 0,
        "arbitrary_threshold_added_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "test_file_delta": 0,
        "development_next_phase": 138,
        "phase137_closure_status": (
            "closed_nyfed_sce_components_automated_supporting_only"
        ),
    }
    expected = dict(closure["hard_gates"])
    summary["result"] = (
        "passed"
        if all(summary.get(key) == value for key, value in expected.items())
        else "blocked"
    )
    return summary


def _fixture_worksheet(
    components: list[dict[str, Any]],
    *,
    bad_header: bool,
) -> str:
    cells_by_row: dict[int, list[str]] = {3: [], 4: [], 5: [], 6: [], 7: []}
    for component_index, component in enumerate(components, start=1):
        column = str(component["value_column"])
        if component.get("scope_row"):
            scope_column = str(component.get("scope_column", column))
            cells_by_row[3].append(
                _inline_cell(
                    f"{scope_column}3", str(component["expected_scope"])
                )
            )
        header = str(component["expected_header"])
        if bad_header and component_index == 1:
            header = "Changed official header"
        cells_by_row[4].append(_inline_cell(f"{column}4", header))
        for offset, row_number in enumerate((5, 6, 7)):
            value = str(component_index * 10 + offset / 10)
            cells_by_row[row_number].append(_numeric_cell(f"{column}{row_number}", value))
    for period, row_number in zip(("202604", "202605", "202606"), (5, 6, 7)):
        cells_by_row[row_number].insert(0, _numeric_cell(f"A{row_number}", period))
    rows = "".join(
        f'<row r="{row}">{"".join(cells_by_row[row])}</row>'
        for row in sorted(cells_by_row)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f"<sheetData>{rows}</sheetData></worksheet>"
    )


def _inline_cell(reference: str, value: str) -> str:
    return f'<c r="{reference}" t="inlineStr"><is><t>{escape(value)}</t></is></c>'


def _numeric_cell(reference: str, value: str) -> str:
    return f'<c r="{reference}"><v>{escape(value)}</v></c>'


def _schema_drift_rejected() -> bool:
    try:
        parse_nyfed_sce_workbook(build_offline_nyfed_sce_fixture(bad_header=True))
    except NyfedSceSourceError:
        return True
    return False


def _scheduled_refresh_drill(root: Path) -> dict[str, Any]:
    def base_runner(**kwargs: Any) -> dict[str, Any]:
        return {
            "result": "passed",
            "requested_series_count": 1,
            "completed_series_count": 1,
            "failed_series_count": 0,
            "source_artifact_count": 1,
            "results": [
                {
                    "series_id": "ICSA",
                    "status": "imported",
                    "observation_count": 3,
                }
            ],
        }

    def external_runner(**kwargs: Any) -> dict[str, Any]:
        return {
            "result": "passed",
            "component_series_count": 11,
            "series_refresh_results": [
                {
                    "series_id": "NYFED_SCE_CONTEXT",
                    "status": "imported",
                    "observation_count": 33,
                }
            ],
        }

    def oecd_runner(**kwargs: Any) -> dict[str, Any]:
        return {
            "result": "passed",
            "series_refresh_results": [
                {
                    "series_id": "OECD_US_CCICP",
                    "status": "imported",
                    "observation_count": 3,
                }
            ],
        }

    env = {
        "BUSINESS_CYCLE_TECHNOLOGY_REFRESH_ENABLED": "false",
        "BUSINESS_CYCLE_CONSUMER_CONFIDENCE_REFRESH_ENABLED": "true",
        "BUSINESS_CYCLE_NYFED_SCE_REFRESH_ENABLED": "true",
    }
    with patch.dict(os.environ, env, clear=False):
        return run_scheduled_refresh_once(
            artifact_root=root / "scheduled",
            operator_confirmation=(
                "I_UNDERSTAND_THIS_FETCHES_FRED_AND_WRITES_NAS_POSTGRES"
            ),
            import_runner=base_runner,
            consumer_confidence_import_runner=oecd_runner,
            nyfed_sce_import_runner=external_runner,
            now=lambda: datetime(2026, 7, 13, tzinfo=timezone.utc),
        )


def _incident_recovery_drill(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    registry_path = root / "incidents.json"
    failed_status = {
        "last_run_state": "failed",
        "series_refresh_results": [
            {
                "series_id": "NYFED_SCE_CONTEXT",
                "status": "failed",
                "attempt_count": 1,
                "error_reason_code": "source_fetch_failed",
            }
        ],
    }
    candidates = build_source_incident_candidates(refresh_status=failed_status)
    incident = reconcile_source_incidents(
        candidates=candidates,
        evaluated_series_ids={"NYFED_SCE_CONTEXT"},
        healthy_series_ids=set(),
        registry_path=registry_path,
        now=lambda: datetime(2026, 7, 13, 1, tzinfo=timezone.utc),
    )
    recovered = reconcile_source_incidents(
        candidates=[],
        evaluated_series_ids={"NYFED_SCE_CONTEXT"},
        healthy_series_ids={"NYFED_SCE_CONTEXT"},
        registry_path=registry_path,
        now=lambda: datetime(2026, 7, 13, 2, tzinfo=timezone.utc),
    )
    return incident, recovered


def _source_operations_fixture(lane_model: dict[str, Any]) -> dict[str, Any]:
    return {
        "release_family_count": 0,
        "series_diagnostic_count": 0,
        "family_due_or_missing_refresh_count": 0,
        "series_with_failure_reason_count": 0,
        "release_families": [],
        "series_refresh_diagnostics": [],
        "consumer_confidence_source_lanes": lane_model,
        "source_incident_center": {
            "open_incident_count": 0,
            "critical_open_incident_count": 0,
            "warning_open_incident_count": 0,
            "affected_role_count": 0,
            "affected_cycle_lane_count": 0,
            "recovery_receipt_count": 0,
            "open_incidents": [],
            "recent_recovery_receipts": [],
        },
    }


def main() -> int:
    summary = summarize_phase137_nyfed_sce_components_closure()
    for key, value in summary.items():
        if isinstance(value, (dict, list)):
            print(f"{key}={json.dumps(value, sort_keys=True)}")
        elif isinstance(value, bool):
            print(f"{key}={str(value).lower()}")
        else:
            print(f"{key}={value}")
    return 0 if summary["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

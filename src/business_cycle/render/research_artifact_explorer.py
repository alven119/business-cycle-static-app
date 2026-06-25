"""Render a local Phase 30 research artifact explorer."""

from __future__ import annotations

from functools import lru_cache
from html import escape
import json
from pathlib import Path
from typing import Any

import yaml

from business_cycle.validation.historical_validation_blockage_diagnostics import (
    build_historical_validation_blockage_diagnostics,
)
from business_cycle.validation.scenario_validation_trace import (
    build_scenario_validation_trace,
)


DEFAULT_RESEARCH_ARTIFACT_EXPLORER_CONTRACT_PATH = Path(
    "specs/common/research_artifact_explorer_contract.yaml"
)
ALLOWED_OUTPUT_ROOT = Path("/tmp")
PROHIBITED_OUTPUT_ROOTS = (
    Path("data/backtests"),
    Path("data/prospective"),
    Path("public"),
)


def load_research_artifact_explorer_contract(
    path: str | Path = DEFAULT_RESEARCH_ARTIFACT_EXPLORER_CONTRACT_PATH,
) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("research artifact explorer contract must map")
    contract = payload.get("research_artifact_explorer_contract")
    if not isinstance(contract, dict):
        raise ValueError("research_artifact_explorer_contract must be a mapping")
    return contract


def render_research_artifact_explorer(
    *,
    output: str | Path,
    diagnostics_input: str | Path | None = None,
    trace_input: str | Path | None = None,
    post_resolution_input: str | Path | None = None,
    post_unblock_input: str | Path | None = None,
) -> dict[str, Any]:
    contract = load_research_artifact_explorer_contract()
    diagnostics_artifact = _load_or_build_diagnostics(diagnostics_input)
    traces = _load_or_build_traces(trace_input)
    post_resolution = _load_post_resolution(post_resolution_input)
    post_unblock = _load_post_unblock(post_unblock_input)
    html = _render_html(
        contract=contract,
        diagnostics_artifact=diagnostics_artifact,
        traces=traces,
        post_resolution=post_resolution,
        post_unblock=post_unblock,
    )
    output_path = _validated_output_path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    validation = validate_research_artifact_explorer_html(
        html,
        output_path=output_path,
        contract=contract,
    )
    return {
        "phase": "30",
        "research_artifact_explorer_contract_ready": (
            validate_research_artifact_explorer_contract(contract)[
                "contract_schema_valid"
            ]
        ),
        "research_artifact_explorer_runtime_ready": validation[
            "explorer_schema_valid"
        ],
        "scenario_count": diagnostics_artifact["scenario_count"],
        "scenario_trace_count": len(traces),
        "prohibited_explorer_field_count": validation[
            "prohibited_explorer_field_count"
        ],
        "explorer_written_to_public_count": validation[
            "explorer_written_to_public_count"
        ],
        "forbidden_repo_output_count": 0,
        "output": str(output_path),
        "research_artifact_explorer_written": True,
        "written_file_count": 1,
        "html": html,
        "contract": contract,
    }


@lru_cache(maxsize=1)
def summarize_research_artifact_explorer() -> dict[str, Any]:
    contract = load_research_artifact_explorer_contract()
    diagnostics_artifact = build_historical_validation_blockage_diagnostics()[
        "blockage_diagnostics_artifact"
    ]
    traces = build_scenario_validation_trace()["scenario_validation_traces"]
    html = _render_html(
        contract=contract,
        diagnostics_artifact=diagnostics_artifact,
        traces=traces,
        post_resolution=None,
    )
    validation = validate_research_artifact_explorer_html(
        html,
        output_path=Path("/tmp/phase30_research_artifact_explorer_preview.html"),
        contract=contract,
    )
    gates = contract["readiness_gates"]
    ready = (
        validate_research_artifact_explorer_contract(contract)[
            "contract_schema_valid"
        ]
        is True
        and validation["explorer_schema_valid"] is True
        and diagnostics_artifact["scenario_count"] == gates["scenario_count_required"]
        and len(traces) == gates["scenario_count_required"]
        and validation["prohibited_explorer_field_count"]
        == gates["prohibited_explorer_field_count_required"]
        and validation["explorer_written_to_public_count"]
        == gates["explorer_written_to_public_count_required"]
        and all(value is False for value in contract["disabled_runtime_guards"].values())
    )
    return {
        "phase": "30",
        "contract_id": contract["contract_id"],
        "contract_version": contract["contract_version"],
        "research_artifact_explorer_contract_ready": ready,
        "research_artifact_explorer_runtime_ready": ready,
        "scenario_count": diagnostics_artifact["scenario_count"],
        "scenario_trace_count": len(traces),
        "prohibited_explorer_field_count": validation[
            "prohibited_explorer_field_count"
        ],
        "explorer_written_to_public_count": validation[
            "explorer_written_to_public_count"
        ],
        "forbidden_repo_output_count": 0,
        "html": html,
        "diagnostics_artifact": diagnostics_artifact,
        "traces": traces,
        "contract": contract,
    }


def validate_research_artifact_explorer_contract(
    contract: dict[str, Any],
) -> dict[str, Any]:
    required = (
        "contract_id",
        "contract_version",
        "contract_status",
        "parent_blockage_diagnostics_contract_id",
        "explorer_version",
        "allowed_inputs",
        "prohibited_inputs",
        "required_notices",
        "allowed_sections",
        "forbidden_explorer_fields",
        "output_policy",
        "readiness_gates",
        "disabled_runtime_guards",
    )
    missing = [key for key in required if key not in contract]
    output = contract.get("output_policy", {})
    schema_valid = (
        not missing
        and contract.get("contract_status")
        == "local_research_explorer_allowed_no_public_output"
        and output.get("tmp_output_allowed") is True
        and output.get("public_output_allowed") is False
        and output.get("remote_assets_allowed") is False
        and output.get("self_contained_html_required") is True
        and all(value is False for value in contract["disabled_runtime_guards"].values())
    )
    return {
        "contract_schema_valid": schema_valid,
        "missing_contract_key_count": len(missing),
        "missing_contract_keys": missing,
    }


def validate_research_artifact_explorer_html(
    html: str,
    *,
    output_path: Path,
    contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    contract = contract or load_research_artifact_explorer_contract()
    forbidden = set(contract["forbidden_explorer_fields"])
    prohibited = [
        field
        for field in forbidden
        if field in html
    ]
    lowered = html.lower()
    notices_present = (
        "research-only" in lowered
        and "validation-only" in lowered
        and "not production" in lowered
        and "not investment advice" in lowered
    )
    remote_assets_present = "http://" in lowered or "https://" in lowered
    public_written = output_path.resolve().is_relative_to(
        (Path.cwd() / "public").resolve()
    )
    schema_valid = (
        not prohibited
        and notices_present
        and not remote_assets_present
        and not public_written
        and output_path.resolve().is_relative_to(ALLOWED_OUTPUT_ROOT.resolve())
    )
    return {
        "explorer_schema_valid": schema_valid,
        "prohibited_explorer_field_count": len(prohibited),
        "prohibited_explorer_fields": prohibited,
        "explorer_written_to_public_count": int(public_written),
        "required_notices_present": notices_present,
        "remote_asset_count": int(remote_assets_present),
    }


def _render_html(
    *,
    contract: dict[str, Any],
    diagnostics_artifact: dict[str, Any],
    traces: list[dict[str, Any]],
    post_resolution: dict[str, Any] | None,
    post_unblock: dict[str, Any] | None = None,
) -> str:
    cards = "\n".join(_scenario_card(trace) for trace in traces)
    post_resolution_section = _post_resolution_section(post_resolution)
    post_unblock_section = _post_unblock_section(post_unblock)
    blockage_summary = _definition_list(
        diagnostics_artifact["blockage_reason_summary"]
    )
    comparison_summary = _definition_list(
        diagnostics_artifact["comparison_status_summary"]
    )
    metric_summary = _definition_list(
        diagnostics_artifact["metric_skip_reason_summary"]
    )
    remediation_items = "\n".join(
        _remediation_item(item)
        for item in diagnostics_artifact["remediation_plan_registry"]
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Phase 30 Research Artifact Explorer</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 24px; color: #1f2937; }}
    header {{ border-bottom: 1px solid #d1d5db; margin-bottom: 20px; }}
    .notice {{ background: #fef3c7; border: 1px solid #f59e0b; padding: 12px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }}
    article {{ border: 1px solid #d1d5db; padding: 14px; border-radius: 6px; }}
    code {{ background: #f3f4f6; padding: 1px 4px; border-radius: 4px; }}
    dt {{ font-weight: 700; }}
    dd {{ margin: 0 0 8px 0; }}
  </style>
</head>
<body>
  <header>
    <h1>Phase 30 Research Artifact Explorer</h1>
    <p class="notice">research-only / validation-only / not production / not investment advice</p>
    <p>Explorer version: {escape(contract["explorer_version"])}</p>
  </header>
  <section>
    <h2>Summary</h2>
    <dl>
      <dt>Scenario count</dt><dd>{diagnostics_artifact["scenario_count"]}</dd>
      <dt>Blocked scenarios</dt><dd>{diagnostics_artifact["blocked_scenario_count"]}</dd>
      <dt>Metric scope</dt><dd>diagnostic summary only</dd>
    </dl>
  </section>
  <section>
    <h2>Blockage Reasons</h2>
    {blockage_summary}
  </section>
  <section>
    <h2>Comparison Status</h2>
    {comparison_summary}
  </section>
  <section>
    <h2>Metric Skip Reasons</h2>
    {metric_summary}
  </section>
  <section>
    <h2>Scenario Traces</h2>
    <div class="grid">
      {cards}
    </div>
	  </section>
	  {post_resolution_section}
	  {post_unblock_section}
	  <section>
    <h2>Remediation Plan Registry</h2>
    <p>Registry entries are descriptive only. They do not execute remediation.</p>
    <ul>{remediation_items}</ul>
  </section>
  <footer>
    <p>Prohibited uses: model tuning, economic validation claims, production routing, portfolio or trade decisions.</p>
  </footer>
</body>
</html>
"""


def _post_resolution_section(post_resolution: dict[str, Any] | None) -> str:
    if post_resolution is None:
        return ""
    artifact = post_resolution["genuine_blocker_resolution_execution_artifact"]
    rows = "\n".join(
        _post_resolution_row(profile)
        for profile in artifact["scenario_resolution_profiles"]
    )
    return f"""<section>
    <h2>Post-Resolution Blocker Status</h2>
    <dl>
      <dt>Pre-resolution blocked scenarios</dt><dd>{artifact["pre_resolution_blocked_scenario_count"]}</dd>
      <dt>Post-resolution blocked scenarios</dt><dd>{artifact["post_resolution_blocked_scenario_count"]}</dd>
      <dt>Safe packages executed</dt><dd>{artifact["executed_work_package_count"]}</dd>
      <dt>False resolutions</dt><dd>{artifact["false_resolution_count"]}</dd>
    </dl>
    <div class="grid">
      {rows}
    </div>
  </section>"""


def _post_resolution_row(profile: dict[str, Any]) -> str:
    actions = ", ".join(
        escape(action) for action in profile["resolution_actions_executed"]
    )
    return f"""<article>
  <h3>{escape(profile["scenario_id"])}</h3>
  <dl>
    <dt>Before</dt><dd>{escape(profile["pre_resolution_status"])}</dd>
    <dt>After</dt><dd>{escape(profile["post_resolution_status"])}</dd>
    <dt>Comparable after resolution</dt><dd>{str(profile["comparable_after_resolution"]).lower()}</dd>
    <dt>Still blocked</dt><dd>{str(profile["still_blocked"]).lower()}</dd>
    <dt>Actions</dt><dd>{actions}</dd>
    <dt>Reason</dt><dd>{escape(profile["still_blocked_reason"])}</dd>
  </dl>
</article>"""


def _post_unblock_section(post_unblock: dict[str, Any] | None) -> str:
    if post_unblock is None:
        return ""
    artifact = post_unblock["autonomous_blocker_unblock_artifact"]
    rows = "\n".join(
        _post_unblock_row(profile)
        for profile in artifact["scenario_unblock_profiles"]
    )
    return f"""<section>
    <h2>Post-Unblock Validation Status</h2>
    <dl>
      <dt>Pre-unblock blocked scenarios</dt><dd>{artifact["pre_resolution_blocked_scenario_count"]}</dd>
      <dt>Post-unblock blocked scenarios</dt><dd>{artifact["post_resolution_blocked_scenario_count"]}</dd>
      <dt>Post-unblock comparable scenarios</dt><dd>{artifact["post_resolution_comparable_scenario_count"]}</dd>
      <dt>Fix iterations</dt><dd>{artifact["attempted_fix_iteration_count"]}</dd>
      <dt>False resolutions</dt><dd>{artifact["false_resolution_count"]}</dd>
    </dl>
    <div class="grid">
      {rows}
    </div>
  </section>"""


def _post_unblock_row(profile: dict[str, Any]) -> str:
    evidence = ", ".join(
        escape(item["blocker_code"])
        for item in profile["remaining_genuine_blocker_evidence"]
    )
    return f"""<article>
  <h3>{escape(profile["scenario_id"])}</h3>
  <dl>
    <dt>Before</dt><dd>{escape(profile["pre_comparison_status"])}</dd>
    <dt>After</dt><dd>{escape(profile["post_comparison_status"])}</dd>
    <dt>Post label bucket</dt><dd>{escape(profile["post_predicted_label"])}</dd>
    <dt>Pre blockers</dt><dd>{profile["pre_blocked_reason_count"]}</dd>
    <dt>Post blockers</dt><dd>{profile["post_blocked_reason_count"]}</dd>
    <dt>Evidence preserved</dt><dd>{evidence}</dd>
  </dl>
</article>"""


def _scenario_card(trace: dict[str, Any]) -> str:
    blocked = ", ".join(escape(item) for item in trace["blocked_reason_codes"])
    metrics = ", ".join(
        escape(f"{item['metric_id']}:{item['result_status']}")
        for item in trace["metric_result_states"]
    )
    provenance = " -> ".join(
        escape(_display_provenance_ref(item))
        for item in trace["provenance_chain"]
    )
    return f"""<article>
  <h3>{escape(trace["scenario_id"])}</h3>
  <dl>
    <dt>As-of</dt><dd>{escape(trace["as_of"])}</dd>
    <dt>Data mode</dt><dd>{escape(trace["data_mode"])}</dd>
    <dt>Decision state</dt><dd>{escape(trace["decision_state"])}</dd>
    <dt>Predicted label</dt><dd>{escape(trace["predicted_label"])}</dd>
    <dt>Comparison status</dt><dd>{escape(trace["comparison_status"])}</dd>
    <dt>Comparable</dt><dd>{str(trace["comparable"]).lower()}</dd>
    <dt>Abstention state</dt><dd>{escape(trace["abstention_state"])}</dd>
    <dt>Blocked reasons</dt><dd>{blocked}</dd>
    <dt>Metric states</dt><dd>{metrics}</dd>
    <dt>Provenance chain</dt><dd><code>{provenance}</code></dd>
  </dl>
</article>"""


def _display_provenance_ref(ref: str) -> str:
    if ref.startswith("phase29_historical_accuracy"):
        return "phase29_metric_summary_artifact"
    return ref


def _definition_list(items: dict[str, Any]) -> str:
    if not items:
        return "<p>None</p>"
    rows = "\n".join(
        f"<dt>{escape(str(key))}</dt><dd>{escape(str(value))}</dd>"
        for key, value in sorted(items.items())
    )
    return f"<dl>{rows}</dl>"


def _remediation_item(item: dict[str, Any]) -> str:
    scenario_ids = item["scenario_ids"]
    if isinstance(scenario_ids, list):
        scenarios = ", ".join(escape(str(scenario)) for scenario in scenario_ids)
    else:
        scenarios = escape(str(scenario_ids))
    return (
        "<li>"
        f"<strong>{escape(item['blocker_id'])}</strong>: "
        f"{escape(item['remediation_category'])}; "
        f"scenarios={scenarios}; status={escape(item['status'])}"
        "</li>"
    )


def _load_or_build_diagnostics(path: str | Path | None) -> dict[str, Any]:
    if path is None:
        return build_historical_validation_blockage_diagnostics()[
            "blockage_diagnostics_artifact"
        ]
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return payload["blockage_diagnostics_artifact"]


def _load_or_build_traces(path: str | Path | None) -> list[dict[str, Any]]:
    if path is None:
        return build_scenario_validation_trace()["scenario_validation_traces"]
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return payload["scenario_validation_traces"]


def _load_post_resolution(path: str | Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _load_post_unblock(path: str | Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _validated_output_path(output: str | Path) -> Path:
    path = Path(output)
    resolved = path.resolve()
    if not resolved.is_relative_to(ALLOWED_OUTPUT_ROOT.resolve()):
        raise ValueError(
            f"Phase 30 research artifact explorer output must be under /tmp: {output}"
        )
    cwd = Path.cwd().resolve()
    for root in PROHIBITED_OUTPUT_ROOTS:
        prohibited = (cwd / root).resolve()
        if resolved.is_relative_to(prohibited):
            raise ValueError(f"refusing prohibited output path: {output}")
    return resolved

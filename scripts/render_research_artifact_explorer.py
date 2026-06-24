#!/usr/bin/env python
from __future__ import annotations

import argparse

from business_cycle.render.research_artifact_explorer import (
    render_research_artifact_explorer,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--diagnostics-input")
    parser.add_argument("--trace-input")
    args = parser.parse_args()

    render_result = render_research_artifact_explorer(
        output=args.output,
        diagnostics_input=args.diagnostics_input,
        trace_input=args.trace_input,
    )
    for key in (
        "phase",
        "research_artifact_explorer_contract_ready",
        "research_artifact_explorer_runtime_ready",
        "scenario_count",
        "scenario_trace_count",
        "prohibited_explorer_field_count",
        "explorer_written_to_public_count",
        "forbidden_repo_output_count",
        "research_artifact_explorer_written",
        "written_file_count",
    ):
        value = render_result[key]
        print(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
    print(f"output={render_result['output']}")


if __name__ == "__main__":
    main()

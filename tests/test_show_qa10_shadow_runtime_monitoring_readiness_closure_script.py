from __future__ import annotations

import subprocess
import sys


def test_show_qa10_shadow_runtime_monitoring_readiness_closure_script() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/show_qa10_shadow_runtime_monitoring_readiness_closure.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "result=passed" in result.stdout
    assert "recommended_next_phase=QA11" in result.stdout
    assert (
        "qa10_closure_status=closed_runtime_path_ready_prestart_no_real_records_candidate_capability_incomplete"
        in result.stdout
    )

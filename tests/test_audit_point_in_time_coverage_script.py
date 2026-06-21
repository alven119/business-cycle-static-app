from __future__ import annotations

import scripts.audit_point_in_time_coverage as script


def test_audit_point_in_time_coverage_script_runs_with_empty_tmp_cache(tmp_path) -> None:
    exit_code = script.main(["--cache-dir", str(tmp_path)])

    assert exit_code == 0

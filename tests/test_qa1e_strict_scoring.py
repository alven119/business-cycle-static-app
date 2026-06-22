import json

import scripts.score_indicators as score_script


def test_revised_scoring_default_still_unchanged(tmp_path) -> None:
    output = tmp_path / "scores.json"

    score_script.main(["--as-of", "2019-12-31", "--output", str(output)])

    summary = json.loads(output.read_text(encoding="utf-8"))["summary"]
    assert summary["requested_data_mode"] == "revised"
    assert summary["actual_data_mode"] == "revised"
    assert summary["scored_indicators"] == 13

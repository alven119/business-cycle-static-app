from __future__ import annotations

from pathlib import Path

from business_cycle.render.labels import label_for, load_display_labels


def test_display_labels_yaml_can_be_loaded() -> None:
    labels = load_display_labels("specs/common/display_labels_zh.yaml")

    assert labels["phases"]["boom"] == "榮景期"


def test_display_labels_include_required_categories() -> None:
    labels = load_display_labels("specs/common/display_labels_zh.yaml")

    assert label_for(labels, "phases", "recovery") == "復甦期"
    assert label_for(labels, "indicators", "unemployment_rate") == "失業率"
    assert label_for(labels, "methods", "level_percentile_score") == "歷史分位數評分"
    assert label_for(labels, "decision_statuses", "hold_current") == "維持目前階段"


def test_missing_display_label_falls_back_without_crashing(tmp_path: Path) -> None:
    path = tmp_path / "labels.yaml"
    path.write_text("phases:\n  boom: 榮景期\n", encoding="utf-8")

    labels = load_display_labels(path)

    assert label_for(labels, "phases", "missing_phase") == "missing_phase"
    assert label_for(labels, "missing_category", "unknown") == "unknown"
    assert label_for(labels, "phases", "missing_phase", fallback="備援") == "備援"

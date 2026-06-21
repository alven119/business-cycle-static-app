"""Repository inventory discovery for QA0 audit reconciliation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


class RepositoryInventoryError(ValueError):
    """Raised when repository inventory inputs are invalid."""


@dataclass(frozen=True)
class InventoryItem:
    """A discovered repository item that requires audit mapping."""

    inventory_id: str
    inventory_type: str
    source_path: str
    source_key_path: str
    formal_or_experimental: str
    production_or_research: str
    referenced_series_ids: tuple[str, ...] = field(default_factory=tuple)
    provenance_class: str = "unknown"
    audit_mapping_required: bool = True


FORMAL_INDICATOR_PATH = Path("specs/indicator_catalog.yaml")
EXPERIMENTAL_INDICATOR_PATHS = (
    Path("specs/backtests/recession_confirmation_candidate_indicators.yaml"),
    Path("specs/backtests/boom_ending_candidate_indicators.yaml"),
    Path("specs/backtests/recovery_candidate_indicators.yaml"),
)
PHASE_RULE_PATHS = (
    Path("specs/common/phase_state_machine.yaml"),
    Path("specs/common/transition_policy.yaml"),
    Path("specs/common/current_cycle_context.yaml"),
    Path("specs/backtests/transition_controls_enabled_experiment.yaml"),
    Path("specs/backtests/transition_controls_experiment.yaml"),
    Path("specs/backtests/transition_controls_recession_breadth_experiment.yaml"),
)
PORTFOLIO_PATH_GLOB = "specs/portfolio/*.yaml"
DASHBOARD_SEMANTIC_PATHS = (
    Path("specs/audits/dashboard_semantics_contract.yaml"),
    Path("specs/common/display_labels_zh.yaml"),
    Path("specs/common/transition_evidence_badge_schema.yaml"),
    Path("specs/common/transition_evidence_badge_renderer_contract.yaml"),
)


def collect_repository_inventory(root: str | Path = ".") -> dict[str, Any]:
    """Discover indicators, series, phase rules, portfolio artifacts, and dashboard semantics."""

    root_path = Path(root)
    items: list[InventoryItem] = []
    items.extend(_formal_indicator_items(root_path))
    items.extend(_experimental_indicator_items(root_path))
    items.extend(_series_items(items))
    items.extend(_phase_rule_items(root_path))
    items.extend(_portfolio_items(root_path))
    items.extend(_dashboard_semantic_items(root_path))
    duplicate_inventory_ids = _duplicate_count([item.inventory_id for item in items])
    indicator_items = [
        item
        for item in items
        if item.inventory_type in {"formal_indicator", "experimental_indicator"}
    ]
    formal_indicators = [
        item for item in indicator_items if item.inventory_type == "formal_indicator"
    ]
    experimental_indicators = [
        item for item in indicator_items if item.inventory_type == "experimental_indicator"
    ]
    direct_series = [item for item in items if item.inventory_type == "direct_series"]
    derived_series = [item for item in items if item.inventory_type == "derived_series"]
    phase_rules = [item for item in items if item.inventory_type == "phase_rule"]
    portfolio_artifacts = [
        item for item in items if item.inventory_type == "portfolio_artifact"
    ]
    dashboard_semantics = [
        item for item in items if item.inventory_type == "dashboard_semantic"
    ]
    return {
        "items": [_item_to_dict(item) for item in sorted(items, key=lambda item: item.inventory_id)],
        "discovered_formal_indicator_count": len(formal_indicators),
        "discovered_experimental_indicator_count": len(experimental_indicators),
        "discovered_unique_indicator_count": len(
            {item.inventory_id for item in indicator_items}
        ),
        "discovered_direct_series_count": len({item.inventory_id for item in direct_series}),
        "discovered_derived_series_count": len(
            {item.inventory_id for item in derived_series}
        ),
        "discovered_unique_series_count": len(
            {item.inventory_id for item in direct_series + derived_series}
        ),
        "discovered_phase_rule_count": len(phase_rules),
        "discovered_portfolio_artifact_count": len(portfolio_artifacts),
        "discovered_dashboard_semantic_item_count": len(dashboard_semantics),
        "duplicate_inventory_id_count": duplicate_inventory_ids,
        "duplicate_series_alias_count": 0,
    }


def _formal_indicator_items(root: Path) -> list[InventoryItem]:
    path = FORMAL_INDICATOR_PATH
    payload = _load_yaml(root / path)
    indicators = payload.get("indicators", [])
    if not isinstance(indicators, list):
        raise RepositoryInventoryError(f"{path} indicators must be a list")
    items = []
    for index, indicator in enumerate(indicators):
        indicator_id = str(indicator["indicator_id"])
        series_ids = tuple(sorted(_extract_series_ids(indicator)))
        items.append(
            InventoryItem(
                inventory_id=f"indicator:{indicator_id}",
                inventory_type="formal_indicator",
                source_path=str(path),
                source_key_path=f"indicators[{index}]",
                formal_or_experimental="formal",
                production_or_research="production",
                referenced_series_ids=series_ids,
            )
        )
    return items


def _experimental_indicator_items(root: Path) -> list[InventoryItem]:
    items: list[InventoryItem] = []
    for path in EXPERIMENTAL_INDICATOR_PATHS:
        payload = _load_yaml(root / path)
        root_value = next(iter(payload.values()))
        indicators = root_value.get("indicators", [])
        if not isinstance(indicators, list):
            raise RepositoryInventoryError(f"{path} indicators must be a list")
        for index, indicator in enumerate(indicators):
            indicator_id = str(indicator["indicator_id"])
            series_ids = tuple(sorted(_extract_series_ids(indicator)))
            items.append(
                InventoryItem(
                    inventory_id=f"indicator:{indicator_id}",
                    inventory_type="experimental_indicator",
                    source_path=str(path),
                    source_key_path=f"{next(iter(payload))}.indicators[{index}]",
                    formal_or_experimental="experimental",
                    production_or_research="research",
                    referenced_series_ids=series_ids,
                )
            )
    return items


def _series_items(indicator_items: list[InventoryItem]) -> list[InventoryItem]:
    direct_sources: dict[str, set[str]] = {}
    derived_sources: dict[str, set[str]] = {}
    for item in indicator_items:
        if item.inventory_type not in {"formal_indicator", "experimental_indicator"}:
            continue
        for series_id in item.referenced_series_ids:
            direct_sources.setdefault(series_id, set()).add(item.inventory_id)
        if any(token in item.inventory_id for token in ("spread", "yield_curve")):
            derived_id = f"derived:{item.inventory_id.removeprefix('indicator:')}"
            derived_sources.setdefault(derived_id, set()).add(item.inventory_id)

    series_items = [
        InventoryItem(
            inventory_id=f"series:{series_id}",
            inventory_type="direct_series",
            source_path=";".join(sorted(sources)),
            source_key_path="referenced_series_ids",
            formal_or_experimental="mixed",
            production_or_research="mixed",
            referenced_series_ids=(series_id,),
            provenance_class="series_reference",
        )
        for series_id, sources in direct_sources.items()
    ]
    series_items.extend(
        InventoryItem(
            inventory_id=f"series:{series_id}",
            inventory_type="derived_series",
            source_path=";".join(sorted(sources)),
            source_key_path="derived_formula",
            formal_or_experimental="experimental",
            production_or_research="research",
            referenced_series_ids=(series_id,),
            provenance_class="derived_series",
        )
        for series_id, sources in derived_sources.items()
    )
    return series_items


def _phase_rule_items(root: Path) -> list[InventoryItem]:
    return [
        InventoryItem(
            inventory_id=f"phase_rule:{path.stem}",
            inventory_type="phase_rule",
            source_path=str(path),
            source_key_path="<root>",
            formal_or_experimental="formal" if "experiment" not in path.stem else "experimental",
            production_or_research="production" if "experiment" not in path.stem else "research",
            audit_mapping_required=False,
            provenance_class="phase_rule",
        )
        for path in PHASE_RULE_PATHS
        if (root / path).exists()
    ]


def _portfolio_items(root: Path) -> list[InventoryItem]:
    return [
        InventoryItem(
            inventory_id=f"portfolio:{path.stem}",
            inventory_type="portfolio_artifact",
            source_path=str(path.relative_to(root)),
            source_key_path="<root>",
            formal_or_experimental="research",
            production_or_research="research",
            audit_mapping_required=False,
            provenance_class="portfolio_contract",
        )
        for path in sorted(root.glob(PORTFOLIO_PATH_GLOB))
    ]


def _dashboard_semantic_items(root: Path) -> list[InventoryItem]:
    return [
        InventoryItem(
            inventory_id=f"dashboard_semantic:{path.stem}",
            inventory_type="dashboard_semantic",
            source_path=str(path),
            source_key_path="<root>",
            formal_or_experimental="research",
            production_or_research="research",
            audit_mapping_required=False,
            provenance_class="dashboard_semantics",
        )
        for path in DASHBOARD_SEMANTIC_PATHS
        if (root / path).exists()
    ]


def _extract_series_ids(value: Any) -> set[str]:
    series_ids: set[str] = set()

    def visit(node: Any) -> None:
        if isinstance(node, dict):
            if isinstance(node.get("series_id"), str):
                series_ids.add(node["series_id"])
            if isinstance(node.get("preferred_series"), str):
                series_ids.add(node["preferred_series"])
            if isinstance(node.get("candidate_fred_series"), list):
                for candidate in node["candidate_fred_series"]:
                    if isinstance(candidate, str):
                        series_ids.add(candidate)
                    elif isinstance(candidate, dict) and isinstance(candidate.get("series_id"), str):
                        series_ids.add(candidate["series_id"])
            if isinstance(node.get("source_priority"), list):
                for priority in node["source_priority"]:
                    if isinstance(priority, dict):
                        for series_id in priority.values():
                            if isinstance(series_id, str):
                                series_ids.add(series_id)
            for child in node.values():
                visit(child)
        elif isinstance(node, list):
            for child in node:
                visit(child)

    visit(value)
    return {_normalize_series_id(series_id) for series_id in series_ids}


def _normalize_series_id(series_id: str) -> str:
    return series_id.strip().upper()


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RepositoryInventoryError(f"inventory source path does not exist: {path}")
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RepositoryInventoryError(f"{path} must contain a YAML mapping")
    return payload


def _duplicate_count(values: list[str]) -> int:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return len(duplicates)


def _item_to_dict(item: InventoryItem) -> dict[str, Any]:
    return {
        "inventory_id": item.inventory_id,
        "inventory_type": item.inventory_type,
        "source_path": item.source_path,
        "source_key_path": item.source_key_path,
        "formal_or_experimental": item.formal_or_experimental,
        "production_or_research": item.production_or_research,
        "referenced_series_ids": list(item.referenced_series_ids),
        "provenance_class": item.provenance_class,
        "audit_mapping_required": item.audit_mapping_required,
    }

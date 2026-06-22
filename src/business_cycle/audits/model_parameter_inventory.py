"""QA3 model parameter inventory discovery and provenance classification."""

from __future__ import annotations

import ast
import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


DEFAULT_REGISTRY_PATH = Path("specs/audits/model_parameter_registry.yaml")
CURRENT_SCENARIOS = (
    "dotcom_bubble",
    "global_financial_crisis",
    "covid_recession",
    "euro_debt_slowdown",
    "late_cycle_2018",
)


@dataclass(frozen=True)
class ModelParameter:
    """One discovered model parameter with QA3 provenance fields."""

    parameter_id: str
    source_path: str
    source_key_path: str
    parameter_layer: str
    value: Any
    value_type: str
    formal_or_experimental: str
    production_or_research: str
    affects_candidate_phase: bool
    affects_final_phase: bool
    affects_confidence: bool
    affects_transition_timing: bool
    affects_display_only: bool
    book_provenance_class: str
    selection_basis: str
    first_introduced_phase: str
    first_introduced_commit_if_available: str | None
    scenarios_visible_before_selection: list[str]
    selected_after_results_seen: bool
    currently_mutable: bool
    freeze_scope: str
    provenance_status: str
    contaminated_for_independent_validation: bool

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON/YAML-friendly representation."""

        return {
            "parameter_id": self.parameter_id,
            "source_path": self.source_path,
            "source_key_path": self.source_key_path,
            "parameter_layer": self.parameter_layer,
            "value": self.value,
            "value_type": self.value_type,
            "formal_or_experimental": self.formal_or_experimental,
            "production_or_research": self.production_or_research,
            "affects_candidate_phase": self.affects_candidate_phase,
            "affects_final_phase": self.affects_final_phase,
            "affects_confidence": self.affects_confidence,
            "affects_transition_timing": self.affects_transition_timing,
            "affects_display_only": self.affects_display_only,
            "book_provenance_class": self.book_provenance_class,
            "selection_basis": self.selection_basis,
            "first_introduced_phase": self.first_introduced_phase,
            "first_introduced_commit_if_available": (
                self.first_introduced_commit_if_available
            ),
            "scenarios_visible_before_selection": self.scenarios_visible_before_selection,
            "selected_after_results_seen": self.selected_after_results_seen,
            "currently_mutable": self.currently_mutable,
            "freeze_scope": self.freeze_scope,
            "provenance_status": self.provenance_status,
            "contaminated_for_independent_validation": (
                self.contaminated_for_independent_validation
            ),
        }


def load_model_parameter_registry(path: str | Path = DEFAULT_REGISTRY_PATH) -> dict[str, Any]:
    """Load the QA3 parameter registry rules."""

    registry_path = Path(path)
    payload = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("model_parameter_registry"), dict):
        raise ValueError("model_parameter_registry YAML must contain a mapping")
    return payload["model_parameter_registry"]


def discover_model_parameters(
    *,
    registry_path: str | Path = DEFAULT_REGISTRY_PATH,
    additional_yaml_paths: list[str | Path] | None = None,
    additional_python_paths: list[str | Path] | None = None,
) -> list[ModelParameter]:
    """Discover all QA3-tracked parameters from source specs and Python constants."""

    registry = load_model_parameter_registry(registry_path)
    yaml_paths, python_paths = _registered_paths(registry)
    yaml_paths.extend(Path(path) for path in additional_yaml_paths or [])
    python_paths.extend(Path(path) for path in additional_python_paths or [])

    rows: list[ModelParameter] = []
    for path in sorted({path for path in yaml_paths if path.exists()}):
        rows.extend(_discover_yaml_parameters(path, registry))
    for path in sorted({path for path in python_paths if path.exists()}):
        rows.extend(_discover_python_parameters(path, registry))
    return sorted(rows, key=lambda row: row.parameter_id)


def summarize_model_parameter_inventory(
    *,
    registry_path: str | Path = DEFAULT_REGISTRY_PATH,
) -> dict[str, Any]:
    """Return QA3 inventory counts and hard-gate fields."""

    registry = load_model_parameter_registry(registry_path)
    parameters = discover_model_parameters(registry_path=registry_path)
    ids = [parameter.parameter_id for parameter in parameters]
    duplicate_ids = {key for key, count in Counter(ids).items() if count > 1}
    required_parameter_ids = set(registry.get("required_parameter_ids") or [])
    discovered_ids = set(ids)
    registered_paths = [Path(path) for path in registry.get("registered_source_paths", [])]
    missing_source_paths = [path for path in registered_paths if not path.exists()]
    orphaned_required_ids = sorted(required_parameter_ids - discovered_ids)
    unclassified = [
        parameter for parameter in parameters if parameter.provenance_status != "complete"
    ]
    unknown_origin = [
        parameter for parameter in parameters if parameter.selection_basis == "unknown"
    ]
    after_result = [
        parameter for parameter in parameters if parameter.selected_after_results_seen
    ]
    return {
        "phase": "QA3",
        "parameter_inventory_ready": not unclassified
        and not duplicate_ids
        and not missing_source_paths
        and not orphaned_required_ids,
        "discovered_parameter_count": len(parameters),
        "formal_parameter_count": sum(
            parameter.formal_or_experimental == "formal" for parameter in parameters
        ),
        "experimental_parameter_count": sum(
            parameter.formal_or_experimental == "experimental" for parameter in parameters
        ),
        "production_parameter_count": sum(
            parameter.production_or_research == "production" for parameter in parameters
        ),
        "research_parameter_count": sum(
            parameter.production_or_research == "research" for parameter in parameters
        ),
        "book_core_parameter_count": sum(
            parameter.book_provenance_class == "book_core" for parameter in parameters
        ),
        "modern_extension_parameter_count": sum(
            parameter.book_provenance_class == "modern_extension" for parameter in parameters
        ),
        "project_safety_parameter_count": sum(
            parameter.book_provenance_class == "project_safety" for parameter in parameters
        ),
        "parameter_with_complete_provenance_count": sum(
            parameter.provenance_status == "complete" for parameter in parameters
        ),
        "parameter_with_unknown_origin_count": len(unknown_origin),
        "parameter_selected_after_result_observation_count": len(after_result),
        "unclassified_parameter_count": len(unclassified),
        "duplicate_parameter_id_count": len(duplicate_ids),
        "orphaned_parameter_path_count": len(missing_source_paths)
        + len(orphaned_required_ids),
        "parameter_manifest_hash": compute_parameter_manifest_hash(parameters),
        "parameters": [parameter.to_dict() for parameter in parameters],
    }


def compute_parameter_manifest_hash(parameters: list[ModelParameter] | None = None) -> str:
    """Compute a deterministic hash for parameter identity, value, and classification."""

    rows = parameters if parameters is not None else discover_model_parameters()
    payload = [
        {
            "parameter_id": row.parameter_id,
            "value": row.value,
            "formal_or_experimental": row.formal_or_experimental,
            "production_or_research": row.production_or_research,
            "selection_basis": row.selection_basis,
            "parameter_layer": row.parameter_layer,
        }
        for row in sorted(rows, key=lambda item: item.parameter_id)
    ]
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str).encode(
        "utf-8"
    )
    return hashlib.sha256(encoded).hexdigest()


def parameter_id_for(source_path: str | Path, key_path: str) -> str:
    """Build a stable parameter id from source and key path."""

    source = _normalize_path(source_path)
    cleaned = key_path.replace(" ", "_").replace('"', "")
    return f"{source}::{cleaned}"


def _registered_paths(registry: dict[str, Any]) -> tuple[list[Path], list[Path]]:
    source_paths = [Path(path) for path in registry.get("registered_source_paths", [])]
    yaml_paths = [path for path in source_paths if path.suffix in {".yaml", ".yml"}]
    python_paths = [path for path in source_paths if path.suffix == ".py"]
    return yaml_paths, python_paths


def _discover_yaml_parameters(path: Path, registry: dict[str, Any]) -> list[ModelParameter]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    rows: list[ModelParameter] = []
    _walk_yaml(payload, path, "$", rows, registry)
    return rows


def _walk_yaml(
    value: Any,
    path: Path,
    key_path: str,
    rows: list[ModelParameter],
    registry: dict[str, Any],
) -> None:
    if isinstance(value, dict):
        for raw_key, child in value.items():
            key = str(raw_key)
            child_key_path = f"{key_path}.{key}" if key_path != "$" else key
            if _is_scalar_list(child) and _is_parameter_value(key, child, path):
                rows.append(_build_parameter(path, child_key_path, child, registry))
            else:
                _walk_yaml(child, path, child_key_path, rows, registry)
        return
    if isinstance(value, list):
        for index, child in enumerate(value):
            identifier = _list_identifier(child, index)
            child_key_path = f"{key_path}[{identifier}]"
            _walk_yaml(child, path, child_key_path, rows, registry)
        return
    key = key_path.split(".")[-1]
    if _is_parameter_value(key, value, path):
        rows.append(_build_parameter(path, key_path, value, registry))


def _discover_python_parameters(path: Path, registry: dict[str, Any]) -> list[ModelParameter]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    rows: list[ModelParameter] = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and _track_python_name(target.id):
                    value = _literal_value(node.value)
                    if value is not _MISSING:
                        rows.append(
                            _build_parameter(path, f"python_constant.{target.id}", value, registry)
                        )
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if _track_python_name(node.target.id):
                value = _literal_value(node.value)
                if value is not _MISSING:
                    rows.append(
                        _build_parameter(path, f"python_constant.{node.target.id}", value, registry)
                    )
        elif isinstance(node, ast.ClassDef):
            rows.extend(_class_default_parameters(path, node, registry))
        elif isinstance(node, ast.FunctionDef):
            rows.extend(_function_default_parameters(path, node, registry))

    rows.extend(_numeric_literal_parameters(path, tree, registry))
    return rows


def _class_default_parameters(
    path: Path,
    node: ast.ClassDef,
    registry: dict[str, Any],
) -> list[ModelParameter]:
    rows: list[ModelParameter] = []
    for child in node.body:
        if isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name):
            value = _literal_value(child.value)
            if value is not _MISSING and _track_python_name(child.target.id):
                rows.append(
                    _build_parameter(
                        path,
                        f"class_default.{node.name}.{child.target.id}",
                        value,
                        registry,
                    )
                )
    return rows


def _function_default_parameters(
    path: Path,
    node: ast.FunctionDef,
    registry: dict[str, Any],
) -> list[ModelParameter]:
    rows: list[ModelParameter] = []
    args = list(node.args.args)
    defaults = list(node.args.defaults)
    if not defaults:
        return rows
    defaulted_args = args[-len(defaults) :]
    for arg, default in zip(defaulted_args, defaults, strict=True):
        if not _track_python_name(arg.arg):
            continue
        value = _literal_value(default)
        if value is _MISSING:
            continue
        rows.append(
            _build_parameter(
                path,
                f"function_default.{node.name}.{arg.arg}",
                value,
                registry,
            )
        )
    return rows


def _numeric_literal_parameters(
    path: Path,
    tree: ast.AST,
    registry: dict[str, Any],
) -> list[ModelParameter]:
    rows: list[ModelParameter] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Constant):
            continue
        if not isinstance(node.value, int | float):
            continue
        if isinstance(node.value, bool):
            continue
        parent_key = f"python_literal.line_{node.lineno}_col_{node.col_offset}"
        rows.append(_build_parameter(path, parent_key, node.value, registry))
    return rows


def _build_parameter(
    source_path: str | Path,
    key_path: str,
    value: Any,
    registry: dict[str, Any],
) -> ModelParameter:
    source = _normalize_path(source_path)
    classification = _classify_source(source, registry)
    selected_after_results = classification["selection_basis"] in set(
        registry.get("contaminated_selection_basis", [])
    )
    scenarios = list(CURRENT_SCENARIOS) if selected_after_results else []
    layer = classification["parameter_layer"]
    affects = _affects(layer, source, key_path)
    provenance_status = "complete" if classification["parameter_layer"] != "unclassified" else "unclassified"
    contaminated = selected_after_results
    return ModelParameter(
        parameter_id=parameter_id_for(source, key_path),
        source_path=source,
        source_key_path=key_path,
        parameter_layer=layer,
        value=_json_safe_value(value),
        value_type=_value_type(value),
        formal_or_experimental=classification["formal_or_experimental"],
        production_or_research=classification["production_or_research"],
        affects_candidate_phase=affects["candidate"],
        affects_final_phase=affects["final"],
        affects_confidence=affects["confidence"],
        affects_transition_timing=affects["transition"],
        affects_display_only=affects["display"],
        book_provenance_class=classification["book_provenance_class"],
        selection_basis=classification["selection_basis"],
        first_introduced_phase=classification["first_introduced_phase"],
        first_introduced_commit_if_available=classification[
            "first_introduced_commit_if_available"
        ],
        scenarios_visible_before_selection=scenarios,
        selected_after_results_seen=selected_after_results,
        currently_mutable=False,
        freeze_scope=str(registry.get("freeze_scope", "data_only_baseline_v1")),
        provenance_status=provenance_status,
        contaminated_for_independent_validation=contaminated,
    )


def _classify_source(source: str, registry: dict[str, Any]) -> dict[str, str | None]:
    for layer, rule in registry.get("source_classification", {}).items():
        prefixes = [str(prefix) for prefix in rule.get("path_prefixes", [])]
        if any(source == prefix or source.startswith(prefix) for prefix in prefixes):
            return {
                "parameter_layer": str(layer),
                "formal_or_experimental": str(rule["formal_or_experimental"]),
                "production_or_research": str(rule["production_or_research"]),
                "book_provenance_class": str(rule["book_provenance_class"]),
                "selection_basis": str(rule["selection_basis"]),
                "first_introduced_phase": str(rule["first_introduced_phase"]),
                "first_introduced_commit_if_available": str(
                    rule.get("first_introduced_commit_if_available") or ""
                ),
            }
    return {
        "parameter_layer": "unclassified",
        "formal_or_experimental": "unknown",
        "production_or_research": "unknown",
        "book_provenance_class": "unknown",
        "selection_basis": "unknown",
        "first_introduced_phase": "unknown",
        "first_introduced_commit_if_available": "",
    }


def _affects(layer: str, source: str, key_path: str) -> dict[str, bool]:
    candidate_layers = {
        "formal_indicator",
        "phase_scoring",
        "state_machine",
        "production_context",
        "transition_control",
        "experimental_rule",
    }
    final_layers = {
        "formal_indicator",
        "phase_scoring",
        "state_machine",
        "production_context",
    }
    confidence_terms = ("confidence", "stale", "available_weight", "min_periods")
    transition_terms = (
        "transition",
        "confirmation",
        "hysteresis",
        "cooldown",
        "breadth",
        "phase_order",
        "NEXT_PHASE",
    )
    display_only = "display" in key_path and layer not in final_layers
    return {
        "candidate": layer in candidate_layers,
        "final": layer in final_layers,
        "confidence": any(term in key_path for term in confidence_terms)
        or layer in {"formal_indicator", "phase_scoring"},
        "transition": any(term in key_path for term in transition_terms)
        or layer in {"state_machine", "transition_control", "experimental_rule"},
        "display": display_only or "render" in source,
    }


def _is_parameter_value(key: str, value: Any, source_path: Path) -> bool:
    if isinstance(value, dict):
        return False
    if key.endswith("_zh") or key in _TEXT_KEYS:
        return False
    if key in {"version", "title", "reason", "mapping_note", "objective"}:
        return False
    if isinstance(value, int | float | bool):
        return True
    if isinstance(value, list):
        return _is_scalar_list(value) and _is_parameter_key(key, source_path)
    if isinstance(value, str):
        if not value or len(value) > 96:
            return False
        if _looks_like_text(value):
            return False
        return _is_parameter_key(key, source_path) or value in _KNOWN_ENUM_VALUES
    return False


def _is_parameter_key(key: str, source_path: Path) -> bool:
    lowered = key.lower()
    if key in {"series_id", "frequency", "direction", "score_method", "source_priority"}:
        return "indicator_catalog" in str(source_path)
    return any(term in lowered for term in _PARAMETER_KEY_TERMS)


def _is_scalar_list(value: Any) -> bool:
    return isinstance(value, list) and all(
        isinstance(item, str | int | float | bool) for item in value
    )


def _list_identifier(value: Any, index: int) -> str:
    if isinstance(value, dict):
        for key in (
            "indicator_id",
            "scenario_id",
            "template_id",
            "target_id",
            "phase_id",
            "group_id",
            "id",
        ):
            if key in value:
                return f"{index}:{value[key]}"
    return str(index)


def _track_python_name(name: str) -> bool:
    lowered = name.lower()
    return (
        name.isupper()
        or name.startswith("_CORE")
        or any(term in lowered for term in _PARAMETER_KEY_TERMS)
    )


def _literal_value(node: ast.AST | None) -> Any:
    if node is None:
        return _MISSING
    try:
        return ast.literal_eval(node)
    except (ValueError, TypeError):
        return _MISSING


def _json_safe_value(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_json_safe_value(item) for item in value]
    if isinstance(value, set):
        return sorted(_json_safe_value(item) for item in value)
    if isinstance(value, dict):
        return {str(key): _json_safe_value(raw) for key, raw in value.items()}
    if isinstance(value, list):
        return [_json_safe_value(item) for item in value]
    return value


def _value_type(value: Any) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int | float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list | tuple | set):
        return "list"
    if isinstance(value, dict):
        return "mapping"
    if value is None:
        return "null"
    return type(value).__name__


def _looks_like_text(value: str) -> bool:
    return any(char in value for char in "，。；：、") or " " in value.strip()


def _normalize_path(path: str | Path) -> str:
    raw = str(path)
    try:
        return str(Path(raw).resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return raw


class _Missing:
    pass


_MISSING = _Missing()

_TEXT_KEYS = {
    "description",
    "display_name",
    "display_name_zh",
    "description_zh",
    "public_explanation_zh",
    "reason_zh",
    "rationale_zh",
    "caveats_zh",
    "expected_behavior_zh",
    "note",
    "notes",
    "mapping_note",
}

_PARAMETER_KEY_TERMS = (
    "threshold",
    "window",
    "period",
    "confidence",
    "weight",
    "direction",
    "score",
    "margin",
    "cooldown",
    "hysteresis",
    "confirmation",
    "breadth",
    "stale",
    "fallback",
    "rule",
    "status",
    "phase",
    "signal",
    "transform",
    "mode",
    "allowed",
    "required",
    "enabled",
    "min_",
    "max_",
    "frequency",
    "persistence",
    "rebalance",
    "allocation",
    "ratio",
    "levels",
    "series_id",
    "source_priority",
)

_KNOWN_ENUM_VALUES = {
    "recession",
    "recovery",
    "growth",
    "boom",
    "as_is",
    "inverted",
    "higher_is_better",
    "lower_is_better",
    "rising_is_better",
    "falling_is_better",
    "higher_is_worse",
    "lower_is_worse",
    "neutral_midpoint",
    "data_only",
    "revised",
    "strict_complete",
    "strict_partial",
}

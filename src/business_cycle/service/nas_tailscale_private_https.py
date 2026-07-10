"""Phase109 private Tailscale HTTPS acceptance and runtime hardening package."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import json

import yaml

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONTRACT_PATH = ROOT / "specs/common/nas_tailscale_private_https_contract.yaml"
PHASE108_CLOSURE_PATH = (
    ROOT / "specs/audits/phase108_nas_container_manager_live_start_closure.yaml"
)
RUNTIME_PATH = ROOT / "src/business_cycle/service/nas_runtime_server.py"

PROHIBITED_FIELDS = {
    "current_phase",
    "candidate_phase",
    "selected_phase",
    "winning_phase",
    "phase_rank",
    "phase_score",
    "target_weight",
    "allocation_recommendation",
    "buy_signal",
    "sell_signal",
    "trade_action",
    "password",
    "token",
    "tailnet_ip",
    "tailnet_dns_name",
}


def load_nas_tailscale_private_https_contract(
    path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Load the Phase109 private HTTPS contract."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return dict(payload["nas_tailscale_private_https_contract"])


def build_nas_tailscale_private_https_acceptance(
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
    acceptance_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a no-secret acceptance package without changing tailnet state."""

    contract = load_nas_tailscale_private_https_contract(contract_path)
    observed = dict(contract["observed_live_state"])
    sample_report = _sample_acceptance_report(contract)
    sample_validation = validate_nas_tailscale_private_https_report(
        sample_report,
        contract,
    )
    actual_validation = (
        validate_nas_tailscale_private_https_report(acceptance_report, contract)
        if acceptance_report is not None
        else _missing_acceptance(contract)
    )
    hardening = _runtime_hardening_status(contract)
    rebaseline = contract["product_readiness_rebaseline"]
    summary: dict[str, Any] = {
        "phase": "109",
        "phase_id": 109,
        "phase_label": contract["phase_label"],
        "artifact_id": "phase109_nas_tailscale_private_https_acceptance",
        "artifact_version": contract["version"],
        "output_mode": "private_https_acceptance_checkpoint_no_secret",
        "research_only": True,
        "nas_tailscale_private_https_contract_ready": _contract_ready(contract),
        "phase108_dependency_ready": _phase108_dependency_ready(),
        **hardening,
        "tailscale_live_state_reconciled": _observed_state_ready(observed),
        "tailscale_backend_online_observed": (
            observed["tailscale_backend_state"] == "Running"
            and observed["tailscale_online"] is True
        ),
        "tailscale_installed_version_observed": observed[
            "tailscale_installed_version"
        ],
        "tailscale_serve_configured": observed["tailscale_serve_configured"],
        "tailscale_funnel_configured": observed["tailscale_funnel_configured"],
        "mobile_cellular_smoke_passed": observed[
            "mobile_cellular_smoke_passed"
        ],
        "sample_acceptance_report_valid": sample_validation["report_valid"],
        "private_https_acceptance_status": actual_validation[
            "private_https_acceptance_status"
        ],
        "private_https_accepted": actual_validation["private_https_accepted"],
        "operator_action_required": not actual_validation["private_https_accepted"],
        "production_readiness_rebaseline_required": rebaseline["required"],
        "production_readiness_rebaseline_status": rebaseline["status"],
        "production_readiness_rebaseline_reason_count": len(rebaseline["reasons"]),
        "product_progress_percentage_change_count": 0,
        "postgres_business_table_count_observed": observed[
            "postgres_business_table_count"
        ],
        "public_exposure_enabled": False,
        "secure_value_committed_count": 0,
        "candidate_phase_emitted": False,
        "current_phase_emitted": False,
        "standalone_classifier_added_count": 0,
        "phase_rank_or_score_added_count": 0,
        "production_behavior_change_count": 0,
        "semantic_drift_count": 0,
        "activation_checklist": _activation_checklist(contract),
        "sample_acceptance_report": sample_report,
        "acceptance_report_validation": actual_validation,
        "allowed_uses": contract["allowed_uses"],
        "prohibited_uses": contract["prohibited_uses"],
        "development_next_phase": contract["hard_gates"]["development_next_phase"],
    }
    summary["prohibited_output_field_count"] = _contains_prohibited_field(summary)
    summary["nas_tailscale_private_https_package_ready"] = _passes(
        summary,
        contract["hard_gates"],
    )
    summary["result"] = (
        "passed" if summary["nas_tailscale_private_https_package_ready"] else "blocked"
    )
    return summary


def summarize_nas_tailscale_private_https(
    *,
    contract_path: str | Path = DEFAULT_CONTRACT_PATH,
) -> dict[str, Any]:
    """Return compact Phase109 private HTTPS checkpoint fields."""

    package = build_nas_tailscale_private_https_acceptance(
        contract_path=contract_path,
    )
    keys = (
        "phase",
        "phase_id",
        "nas_tailscale_private_https_contract_ready",
        "nas_tailscale_private_https_package_ready",
        "phase108_dependency_ready",
        "runtime_https_cookie_contract_ready",
        "runtime_login_rate_limit_ready",
        "runtime_security_headers_ready",
        "tailscale_live_state_reconciled",
        "tailscale_backend_online_observed",
        "tailscale_installed_version_observed",
        "tailscale_serve_configured",
        "tailscale_funnel_configured",
        "mobile_cellular_smoke_passed",
        "sample_acceptance_report_valid",
        "private_https_acceptance_status",
        "private_https_accepted",
        "operator_action_required",
        "production_readiness_rebaseline_required",
        "production_readiness_rebaseline_status",
        "production_readiness_rebaseline_reason_count",
        "product_progress_percentage_change_count",
        "postgres_business_table_count_observed",
        "public_exposure_enabled",
        "secure_value_committed_count",
        "prohibited_output_field_count",
        "candidate_phase_emitted",
        "current_phase_emitted",
        "standalone_classifier_added_count",
        "phase_rank_or_score_added_count",
        "production_behavior_change_count",
        "semantic_drift_count",
        "development_next_phase",
        "result",
    )
    return {key: package[key] for key in keys} | {
        "nas_tailscale_private_https_package": package,
    }


def validate_nas_tailscale_private_https_report(
    report: dict[str, Any],
    contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate a redacted operator report without contacting Tailscale."""

    contract = contract or load_nas_tailscale_private_https_contract()
    report_contract = contract["acceptance_report"]
    boolean_fields = list(report_contract["required_boolean_fields"])
    text_fields = list(report_contract["required_text_fields"])
    missing_fields = [
        field
        for field in [*boolean_fields, *text_fields]
        if field not in report
    ]
    false_fields = [field for field in boolean_fields if report.get(field) is not True]
    wrong_mode = report.get("report_mode") != report_contract["report_mode"]
    wrong_target = report.get("serve_target") != report_contract[
        "expected_serve_target"
    ]
    prohibited_count = _contains_prohibited_field(report)
    report_valid = not any(
        (missing_fields, false_fields, wrong_mode, wrong_target, prohibited_count)
    )
    return {
        "report_valid": report_valid,
        "missing_field_count": len(missing_fields),
        "false_acceptance_field_count": len(false_fields),
        "wrong_report_mode": wrong_mode,
        "wrong_serve_target": wrong_target,
        "prohibited_report_field_count": prohibited_count,
        "private_https_acceptance_status": (
            report_contract["accepted_status"]
            if report_valid
            else "blocked_invalid_operator_report"
        ),
        "private_https_accepted": report_valid,
    }


def _contract_ready(contract: dict[str, Any]) -> bool:
    target = contract["target_private_access"]
    hardening = contract["runtime_hardening"]
    return (
        contract["status"] == "active_private_https_acceptance_contract"
        and target["access_mode"] == "tailscale_serve_private_https"
        and target["serve_target"] == "http://127.0.0.1:18080"
        and target["serve_protocol"] == "https"
        and target["public_funnel_allowed"] is False
        and target["public_router_port_forward_allowed"] is False
        and hardening["secure_cookie_required_after_https_activation"] is True
        and hardening["login_max_failures_default"] == 5
        and hardening["login_window_seconds_default"] == 300
    )


def _phase108_dependency_ready() -> bool:
    payload = yaml.safe_load(PHASE108_CLOSURE_PATH.read_text(encoding="utf-8"))
    gates = payload["phase108_nas_container_manager_live_start_closure"][
        "hard_gates"
    ]
    return (
        gates["phase108_closure_ready"] is True
        and gates["nas_container_manager_live_start_package_ready"] is True
    )


def _runtime_hardening_status(contract: dict[str, Any]) -> dict[str, bool]:
    source = RUNTIME_PATH.read_text(encoding="utf-8")
    required_headers = contract["runtime_hardening"]["required_security_headers"]
    return {
        "runtime_https_cookie_contract_ready": all(
            marker in source
            for marker in (
                "BUSINESS_CYCLE_APP_SECURE_COOKIE",
                'attributes.append("Secure")',
                "Strict-Transport-Security",
            )
        ),
        "runtime_login_rate_limit_ready": all(
            marker in source
            for marker in (
                "class LoginAttemptLimiter",
                "BUSINESS_CYCLE_LOGIN_MAX_FAILURES",
                "BUSINESS_CYCLE_LOGIN_WINDOW_SECONDS",
                "Retry-After",
            )
        ),
        "runtime_security_headers_ready": all(
            header in source for header in required_headers
        ),
    }


def _observed_state_ready(observed: dict[str, Any]) -> bool:
    return (
        observed["app_container_healthy"] is True
        and observed["postgres_container_healthy"] is True
        and observed["tailscale_backend_state"] == "Running"
        and observed["tailscale_online"] is True
        and observed["tailscale_serve_configured"] is False
        and observed["tailscale_funnel_configured"] is False
        and observed["tailnet_ip_or_dns_committed"] is False
    )


def _sample_acceptance_report(contract: dict[str, Any]) -> dict[str, Any]:
    report = {
        field: True
        for field in contract["acceptance_report"]["required_boolean_fields"]
    }
    return report | {
        "report_id": "phase109_sample_redacted_private_https_acceptance",
        "report_mode": contract["acceptance_report"]["report_mode"],
        "serve_target": contract["acceptance_report"]["expected_serve_target"],
    }


def _missing_acceptance(contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "report_valid": False,
        "missing_field_count": len(
            contract["acceptance_report"]["required_boolean_fields"],
        ),
        "false_acceptance_field_count": 0,
        "wrong_report_mode": False,
        "wrong_serve_target": False,
        "prohibited_report_field_count": 0,
        "private_https_acceptance_status": contract["acceptance_report"][
            "missing_status"
        ],
        "private_https_accepted": False,
    }


def _activation_checklist(contract: dict[str, Any]) -> list[dict[str, Any]]:
    observed = contract["observed_live_state"]
    completed = {
        "confirm_funnel_disabled": observed["tailscale_funnel_configured"] is False,
    }
    return [
        {
            "step_id": step,
            "status": "observed_passed" if completed.get(step) else "operator_required",
            "secret_input_required": False,
        }
        for step in contract["operator_acceptance_steps"]
    ]


def _contains_prohibited_field(value: Any) -> int:
    if isinstance(value, dict):
        return sum(
            (1 if key in PROHIBITED_FIELDS else 0) + _contains_prohibited_field(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return sum(_contains_prohibited_field(item) for item in value)
    return 0


def _passes(summary: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(summary.get(key) == value for key, value in expected.items())


def format_nas_tailscale_private_https_summary(summary: dict[str, Any]) -> str:
    """Format compact fields for the CLI without private tailnet identifiers."""

    excluded = {"nas_tailscale_private_https_package"}
    return "\n".join(
        f"{key}={json.dumps(value) if isinstance(value, list) else _format(value)}"
        for key, value in summary.items()
        if key not in excluded
    )


def _format(value: Any) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)

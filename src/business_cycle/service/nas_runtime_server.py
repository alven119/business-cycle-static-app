"""Private NAS runtime HTTP server for the research dashboard.

The server intentionally uses the Python standard library. It wraps the
Phase96/97 NAS app shell so the DS925+ container can serve the research
dashboard without adding a new web-framework dependency in this phase.
"""

from __future__ import annotations

from argparse import ArgumentParser
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from typing import Any
from urllib.parse import urlparse

from business_cycle.service.nas_app_shell import (
    NasAppRequest,
    build_nas_app_shell,
    dispatch_nas_app_request,
)

DEFAULT_SESSION_HEADER = "X-Business-Cycle-Session"
LOCAL_HEALTH_PATHS = {"/healthz", "/readyz"}


@dataclass(frozen=True)
class RuntimeResponse:
    """Small response object shared by tests and the HTTP handler."""

    status_code: int
    content_type: str
    body: str
    route_id: str | None = None


def build_runtime_response(
    *,
    path: str,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    session_secret: str | None = None,
    shell: dict[str, Any] | None = None,
) -> RuntimeResponse:
    """Return a private NAS runtime response without binding a network port."""

    normalized_path = urlparse(path).path or "/"
    headers = _normalize_headers(headers or {})
    if normalized_path == "/healthz":
        return _json_response(
            200,
            {
                "status": "ok",
                "service": "business_cycle_private_nas",
                "research_only": True,
                "public_exposure": False,
            },
        )
    if normalized_path == "/readyz":
        shell = shell or build_nas_app_shell()
        return _json_response(
            200,
            {
                "status": "ready",
                "route_count": shell["route_count"],
                "research_only": True,
                "public_exposure": False,
            },
        )
    if method.upper() != "GET":
        return _json_response(405, {"error": "method_not_allowed", "research_only": True})

    secret = session_secret if session_secret is not None else _session_secret()
    if not secret:
        return _json_response(
            503,
            {
                "error": "session_secret_not_configured",
                "research_only": True,
                "private_nas_only": True,
            },
        )
    if not _authorized(headers, secret):
        return _json_response(
            401,
            {
                "error": "unauthorized",
                "research_only": True,
                "private_nas_only": True,
            },
        )

    shell = shell or build_nas_app_shell()
    local_policy = shell["auth_policy"]
    shell_response = dispatch_nas_app_request(
        shell,
        NasAppRequest(
            path=normalized_path,
            method=method.upper(),
            headers={
                local_policy["session_header_name"]: local_policy[
                    "local_smoke_session_marker"
                ],
            },
        ),
    )
    return RuntimeResponse(
        status_code=int(shell_response["status_code"]),
        content_type=str(shell_response["content_type"]),
        body=str(shell_response["body"]),
        route_id=shell_response.get("route_id"),
    )


def main(argv: list[str] | None = None) -> int:
    """Run the private NAS HTTP server."""

    parser = ArgumentParser()
    parser.add_argument("--host", default=os.environ.get("BUSINESS_CYCLE_BIND_HOST", "127.0.0.1"))
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("BUSINESS_CYCLE_BIND_PORT", "8000")),
    )
    args = parser.parse_args(argv)

    server = ThreadingHTTPServer((args.host, args.port), _RuntimeHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    finally:
        server.server_close()
    return 0


class _RuntimeHandler(BaseHTTPRequestHandler):
    server_version = "BusinessCycleNAS/phase107"

    def do_GET(self) -> None:  # noqa: N802
        response = build_runtime_response(
            path=self.path,
            method="GET",
            headers={key: value for key, value in self.headers.items()},
        )
        self._send_runtime_response(response)

    def do_POST(self) -> None:  # noqa: N802
        response = build_runtime_response(
            path=self.path,
            method="POST",
            headers={key: value for key, value in self.headers.items()},
        )
        self._send_runtime_response(response)

    def log_message(self, format: str, *args: object) -> None:
        """Silence default request logging; DSM/container logs stay compact."""

        _ = (format, args)

    def _send_runtime_response(self, response: RuntimeResponse) -> None:
        body = response.body.encode("utf-8")
        self.send_response(response.status_code)
        self.send_header("content-type", response.content_type)
        self.send_header("cache-control", "no-store")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def _json_response(status_code: int, payload: dict[str, Any]) -> RuntimeResponse:
    return RuntimeResponse(
        status_code=status_code,
        content_type="application/json",
        body=json.dumps(payload, sort_keys=True),
    )


def _session_secret() -> str:
    return os.environ.get("BUSINESS_CYCLE_APP_SESSION_SECRET", "")


def _session_header_name() -> str:
    return os.environ.get("BUSINESS_CYCLE_APP_SESSION_HEADER", DEFAULT_SESSION_HEADER)


def _normalize_headers(headers: dict[str, str]) -> dict[str, str]:
    normalized = dict(headers)
    for key, value in headers.items():
        normalized[key.lower()] = value
    return normalized


def _authorized(headers: dict[str, str], secret: str) -> bool:
    header_name = _session_header_name()
    return (
        headers.get(header_name) == secret
        or headers.get(header_name.lower()) == secret
    )


if __name__ == "__main__":
    raise SystemExit(main())

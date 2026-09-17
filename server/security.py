"""
API-key protection for the OpenAI-compatible endpoints.

Every request under `protect_prefix` (default /v1) must carry a bearer token
matching WEUI_AI_API_KEY. Comparison is constant-time to avoid leaking the key
through timing. /healthz stays open so container health checks keep working.

When WEUI_AI_API_KEY is unset the middleware refuses to start unless
WEUI_AI_ALLOW_UNAUTH is explicitly enabled — that escape hatch exists only for
local development, never for the deployed server.
"""

from __future__ import annotations

import os
import secrets

from starlette.requests import Request
from starlette.responses import JSONResponse

API_KEY = os.getenv("WEUI_AI_API_KEY", "").strip()
ALLOW_UNAUTH = os.getenv("WEUI_AI_ALLOW_UNAUTH", "0").lower() in (
    "1", "true", "yes", "on",
)


class ConfigurationError(RuntimeError):
    """Raised at startup when the server is misconfigured (e.g. no API key)."""


def bearer_token(request: Request) -> str:
    """Return the bearer token from the Authorization header, or ''."""
    header = request.headers.get("authorization", "")
    if header.lower().startswith("bearer "):
        return header[7:].strip()
    return ""


def install_api_key(
    app,
    *,
    key: str = API_KEY,
    allow_unauth: bool = ALLOW_UNAUTH,
    protect_prefix: str = "/v1",
) -> None:
    """Require a valid bearer token on every path under `protect_prefix`."""

    if not key and not allow_unauth:
        raise ConfigurationError(
            "WEUI_AI_API_KEY is not set. Set it to a strong secret before "
            "starting the server (or set WEUI_AI_ALLOW_UNAUTH=1 for local dev)."
        )

    @app.middleware("http")
    async def _api_key(request: Request, call_next):
        if not key or not request.url.path.startswith(protect_prefix):
            return await call_next(request)

        if secrets.compare_digest(bearer_token(request), key):
            return await call_next(request)

        return JSONResponse(
            status_code=401,
            content={
                "error": {
                    "message": "Missing or invalid API key.",
                    "type": "authentication_error",
                }
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

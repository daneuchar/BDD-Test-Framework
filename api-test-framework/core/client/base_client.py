"""Template Method pattern for API client request lifecycle.

BaseAPIClient defines the invariant request lifecycle:
    prepare -> authenticate -> send -> handle response -> log

Subclasses override only _send() to provide sync or async HTTP transport.
"""

from __future__ import annotations

import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PreparedRequest:
    """Immutable representation of an outgoing HTTP request."""

    method: str
    url: str
    headers: dict[str, str] = field(default_factory=dict)
    json: dict[str, Any] | None = None
    params: dict[str, Any] | None = None
    data: Any | None = None
    files: dict[str, Any] | None = None


@dataclass
class APIResponse:
    """Normalized response returned by every client implementation."""

    status_code: int
    json_data: dict[str, Any] | list[Any] | None
    headers: dict[str, str]
    elapsed_ms: float
    raw_response: Any = field(repr=False, default=None)


# Thread-local storage so allure/logging plugins can access the most recent
# request/response pair without cross-thread contamination.
_thread_local = threading.local()


def get_last_request() -> PreparedRequest | None:
    """Return the most recent PreparedRequest on the current thread."""
    return getattr(_thread_local, "last_request", None)


def get_last_response() -> APIResponse | None:
    """Return the most recent APIResponse on the current thread."""
    return getattr(_thread_local, "last_response", None)


class BaseAPIClient(ABC):
    """Abstract base for all API clients (Template Method pattern).

    Constructor Parameters:
        base_url: Root URL for the API (e.g. "https://api.example.com").
        auth:     Optional auth strategy implementing ``authenticate(request)``.
        response_handler: Optional chain-of-responsibility handler.
        timeout:  Default request timeout in seconds.
        default_headers: Headers merged into every request.
    """

    def __init__(
        self,
        base_url: str,
        auth: Any | None = None,
        response_handler: Any | None = None,
        timeout: float = 30.0,
        default_headers: dict[str, str] | None = None,
        api_version: str | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.auth = auth
        self.response_handler = response_handler
        self.timeout = timeout
        self.default_headers: dict[str, str] = default_headers or {}
        self.api_version = api_version

    # ------------------------------------------------------------------
    # Public convenience methods
    # ------------------------------------------------------------------

    def get(self, endpoint: str, **kwargs: Any) -> APIResponse:
        return self.request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs: Any) -> APIResponse:
        return self.request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs: Any) -> APIResponse:
        return self.request("PUT", endpoint, **kwargs)

    def patch(self, endpoint: str, **kwargs: Any) -> APIResponse:
        return self.request("PATCH", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs: Any) -> APIResponse:
        return self.request("DELETE", endpoint, **kwargs)

    # ------------------------------------------------------------------
    # Template Method — the invariant request lifecycle
    # ------------------------------------------------------------------

    def request(self, method: str, endpoint: str, **kwargs: Any) -> APIResponse:
        """Execute the full request lifecycle.

        Steps:
            1. _prepare_request  — build PreparedRequest from args
            2. _authenticate     — delegate to auth strategy
            3. _send             — abstract, implemented by subclass
            4. _handle_response  — run response through handler chain
            5. _log_request      — store in thread-local for plugins
        """
        prepared = self._prepare_request(method, endpoint, **kwargs)
        prepared = self._authenticate(prepared)

        start = time.monotonic()
        raw_response = self._send(prepared)
        elapsed_ms = (time.monotonic() - start) * 1000

        response = self._build_api_response(raw_response, elapsed_ms)
        response = self._handle_response(response)
        self._log_request(prepared, response)
        return response

    # ------------------------------------------------------------------
    # Lifecycle hooks (overridable)
    # ------------------------------------------------------------------

    def _prepare_request(
        self, method: str, endpoint: str, **kwargs: Any
    ) -> PreparedRequest:
        if self.api_version is not None:
            url = f"{self.base_url}/api/{self.api_version}/{endpoint.lstrip('/')}"
        else:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {**self.default_headers, **kwargs.pop("headers", {})}
        return PreparedRequest(
            method=method.upper(),
            url=url,
            headers=headers,
            json=kwargs.get("json"),
            params=kwargs.get("params"),
            data=kwargs.get("data"),
            files=kwargs.get("files"),
        )

    def _authenticate(self, request: PreparedRequest) -> PreparedRequest:
        if self.auth is not None:
            return self.auth.authenticate(request)
        return request

    @abstractmethod
    def _send(self, request: PreparedRequest) -> Any:
        """Transport-level send — must be implemented by subclass."""

    def _build_api_response(self, raw_response: Any, elapsed_ms: float) -> APIResponse:
        """Convert a raw transport response into an APIResponse.

        Subclasses may override if the raw response requires special handling.
        """
        try:
            json_data = raw_response.json()
        except Exception:
            json_data = None

        headers = dict(raw_response.headers) if hasattr(raw_response, "headers") else {}
        status_code = getattr(raw_response, "status_code", 0)

        return APIResponse(
            status_code=status_code,
            json_data=json_data,
            headers=headers,
            elapsed_ms=elapsed_ms,
            raw_response=raw_response,
        )

    def _handle_response(self, response: APIResponse) -> APIResponse:
        if self.response_handler is not None:
            return self.response_handler.handle(response)
        return response

    def _log_request(
        self, request: PreparedRequest, response: APIResponse
    ) -> None:
        """Store in thread-local so allure/logging plugins can pick it up."""
        _thread_local.last_request = request
        _thread_local.last_response = response

    # ------------------------------------------------------------------
    # Auth mutation helpers
    # ------------------------------------------------------------------

    def set_auth(self, auth: Any) -> None:
        """Replace the auth strategy at runtime."""
        self.auth = auth

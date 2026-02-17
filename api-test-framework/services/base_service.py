"""Base service with client injection and request helper."""

from __future__ import annotations

from typing import Any, TypeVar

from pydantic import BaseModel

from core.client.base_client import APIResponse, BaseAPIClient

T = TypeVar("T", bound=BaseModel)


class BaseService:
    """Base class for all service objects.

    Accepts a :class:`BaseAPIClient` via constructor injection and provides
    a ``_request`` helper that serializes Pydantic models and delegates to
    the underlying client.
    """

    def __init__(self, client: BaseAPIClient) -> None:
        self.client = client

    @property
    def api_version(self) -> str | None:
        """Return the API version from the underlying client, if set."""
        return getattr(self.client, "api_version", None)

    def _request(
        self,
        method: str,
        endpoint: str,
        *,
        body: BaseModel | None = None,
        params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> APIResponse:
        """Serialize a Pydantic model body and delegate to the client.

        Args:
            method:   HTTP method (GET, POST, PUT, PATCH, DELETE).
            endpoint: URL path (from Endpoints enum).
            body:     Optional Pydantic model to serialize as JSON.
            params:   Optional query parameters.
            **kwargs: Forwarded to ``client.request()``.

        Returns:
            The :class:`APIResponse` from the client.
        """
        if body is not None:
            kwargs["json"] = body.model_dump(by_alias=True, exclude_none=True)
        if params is not None:
            kwargs["params"] = params
        return self.client.request(method, endpoint, **kwargs)

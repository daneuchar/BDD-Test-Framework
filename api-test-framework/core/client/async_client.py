"""Asynchronous API client using ``httpx.AsyncClient``."""

from __future__ import annotations

import time
from typing import Any

import httpx

from .base_client import APIResponse, BaseAPIClient, PreparedRequest


class AsyncAPIClient(BaseAPIClient):
    """Concrete client backed by :class:`httpx.AsyncClient`.

    Use as an async context manager for proper resource cleanup::

        async with AsyncAPIClient(base_url="...") as client:
            resp = await client.async_request("GET", "/users")
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    # ------------------------------------------------------------------
    # Sync _send is not used — override the full lifecycle for async
    # ------------------------------------------------------------------

    def _send(self, request: PreparedRequest) -> Any:
        raise NotImplementedError(
            "Use async_request() instead of the synchronous request() path."
        )

    async def async_send(self, request: PreparedRequest) -> httpx.Response:
        return await self.client.request(
            method=request.method,
            url=request.url,
            headers=request.headers,
            json=request.json,
            params=request.params,
            data=request.data,
            files=request.files,
        )

    async def async_request(
        self, method: str, endpoint: str, **kwargs: Any
    ) -> APIResponse:
        """Full async request lifecycle — mirrors the sync template method."""
        prepared = self._prepare_request(method, endpoint, **kwargs)
        prepared = self._authenticate(prepared)

        start = time.monotonic()
        raw_response = await self.async_send(prepared)
        elapsed_ms = (time.monotonic() - start) * 1000

        response = self._build_api_response(raw_response, elapsed_ms)
        response = self._handle_response(response)
        self._log_request(prepared, response)
        return response

    # Convenience async helpers
    async def async_get(self, endpoint: str, **kwargs: Any) -> APIResponse:
        return await self.async_request("GET", endpoint, **kwargs)

    async def async_post(self, endpoint: str, **kwargs: Any) -> APIResponse:
        return await self.async_request("POST", endpoint, **kwargs)

    async def async_put(self, endpoint: str, **kwargs: Any) -> APIResponse:
        return await self.async_request("PUT", endpoint, **kwargs)

    async def async_patch(self, endpoint: str, **kwargs: Any) -> APIResponse:
        return await self.async_request("PATCH", endpoint, **kwargs)

    async def async_delete(self, endpoint: str, **kwargs: Any) -> APIResponse:
        return await self.async_request("DELETE", endpoint, **kwargs)

    async def close(self) -> None:
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> AsyncAPIClient:
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.close()

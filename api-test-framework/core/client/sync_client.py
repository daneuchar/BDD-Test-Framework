"""Synchronous API client using ``requests.Session``."""

from __future__ import annotations

from typing import Any

import requests

from .base_client import APIResponse, BaseAPIClient, PreparedRequest


class SyncAPIClient(BaseAPIClient):
    """Concrete client backed by :class:`requests.Session`.

    The session is lazily created on first use and can be explicitly
    closed via :meth:`close` or used as a context manager.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._session: requests.Session | None = None

    @property
    def session(self) -> requests.Session:
        if self._session is None:
            self._session = requests.Session()
        return self._session

    def _send(self, request: PreparedRequest) -> requests.Response:
        return self.session.request(
            method=request.method,
            url=request.url,
            headers=request.headers,
            json=request.json,
            params=request.params,
            data=request.data,
            files=request.files,
            timeout=self.timeout,
        )

    def close(self) -> None:
        if self._session is not None:
            self._session.close()
            self._session = None

    def __enter__(self) -> SyncAPIClient:
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

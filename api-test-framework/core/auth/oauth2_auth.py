"""OAuth 2.0 client-credentials authentication strategy."""

from __future__ import annotations

import threading
import time
from typing import TYPE_CHECKING, Any

import requests

from .base_auth import BaseAuth

if TYPE_CHECKING:
    from core.client.base_client import PreparedRequest


class OAuth2Auth(BaseAuth):
    """Fetches and caches an OAuth 2.0 access token using the
    client-credentials grant.  Automatically refreshes when expired.

    Parameters:
        client_id:     OAuth client identifier.
        client_secret: OAuth client secret.
        token_url:     Token endpoint URL.
        scope:         Optional scope string.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        token_url: str,
        scope: str | None = None,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.scope = scope

        self._token: str | None = None
        self._expires_at: float = 0.0
        self._lock = threading.Lock()

    def authenticate(self, request: PreparedRequest) -> PreparedRequest:
        token = self._get_token()
        request.headers["Authorization"] = f"Bearer {token}"
        return request

    def _get_token(self) -> str:
        with self._lock:
            if self._token is None or time.monotonic() >= self._expires_at:
                self._refresh_token()
            assert self._token is not None
            return self._token

    def _refresh_token(self) -> None:
        payload: dict[str, Any] = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        if self.scope:
            payload["scope"] = self.scope

        resp = requests.post(self.token_url, data=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        self._token = data["access_token"]
        # Refresh 60 s before actual expiry to avoid edge-case failures
        expires_in = data.get("expires_in", 3600)
        self._expires_at = time.monotonic() + max(expires_in - 60, 0)

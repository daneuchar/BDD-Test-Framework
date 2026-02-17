"""Bearer token authentication strategy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base_auth import BaseAuth

if TYPE_CHECKING:
    from core.client.base_client import PreparedRequest


class BearerAuth(BaseAuth):
    """Adds ``Authorization: Bearer <token>`` to every request."""

    def __init__(self, token: str) -> None:
        self.token = token

    def authenticate(self, request: PreparedRequest) -> PreparedRequest:
        request.headers["Authorization"] = f"Bearer {self.token}"
        return request

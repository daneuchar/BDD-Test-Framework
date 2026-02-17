"""API-key authentication strategy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base_auth import BaseAuth

if TYPE_CHECKING:
    from core.client.base_client import PreparedRequest


class ApiKeyAuth(BaseAuth):
    """Adds a custom API-key header to every request.

    Parameters:
        key:         The API key value.
        header_name: Header name (default ``X-API-Key``).
    """

    def __init__(self, key: str, header_name: str = "X-API-Key") -> None:
        self.key = key
        self.header_name = header_name

    def authenticate(self, request: PreparedRequest) -> PreparedRequest:
        request.headers[self.header_name] = self.key
        return request

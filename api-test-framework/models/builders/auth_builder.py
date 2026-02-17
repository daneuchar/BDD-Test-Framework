"""Fluent builder for LoginRequest."""

from __future__ import annotations

from models.auth import LoginRequest


class AuthBuilder:
    """Build :class:`LoginRequest` objects using a fluent interface.

    Usage::

        login = (
            AuthBuilder()
            .with_credentials("admin", "secret")
            .build()
        )
    """

    def __init__(self) -> None:
        self._username: str = ""
        self._password: str = ""

    def with_credentials(self, username: str, password: str) -> AuthBuilder:
        self._username = username
        self._password = password
        return self

    def with_defaults(self) -> AuthBuilder:
        """Populate fields with default test credentials."""
        self._username = "testuser"
        self._password = "P@ssw0rd123"
        return self

    def build(self) -> LoginRequest:
        return LoginRequest(
            username=self._username,
            password=self._password,
        )

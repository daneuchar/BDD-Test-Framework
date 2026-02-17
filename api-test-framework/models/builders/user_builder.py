"""Fluent builder for CreateUserRequest."""

from __future__ import annotations

from models.user import CreateUserRequest


class UserBuilder:
    """Build :class:`CreateUserRequest` objects using a fluent interface.

    Usage::

        user = (
            UserBuilder()
            .with_name("Alice")
            .with_email("alice@example.com")
            .with_password("Str0ngP@ss!")
            .with_role("admin")
            .build()
        )
    """

    def __init__(self) -> None:
        self._name: str = ""
        self._email: str = ""
        self._password: str = ""
        self._role: str = "user"

    def with_name(self, name: str) -> UserBuilder:
        self._name = name
        return self

    def with_email(self, email: str) -> UserBuilder:
        self._email = email
        return self

    def with_password(self, password: str) -> UserBuilder:
        self._password = password
        return self

    def with_role(self, role: str) -> UserBuilder:
        self._role = role
        return self

    def with_defaults(self) -> UserBuilder:
        """Populate every field with sensible default values."""
        self._name = "Test User"
        self._email = "testuser@example.com"
        self._password = "P@ssw0rd123"
        self._role = "user"
        return self

    def build(self) -> CreateUserRequest:
        return CreateUserRequest(
            name=self._name,
            email=self._email,
            password=self._password,
            role=self._role,
        )

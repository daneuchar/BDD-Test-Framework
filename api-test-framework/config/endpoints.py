"""Enum-based route registry.

All API endpoints are defined here as enum members. Use the ``url()`` method
to render path parameters::

    Endpoints.USER_BY_ID.url(user_id="123")
    # => "/users/123"
"""

from enum import Enum


class Endpoints(str, Enum):
    # User endpoints
    USERS = "/users"
    USER_BY_ID = "/users/{user_id}"

    # Auth endpoints
    AUTH_LOGIN = "/auth/login"
    AUTH_REFRESH = "/auth/refresh"
    AUTH_LOGOUT = "/auth/logout"

    # User search (v2-only)
    USERS_SEARCH = "/users/search"

    # System endpoints
    HEALTH = "/health"

    def url(self, **kwargs: str) -> str:
        """Render the endpoint path with the given path parameters."""
        return self.value.format(**kwargs)

"""Auth request DTOs."""

from __future__ import annotations

from pydantic import Field

from .base_model import BaseDTO


class LoginRequest(BaseDTO):
    """Payload for POST /auth/login."""

    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class RefreshRequest(BaseDTO):
    """Payload for POST /auth/refresh."""

    refresh_token: str = Field(..., alias="refreshToken")

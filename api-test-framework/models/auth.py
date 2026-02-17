"""Auth request and response DTOs."""

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


class TokenResponse(BaseDTO):
    """Expected shape of an authentication token response."""

    access_token: str = Field(..., alias="accessToken")
    refresh_token: str = Field(..., alias="refreshToken")
    token_type: str = Field(default="bearer", alias="tokenType")
    expires_in: int = Field(..., alias="expiresIn")

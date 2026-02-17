# AUTO-GENERATED -- DO NOT EDIT
# Re-generate with: python scripts/generate_models.py

from __future__ import annotations

from pydantic import Field

from models.base_model import BaseDTO


class LoginResponse(BaseDTO):
    """Schema for authentication token response (v2)."""

    access_token: str = Field(..., min_length=1, alias="accessToken")
    refresh_token: str = Field(..., min_length=1, alias="refreshToken")
    token_type: str = Field(..., alias="tokenType")
    expires_in: int = Field(..., ge=1, alias="expiresIn")

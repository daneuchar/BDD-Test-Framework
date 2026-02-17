# AUTO-GENERATED -- DO NOT EDIT
# Re-generate with: python scripts/generate_models.py

from __future__ import annotations

from pydantic import Field

from models.base_model import BaseDTO
from .user_response import UserResponse


class UserListResponse(BaseDTO):
    """Schema for paginated list of users (v2)."""

    data: list[UserResponse]
    total: int = Field(..., ge=0)
    page: int = Field(..., ge=1)
    size: int = Field(..., ge=1)

# AUTO-GENERATED -- DO NOT EDIT
# Re-generate with: python scripts/generate_models.py

from __future__ import annotations

from typing import Any, Optional

from pydantic import Field

from models.base_model import BaseDTO


class UserResponse(BaseDTO):
    """Schema for a single user object returned by the API (v2)."""

    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=255)
    email: str
    role: str
    created_at: Optional[str] = Field(default=None, alias="createdAt")
    updated_at: Optional[str] = Field(default=None, alias="updatedAt")
    metadata: Optional[dict[str, Any]] = None
    tags: Optional[list[str]] = None

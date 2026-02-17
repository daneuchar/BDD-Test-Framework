"""User request and response DTOs."""

from __future__ import annotations

from pydantic import EmailStr, Field

from .base_model import BaseDTO


class CreateUserRequest(BaseDTO):
    """Payload for POST /users."""

    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    role: str = Field(default="user")


class UpdateUserRequest(BaseDTO):
    """Payload for PUT /users/{user_id}."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = None
    role: str | None = None


class UserResponse(BaseDTO):
    """Expected shape of a single user in API responses."""

    id: str
    name: str
    email: str
    role: str
    created_at: str | None = Field(default=None, alias="createdAt")
    updated_at: str | None = Field(default=None, alias="updatedAt")

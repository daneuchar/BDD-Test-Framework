"""User-domain event DTOs."""

from __future__ import annotations

from pydantic import EmailStr, Field

from .base_event import BaseEvent


class UserCreatedEvent(BaseEvent):
    """Event payload emitted when a user is created."""

    event_type: str = Field(default="user.created", alias="eventType")
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    role: str = Field(default="user")


class UserUpdatedEvent(BaseEvent):
    """Event payload emitted when a user is updated."""

    event_type: str = Field(default="user.updated", alias="eventType")
    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = None
    role: str | None = None

# AUTO-GENERATED -- DO NOT EDIT
# Re-generate with: python scripts/generate_models.py

from __future__ import annotations

from pydantic import Field

from models.base_model import BaseDTO


class UserCreatedEvent(BaseDTO):
    """Event payload emitted when a user is created."""

    event_id: str = Field(..., min_length=1, alias="eventId")
    event_type: str = Field(..., alias="eventType")
    timestamp: str
    version: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=255)
    email: str
    role: str

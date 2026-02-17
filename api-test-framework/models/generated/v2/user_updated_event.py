# AUTO-GENERATED -- DO NOT EDIT
# Re-generate with: python scripts/generate_models.py

from __future__ import annotations

from typing import Optional

from pydantic import Field

from models.base_model import BaseDTO


class UserUpdatedEvent(BaseDTO):
    """Event payload emitted when a user is updated (v2)."""

    event_id: str = Field(..., min_length=1, alias="eventId")
    event_type: str = Field(..., alias="eventType")
    timestamp: str
    version: str = Field(..., min_length=1)
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    email: Optional[str] = None
    role: Optional[str] = None

"""Base event DTO for all messaging events."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from pydantic import Field

from models.base_model import BaseDTO


class BaseEvent(BaseDTO):
    """Base data-transfer object for all event payloads.

    Provides common event metadata fields with sensible defaults:
        - ``event_id``:  Auto-generated UUID.
        - ``event_type``: Discriminator string set by subclasses.
        - ``timestamp``:  ISO-8601 UTC timestamp at creation time.
        - ``version``:    Schema version string.
    """

    event_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        alias="eventId",
    )
    event_type: str = Field(default="", alias="eventType")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
    )
    version: str = "1.0"

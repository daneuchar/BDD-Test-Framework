"""Fluent builder for user event models."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from models.events.user_event import UserCreatedEvent, UserUpdatedEvent


class EventBuilder:
    """Build :class:`UserCreatedEvent` or :class:`UserUpdatedEvent` using a fluent interface.

    Usage::

        event = (
            EventBuilder()
            .with_type("user.created")
            .with_user_data(name="Alice", email="alice@example.com", role="admin")
            .build()
        )
    """

    def __init__(self) -> None:
        self._event_type: str = "user.created"
        self._event_id: str = str(uuid.uuid4())
        self._timestamp: str = datetime.now(timezone.utc).isoformat()
        self._version: str = "1.0"
        self._name: str = ""
        self._email: str = ""
        self._role: str = "user"

    def with_type(self, event_type: str) -> EventBuilder:
        """Set the event type (e.g. ``'user.created'``, ``'user.updated'``)."""
        self._event_type = event_type
        return self

    def with_user_data(
        self,
        name: str,
        email: str,
        role: str = "user",
    ) -> EventBuilder:
        """Set the user-specific payload fields."""
        self._name = name
        self._email = email
        self._role = role
        return self

    def with_event_id(self, event_id: str) -> EventBuilder:
        """Override the auto-generated event ID."""
        self._event_id = event_id
        return self

    def with_timestamp(self, timestamp: str) -> EventBuilder:
        """Override the auto-generated timestamp."""
        self._timestamp = timestamp
        return self

    def with_version(self, version: str) -> EventBuilder:
        """Override the schema version."""
        self._version = version
        return self

    def with_defaults(self) -> EventBuilder:
        """Populate every field with sensible default values."""
        self._event_type = "user.created"
        self._event_id = str(uuid.uuid4())
        self._timestamp = datetime.now(timezone.utc).isoformat()
        self._version = "1.0"
        self._name = "Test User"
        self._email = "testuser@example.com"
        self._role = "user"
        return self

    def build(self) -> UserCreatedEvent | UserUpdatedEvent:
        """Build the event model based on the configured event type.

        Returns:
            :class:`UserCreatedEvent` for ``'user.created'``,
            :class:`UserUpdatedEvent` for ``'user.updated'``.
        """
        common = {
            "eventId": self._event_id,
            "eventType": self._event_type,
            "timestamp": self._timestamp,
            "version": self._version,
        }

        if self._event_type == "user.updated":
            return UserUpdatedEvent(
                **common,
                name=self._name or None,
                email=self._email or None,
                role=self._role or None,
            )

        return UserCreatedEvent(
            **common,
            name=self._name,
            email=self._email,
            role=self._role,
        )

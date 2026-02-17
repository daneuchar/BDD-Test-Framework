"""Object Mother / Factory for event test data."""

from __future__ import annotations

from models.builders.event_builder import EventBuilder
from models.generated.v1.user_created_event import UserCreatedEvent
from models.generated.v1.user_updated_event import UserUpdatedEvent

from .base_factory import BaseFactory


class EventFactory(BaseFactory):
    """Generate event model instances with randomized data."""

    def user_created(self) -> UserCreatedEvent:
        """Create a :class:`UserCreatedEvent` with random valid data."""
        result = (
            EventBuilder()
            .with_type("user.created")
            .with_user_data(
                name=self.fake.name(),
                email=self.fake.unique.email(),
                role="user",
            )
            .build()
        )
        assert isinstance(result, UserCreatedEvent)
        return result

    def user_updated(self) -> UserUpdatedEvent:
        """Create a :class:`UserUpdatedEvent` with random valid data."""
        result = (
            EventBuilder()
            .with_type("user.updated")
            .with_user_data(
                name=self.fake.name(),
                email=self.fake.unique.email(),
                role="admin",
            )
            .build()
        )
        assert isinstance(result, UserUpdatedEvent)
        return result

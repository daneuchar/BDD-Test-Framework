"""Template Method pattern for event consumers.

BaseConsumer defines the invariant consume lifecycle:
    connect -> poll -> deserialize

Subclasses override _poll() and _deserialize() to provide transport-specific consumption.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ConsumedEvent:
    """Normalized representation of a consumed event."""

    topic: str
    key: str | None = None
    body: dict[str, Any] | None = None
    raw_body: bytes = b""
    headers: dict[str, str] = field(default_factory=dict)
    partition: int | None = None
    offset: int | None = None
    timestamp_ms: float | None = None


class BaseConsumer(ABC):
    """Abstract base for all event consumers (Template Method pattern).

    Constructor Parameters:
        topics:          List of topics to subscribe to.
        group_id:        Consumer group identifier.
        timeout_seconds: Default poll timeout.
    """

    def __init__(
        self,
        topics: list[str],
        group_id: str,
        timeout_seconds: float = 30.0,
    ) -> None:
        self.topics = topics
        self.group_id = group_id
        self.timeout_seconds = timeout_seconds

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    @abstractmethod
    def connect(self) -> None:
        """Establish connection and subscribe to topics."""

    def consume_one(self, timeout: float | None = None) -> ConsumedEvent | None:
        """Poll for a single message, deserialize, and return it.

        Returns None if no message is available within the timeout.
        """
        effective_timeout = timeout if timeout is not None else self.timeout_seconds
        raw = self._poll(effective_timeout)
        if raw is None:
            return None
        return self._deserialize(raw)

    def consume_until(
        self,
        predicate: Callable[[ConsumedEvent], bool],
        timeout: float | None = None,
        max_messages: int = 100,
    ) -> ConsumedEvent | None:
        """Consume messages until predicate returns True or limits are hit.

        Returns the matching ConsumedEvent, or None if timeout/max_messages
        is reached without a match.
        """
        effective_timeout = timeout if timeout is not None else self.timeout_seconds
        deadline = time.monotonic() + effective_timeout
        consumed = 0

        while consumed < max_messages:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break

            raw = self._poll(min(remaining, 1.0))
            if raw is None:
                continue

            event = self._deserialize(raw)
            consumed += 1

            if predicate(event):
                return event

        return None

    # ------------------------------------------------------------------
    # Abstract transport hooks
    # ------------------------------------------------------------------

    @abstractmethod
    def _poll(self, timeout: float) -> Any | None:
        """Poll the transport for a single raw message."""

    @abstractmethod
    def _deserialize(self, raw: Any) -> ConsumedEvent:
        """Convert a raw transport message into a ConsumedEvent."""

    @abstractmethod
    def close(self) -> None:
        """Release transport resources."""

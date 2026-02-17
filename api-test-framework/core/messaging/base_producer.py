"""Template Method pattern for event producers.

BaseProducer defines the invariant publish lifecycle:
    prepare -> authenticate -> send -> handle result -> log

Subclasses override only _send() to provide transport-specific publishing.
"""

from __future__ import annotations

import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class EventEnvelope:
    """Immutable representation of an outgoing event."""

    topic: str
    key: str | None = None
    body: dict[str, Any] = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)
    partition_key: str | None = None
    content_type: str = "application/json"


@dataclass
class PublishResult:
    """Normalized result returned by every producer implementation."""

    success: bool
    topic: str
    partition: int | None = None
    offset: int | None = None
    elapsed_ms: float = 0.0
    error: str | None = None


# Thread-local storage so allure/logging plugins can access the most recent
# event/result pair without cross-thread contamination.
_thread_local = threading.local()


def get_last_event() -> EventEnvelope | None:
    """Return the most recent EventEnvelope on the current thread."""
    return getattr(_thread_local, "last_event", None)


def get_last_publish_result() -> PublishResult | None:
    """Return the most recent PublishResult on the current thread."""
    return getattr(_thread_local, "last_publish_result", None)


class BaseProducer(ABC):
    """Abstract base for all event producers (Template Method pattern).

    Constructor Parameters:
        default_topic: Fallback topic when EventEnvelope.topic is empty.
    """

    def __init__(self, default_topic: str | None = None) -> None:
        self.default_topic = default_topic

    # ------------------------------------------------------------------
    # Template Method — the invariant publish lifecycle
    # ------------------------------------------------------------------

    def publish(self, event: EventEnvelope) -> PublishResult:
        """Execute the full publish lifecycle.

        Steps:
            1. _prepare_event    — apply defaults, add standard headers
            2. _authenticate_event — hook for subclass auth injection
            3. _send             — abstract, implemented by subclass
            4. _handle_result    — post-send hook
            5. _log_event        — store in thread-local for plugins
        """
        event = self._prepare_event(event)
        event = self._authenticate_event(event)

        start = time.monotonic()
        result = self._send(event)
        elapsed_ms = (time.monotonic() - start) * 1000
        result = PublishResult(
            success=result.success,
            topic=result.topic,
            partition=result.partition,
            offset=result.offset,
            elapsed_ms=elapsed_ms,
            error=result.error,
        )

        result = self._handle_result(result)
        self._log_event(event, result)
        return result

    # ------------------------------------------------------------------
    # Lifecycle hooks (overridable)
    # ------------------------------------------------------------------

    def _prepare_event(self, event: EventEnvelope) -> EventEnvelope:
        """Apply default topic and add standard headers."""
        if not event.topic and self.default_topic:
            event = EventEnvelope(
                topic=self.default_topic,
                key=event.key,
                body=event.body,
                headers=dict(event.headers),
                partition_key=event.partition_key,
                content_type=event.content_type,
            )

        headers = dict(event.headers)
        headers.setdefault("timestamp", str(time.time_ns() // 1_000_000))
        headers.setdefault("content-type", event.content_type)

        return EventEnvelope(
            topic=event.topic,
            key=event.key,
            body=event.body,
            headers=headers,
            partition_key=event.partition_key,
            content_type=event.content_type,
        )

    def _authenticate_event(self, event: EventEnvelope) -> EventEnvelope:
        """Hook for subclasses to inject auth headers or tokens."""
        return event

    @abstractmethod
    def _send(self, event: EventEnvelope) -> PublishResult:
        """Transport-level send — must be implemented by subclass."""

    def _handle_result(self, result: PublishResult) -> PublishResult:
        """Post-send hook for subclasses to modify or inspect the result."""
        return result

    def _log_event(self, event: EventEnvelope, result: PublishResult) -> None:
        """Store in thread-local so allure/logging plugins can pick it up."""
        _thread_local.last_event = event
        _thread_local.last_publish_result = result

    @abstractmethod
    def close(self) -> None:
        """Release transport resources."""

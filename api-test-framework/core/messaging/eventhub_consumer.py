"""Azure Event Hub consumer implementation."""

from __future__ import annotations

import json
import threading
from typing import Any

from azure.eventhub import EventHubConsumerClient

from core.messaging.base_consumer import BaseConsumer, ConsumedEvent


class EventHubConsumer(BaseConsumer):
    """Consumer that reads events from Azure Event Hubs.

    Constructor Parameters:
        connection_string: Event Hub namespace connection string.
        eventhub_name:     Name of the specific Event Hub.
        consumer_group:    Consumer group name (e.g. "$Default").
        topics:            Ignored for Event Hubs (present for interface compat).
        timeout_seconds:   Default poll timeout.
    """

    def __init__(
        self,
        connection_string: str,
        eventhub_name: str,
        consumer_group: str,
        topics: list[str] | None = None,
        timeout_seconds: float = 30.0,
    ) -> None:
        super().__init__(
            topics=topics or [eventhub_name],
            group_id=consumer_group,
            timeout_seconds=timeout_seconds,
        )
        self._connection_string = connection_string
        self._eventhub_name = eventhub_name
        self._consumer_group = consumer_group
        self._client: EventHubConsumerClient | None = None
        self._lock = threading.Lock()
        self._buffer: list[Any] = []
        self._buffer_lock = threading.Lock()

    def connect(self) -> None:
        """Create the EventHubConsumerClient."""
        with self._lock:
            if self._client is None:
                self._client = EventHubConsumerClient.from_connection_string(
                    conn_str=self._connection_string,
                    consumer_group=self._consumer_group,
                    eventhub_name=self._eventhub_name,
                )

    def _poll(self, timeout: float) -> Any | None:
        """Receive a batch and return the first event, buffering the rest."""
        with self._buffer_lock:
            if self._buffer:
                return self._buffer.pop(0)

        if self._client is None:
            return None

        received: list[Any] = []

        def on_event(partition_context: Any, event: Any) -> None:
            if event is not None:
                received.append(event)

        try:
            self._client.receive_batch(
                on_event_batch=lambda ctx, events: received.extend(events or []),
                max_wait_time=timeout,
                max_batch_size=10,
                starting_position="-1",
            )
        except Exception:
            return None

        if not received:
            return None

        with self._buffer_lock:
            self._buffer.extend(received[1:])

        return received[0]

    def _deserialize(self, raw: Any) -> ConsumedEvent:
        """Convert an EventData object into a ConsumedEvent."""
        raw_body = raw.body_as_str(encoding="UTF-8") if raw else ""
        try:
            body = json.loads(raw_body)
        except (json.JSONDecodeError, TypeError):
            body = None

        headers: dict[str, str] = {}
        if hasattr(raw, "properties") and raw.properties:
            headers = {str(k): str(v) for k, v in raw.properties.items()}

        timestamp_ms: float | None = None
        if hasattr(raw, "enqueued_time") and raw.enqueued_time is not None:
            timestamp_ms = raw.enqueued_time.timestamp() * 1000

        return ConsumedEvent(
            topic=self._eventhub_name,
            key=None,
            body=body,
            raw_body=raw_body.encode("utf-8") if isinstance(raw_body, str) else b"",
            headers=headers,
            partition=None,
            offset=int(raw.offset) if hasattr(raw, "offset") and raw.offset is not None else None,
            timestamp_ms=timestamp_ms,
        )

    def close(self) -> None:
        """Close the underlying Event Hub consumer client."""
        with self._lock:
            if self._client is not None:
                self._client.close()
                self._client = None

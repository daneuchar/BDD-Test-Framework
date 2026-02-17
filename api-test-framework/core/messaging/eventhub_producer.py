"""Azure Event Hub producer implementation."""

from __future__ import annotations

import json
import threading
from typing import Any

from azure.eventhub import EventData, EventHubProducerClient

from core.messaging.base_producer import BaseProducer, EventEnvelope, PublishResult


class EventHubProducer(BaseProducer):
    """Producer that publishes events to Azure Event Hubs.

    Constructor Parameters:
        connection_string: Event Hub namespace connection string.
        eventhub_name:     Name of the specific Event Hub.
        default_topic:     Fallback topic (used as eventhub_name override).
    """

    def __init__(
        self,
        connection_string: str,
        eventhub_name: str,
        default_topic: str | None = None,
    ) -> None:
        super().__init__(default_topic=default_topic)
        self._connection_string = connection_string
        self._eventhub_name = eventhub_name
        self._client: EventHubProducerClient | None = None
        self._lock = threading.Lock()

    @property
    def client(self) -> EventHubProducerClient:
        """Lazy-initialized, thread-safe client creation."""
        if self._client is None:
            with self._lock:
                if self._client is None:
                    self._client = EventHubProducerClient.from_connection_string(
                        conn_str=self._connection_string,
                        eventhub_name=self._eventhub_name,
                    )
        return self._client

    def _send(self, event: EventEnvelope) -> PublishResult:
        """Send an event to Azure Event Hubs via a batch."""
        try:
            event_data = EventData(json.dumps(event.body))

            for header_key, header_value in event.headers.items():
                event_data.properties[header_key] = header_value

            batch = self.client.create_batch(
                partition_key=event.partition_key,
            )
            batch.add(event_data)
            self.client.send_batch(batch)

            return PublishResult(
                success=True,
                topic=event.topic or self._eventhub_name,
            )
        except Exception as exc:
            return PublishResult(
                success=False,
                topic=event.topic or self._eventhub_name,
                error=str(exc),
            )

    def close(self) -> None:
        """Close the underlying Event Hub client."""
        with self._lock:
            if self._client is not None:
                self._client.close()
                self._client = None

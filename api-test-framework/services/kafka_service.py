"""Service object for Apache Kafka publish/consume operations."""

from __future__ import annotations

from typing import Any

import allure

from core.messaging.base_consumer import BaseConsumer, ConsumedEvent
from core.messaging.base_producer import BaseProducer, EventEnvelope, PublishResult


class KafkaService:
    """High-level facade for publishing and consuming Kafka events.

    Accepts a :class:`BaseProducer` and optional :class:`BaseConsumer` via
    constructor injection, following the same DI pattern as :class:`BaseService`.
    """

    def __init__(
        self,
        producer: BaseProducer,
        consumer: BaseConsumer | None = None,
    ) -> None:
        self.producer = producer
        self.consumer = consumer

    @allure.step("Publish event to Kafka topic '{topic}'")
    def publish(
        self,
        topic: str,
        body: dict[str, Any],
        key: str | None = None,
    ) -> PublishResult:
        """Publish a single event to the given Kafka topic.

        Args:
            topic: Target Kafka topic.
            body:  Event payload as a dictionary.
            key:   Optional message key.

        Returns:
            :class:`PublishResult` with delivery metadata.
        """
        envelope = EventEnvelope(topic=topic, body=body, key=key)
        return self.producer.publish(envelope)

    @allure.step("Publish and consume event on Kafka topic '{topic}'")
    def publish_and_consume(
        self,
        topic: str,
        body: dict[str, Any],
        key: str | None = None,
        timeout: float = 30,
    ) -> tuple[PublishResult, ConsumedEvent | None]:
        """Publish an event and then consume the first matching event.

        Args:
            topic:   Target Kafka topic.
            body:    Event payload as a dictionary.
            key:     Optional message key.
            timeout: Maximum seconds to wait for a consumed event.

        Returns:
            A tuple of (:class:`PublishResult`, :class:`ConsumedEvent` | None).
        """
        result = self.publish(topic, body, key)

        consumed: ConsumedEvent | None = None
        if self.consumer is not None and result.success:
            self.consumer.connect()
            consumed = self.consumer.consume_until(
                predicate=lambda evt: evt.body == body,
                timeout=timeout,
            )

        return result, consumed

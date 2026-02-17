"""Messaging fixtures -- producer, consumer, and service injection."""

from __future__ import annotations

from uuid import uuid4

import pytest

from config.settings import settings
from core.messaging.eventhub_consumer import EventHubConsumer
from core.messaging.eventhub_producer import EventHubProducer
from core.messaging.kafka_consumer import KafkaConsumer
from core.messaging.kafka_producer import KafkaProducer
from services.eventhub_service import EventHubService
from services.kafka_service import KafkaService


# ---------------------------------------------------------------------------
# Producers (session-scoped, shared across all tests in one worker)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def eventhub_producer() -> EventHubProducer:
    """Session-scoped Event Hub producer. Skips if not configured."""
    if not settings.eventhub_connection_string:
        pytest.skip("Event Hub connection string not configured")
    producer = EventHubProducer(
        connection_string=settings.eventhub_connection_string,
        eventhub_name=settings.eventhub_name,
    )
    yield producer
    producer.close()


@pytest.fixture(scope="session")
def kafka_producer() -> KafkaProducer:
    """Session-scoped Kafka producer. Skips if not configured."""
    if not settings.kafka_bootstrap_servers:
        pytest.skip("Kafka bootstrap servers not configured")
    producer = KafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        username=settings.kafka_username,
        password=settings.kafka_password,
    )
    yield producer
    producer.close()


# ---------------------------------------------------------------------------
# Consumers (function-scoped, worker-isolated)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="function")
def eventhub_consumer(worker_id: str) -> EventHubConsumer:
    """Function-scoped Event Hub consumer with worker-isolated consumer group."""
    if not settings.eventhub_connection_string:
        pytest.skip("Event Hub connection string not configured")
    consumer = EventHubConsumer(
        connection_string=settings.eventhub_connection_string,
        eventhub_name=settings.eventhub_name,
        consumer_group=f"test-{worker_id}",
    )
    yield consumer
    consumer.close()


@pytest.fixture(scope="function")
def kafka_consumer(worker_id: str) -> KafkaConsumer:
    """Function-scoped Kafka consumer with worker-isolated topic and group."""
    if not settings.kafka_bootstrap_servers:
        pytest.skip("Kafka bootstrap servers not configured")
    topic = f"{settings.kafka_topic_prefix}-{worker_id}"
    group_id = f"test-group-{worker_id}-{uuid4().hex[:8]}"
    consumer = KafkaConsumer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        username=settings.kafka_username,
        password=settings.kafka_password,
        topics=[topic],
        group_id=group_id,
    )
    yield consumer
    consumer.close()


# ---------------------------------------------------------------------------
# Services -- publish-only (no consumer)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="function")
def eventhub_service(eventhub_producer: EventHubProducer) -> EventHubService:
    """Function-scoped EventHubService for publish-only tests."""
    return EventHubService(producer=eventhub_producer, consumer=None)


@pytest.fixture(scope="function")
def kafka_service(kafka_producer: KafkaProducer) -> KafkaService:
    """Function-scoped KafkaService for publish-only tests."""
    return KafkaService(producer=kafka_producer, consumer=None)


# ---------------------------------------------------------------------------
# Services -- round-trip (producer + consumer)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="function")
def eventhub_roundtrip_service(
    eventhub_producer: EventHubProducer,
    eventhub_consumer: EventHubConsumer,
) -> EventHubService:
    """Function-scoped EventHubService with consumer for round-trip tests."""
    return EventHubService(producer=eventhub_producer, consumer=eventhub_consumer)


@pytest.fixture(scope="function")
def kafka_roundtrip_service(
    kafka_producer: KafkaProducer,
    kafka_consumer: KafkaConsumer,
) -> KafkaService:
    """Function-scoped KafkaService with consumer for round-trip tests."""
    return KafkaService(producer=kafka_producer, consumer=kafka_consumer)

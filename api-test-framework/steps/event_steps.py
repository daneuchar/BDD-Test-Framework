"""Event feature step definitions -- thin glue delegating to services and assertions."""

from __future__ import annotations

from pytest_bdd import given, parsers, then, when

from assertions.messaging_assertions import MessagingAssertions
from data.factories import EventFactory
from models.generated.v1.user_created_event import UserCreatedEvent
from services.eventhub_service import EventHubService
from services.kafka_service import KafkaService


@given("a valid user created event payload", target_fixture="event_payload")
def valid_user_created_event(event_factory: EventFactory) -> UserCreatedEvent:
    """Build a valid user-created event payload via the factory."""
    return event_factory.user_created()


@when("I publish the event to Event Hub", target_fixture="publish_result")
def publish_to_eventhub(eventhub_service: EventHubService, event_payload: UserCreatedEvent):
    """Publish the event payload to Azure Event Hub."""
    return eventhub_service.publish(topic="", body=event_payload.model_dump(by_alias=True))


@when("I publish the event to Kafka", target_fixture="publish_result")
def publish_to_kafka(kafka_service: KafkaService, event_payload: UserCreatedEvent):
    """Publish the event payload to Apache Kafka."""
    return kafka_service.publish(topic="", body=event_payload.model_dump(by_alias=True))


@when("I publish and consume the event via Event Hub", target_fixture="round_trip")
def roundtrip_eventhub(eventhub_roundtrip_service: EventHubService, event_payload: UserCreatedEvent):
    """Publish and consume the event via Event Hub round-trip."""
    return eventhub_roundtrip_service.publish_and_consume(topic="", body=event_payload.model_dump(by_alias=True))


@when("I publish and consume the event via Kafka", target_fixture="round_trip")
def roundtrip_kafka(kafka_roundtrip_service: KafkaService, event_payload: UserCreatedEvent):
    """Publish and consume the event via Kafka round-trip."""
    return kafka_roundtrip_service.publish_and_consume(topic="", body=event_payload.model_dump(by_alias=True))


@then("the event should be published successfully")
def assert_published(publish_result):
    """Assert the event was published without errors."""
    MessagingAssertions(publish_result).published_successfully()


@then(parsers.parse("the event should be delivered within {max_ms:d}ms"))
def assert_delivered_within(publish_result, max_ms: int):
    """Assert the event was delivered within the time limit."""
    MessagingAssertions(publish_result).delivered_within(max_ms)


@then("the event should be received by the consumer")
def assert_event_received(round_trip):
    """Assert the consumed event was received (not None)."""
    publish_result, consumed_event = round_trip
    MessagingAssertions(publish_result, consumed_event).event_received()


@then("the consumed event body should match the published payload")
def assert_body_matches(round_trip, event_payload: UserCreatedEvent):
    """Assert the consumed event body matches the original payload."""
    publish_result, consumed_event = round_trip
    MessagingAssertions(publish_result, consumed_event).event_body_matches(event_payload.model_dump(by_alias=True))

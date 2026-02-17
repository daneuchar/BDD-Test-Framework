"""Facade pattern -- unified fluent assertion API for messaging results.

Usage::

    MessagingAssertions(publish_result, consumed_event) \\
        .published_successfully() \\
        .on_topic("user-events") \\
        .delivered_within(500) \\
        .event_received() \\
        .event_body_matches(expected_body) \\
        .event_body_contains("name", "Alice")
"""

from __future__ import annotations

from typing import Any

import allure

from core.messaging.base_consumer import ConsumedEvent
from core.messaging.base_producer import PublishResult


class MessagingAssertions:
    """Fluent assertion wrapper for messaging publish/consume results.

    Every assertion method returns ``self`` so calls can be chained.
    Each assertion is wrapped in an ``allure.step`` for rich reporting.
    """

    def __init__(
        self,
        publish_result: PublishResult,
        consumed_event: ConsumedEvent | None = None,
    ) -> None:
        self.publish_result = publish_result
        self.consumed_event = consumed_event

    @allure.step("Assert event published successfully")
    def published_successfully(self) -> MessagingAssertions:
        """Assert the publish operation succeeded."""
        assert self.publish_result.success, (
            f"Publish failed: {self.publish_result.error}"
        )
        return self

    @allure.step("Assert event delivered within {max_ms}ms")
    def delivered_within(self, max_ms: float) -> MessagingAssertions:
        """Assert the publish operation completed within *max_ms* milliseconds."""
        assert self.publish_result.elapsed_ms <= max_ms, (
            f"Publish took {self.publish_result.elapsed_ms:.1f}ms, "
            f"expected <= {max_ms}ms"
        )
        return self

    @allure.step("Assert event was received by consumer")
    def event_received(self) -> MessagingAssertions:
        """Assert that a consumed event was received (not None)."""
        assert self.consumed_event is not None, (
            "Expected a consumed event but none was received"
        )
        return self

    @allure.step("Assert event body matches expected payload")
    def event_body_matches(self, expected: dict[str, Any]) -> MessagingAssertions:
        """Assert the consumed event body equals *expected* exactly."""
        assert self.consumed_event is not None, (
            "Cannot assert body: no consumed event received"
        )
        assert self.consumed_event.body == expected, (
            f"Event body mismatch:\n"
            f"  expected: {expected!r}\n"
            f"  actual:   {self.consumed_event.body!r}"
        )
        return self

    @allure.step("Assert event body contains '{key}'")
    def event_body_contains(self, key: str, value: Any = None) -> MessagingAssertions:
        """Assert the consumed event body contains *key*, optionally with *value*."""
        assert self.consumed_event is not None, (
            "Cannot assert body: no consumed event received"
        )
        assert isinstance(self.consumed_event.body, dict), (
            f"Event body is not a dict: {type(self.consumed_event.body).__name__}"
        )
        assert key in self.consumed_event.body, (
            f"Key '{key}' not found in event body"
        )
        if value is not None:
            actual = self.consumed_event.body[key]
            assert actual == value, (
                f"body['{key}'] expected {value!r}, got {actual!r}"
            )
        return self

    @allure.step("Assert event published on topic '{topic}'")
    def on_topic(self, topic: str) -> MessagingAssertions:
        """Assert the event was published to the expected topic."""
        assert self.publish_result.topic == topic, (
            f"Expected topic '{topic}', got '{self.publish_result.topic}'"
        )
        return self

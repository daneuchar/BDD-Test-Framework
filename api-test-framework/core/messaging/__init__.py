"""Core messaging abstractions and transport implementations.

Public API:
    EventEnvelope, PublishResult   — producer data classes
    ConsumedEvent                  — consumer data class
    BaseProducer, BaseConsumer     — abstract base classes (Template Method)
    get_last_event, get_last_publish_result — thread-local accessors
"""

from core.messaging.base_consumer import BaseConsumer, ConsumedEvent
from core.messaging.base_producer import (
    BaseProducer,
    EventEnvelope,
    PublishResult,
    get_last_event,
    get_last_publish_result,
)

__all__ = [
    "EventEnvelope",
    "PublishResult",
    "ConsumedEvent",
    "BaseProducer",
    "BaseConsumer",
    "get_last_event",
    "get_last_publish_result",
]

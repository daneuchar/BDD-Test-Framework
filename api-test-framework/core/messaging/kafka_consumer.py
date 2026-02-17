"""Kafka consumer implementation using confluent-kafka."""

from __future__ import annotations

import json
import threading
from typing import Any

from confluent_kafka import Consumer

from core.messaging.base_consumer import BaseConsumer, ConsumedEvent


class KafkaConsumer(BaseConsumer):
    """Consumer that reads events from Apache Kafka via confluent-kafka.

    Constructor Parameters:
        bootstrap_servers: Kafka broker addresses (comma-separated).
        username:          SASL username.
        password:          SASL password.
        topics:            List of topics to subscribe to.
        group_id:          Consumer group identifier.
        timeout_seconds:   Default poll timeout.
        extra_config:      Additional confluent-kafka consumer config overrides.
    """

    def __init__(
        self,
        bootstrap_servers: str,
        username: str,
        password: str,
        topics: list[str],
        group_id: str,
        timeout_seconds: float = 30.0,
        extra_config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            topics=topics,
            group_id=group_id,
            timeout_seconds=timeout_seconds,
        )
        self._bootstrap_servers = bootstrap_servers
        self._username = username
        self._password = password
        self._extra_config = extra_config or {}
        self._consumer: Consumer | None = None
        self._lock = threading.Lock()

    def connect(self) -> None:
        """Create the Kafka consumer and subscribe to topics."""
        with self._lock:
            if self._consumer is not None:
                return

            config: dict[str, Any] = {
                "bootstrap.servers": self._bootstrap_servers,
                "security.protocol": "SASL_SSL",
                "sasl.mechanism": "PLAIN",
                "sasl.username": self._username,
                "sasl.password": self._password,
                "group.id": self.group_id,
                "auto.offset.reset": "latest",
            }
            config.update(self._extra_config)

            self._consumer = Consumer(config)
            self._consumer.subscribe(self.topics)

    def _poll(self, timeout: float) -> Any | None:
        """Poll Kafka for a single message."""
        if self._consumer is None:
            return None

        msg = self._consumer.poll(timeout=timeout)
        if msg is None:
            return None
        if msg.error():
            return None

        return msg

    def _deserialize(self, raw: Any) -> ConsumedEvent:
        """Convert a confluent_kafka.Message into a ConsumedEvent."""
        raw_value = raw.value() or b""

        try:
            body = json.loads(raw_value)
        except (json.JSONDecodeError, TypeError):
            body = None

        headers: dict[str, str] = {}
        if raw.headers():
            for header_key, header_value in raw.headers():
                headers[header_key] = (
                    header_value.decode("utf-8") if isinstance(header_value, bytes) else str(header_value)
                )

        key_raw = raw.key()
        key: str | None = None
        if key_raw is not None:
            key = key_raw.decode("utf-8") if isinstance(key_raw, bytes) else str(key_raw)

        timestamp_type, timestamp_val = raw.timestamp()
        timestamp_ms = float(timestamp_val) if timestamp_type != 0 else None

        return ConsumedEvent(
            topic=raw.topic(),
            key=key,
            body=body,
            raw_body=raw_value if isinstance(raw_value, bytes) else raw_value.encode("utf-8"),
            headers=headers,
            partition=raw.partition(),
            offset=raw.offset(),
            timestamp_ms=timestamp_ms,
        )

    def close(self) -> None:
        """Close the underlying Kafka consumer."""
        with self._lock:
            if self._consumer is not None:
                self._consumer.close()
                self._consumer = None

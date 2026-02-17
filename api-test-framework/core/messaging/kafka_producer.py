"""Kafka producer implementation using confluent-kafka."""

from __future__ import annotations

import json
import threading
from typing import Any

from confluent_kafka import Producer

from core.messaging.base_producer import BaseProducer, EventEnvelope, PublishResult


class KafkaProducer(BaseProducer):
    """Producer that publishes events to Apache Kafka via confluent-kafka.

    Constructor Parameters:
        bootstrap_servers: Kafka broker addresses (comma-separated).
        username:          SASL username.
        password:          SASL password.
        default_topic:     Fallback topic when EventEnvelope.topic is empty.
        extra_config:      Additional confluent-kafka producer config overrides.
    """

    def __init__(
        self,
        bootstrap_servers: str,
        username: str,
        password: str,
        default_topic: str | None = None,
        extra_config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(default_topic=default_topic)
        config: dict[str, Any] = {
            "bootstrap.servers": bootstrap_servers,
            "security.protocol": "SASL_SSL",
            "sasl.mechanism": "PLAIN",
            "sasl.username": username,
            "sasl.password": password,
        }
        if extra_config:
            config.update(extra_config)

        self._producer = Producer(config)
        self._lock = threading.Lock()

    def _send(self, event: EventEnvelope) -> PublishResult:
        """Produce a message to Kafka and flush."""
        result_holder: dict[str, Any] = {}

        def on_delivery(err: Any, msg: Any) -> None:
            if err is not None:
                result_holder["error"] = str(err)
            else:
                result_holder["partition"] = msg.partition()
                result_holder["offset"] = msg.offset()

        try:
            headers_list = [(k, v.encode("utf-8")) for k, v in event.headers.items()]

            self._producer.produce(
                topic=event.topic,
                key=event.key.encode("utf-8") if event.key else None,
                value=json.dumps(event.body).encode("utf-8"),
                headers=headers_list,
                on_delivery=on_delivery,
            )
            self._producer.flush(timeout=10)

            if "error" in result_holder:
                return PublishResult(
                    success=False,
                    topic=event.topic,
                    error=result_holder["error"],
                )

            return PublishResult(
                success=True,
                topic=event.topic,
                partition=result_holder.get("partition"),
                offset=result_holder.get("offset"),
            )
        except Exception as exc:
            return PublishResult(
                success=False,
                topic=event.topic,
                error=str(exc),
            )

    def close(self) -> None:
        """Flush remaining messages and release resources."""
        with self._lock:
            self._producer.flush(timeout=5)

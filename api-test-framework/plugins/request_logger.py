"""Structured JSON logging plugin for HTTP requests.

Logs each request/response cycle as a JSON object to the ``api_requests`` logger.

Registered via pytest.ini: ``-p plugins.request_logger``
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any

import pytest

logger = logging.getLogger("api_requests")


def pytest_configure(config: pytest.Config) -> None:
    """Set up the structured JSON logger for API requests."""
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(_JsonFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)


class _JsonFormatter(logging.Formatter):
    """Format log records as single-line JSON."""

    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, Any] = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "request_data"):
            log_data["request"] = record.request_data
        if hasattr(record, "response_data"):
            log_data["response"] = record.response_data
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        return json.dumps(log_data, default=str)


def log_request(
    method: str,
    url: str,
    headers: dict[str, str] | None = None,
    body: Any = None,
) -> float:
    """Log an outgoing request and return the start time."""
    record = logger.makeRecord(
        name=logger.name,
        level=logging.DEBUG,
        fn="",
        lno=0,
        msg=f"{method} {url}",
        args=(),
        exc_info=None,
    )
    record.request_data = {  # type: ignore[attr-defined]
        "method": method,
        "url": url,
        "headers": headers or {},
        "body": body,
    }
    logger.handle(record)
    return time.monotonic()


def log_response(
    status_code: int,
    url: str,
    body: Any = None,
    start_time: float | None = None,
) -> None:
    """Log an incoming response."""
    duration_ms = (
        round((time.monotonic() - start_time) * 1000, 2) if start_time else None
    )
    record = logger.makeRecord(
        name=logger.name,
        level=logging.DEBUG,
        fn="",
        lno=0,
        msg=f"Response {status_code} from {url}",
        args=(),
        exc_info=None,
    )
    record.response_data = {  # type: ignore[attr-defined]
        "status_code": status_code,
        "url": url,
        "body": body,
    }
    if duration_ms is not None:
        record.duration_ms = duration_ms  # type: ignore[attr-defined]
    logger.handle(record)

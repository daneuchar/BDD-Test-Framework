"""Chain of Responsibility for response processing.

Each handler inspects/transforms the APIResponse and optionally
forwards to the next handler in the chain.
"""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from core.client.base_client import APIResponse

logger = logging.getLogger(__name__)


class ResponseHandler(ABC):
    """Base handler in the chain."""

    def __init__(self) -> None:
        self._next: ResponseHandler | None = None

    def set_next(self, handler: ResponseHandler) -> ResponseHandler:
        """Set the next handler and return it (for fluent chaining)."""
        self._next = handler
        return handler

    def handle(self, response: APIResponse) -> APIResponse:
        """Process *response* and delegate to next handler if present."""
        result = self._process(response)
        if self._next is not None:
            return self._next.handle(result)
        return result

    @abstractmethod
    def _process(self, response: APIResponse) -> APIResponse:
        """Subclass-specific processing logic."""


class StatusCheckHandler(ResponseHandler):
    """Raises for unexpected status codes (>= 500 by default)."""

    def __init__(self, raise_for_statuses: tuple[int, ...] | None = None) -> None:
        super().__init__()
        self.raise_for_statuses = raise_for_statuses

    def _process(self, response: APIResponse) -> APIResponse:
        if self.raise_for_statuses and response.status_code in self.raise_for_statuses:
            raise HTTPStatusError(
                f"Unexpected status {response.status_code}", response=response
            )
        return response


class SchemaValidationHandler(ResponseHandler):
    """Validates the response body against a JSON schema (if configured)."""

    def __init__(self, schema: dict[str, Any] | None = None) -> None:
        super().__init__()
        self.schema = schema

    def _process(self, response: APIResponse) -> APIResponse:
        if self.schema is not None and response.json_data is not None:
            import jsonschema

            jsonschema.validate(instance=response.json_data, schema=self.schema)
        return response


class LoggingHandler(ResponseHandler):
    """Logs request/response details at DEBUG level."""

    def _process(self, response: APIResponse) -> APIResponse:
        logger.debug(
            "Response %s — %s bytes — %.1f ms",
            response.status_code,
            len(json.dumps(response.json_data)) if response.json_data else 0,
            response.elapsed_ms,
        )
        return response


class AllureAttachmentHandler(ResponseHandler):
    """Attaches response body to the Allure report (if allure is available)."""

    def _process(self, response: APIResponse) -> APIResponse:
        try:
            import allure

            if response.json_data is not None:
                allure.attach(
                    json.dumps(response.json_data, indent=2),
                    name="Response Body",
                    attachment_type=allure.attachment_type.JSON,
                )
        except ImportError:
            pass
        return response


class HTTPStatusError(Exception):
    """Raised when the response has an unexpected HTTP status."""

    def __init__(self, message: str, response: APIResponse) -> None:
        super().__init__(message)
        self.response = response


def build_default_chain() -> ResponseHandler:
    """Build the default handler chain: status -> logging -> allure."""
    status = StatusCheckHandler()
    logging_h = LoggingHandler()
    allure_h = AllureAttachmentHandler()

    status.set_next(logging_h).set_next(allure_h)
    return status

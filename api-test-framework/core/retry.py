"""Decorator pattern for configurable retry with exponential backoff.

Works transparently with both synchronous and asynchronous functions.

Usage::

    @retry(max_attempts=3, backoff_factor=2, retryable_statuses=[500, 502, 503])
    def create_user(client, payload):
        return client.post("/users", json=payload)
"""

from __future__ import annotations

import asyncio
import functools
import logging
import time
from typing import Any, Callable

from core.client.base_client import APIResponse

logger = logging.getLogger(__name__)

_DEFAULT_RETRYABLE = (500, 502, 503, 504)


def retry(
    max_attempts: int = 3,
    backoff_factor: float = 2.0,
    retryable_statuses: tuple[int, ...] | list[int] = _DEFAULT_RETRYABLE,
    retryable_exceptions: tuple[type[Exception], ...] = (ConnectionError, TimeoutError),
) -> Callable[..., Any]:
    """Retry decorator with exponential backoff.

    Parameters:
        max_attempts:        Total number of attempts (including the first).
        backoff_factor:      Multiplier for successive wait times.
        retryable_statuses:  HTTP status codes that trigger a retry.
        retryable_exceptions: Exception types that trigger a retry.
    """
    retryable = tuple(retryable_statuses)

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                last_exc: Exception | None = None
                for attempt in range(1, max_attempts + 1):
                    try:
                        result = await func(*args, **kwargs)
                        if (
                            isinstance(result, APIResponse)
                            and result.status_code in retryable
                            and attempt < max_attempts
                        ):
                            wait = backoff_factor ** (attempt - 1)
                            logger.warning(
                                "Retry %d/%d — status %s — waiting %.1fs",
                                attempt,
                                max_attempts,
                                result.status_code,
                                wait,
                            )
                            await asyncio.sleep(wait)
                            continue
                        return result
                    except retryable_exceptions as exc:
                        last_exc = exc
                        if attempt < max_attempts:
                            wait = backoff_factor ** (attempt - 1)
                            logger.warning(
                                "Retry %d/%d — %s — waiting %.1fs",
                                attempt,
                                max_attempts,
                                exc,
                                wait,
                            )
                            await asyncio.sleep(wait)
                        else:
                            raise
                raise last_exc  # type: ignore[misc]

            return async_wrapper

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exc: Exception | None = None
            for attempt in range(1, max_attempts + 1):
                try:
                    result = func(*args, **kwargs)
                    if (
                        isinstance(result, APIResponse)
                        and result.status_code in retryable
                        and attempt < max_attempts
                    ):
                        wait = backoff_factor ** (attempt - 1)
                        logger.warning(
                            "Retry %d/%d — status %s — waiting %.1fs",
                            attempt,
                            max_attempts,
                            result.status_code,
                            wait,
                        )
                        time.sleep(wait)
                        continue
                    return result
                except retryable_exceptions as exc:
                    last_exc = exc
                    if attempt < max_attempts:
                        wait = backoff_factor ** (attempt - 1)
                        logger.warning(
                            "Retry %d/%d — %s — waiting %.1fs",
                            attempt,
                            max_attempts,
                            exc,
                            wait,
                        )
                        time.sleep(wait)
                    else:
                        raise
            raise last_exc  # type: ignore[misc]

        return sync_wrapper

    return decorator

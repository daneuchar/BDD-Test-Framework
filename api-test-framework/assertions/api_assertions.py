"""Facade pattern — unified fluent assertion API for API responses.

Usage::

    ApiAssertions(response) \\
        .status(201) \\
        .schema("user_response") \\
        .response_time(500) \\
        .header("Content-Type", "application/json") \\
        .json_path("$.data.id", expected_id)
"""

from __future__ import annotations

from typing import Any

import allure

from core.client.base_client import APIResponse
from models.generated import ModelNotFoundError, resolve_model
from validators.pydantic_validator import PydanticValidator
from validators.schema_validator import SchemaValidator


class ApiAssertions:
    """Fluent assertion wrapper around :class:`APIResponse`.

    Every assertion method returns ``self`` so calls can be chained.
    Each assertion is wrapped in an ``allure.step`` for rich reporting.
    """

    def __init__(self, response: APIResponse, version: str | None = None) -> None:
        self.response = response
        self.version = version

    def status(self, expected: int) -> ApiAssertions:
        """Assert the HTTP status code equals *expected*."""
        with allure.step(f"Assert status code is {expected}"):
            assert self.response.status_code == expected, (
                f"Expected status {expected}, got {self.response.status_code}"
            )
        return self

    def schema(self, schema_name: str) -> ApiAssertions:
        """Assert the response body matches the schema *schema_name*.

        Uses generated Pydantic models as the primary validation path.
        Falls back to JSON schema validation if no generated model is
        registered for the given schema name (migration safety net).
        """
        with allure.step(f"Assert response matches schema '{schema_name}'"):
            try:
                model_cls = resolve_model(schema_name, version=self.version)
                validator = PydanticValidator(model=model_cls)
            except ModelNotFoundError:
                validator = SchemaValidator(schema_name=schema_name, version=self.version)
            result = validator.validate(self.response)
            assert result.is_valid, (
                f"Schema validation failed: {'; '.join(result.errors)}"
            )
        return self

    def response_time(self, max_ms: int) -> ApiAssertions:
        """Assert the response was received within *max_ms* milliseconds."""
        with allure.step(f"Assert response time < {max_ms}ms"):
            assert self.response.elapsed_ms <= max_ms, (
                f"Response took {self.response.elapsed_ms:.1f}ms, "
                f"expected <= {max_ms}ms"
            )
        return self

    def header(self, name: str, value: str | None = None) -> ApiAssertions:
        """Assert that response header *name* exists and optionally equals *value*."""
        with allure.step(f"Assert header '{name}'" + (f" == '{value}'" if value else "")):
            actual = self.response.headers.get(name)
            assert actual is not None, f"Header '{name}' not found in response"
            if value is not None:
                assert actual == value, (
                    f"Header '{name}' expected '{value}', got '{actual}'"
                )
        return self

    def json_path(self, path: str, expected: Any) -> ApiAssertions:
        """Assert that the value at *path* equals *expected*.

        Supports dot-notation paths like ``"data.id"`` or ``"data.items[0].name"``.
        A leading ``$.`` prefix is stripped for convenience.
        """
        with allure.step(f"Assert json_path '{path}' == {expected!r}"):
            actual = self._resolve_path(path)
            assert actual == expected, (
                f"json_path '{path}': expected {expected!r}, got {actual!r}"
            )
        return self

    def json_path_exists(self, path: str) -> ApiAssertions:
        """Assert that *path* exists in the response JSON."""
        with allure.step(f"Assert json_path '{path}' exists"):
            self._resolve_path(path)  # raises if missing
        return self

    def body_contains(self, key: str, value: Any = None) -> ApiAssertions:
        """Assert top-level JSON body contains *key*, optionally with *value*."""
        with allure.step(f"Assert body contains '{key}'"):
            assert isinstance(self.response.json_data, dict), "Response body is not a JSON object"
            assert key in self.response.json_data, f"Key '{key}' not in response body"
            if value is not None:
                actual = self.response.json_data[key]
                assert actual == value, (
                    f"body['{key}'] expected {value!r}, got {actual!r}"
                )
        return self

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _resolve_path(self, path: str) -> Any:
        """Walk a dot-notation path through the JSON response data."""
        # Strip optional JSONPath root prefix
        if path.startswith("$."):
            path = path[2:]

        current: Any = self.response.json_data
        for segment in self._tokenize_path(path):
            if isinstance(segment, int):
                if not isinstance(current, list) or segment >= len(current):
                    raise AssertionError(
                        f"Cannot index into {type(current).__name__} with [{segment}]"
                    )
                current = current[segment]
            else:
                if not isinstance(current, dict) or segment not in current:
                    raise AssertionError(
                        f"Key '{segment}' not found at this level"
                    )
                current = current[segment]
        return current

    @staticmethod
    def _tokenize_path(path: str) -> list[str | int]:
        """Split ``"data.items[0].name"`` into ``["data", "items", 0, "name"]``."""
        tokens: list[str | int] = []
        for part in path.split("."):
            if "[" in part:
                key, rest = part.split("[", 1)
                if key:
                    tokens.append(key)
                idx = rest.rstrip("]")
                tokens.append(int(idx))
            else:
                tokens.append(part)
        return tokens

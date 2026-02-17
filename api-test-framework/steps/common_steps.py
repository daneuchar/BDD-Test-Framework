"""Shared BDD step definitions used across all feature files."""

from __future__ import annotations

from pytest_bdd import given, then

from assertions.api_assertions import ApiAssertions
from config.endpoints import Endpoints
from core.client.base_client import APIResponse
from core.client.sync_client import SyncAPIClient


@given("the API is available")
def health_check(api_client: SyncAPIClient) -> None:
    """Verify the API is reachable via the health endpoint."""
    response = api_client.get(Endpoints.HEALTH.value)
    ApiAssertions(response).status(200)


@then("the response status code should be {status_code:d}")
def assert_status_code(api_response: APIResponse, status_code: int) -> None:
    """Assert the response has the expected HTTP status code."""
    ApiAssertions(api_response).status(status_code)


@then("the response should match the {schema_name} schema")
def assert_schema(api_response: APIResponse, schema_name: str, api_version: str) -> None:
    """Assert the response body matches the named JSON schema."""
    ApiAssertions(api_response, version=api_version).schema(schema_name)


@then("the response time should be less than {max_ms:d}ms")
def assert_response_time(api_response: APIResponse, max_ms: int) -> None:
    """Assert the response was received within the time limit."""
    ApiAssertions(api_response).response_time(max_ms)


@then('the response should contain error message "{message}"')
def assert_error_message(api_response: APIResponse, message: str) -> None:
    """Assert the response body contains the expected error message."""
    ApiAssertions(api_response).body_contains("message", message)

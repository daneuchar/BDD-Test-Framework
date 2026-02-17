"""Auth feature step definitions — thin glue delegating to services and builders."""

from __future__ import annotations

from pytest_bdd import given, parsers, when

from config.settings import settings
from core.client.base_client import APIResponse
from data.factories import AuthFactory
from models.auth import LoginRequest, RefreshRequest
from models.builders.auth_builder import AuthBuilder
from services.auth_service import AuthService


@given("valid login credentials", target_fixture="login_payload")
def valid_credentials(auth_factory: AuthFactory) -> LoginRequest:
    """Build login credentials from default settings."""
    return auth_factory.valid_credentials()


@given("login credentials with wrong password", target_fixture="login_payload")
def wrong_password_credentials(auth_factory: AuthFactory) -> LoginRequest:
    """Build login credentials with an incorrect password."""
    return auth_factory.invalid_password()


@given("login credentials for a non-existent user", target_fixture="login_payload")
def nonexistent_user_credentials() -> LoginRequest:
    """Build login credentials for a user that does not exist."""
    return AuthBuilder().with_credentials("nonexistent_user_xyz", "P@ssw0rd123").build()


@given("login credentials for a locked account", target_fixture="login_payload")
def locked_account_credentials() -> LoginRequest:
    """Build login credentials for a known locked account."""
    return AuthBuilder().with_credentials("locked_user", "P@ssw0rd123").build()


@given(parsers.parse("login credentials with {field} missing"), target_fixture="login_payload")
def credentials_missing_field(field: str) -> LoginRequest:
    """Build login credentials with a required field omitted."""
    fields = {"username": settings.auth_username, "password": settings.auth_password}
    fields[field] = ""
    return LoginRequest(**fields)


@given("a valid refresh token", target_fixture="refresh_payload")
def valid_refresh_token(auth_service: AuthService, auth_factory: AuthFactory) -> RefreshRequest:
    """Obtain a valid refresh token by logging in first."""
    response = auth_service.login(auth_factory.valid_credentials())
    return RefreshRequest(refresh_token=response.json_data["refreshToken"])


@given("an expired refresh token", target_fixture="refresh_payload")
def expired_refresh_token(auth_factory: AuthFactory) -> RefreshRequest:
    """Build a refresh request with a known expired token."""
    return auth_factory.expired_token()


@given("an invalid refresh token", target_fixture="refresh_payload")
def invalid_refresh_token() -> RefreshRequest:
    """Build a refresh request with a malformed token."""
    return RefreshRequest.model_construct(refresh_token="invalid.token.value")


@given("no refresh token", target_fixture="refresh_payload")
def no_refresh_token() -> RefreshRequest:
    """Build a refresh request with an empty token."""
    return RefreshRequest.model_construct(refresh_token="")


@when("I send a login request", target_fixture="api_response")
def send_login(auth_service: AuthService, login_payload) -> APIResponse:
    """POST login credentials via AuthService."""
    return auth_service.login(login_payload)


@when("I send a token refresh request", target_fixture="api_response")
def send_refresh(auth_service: AuthService, refresh_payload) -> APIResponse:
    """POST refresh token via AuthService."""
    return auth_service.refresh(refresh_payload)

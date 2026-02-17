"""Authentication fixtures — token retrieval and authenticated client."""

from __future__ import annotations

import pytest

from config.settings import settings
from core.auth.bearer_auth import BearerAuth
from core.client.sync_client import SyncAPIClient
from models.auth import LoginRequest
from services.auth_service import AuthService


@pytest.fixture(scope="session")
def auth_token(auth_service: AuthService) -> str:
    """Session-scoped bearer token.

    Uses ``BEARER_TOKEN`` env var when set, otherwise falls back to
    obtaining a token via ``AuthService.login()``.
    """
    if settings.bearer_token:
        return settings.bearer_token
    credentials = LoginRequest(
        username=settings.auth_username,
        password=settings.auth_password,
    )
    response = auth_service.login(credentials)
    return response.json_data["access_token"]


@pytest.fixture(scope="session")
def authenticated_client(api_client: SyncAPIClient, auth_token: str) -> SyncAPIClient:
    """Session-scoped API client with bearer auth injected."""
    api_client.set_auth(BearerAuth(auth_token))
    return api_client

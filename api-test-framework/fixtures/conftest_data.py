"""Data fixtures — service objects and test data factories."""

from __future__ import annotations

import pytest

from core.client.sync_client import SyncAPIClient
from data.factories import AuthFactory, EventFactory, UserFactory
from services.auth_service import AuthService
from services.user_service import UserService


@pytest.fixture(scope="session")
def user_factory() -> UserFactory:
    """Session-scoped user factory (worker-aware via BaseFactory seed)."""
    return UserFactory()


@pytest.fixture(scope="session")
def auth_factory() -> AuthFactory:
    """Session-scoped auth factory (worker-aware via BaseFactory seed)."""
    return AuthFactory()


@pytest.fixture(scope="session")
def user_service(authenticated_client: SyncAPIClient) -> UserService:
    """Session-scoped user service using the authenticated client."""
    return UserService(authenticated_client)


@pytest.fixture(scope="session")
def event_factory() -> EventFactory:
    """Session-scoped event factory (worker-aware via BaseFactory seed)."""
    return EventFactory()


@pytest.fixture(scope="session")
def auth_service(api_client: SyncAPIClient) -> AuthService:
    """Session-scoped auth service using the unauthenticated client."""
    return AuthService(api_client)

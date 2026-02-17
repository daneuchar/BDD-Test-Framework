"""Client fixtures — session-scoped, worker-aware API clients."""

from __future__ import annotations

import pytest

from config.settings import settings
from config.version_registry import get_default_version
from core.client.sync_client import SyncAPIClient
from core.client.async_client import AsyncAPIClient


@pytest.fixture(scope="session")
def api_version(request: pytest.FixtureRequest) -> str | None:
    """Resolve the API version from CLI option or environment default."""
    cli_value = request.config.getoption("--api-version", default=None)
    if cli_value is not None:
        return cli_value
    return get_default_version(settings.env).value


@pytest.fixture(scope="session")
def api_client(worker_id: str, api_version: str | None) -> SyncAPIClient:
    """Session-scoped synchronous API client, unique per xdist worker."""
    client = SyncAPIClient(
        base_url=settings.base_url,
        timeout=settings.timeout,
        default_headers={"X-Worker-ID": worker_id},
        api_version=api_version,
    )
    yield client
    client.close()


@pytest.fixture(scope="session")
async def async_api_client(worker_id: str, api_version: str | None) -> AsyncAPIClient:
    """Session-scoped asynchronous API client."""
    client = AsyncAPIClient(
        base_url=settings.base_url,
        timeout=settings.timeout,
        default_headers={"X-Worker-ID": worker_id},
        api_version=api_version,
    )
    yield client
    await client.close()

"""Parallel isolation plugin for pytest-xdist.

Seeds Faker instances with a deterministic hash based on the xdist worker ID
so that each worker generates unique but reproducible test data.

Registered via pytest.ini: ``-p plugins.parallel_isolation``
"""

from __future__ import annotations

import hashlib

import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Seed Faker with a worker-specific hash when running under xdist."""
    worker_id = _get_worker_id_from_env()
    if worker_id != "master":
        seed = int(hashlib.sha256(worker_id.encode()).hexdigest(), 16) % (2**32)
        try:
            from faker import Faker

            Faker.seed(seed)
        except ImportError:
            pass


def _get_worker_id_from_env() -> str:
    """Return the xdist worker id from the environment, or 'master'."""
    import os

    return os.environ.get("PYTEST_XDIST_WORKER", "master")


@pytest.fixture(scope="session")
def worker_id() -> str:
    """Return the xdist worker ID ('master' for single-process runs, 'gw0' etc. for xdist)."""
    return _get_worker_id_from_env()

"""Base factory with Faker instance and worker-aware seed management."""

from __future__ import annotations

import os

from faker import Faker


class BaseFactory:
    """Base class for all data factories.

    Provides a :class:`Faker` instance seeded deterministically based on the
    ``PYTEST_XDIST_WORKER`` environment variable so that parallel workers
    produce reproducible but non-overlapping data.
    """

    def __init__(self, locale: str = "en_US") -> None:
        self.fake = Faker(locale)
        self._apply_worker_seed()

    def _apply_worker_seed(self) -> None:
        """Seed Faker based on the pytest-xdist worker ID.

        Worker IDs look like ``gw0``, ``gw1``, etc.  When running without
        xdist the env var is absent and we fall back to a fixed seed of 0.
        """
        worker_id = os.environ.get("PYTEST_XDIST_WORKER", "gw0")
        numeric_part = int("".join(ch for ch in worker_id if ch.isdigit()) or "0")
        seed = 10_000 + numeric_part
        Faker.seed(seed)
        self.fake.seed_instance(seed)

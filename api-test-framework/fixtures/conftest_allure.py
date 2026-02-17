"""Allure environment info fixtures."""

from __future__ import annotations

import allure
import pytest

from config.settings import settings


@pytest.fixture(autouse=True)
def allure_environment_info(worker_id: str) -> None:
    """Attach environment metadata to every allure test report."""
    allure.dynamic.parameter("base_url", settings.base_url)
    allure.dynamic.parameter("environment", settings.env)
    allure.dynamic.parameter("worker_id", worker_id)

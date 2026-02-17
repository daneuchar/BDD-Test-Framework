"""Allure pytest plugin -- auto-attach request/response on failure and environment info.

Registered via pytest.ini: ``-p plugins.allure_plugin``
"""

from __future__ import annotations

import threading
from typing import Any

import allure
import pytest

# Thread-local storage for the most recent request/response data.
# Clients store data here so the plugin can attach it on failure.
_thread_local = threading.local()


def store_request_data(request_data: dict[str, Any]) -> None:
    """Store the latest request data in thread-local storage."""
    _thread_local.last_request = request_data


def store_response_data(response_data: dict[str, Any]) -> None:
    """Store the latest response data in thread-local storage."""
    _thread_local.last_response = response_data


def get_request_data() -> dict[str, Any] | None:
    return getattr(_thread_local, "last_request", None)


def get_response_data() -> dict[str, Any] | None:
    return getattr(_thread_local, "last_response", None)


def clear_request_response_data() -> None:
    _thread_local.last_request = None
    _thread_local.last_response = None


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> Any:
    """Attach the last request/response to allure on test failure."""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        request_data = get_request_data()
        response_data = get_response_data()

        if request_data:
            allure.attach(
                str(request_data),
                name="Last Request",
                attachment_type=allure.attachment_type.JSON,
            )
        if response_data:
            allure.attach(
                str(response_data),
                name="Last Response",
                attachment_type=allure.attachment_type.JSON,
            )

    # Clear thread-local data after each test
    clear_request_response_data()


def pytest_sessionstart(session: pytest.Session) -> None:
    """Write allure environment.properties at session start."""
    try:
        from config.settings import settings
    except ImportError:
        return

    allure_dir = session.config.getoption("--alluredir", default=None)
    if not allure_dir:
        return

    from pathlib import Path

    env_file = Path(allure_dir) / "environment.properties"
    env_file.parent.mkdir(parents=True, exist_ok=True)
    env_file.write_text(
        f"base_url={settings.base_url}\n"
        f"environment={settings.env}\n"
        f"timeout={settings.timeout}\n"
        f"max_retries={settings.max_retries}\n"
    )


def pytest_bdd_step_error(
    request: pytest.FixtureRequest,
    feature: Any,
    scenario: Any,
    step: Any,
    step_func: Any,
    step_func_args: dict,
    exception: BaseException,
) -> None:
    """Attach BDD step context to allure when a step fails."""
    allure.attach(
        f"Feature: {feature.name}\n"
        f"Scenario: {scenario.name}\n"
        f"Step: {step.name}\n"
        f"Error: {exception!r}",
        name="BDD Step Error Context",
        attachment_type=allure.attachment_type.TEXT,
    )

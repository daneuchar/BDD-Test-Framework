"""Root conftest.py -- plugin registration, fixture imports, and session hooks.

This file is intentionally thin. Business logic belongs in services, not here.
"""

from __future__ import annotations

import allure
import pytest

# ---------------------------------------------------------------------------
# Fixture imports -- pytest discovers fixtures from these modules
# ---------------------------------------------------------------------------
pytest_plugins = [
    "fixtures.conftest_client",
    "fixtures.conftest_auth",
    "fixtures.conftest_data",
    "fixtures.conftest_messaging",
    "fixtures.conftest_allure",
]


# ---------------------------------------------------------------------------
# Collection hooks
# ---------------------------------------------------------------------------
_MARKER_SEVERITY_MAP = {
    "critical": allure.severity_level.CRITICAL,
    "smoke": allure.severity_level.BLOCKER,
    "regression": allure.severity_level.NORMAL,
    "auth": allure.severity_level.NORMAL,
    "users": allure.severity_level.NORMAL,
    "events": allure.severity_level.NORMAL,
}


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    """Map custom pytest markers to allure severity levels."""
    for item in items:
        for marker_name, severity in _MARKER_SEVERITY_MAP.items():
            if item.get_closest_marker(marker_name):
                item.add_marker(allure.severity(severity))
                break  # first matching marker wins

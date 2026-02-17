"""Pytest plugin for API version selection.

Adds a ``--api-version`` CLI option and an ``api_version`` marker so that
individual tests can declare which API version they target.
"""

from __future__ import annotations

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--api-version",
        default=None,
        help="API version to test against (e.g. v1, v2). Defaults to the value in settings.",
    )


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "api_version(version): run test against specific API version",
    )

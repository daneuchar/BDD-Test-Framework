"""Scenario collection for features/auth/token_refresh.feature."""

from pytest_bdd import scenarios

from steps.common_steps import *  # noqa: F401,F403
from steps.auth_steps import *  # noqa: F401,F403

scenarios("auth/token_refresh.feature")

"""Scenario collection for features/auth/login.feature."""

from pytest_bdd import scenarios

from steps.common_steps import *  # noqa: F401,F403
from steps.auth_steps import *  # noqa: F401,F403

scenarios("auth/login.feature")

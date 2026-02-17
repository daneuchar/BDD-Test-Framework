"""Scenario collection for features/users/create_user.feature."""

from pytest_bdd import scenarios

from steps.common_steps import *  # noqa: F401,F403
from steps.user_steps import *  # noqa: F401,F403

scenarios("users/create_user.feature")

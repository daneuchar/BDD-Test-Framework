"""User feature step definitions — thin glue delegating to services and builders."""

from __future__ import annotations

from pytest_bdd import given, parsers, when

from core.client.base_client import APIResponse
from data.factories import UserFactory
from models.user import CreateUserRequest, UpdateUserRequest
from services.user_service import UserService


@given("I am authenticated as an admin", target_fixture="authenticated")
def authenticated_as_admin(authenticated_client):
    """Ensure we use the authenticated client for subsequent requests."""
    return authenticated_client


@given("a valid user payload", target_fixture="user_payload")
def valid_user_payload(user_factory: UserFactory) -> CreateUserRequest:
    """Build a valid user creation payload via the factory."""
    return user_factory.create()


@given("a valid user payload with all optional fields", target_fixture="user_payload")
def valid_user_payload_all_fields(user_factory: UserFactory) -> CreateUserRequest:
    """Build a user payload with all optional fields populated."""
    return user_factory.admin()


@given(parsers.parse('a user payload with {field} set to "{value}"'), target_fixture="user_payload")
def user_payload_with_field(user_factory: UserFactory, field: str, value: str) -> CreateUserRequest:
    """Build a user payload then override a specific field."""
    base = user_factory.create()
    return base.model_copy(update={field: value or None})


@given("an existing user", target_fixture="existing_user")
def existing_user(user_service: UserService, user_factory: UserFactory):
    """Create a user via the API and return the response data."""
    return user_service.create(user_factory.create()).json_data


@given("at least 2 existing users", target_fixture="existing_users")
def at_least_2_users(user_service: UserService, user_factory: UserFactory):
    """Ensure at least 2 users exist in the system."""
    return [user_service.create(u).json_data for u in user_factory.create_batch(2)]


@given("at least 5 existing users", target_fixture="existing_users")
def at_least_5_users(user_service: UserService, user_factory: UserFactory):
    """Ensure at least 5 users exist in the system."""
    return [user_service.create(u).json_data for u in user_factory.create_batch(5)]


@given("a valid full user update payload", target_fixture="update_payload")
def full_update_payload(user_factory: UserFactory) -> UpdateUserRequest:
    """Build a full update payload with all fields populated."""
    data = user_factory.create()
    return UpdateUserRequest(name=data.name, email=data.email, role=data.role)


@given("a partial user update payload", target_fixture="update_payload")
def partial_update_payload(user_factory: UserFactory) -> UpdateUserRequest:
    """Build a partial update payload with only the name field."""
    return UpdateUserRequest(name=user_factory.fake.name())


@given(parsers.parse('an update payload with {field} set to "{value}"'), target_fixture="update_payload")
def update_payload_with_field(field: str, value: str) -> UpdateUserRequest:
    """Build an update payload with a specific field overridden."""
    return UpdateUserRequest(**{field: value or None})


@when("I create a new user", target_fixture="api_response")
def create_user(user_service: UserService, user_payload) -> APIResponse:
    """POST a new user via UserService."""
    return user_service.create(user_payload)


@when("I create a new user without authentication", target_fixture="api_response")
def create_user_no_auth(api_client, user_payload) -> APIResponse:
    """POST a new user using the unauthenticated client."""
    return UserService(api_client).create(user_payload)


@when("I get the user by ID", target_fixture="api_response")
def get_user_by_id(user_service: UserService, existing_user) -> APIResponse:
    """GET a user by their ID."""
    return user_service.get(existing_user["id"])


@when("I get a user with a non-existent ID", target_fixture="api_response")
def get_nonexistent_user(user_service: UserService) -> APIResponse:
    """GET a user with an ID that does not exist."""
    return user_service.get("00000000-0000-0000-0000-000000000000")


@when("I list all users", target_fixture="api_response")
def list_users(user_service: UserService) -> APIResponse:
    """GET the list of all users."""
    return user_service.list()


@when(parsers.parse("I list users with page {page:d} and page_size {page_size:d}"), target_fixture="api_response")
def list_users_paginated(user_service: UserService, page: int, page_size: int) -> APIResponse:
    """GET users with pagination parameters."""
    return user_service.list(page=page, size=page_size)


@when("I list all users without authentication", target_fixture="api_response")
def list_users_no_auth(api_client) -> APIResponse:
    """GET users using the unauthenticated client."""
    return UserService(api_client).list()


@when("I update the user via PUT", target_fixture="api_response")
def update_user_put(user_service: UserService, existing_user, update_payload) -> APIResponse:
    """PUT update a user via UserService."""
    return user_service.update(existing_user["id"], update_payload)


@when("I update the user via PATCH", target_fixture="api_response")
def update_user_patch(user_service: UserService, existing_user, update_payload) -> APIResponse:
    """PATCH update a user via UserService."""
    return user_service.partial_update(existing_user["id"], update_payload)


@when("I update a non-existent user via PUT", target_fixture="api_response")
def update_nonexistent_user(user_service: UserService, update_payload) -> APIResponse:
    """PUT update a user that does not exist."""
    return user_service.update("00000000-0000-0000-0000-000000000000", update_payload)


@when("I update the user via PUT without authentication", target_fixture="api_response")
def update_user_no_auth(api_client, existing_user, update_payload) -> APIResponse:
    """PUT update a user using the unauthenticated client."""
    return UserService(api_client).update(existing_user["id"], update_payload)

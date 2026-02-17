"""Service object for User API endpoints."""

from __future__ import annotations

import allure

from config.endpoints import Endpoints
from core.client.base_client import APIResponse
from models.user import CreateUserRequest, UpdateUserRequest
from models.generated.v1.user_response import UserResponse
from services.base_service import BaseService


class UserService(BaseService):
    """CRUD operations against the ``/users`` resource."""

    @allure.step("Create user")
    def create(self, user: CreateUserRequest) -> APIResponse:
        """POST /users -- create a new user.

        Args:
            user: The user data to create.

        Returns:
            APIResponse whose ``json_data`` matches :class:`UserResponse`.
        """
        return self._request("POST", Endpoints.USERS.url(), body=user)

    @allure.step("Get user by ID: {user_id}")
    def get(self, user_id: str) -> APIResponse:
        """GET /users/{user_id} -- retrieve a single user.

        Args:
            user_id: UUID of the user to retrieve.

        Returns:
            APIResponse whose ``json_data`` matches :class:`UserResponse`.
        """
        return self._request("GET", Endpoints.USER_BY_ID.url(user_id=user_id))

    @allure.step("Update user: {user_id}")
    def update(self, user_id: str, data: UpdateUserRequest) -> APIResponse:
        """PUT /users/{user_id} -- full update of a user.

        Args:
            user_id: UUID of the user to update.
            data:    The fields to update.

        Returns:
            APIResponse whose ``json_data`` matches :class:`UserResponse`.
        """
        return self._request(
            "PUT", Endpoints.USER_BY_ID.url(user_id=user_id), body=data
        )

    @allure.step("Partial update user: {user_id}")
    def partial_update(self, user_id: str, data: UpdateUserRequest) -> APIResponse:
        """PATCH /users/{user_id} -- partial update of a user.

        Args:
            user_id: UUID of the user to update.
            data:    The fields to patch (only non-None fields are sent).

        Returns:
            APIResponse whose ``json_data`` matches :class:`UserResponse`.
        """
        return self._request(
            "PATCH", Endpoints.USER_BY_ID.url(user_id=user_id), body=data
        )

    @allure.step("Delete user: {user_id}")
    def delete(self, user_id: str) -> APIResponse:
        """DELETE /users/{user_id} -- delete a user.

        Args:
            user_id: UUID of the user to delete.

        Returns:
            APIResponse (typically 204 No Content).
        """
        return self._request("DELETE", Endpoints.USER_BY_ID.url(user_id=user_id))

    @allure.step("List users (page={page}, size={size})")
    def list(self, page: int = 1, size: int = 10) -> APIResponse:
        """GET /users -- list users with pagination.

        Args:
            page: Page number (1-indexed).
            size: Number of results per page.

        Returns:
            APIResponse whose ``json_data`` contains a list of users.
        """
        return self._request(
            "GET", Endpoints.USERS.url(), params={"page": page, "size": size}
        )

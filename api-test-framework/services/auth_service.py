"""Service object for Auth API endpoints."""

from __future__ import annotations

import allure

from config.endpoints import Endpoints
from core.client.base_client import APIResponse
from models.auth import LoginRequest, RefreshRequest, TokenResponse
from services.base_service import BaseService


class AuthService(BaseService):
    """Authentication operations against ``/auth/*`` endpoints."""

    @allure.step("Login")
    def login(self, credentials: LoginRequest) -> APIResponse:
        """POST /auth/login -- authenticate and receive tokens.

        Args:
            credentials: Username and password payload.

        Returns:
            APIResponse whose ``json_data`` matches :class:`TokenResponse`.
        """
        return self._request("POST", Endpoints.AUTH_LOGIN.url(), body=credentials)

    @allure.step("Refresh token")
    def refresh(self, token: RefreshRequest) -> APIResponse:
        """POST /auth/refresh -- exchange a refresh token for new tokens.

        Args:
            token: Refresh token payload.

        Returns:
            APIResponse whose ``json_data`` matches :class:`TokenResponse`.
        """
        return self._request("POST", Endpoints.AUTH_REFRESH.url(), body=token)

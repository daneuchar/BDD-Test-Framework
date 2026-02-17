"""Object Mother / Factory for auth test data."""

from __future__ import annotations

from models.auth import LoginRequest, RefreshRequest
from models.builders.auth_builder import AuthBuilder

from .base_factory import BaseFactory


class AuthFactory(BaseFactory):
    """Generate authentication-related test data."""

    def valid_credentials(self) -> LoginRequest:
        """Create a login request with valid default credentials."""
        return AuthBuilder().with_defaults().build()

    def expired_token(self) -> RefreshRequest:
        """Create a refresh request with a clearly expired/invalid token."""
        return RefreshRequest.model_construct(
            refresh_token="expired.jwt.token.payload.signature",
        )

    def invalid_password(self) -> LoginRequest:
        """Create a login request with a random (incorrect) password."""
        return (
            AuthBuilder()
            .with_credentials("testuser", self.fake.password(length=8))
            .build()
        )

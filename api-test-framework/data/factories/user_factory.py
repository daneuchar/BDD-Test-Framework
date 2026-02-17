"""Object Mother / Factory for user test data."""

from __future__ import annotations

from models.user import CreateUserRequest
from models.builders.user_builder import UserBuilder

from .base_factory import BaseFactory


class UserFactory(BaseFactory):
    """Generate :class:`CreateUserRequest` instances with randomized data."""

    def create(self) -> CreateUserRequest:
        """Create a user request with random valid data."""
        return (
            UserBuilder()
            .with_name(self.fake.name())
            .with_email(self.fake.unique.email())
            .with_password(self.fake.password(length=12, special_chars=True))
            .with_role("user")
            .build()
        )

    def admin(self) -> CreateUserRequest:
        """Create an admin user request with random valid data."""
        return (
            UserBuilder()
            .with_name(self.fake.name())
            .with_email(self.fake.unique.email())
            .with_password(self.fake.password(length=12, special_chars=True))
            .with_role("admin")
            .build()
        )

    def create_batch(self, n: int) -> list[CreateUserRequest]:
        """Create *n* user requests with random valid data."""
        return [self.create() for _ in range(n)]

    def invalid_email(self) -> CreateUserRequest:
        """Create a user request with an intentionally invalid email.

        Bypasses Pydantic validation by constructing the model directly.
        """
        return CreateUserRequest.model_construct(
            name=self.fake.name(),
            email="not-an-email",
            password=self.fake.password(length=12, special_chars=True),
            role="user",
        )

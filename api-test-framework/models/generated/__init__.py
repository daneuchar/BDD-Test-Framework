"""Model registry — maps schema names to generated Pydantic classes.

Usage::

    from models.generated import resolve_model

    model_cls = resolve_model("user_response", version="v1")
"""

from __future__ import annotations

from typing import Type

from pydantic import BaseModel

from models.generated.v1 import (
    ErrorResponse as V1ErrorResponse,
    LoginResponse as V1LoginResponse,
    UserCreatedEvent as V1UserCreatedEvent,
    UserListResponse as V1UserListResponse,
    UserResponse as V1UserResponse,
    UserUpdatedEvent as V1UserUpdatedEvent,
)
from models.generated.v2 import (
    ErrorResponse as V2ErrorResponse,
    LoginResponse as V2LoginResponse,
    UserCreatedEvent as V2UserCreatedEvent,
    UserListResponse as V2UserListResponse,
    UserResponse as V2UserResponse,
    UserUpdatedEvent as V2UserUpdatedEvent,
)


class ModelNotFoundError(KeyError):
    """Raised when a schema name cannot be resolved to a generated model."""


_DEFAULT_VERSION = "v1"

_REGISTRY: dict[str, dict[str, Type[BaseModel]]] = {
    "user_response": {"v1": V1UserResponse, "v2": V2UserResponse},
    "user_list_response": {"v1": V1UserListResponse, "v2": V2UserListResponse},
    "login_response": {"v1": V1LoginResponse, "v2": V2LoginResponse},
    "error_response": {"v1": V1ErrorResponse, "v2": V2ErrorResponse},
    "user_created_event": {"v1": V1UserCreatedEvent, "v2": V2UserCreatedEvent},
    "user_updated_event": {"v1": V1UserUpdatedEvent, "v2": V2UserUpdatedEvent},
}


def resolve_model(schema_name: str, version: str | None = None) -> Type[BaseModel]:
    """Resolve a schema name to a generated Pydantic model class.

    Args:
        schema_name: Registry key (e.g. ``"user_response"``).
        version: API version string (e.g. ``"v1"``). Falls back to default.

    Raises:
        ModelNotFoundError: If schema_name or version is not in the registry.
    """
    version = version or _DEFAULT_VERSION

    versions = _REGISTRY.get(schema_name)
    if versions is None:
        raise ModelNotFoundError(
            f"No generated model registered for schema '{schema_name}'"
        )

    model = versions.get(version)
    if model is None:
        raise ModelNotFoundError(
            f"No generated model for schema '{schema_name}' version '{version}'"
        )

    return model

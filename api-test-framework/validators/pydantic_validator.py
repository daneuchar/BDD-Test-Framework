"""Pydantic model validation strategy."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Type

from pydantic import BaseModel, ValidationError

from .base_validator import BaseValidator, ValidationResult

if TYPE_CHECKING:
    from core.client.base_client import APIResponse


class PydanticValidator(BaseValidator):
    """Validate a response body against a Pydantic model class.

    Parameters:
        model: The Pydantic model class to validate against.
    """

    def __init__(self, model: Type[BaseModel]) -> None:
        self.model = model

    def validate(self, response: APIResponse, **kwargs: Any) -> ValidationResult:
        if response.json_data is None:
            return ValidationResult(is_valid=False, errors=["Response body is empty"])

        try:
            self.model.model_validate(response.json_data)
            return ValidationResult(is_valid=True)
        except ValidationError as exc:
            errors = [
                f"{'.'.join(str(loc) for loc in e['loc'])}: {e['msg']}"
                for e in exc.errors()
            ]
            return ValidationResult(is_valid=False, errors=errors)

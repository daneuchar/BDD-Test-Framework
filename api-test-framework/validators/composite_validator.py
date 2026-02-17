"""Composite pattern — run multiple validators and collect all errors."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .base_validator import BaseValidator, ValidationResult

if TYPE_CHECKING:
    from core.client.base_client import APIResponse


class CompositeValidator(BaseValidator):
    """Run a list of validators in sequence and merge results.

    Parameters:
        validators: Ordered list of :class:`BaseValidator` instances.
    """

    def __init__(self, validators: list[BaseValidator]) -> None:
        self._validators = list(validators)

    def add(self, validator: BaseValidator) -> CompositeValidator:
        """Append a validator to the chain."""
        self._validators.append(validator)
        return self

    def validate(self, response: APIResponse, **kwargs: Any) -> ValidationResult:
        result = ValidationResult(is_valid=True)
        for validator in self._validators:
            result = result.merge(validator.validate(response, **kwargs))
        return result

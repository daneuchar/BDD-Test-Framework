"""Strategy ABC for response validation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from core.client.base_client import APIResponse


@dataclass
class ValidationResult:
    """Outcome of a validation run."""

    is_valid: bool
    errors: list[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.is_valid

    def merge(self, other: ValidationResult) -> ValidationResult:
        """Combine two results into one."""
        return ValidationResult(
            is_valid=self.is_valid and other.is_valid,
            errors=self.errors + other.errors,
        )


class BaseValidator(ABC):
    """Abstract base for all response validators."""

    @abstractmethod
    def validate(self, response: APIResponse, **kwargs: Any) -> ValidationResult:
        """Validate *response* and return a :class:`ValidationResult`."""

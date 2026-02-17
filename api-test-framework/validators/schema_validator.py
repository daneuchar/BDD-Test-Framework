"""JSON Schema validation strategy."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

import jsonschema

from .base_validator import BaseValidator, ValidationResult

if TYPE_CHECKING:
    from core.client.base_client import APIResponse

# Resolve schemas/ directory relative to the project root
_SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "schemas"


class SchemaValidator(BaseValidator):
    """Validate a response body against a JSON schema file.

    Parameters:
        schema_name: File stem inside ``schemas/`` (e.g. ``"user_response"``).
        schema:      Alternatively, pass an in-memory schema dict directly.
    """

    def __init__(
        self,
        schema_name: str | None = None,
        schema: dict[str, Any] | None = None,
        version: str | None = None,
    ) -> None:
        if schema is not None:
            self._schema = schema
        elif schema_name is not None:
            schema_path = self._resolve_schema_path(schema_name, version)
            if not schema_path.exists():
                raise FileNotFoundError(f"Schema file not found: {schema_path}")
            self._schema = json.loads(schema_path.read_text(encoding="utf-8"))
        else:
            raise ValueError("Either schema_name or schema must be provided")

    @staticmethod
    def _resolve_schema_path(schema_name: str, version: str | None) -> Path:
        """Resolve schema file path, preferring versioned directory if it exists."""
        if version is not None:
            versioned = _SCHEMAS_DIR / version / f"{schema_name}.json"
            if versioned.exists():
                return versioned
        return _SCHEMAS_DIR / f"{schema_name}.json"

    def validate(self, response: APIResponse, **kwargs: Any) -> ValidationResult:
        if response.json_data is None:
            return ValidationResult(is_valid=False, errors=["Response body is empty"])

        errors: list[str] = []
        validator = jsonschema.Draft7Validator(self._schema)
        for error in validator.iter_errors(response.json_data):
            errors.append(f"{error.json_path}: {error.message}")

        return ValidationResult(is_valid=len(errors) == 0, errors=errors)

# AUTO-GENERATED -- DO NOT EDIT
# Re-generate with: python scripts/generate_models.py

from __future__ import annotations

from typing import Optional

from pydantic import Field

from models.base_model import BaseDTO


class ErrorDetail(BaseDTO):
    """Individual field-level error detail."""

    field: str
    message: str


class ErrorResponse(BaseDTO):
    """Schema for standard API error responses."""

    error: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    details: Optional[list[ErrorDetail]] = None
    status_code: Optional[int] = Field(default=None, alias="statusCode")

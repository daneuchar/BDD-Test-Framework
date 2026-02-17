"""Base DTO model with shared Pydantic configuration."""

from pydantic import BaseModel, ConfigDict


class BaseDTO(BaseModel):
    """Base data-transfer object for all request/response models.

    Configuration:
        - ``from_attributes``: Allow construction from ORM-style objects.
        - ``populate_by_name``: Accept both alias and field name.
        - ``str_strip_whitespace``: Trim whitespace from string fields.
    """

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )

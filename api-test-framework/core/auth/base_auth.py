"""Strategy ABC for authentication."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.client.base_client import PreparedRequest


class BaseAuth(ABC):
    """Abstract base for all authentication strategies.

    Implementations mutate the :class:`PreparedRequest` (typically by
    adding an ``Authorization`` header) and return it.
    """

    @abstractmethod
    def authenticate(self, request: PreparedRequest) -> PreparedRequest:
        """Apply credentials to *request* and return it."""

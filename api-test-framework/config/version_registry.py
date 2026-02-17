"""API version registry.

Centralises version-specific configuration (path prefixes, schema
directories, endpoint overrides) so that tests and helpers can resolve
version details without hard-coding paths.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict


class APIVersion(str, Enum):
    V1 = "v1"
    V2 = "v2"


@dataclass(frozen=True)
class VersionConfig:
    version: APIVersion
    path_prefix: str  # e.g. "api/v1"
    endpoint_overrides: Dict[str, str] = field(default_factory=dict)


# Default API version per environment name.
ENV_DEFAULT_VERSION: Dict[str, APIVersion] = {
    "dev": APIVersion.V2,
    "staging": APIVersion.V1,
    "prod": APIVersion.V1,
}

_REGISTRY: Dict[APIVersion, VersionConfig] = {
    APIVersion.V1: VersionConfig(
        version=APIVersion.V1,
        path_prefix="api/v1",
    ),
    APIVersion.V2: VersionConfig(
        version=APIVersion.V2,
        path_prefix="api/v2",
    ),
}


def get_version_config(version: APIVersion) -> VersionConfig:
    """Return the ``VersionConfig`` for *version*, or raise ``KeyError``."""
    return _REGISTRY[version]


def get_default_version(env: str) -> APIVersion:
    """Return the default ``APIVersion`` for the given environment name."""
    return ENV_DEFAULT_VERSION.get(env, APIVersion.V1)


def register_version(config: VersionConfig) -> None:
    """Register a custom ``VersionConfig`` (useful for extension)."""
    _REGISTRY[config.version] = config

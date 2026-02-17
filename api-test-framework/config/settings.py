"""Singleton settings module using pydantic-settings.

Loads configuration from environment variables or a .env file.
Module-level ``settings`` instance acts as a singleton across the framework.
"""

from enum import Enum
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    base_url: str = Field(
        default="http://localhost:8000",
        description="Base URL for the API under test",
    )
    api_version: str = Field(
        default="v1",
        description="Default API version",
    )
    env: Literal["dev", "staging", "prod"] = Field(
        default="dev",
        description="Target environment",
    )
    auth_username: str = Field(
        default="testuser",
        description="Default authentication username",
    )
    auth_password: str = Field(
        default="testpassword",
        description="Default authentication password",
    )
    timeout: int = Field(
        default=30,
        description="HTTP request timeout in seconds",
    )
    max_retries: int = Field(
        default=3,
        description="Maximum number of retry attempts for failed requests",
    )
    parallel_workers: str = Field(
        default="auto",
        description="Number of parallel workers ('auto' or integer)",
    )

    # Messaging — Azure Event Hubs
    eventhub_connection_string: str = Field(
        default="",
        description="Azure Event Hubs connection string",
    )
    eventhub_name: str = Field(
        default="",
        description="Azure Event Hub name",
    )

    # Messaging — Kafka
    kafka_bootstrap_servers: str = Field(
        default="",
        description="Kafka bootstrap servers",
    )
    kafka_username: str = Field(
        default="",
        description="Kafka SASL username",
    )
    kafka_password: str = Field(
        default="",
        description="Kafka SASL password",
    )
    kafka_topic_prefix: str = Field(
        default="test-events",
        description="Prefix for Kafka test topics",
    )

    @property
    def versioned_base_url(self) -> str:
        """Return the base URL with API version path included."""
        return f"{self.base_url.rstrip('/')}/api/{self.api_version}"


settings = Settings()

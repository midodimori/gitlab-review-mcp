"""Centralized configuration."""

from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    show_logs: bool = Field(
        default=False,
        alias="GITLAB_REVIEW_MCP_SHOW_LOGS",
    )
    log_level: str = Field(default="INFO")

    gitlab_url: str = Field(
        default="https://gitlab.com",
        alias="GITLAB_URL",
        description="GitLab instance URL",
    )
    gitlab_private_token: SecretStr = Field(
        default=SecretStr(""),
        alias="GITLAB_PRIVATE_TOKEN",
        description="GitLab private access token",
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Vehicle Maintenance Scheduler"
    api_v1_prefix: str = "/api/v1"
    evaluation_base_url: str = Field(
        default="http://4.224.186.213/evaluation-service",
        description="Base URL for the evaluation service.",
    )
    request_timeout_seconds: float = Field(default=10.0, gt=0)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()


from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Delivery Enablement Control Plane"
    environment: str = "development"
    database_url: str = "sqlite:///./data/control_plane.db"
    api_key: str = "local-development-key"
    cors_origins: str = "http://localhost:8000"
    seed_demo_data: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_prefix="CONTROL_PLANE_")

    @property
    def origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

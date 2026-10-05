from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    cors_origins: list[str] = Field(
        default_factory=lambda: ["*"]
    )

    jwt_secret: SecretStr
    jwt_algorithm: str = "HS256"

    catalog_service_url: str = "http://catalog-service:8000"
    order_service_url: str = "http://order-service:8000"
    auth_service_url: str = "http://auth-service:8000"


settings = Settings()
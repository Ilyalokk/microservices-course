from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    database_url: str = (
        "postgresql+asyncpg://auth:auth@localhost:5437/auth"
    )
    jwt_secret: SecretStr
    jwt_algorithm: str = "HS256"


settings = Settings()
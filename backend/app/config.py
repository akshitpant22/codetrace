from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # The full database connection URL
    DATABASE_URL: str

    # Auth & Email Settings
    JWT_SECRET: str = "change-this-super-secret-key"
    SMTP_HOST: str | None = None
    SMTP_PORT: int | None = None
    SMTP_USER: str | None = None
    SMTP_PASS: str | None = None

    @field_validator("DATABASE_URL")
    @classmethod
    def fix_database_url_protocol(cls, v: str) -> str:
        # SQLAlchemy 2.0+ requires 'postgresql://' instead of 'postgres://'
        # Supabase sometimes provides 'postgres://' in their connection strings
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()

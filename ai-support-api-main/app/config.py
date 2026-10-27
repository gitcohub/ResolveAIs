from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    app_name: str = "AI Support API"
    app_version: str = "0.2.0"
    app_api_key: str
    openai_api_key: str | None = None
    openai_model: str = "gpt-5.4-mini"
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    @property
    def use_mock_ai(self) -> bool:
        return not bool(self.openai_api_key)
@lru_cache
def get_settings() -> Settings:
    return Settings()
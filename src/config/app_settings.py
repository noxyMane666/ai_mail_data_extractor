from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    anthropic_api_key: str
    anthropic_model_name: str
    llm_default_timeout: float = 60.0
    llm_read_timeout: float = 45.0
    llm_write_timeout: float = 10.0
    llm_connect_timeout: float = 5.0
    llm_max_tokens: int = 1024

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )
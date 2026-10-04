from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    anthropic_api_key: str
    anthropic_model_name: str
    llm_default_timeout: float
    llm_read_timeout: float
    llm_write_timeout: float
    llm_connect_timeout: float
    llm_max_tokens: int

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )
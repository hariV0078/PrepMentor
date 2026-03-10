from functools import lru_cache
from pathlib import Path
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(str(DEFAULT_ENV_FILE), ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "GETLANDED Voice Backend"
    app_env: str = "development"
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8000

    sample_rate: int = 16000
    silence_frames_threshold: int = 30
    vad_threshold: float = 0.35
    max_buffer_seconds: int = 30
    preload_models: bool = True

    whisper_model: str = "tiny.en"
    gemini_model: str = "gemini-2.5-flash-lite-preview-06-17"
    tts_model: str = "kokoro-82m"

    gemini_api_key: str | None = None

    @field_validator("gemini_model")
    @classmethod
    def normalize_gemini_model(cls, value: str) -> str:
        return value.strip()


@lru_cache
def get_settings() -> Settings:
    return Settings()

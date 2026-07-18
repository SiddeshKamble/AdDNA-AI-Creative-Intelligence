from typing import Optional
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openrouter_api_key: Optional[str] = None
    openrouter_model: str = "openai/gpt-4.1-mini"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    foreplay_api_key: Optional[str] = None
    foreplay_base_url: str = "https://public.api.foreplay.co"
    foreplay_discovery_path: str = "/api/discovery/ads"
    foreplay_spyder_path: str = "/api/spyder/brand/ads"

    pipispy_api_key: Optional[str] = None
    pipispy_base_url: str = "https://www.pipispy.com"
    pipispy_endpoint: str = "/open-api/v1/data"
    pipispy_adspy_uri: str = "/v3/api/open/adspy/list"

    cache_dir: Path = Path("storage/cache")
    media_dir: Path = Path("storage/media")
    reports_dir: Path = Path("storage/reports")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
for directory in (settings.cache_dir, settings.media_dir, settings.reports_dir):
    directory.mkdir(parents=True, exist_ok=True)

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    github_token: str | None = None
    x_api_bearer_token: str | None = None
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None
    anthropic_api_key: str | None = None
    twitter_bearer_token: str | None = None
    producthunt_api_key: str | None = None
    huggingface_api_token: str | None = None
    discord_webhook_url: str | None = None
    discord_bot_token: str | None = None
    discord_channel_id: str | None = None
    database_path: Path = Path("data/signal_history.db")
    schedule_daily: str = "07:00"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False

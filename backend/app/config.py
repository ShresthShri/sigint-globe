from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./sigint.db"
    poll_interval_seconds: int = 300
    adsb_base_url: str = "https://api.adsb.lol/v2"
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

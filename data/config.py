from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    tg_api_id: int
    tg_api_hash: str
    tg_bot_token: str
    tg_admins: list[int]

    class Config:
        env_file = "../.env"


@lru_cache
def get_settings():
    return Settings()

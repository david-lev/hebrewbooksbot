from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    sqlite_file_path: str
    tg_api_id: int
    tg_api_hash: str
    tg_bot_token: str
    tg_admins: list[int]
    wa_token: str
    wa_verify_token: str
    wa_phone_number: int
    wa_phone_id: str
    wa_admins: list[str]

    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    return Settings()

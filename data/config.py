from dataclasses import dataclass
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


@dataclass
class Limit:
    limit: int
    minutes: int

    @property
    def seconds(self):
        return self.minutes * 60


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    sqlite_file_path: str
    log_level: str
    under_maintenance: bool
    contact_phone: int
    tg_api_id: int
    tg_api_hash: str
    tg_bot_token: str
    tg_admins: list[int]
    wa_token: str
    wa_verify_token: str
    wa_phone_number: int
    wa_phone_id: str
    wa_admins: list[str]
    hb_api_key: str
    hb_pdf_full_limit: Limit
    hb_pdf_page_limit: Limit
    hb_image_page_limit: Limit


@lru_cache
def get_settings():
    return Settings()
